"""Service for retrieving App Store Connect performance metrics."""
from ._base import BaseService


class PerformanceService(BaseService):  # pylint: disable=too-few-public-methods
    """Service for retrieving App Store Connect performance and power metrics."""

    def get_perf_power_metrics(self, app_id: str):
        """Get a list of performance power metrics for a specific app."""
        return self.get_json(f"{self.auth.base_url}/apps/{app_id}/perfPowerMetrics")
