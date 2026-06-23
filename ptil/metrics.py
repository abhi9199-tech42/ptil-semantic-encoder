import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional
from collections import defaultdict


@dataclass
class MetricValue:
    count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0

    @property
    def avg_time(self) -> float:
        return self.total_time / self.count if self.count else 0.0


class MetricsCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._reset()
        self._data_lock = threading.Lock()

    def _reset(self):
        self._timings: Dict[str, MetricValue] = defaultdict(MetricValue)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauge: Dict[str, float] = {}

    def record_timing(self, name: str, duration: float):
        with self._data_lock:
            mv = self._timings[name]
            mv.count += 1
            mv.total_time += duration
            mv.min_time = min(mv.min_time, duration)
            mv.max_time = max(mv.max_time, duration)

    def increment(self, name: str, value: int = 1):
        with self._data_lock:
            self._counters[name] += value

    def set_gauge(self, name: str, value: float):
        with self._data_lock:
            self._gauge[name] = value

    def get_timing(self, name: str) -> Optional[MetricValue]:
        return self._timings.get(name)

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def snapshot(self) -> dict:
        return {
            "timings": {k: {"count": v.count, "avg_ms": v.avg_time * 1000,
                            "min_ms": v.min_time * 1000, "max_ms": v.max_time * 1000}
                        for k, v in self._timings.items()},
            "counters": dict(self._counters),
            "gauges": dict(self._gauge),
        }

    def timing(self, name: str):
        return _TimingContext(self, name)


class _TimingContext:
    def __init__(self, collector: MetricsCollector, name: str):
        self._collector = collector
        self._name = name
        self._start: Optional[float] = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self._start is not None:
            self._collector.record_timing(self._name, time.perf_counter() - self._start)
