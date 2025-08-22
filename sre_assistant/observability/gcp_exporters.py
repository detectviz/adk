
import os
def init_optional_gcp_exporters(service_name: str="sre-assistant")->None:
    if os.getenv("ENABLE_GCM_EXPORTER","false").lower() in ("1","true","yes"):
        try:
            from opentelemetry.ext.google_cloud_monitoring import GoogleCloudMonitoringMetricsExporter
            from opentelemetry.sdk.metrics import MeterProvider, PeriodicExportingMetricReader
            from opentelemetry import metrics
            exp = GoogleCloudMonitoringMetricsExporter(prefix=service_name)
            reader = PeriodicExportingMetricReader(exp)
            mp = MeterProvider(metric_readers=[reader])
            metrics.set_meter_provider(mp)
        except Exception:
            pass
