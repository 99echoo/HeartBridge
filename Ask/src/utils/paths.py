"""
경로 관련 도우미: 실행 중 생성되는 데이터/로그 디렉토리를 일관되게 관리합니다.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from config.settings import settings


@lru_cache(maxsize=1)
def get_project_root() -> Path:
    """
    Ask 프로젝트 루트 경로를 반환합니다.
    """
    return Path(__file__).resolve().parents[2]


def _get_runtime_root() -> Path:
    """
    실행 환경(APP_ENV)별 런타임 디렉토리를 생성/반환합니다.
    """
    env_name = settings.APP_ENV or "development"
    runtime_root = get_project_root() / "runtime" / env_name
    runtime_root.mkdir(parents=True, exist_ok=True)
    return runtime_root


def get_runtime_data_dir() -> Path:
    """
    런타임 데이터 저장 디렉토리 (CSV 등)를 반환합니다.
    """
    data_dir = _get_runtime_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_runtime_logs_dir() -> Path:
    """
    런타임 로그 디렉토리를 반환합니다.
    """
    logs_dir = _get_runtime_root() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_csv_output_path(filename: str = "survey_results.csv") -> Path:
    """
    CSV 기본 저장 경로를 반환합니다.
    Ask/result/survey_results.csv 위치에 저장됩니다.
    """
    result_dir = get_project_root() / "result"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir / filename


def get_performance_log_path() -> Path:
    """
    성능 계측 로그 파일 경로를 반환합니다.
    """
    return get_runtime_logs_dir() / "performance.log"


def get_csv_log_path() -> Path:
    """
    CSV 저장 관련 로그 파일 경로를 반환합니다.
    """
    return get_runtime_logs_dir() / "csv_logger.log"