"""Metrics collector."""

import asyncio
import logging
import pathlib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, NoReturn, cast

import aiohttp
from pymongo.database import Database

from shared.database.reports import get_reports
from shared.model.report import get_metrics_from_reports

from collector_utilities.functions import timer
from collector_utilities.type import JSONDict
from database.measurements import create_measurement

from . import config
from .metric_collector import MetricCollector

if TYPE_CHECKING:
    from collections.abc import Coroutine


class Collector:
    """Collect measurements for all metrics."""

    def __init__(self, database: Database) -> None:
        self.__previous_metrics: dict[str, Any] = {}
        self.next_fetch: dict[str, datetime] = {}
        self.database: Database = database

    @staticmethod
    def record_health() -> None:
        """Record the current date and time in a file to allow for health checks."""
        filename = pathlib.Path(config.HEALTH_CHECK_FILE)
        try:
            with filename.open("w", encoding="utf-8") as health_check:
                health_check.write(datetime.now(tz=UTC).isoformat())
        except OSError as reason:
            logging.error("Could not write health check time stamp to %s: %s", filename, reason)  # noqa: TRY400

    async def start(self) -> NoReturn:
        """Start fetching measurements indefinitely."""
        timeout = aiohttp.ClientTimeout(total=120)
        while True:
            self.record_health()
            # The TCPConnector has limit 0, meaning unlimited, because aiohttp only closes connections when the response
            # is closed. But due to the architecture of the collector (first collect all the responses, then parse them)
            # the responses are kept around relatively long, and hence the connections too. To prevent time-outs while
            # aiohttp waits for connections to become available we don't limit the connection pool size.
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0, ssl=False),
                raise_for_status=True,
                timeout=timeout,
                trust_env=True,
            ) as session:
                with timer() as collection_timer:
                    await self.collect_metrics(session)
            sleep_duration = max(0, config.MAX_SLEEP_DURATION - collection_timer.duration)
            logging.info(
                "Collecting took %.1f seconds. Sleeping %.1f seconds...",
                collection_timer.duration,
                sleep_duration,
            )
            await asyncio.sleep(sleep_duration)

    async def collect_metrics(self, session: aiohttp.ClientSession) -> None:
        """Collect measurements for metrics, prioritizing edited metrics."""
        reports = get_reports(self.database)
        metrics = get_metrics_from_reports(reports)
        next_fetch = datetime.now(tz=UTC) + timedelta(seconds=config.MEASUREMENT_FREQUENCY)
        tasks: list[Coroutine] = []
        for metric_uuid, metric in self.__sorted_by_edit_status(cast(JSONDict, metrics)):
            if len(tasks) >= config.MEASUREMENT_LIMIT:
                break
            if self.__should_collect(metric_uuid, metric):
                tasks.append(self.collect_metric(session, metric_uuid, metric, next_fetch))
        await asyncio.gather(*tasks)

    async def collect_metric(
        self,
        session: aiohttp.ClientSession,
        metric_uuid: str,
        metric: dict,
        next_fetch: datetime,
    ) -> None:
        """Collect measurements for the metric and add them to the database."""
        self.__previous_metrics[metric_uuid] = metric
        self.next_fetch[metric_uuid] = next_fetch
        metric_collector_class = MetricCollector.get_subclass(metric["type"])
        metric_collector = metric_collector_class(session, metric)
        if measurement := await metric_collector.collect():
            measurement.metric_uuid = metric_uuid
            measurement.report_uuid = metric["report_uuid"]
            create_measurement(self.database, measurement.as_dict())

    def __sorted_by_edit_status(self, metrics: JSONDict) -> list[tuple[str, Any]]:
        """First return the edited metrics, then the rest."""
        return sorted(metrics.items(), key=lambda item: bool(self.__previous_metrics.get(item[0]) == item[1]))

    def __should_collect(self, metric_uuid: str, metric: dict) -> bool:
        """Return whether the metric should be collected.

        Metric should be collected when the user changes the configuration or when it has been collected too long ago.
        """
        metric_edited = self.__previous_metrics.get(metric_uuid) != metric
        metric_due = self.next_fetch.get(metric_uuid, datetime.min.replace(tzinfo=UTC)) <= datetime.now(tz=UTC)
        return metric_edited or metric_due
