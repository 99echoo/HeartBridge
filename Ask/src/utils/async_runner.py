"""
백그라운드 asyncio 이벤트 루프를 관리하고 작업을 제출합니다.
"""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from typing import Awaitable

_loop: asyncio.AbstractEventLoop | None = None
_loop_lock = threading.Lock()


def _ensure_loop() -> asyncio.AbstractEventLoop:
    global _loop
    if _loop and _loop.is_running():
        return _loop

    with _loop_lock:
        if _loop and _loop.is_running():
            return _loop

        loop = asyncio.new_event_loop()

        def _run_loop(event_loop: asyncio.AbstractEventLoop) -> None:
            asyncio.set_event_loop(event_loop)
            event_loop.run_forever()

        thread = threading.Thread(target=_run_loop, args=(loop,), daemon=True)
        thread.start()
        _loop = loop
        return loop


def submit_async(coro: Awaitable) -> Future:
    """
    코루틴을 백그라운드 이벤트 루프에 제출하고 Future를 반환합니다.
    """
    loop = _ensure_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop)
