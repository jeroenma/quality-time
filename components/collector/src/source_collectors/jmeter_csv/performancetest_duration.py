"""JMeter CSV performancetest duration collector."""

from collector_utilities.type import Value
from model import SourceResponses

from .base import JMeterCSVCollector


class JMeterCSVPerformanceTestDuration(JMeterCSVCollector):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the timestamps from the samples and calculate the duration in minutes."""
        timestamps = []
        async for samples in self._samples(responses):
            timestamps.extend([int(sample["timeStamp"]) for sample in samples])
        return str(round((max(timestamps) - min(timestamps)) / 60_000)) if timestamps else "0"
