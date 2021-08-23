"""Metric collector base classes."""

import asyncio
from typing import Optional

import aiohttp

from collector_utilities.type import JSON
from model import MetricMeasurement

from .source_collector import SourceCollector, SourceParameters


class MetricCollector:
    """Collect measurements for a specific metric."""

    subclasses: set[type["MetricCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, metric, data_model: JSON) -> None:
        self.__session = session
        self._metric = metric
        self.__data_model = data_model
        self._parameters = {
            source_uuid: SourceParameters(source, data_model) for source_uuid, source in self._metric["sources"].items()
        }

    def __init_subclass__(cls) -> None:
        MetricCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, metric_type: str) -> type["MetricCollector"]:
        """Return the subclass registered for the metric type. Return this class if no subclass is found."""
        for subclass in cls.subclasses:
            if subclass.__name__.lower() == metric_type.replace("_", ""):
                return subclass
        return cls

    async def collect(self) -> Optional[MetricMeasurement]:
        """Collect the measurements from the metric's sources."""
        collectors = []
        for source in self._metric["sources"].values():
            if collector_class := SourceCollector.get_subclass(source["type"], self._metric["type"]):
                collectors.append(collector_class(self.__session, source, self.__data_model).collect())
        if not collectors:
            return None
        measurements = await asyncio.gather(*collectors)
        for source_measurement, source_uuid in zip(measurements, self._metric["sources"]):
            source_measurement.source_uuid = source_uuid
        return MetricMeasurement(measurements)