"""
간단한 성능 계측 도우미.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.utils.paths import get_performance_log_path


class PerformanceTracker:
    """
    특정 작업 내 주요 구간의 실행 시간을 기록하고 JSONL 형태로 저장합니다.
    """

    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.metadata: Dict[str, Any] = dict(metadata or {})
        self.events: List[Dict[str, Any]] = []
        self._started = time.perf_counter()
        self._status = "pending"
        self._error: Optional[str] = None
        self._finished = False

    @contextmanager
    def span(self, label: str):
        """
        코드 블록 실행 시간을 측정합니다.
        """
        span_start = time.perf_counter()
        try:
            yield
        except Exception as exc:  # noqa: BLE001 - 기록 후 상위로 전달
            duration = time.perf_counter() - span_start
            self.events.append({"label": label, "duration": duration, "error": str(exc)})
            raise
        else:
            duration = time.perf_counter() - span_start
            self.events.append({"label": label, "duration": duration})

    def add_metadata(self, **kwargs: Any) -> None:
        self.metadata.update({k: v for k, v in kwargs.items() if v is not None})

    def mark_event(self, label: str, value: Any) -> None:
        self.events.append({"label": label, "value": value})

    def set_status(self, status: str, error: Optional[str] = None) -> None:
        self._status = status
        if error:
            self._error = error

    def finish(self, status: str = "success") -> None:
        """
        측정 결과를 JSON Lines 로그에 기록합니다.
        """
        if self._finished:
            return

        total_duration = time.perf_counter() - self._started
        final_status = self._status if self._status != "pending" else status

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": self.name,
            "status": final_status,
            "total_duration": total_duration,
            "events": self.events,
            "metadata": self.metadata,
        }

        if self._error:
            payload["error"] = self._error

        log_path = get_performance_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, ensure_ascii=False) + "\n")

        self._finished = True
