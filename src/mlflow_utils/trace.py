import os
import json
from datetime import datetime

class Trace:
    def __init__(self, trace_folder, experiment_id):
        self.trace_folder = trace_folder
        self.trace_id = os.path.basename(trace_folder)
        self.data = self.load_trace()
        self.experiment_id = experiment_id

    def load_trace(self):
        trace_file = os.path.join(self.trace_folder, "artifacts", "traces.json")
        if os.path.isfile(trace_file):
            with open(trace_file) as f:
                return json.load(f)
        return {}

    @property
    def metadata(self):
        spans = self.data.get("spans", [])
        start_time_ns = spans[0].get("start_time_unix_nano", 0) if spans else 0
        readable_time = self._format_time(start_time_ns)

        return {
            "trace_id": self.trace_id,
            "span_count": len(spans),
            "start_time_unix_nano": start_time_ns,
            "start_time_str": readable_time,
            "experiment_id": self.experiment_id
        }

    def _format_time(self, timestamp_ns):
        if not timestamp_ns:
            return "Unknown"
        dt = datetime.utcfromtimestamp(int(timestamp_ns) / 1e9)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def __repr__(self):
        return (f"Trace(id='{self.metadata['trace_id']}', "
                f"spans={self.metadata['span_count']}, "
                f"start='{self.metadata['start_time_str']}')")

