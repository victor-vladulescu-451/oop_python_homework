import threading
import psutil
import time
from datetime import datetime, timezone
from database import get_session  # adapt import if needed
from models import SystemMetric


class ResourceMonitor(threading.Thread):
    def __init__(self, interval=1.0):
        super().__init__(daemon=True)
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                now = datetime.now(timezone.utc)
                with get_session() as session:
                    metric = SystemMetric(
                        timestamp=now, total_cpu_usage=cpu, total_ram_usage=mem
                    )
                    session.add(metric)
                    session.commit()
            except Exception as e:
                print(f"[ResourceMonitor ERROR] {e}")
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()
