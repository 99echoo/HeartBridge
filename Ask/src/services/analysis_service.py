"""
AI 분석 작업을 백그라운드에서 실행하고 상태를 관리합니다.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from concurrent.futures import Future

from src.ai.analyzer_factory import get_analyzer
from src.utils.async_runner import submit_async


@dataclass
class AnalysisJob:
    future: Future
    started_at: float


def start_analysis_job(
    responses: dict,
    dog_photo: bytes,
    behavior_media: Optional[bytes] = None,
) -> AnalysisJob:
    """
    비동기 분석 작업을 시작하고 Future를 반환합니다.
    """
    analyzer = get_analyzer()
    future = submit_async(
        analyzer(
            responses=responses,
            dog_photo=dog_photo,
            behavior_media=behavior_media,
        )
    )
    return AnalysisJob(future=future, started_at=time.time())


def job_done(job: AnalysisJob) -> bool:
    return job.future.done()


def job_result(job: AnalysisJob):
    return job.future.result()
