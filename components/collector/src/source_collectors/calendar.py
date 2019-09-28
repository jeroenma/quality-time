"""Calendar metric source."""

from datetime import datetime
from typing import cast

from utilities.type import Responses, Value
from .source_collector import LocalSourceCollector


class CalendarSourceUpToDateness(LocalSourceCollector):
    """Collector class to get the number of days since a user-specified date."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        days = (datetime.now() - datetime.fromisoformat(cast(str, self._parameter("date")))).days
        return str(days)
