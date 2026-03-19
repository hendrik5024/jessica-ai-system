import datetime
import time
from typing import Any


class Telemetry:

    def __init__(self, log_file: str = "jessica_system_log.txt") -> None:
        self.log_file = log_file

    def log(self, source: str, message: str) -> None:

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        entry = f"[{timestamp}] {source} -> {message}"

        print(entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def log_start(self, task: dict[str, Any]) -> dict[str, Any]:

        return {
            "task": task,
            "start_time": time.time()
        }

    def log_end(self, record: dict[str, Any], result: Any) -> dict[str, Any]:

        record["end_time"] = time.time()
        record["latency"] = record["end_time"] - record["start_time"]
        record["result"] = result

        return record

    def log_error(self, record: dict[str, Any], error: Exception) -> dict[str, Any]:

        record["error"] = str(error)
        record["end_time"] = time.time()

        return record
