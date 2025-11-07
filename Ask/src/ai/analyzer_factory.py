"""
파일명: analyzer_factory.py
목적: AI Analyzer Factory - 설정에 따라 적절한 analyzer 선택
작성일: 2025-01-26
"""

from typing import Callable
from config.settings import settings


def get_analyzer() -> Callable:
    """
    설정(AI_MODEL_PROVIDER)에 따라 적절한 analyzer 함수를 반환합니다.

    Returns:
        Callable: analyze_two_stage 함수

    Raises:
        ValueError: 지원하지 않는 AI_MODEL_PROVIDER 값일 때
    """
    provider = settings.AI_MODEL_PROVIDER.lower()

    if provider == "gpt":
        # GPT-5 Responses API 사용
        from src.ai.analyzer_gpt5 import analyze_two_stage
        return analyze_two_stage
    elif provider == "claude":
        from src.ai.analyzer_claude import analyze_two_stage
        return analyze_two_stage
    else:
        raise ValueError(
            f"지원하지 않는 AI_MODEL_PROVIDER: '{provider}'. "
            f"'claude' 또는 'gpt'를 사용하세요."
        )


def get_analyzer_name() -> str:
    """
    현재 사용 중인 AI Analyzer 이름을 반환합니다.

    Returns:
        str: "Claude Sonnet 4.5" 또는 "GPT-5 Responses"
    """
    provider = settings.AI_MODEL_PROVIDER.lower()

    if provider == "gpt":
        return "GPT-5 Responses"
    elif provider == "claude":
        return "Claude Sonnet 4.5"
    else:
        return "Unknown"


# 편의 함수: 직접 import하여 사용 가능
def analyze_two_stage(*args, **kwargs):
    """
    설정에 따라 적절한 analyzer를 자동으로 선택하여 실행합니다.

    Args:
        *args: analyze_two_stage의 위치 인자들
        **kwargs: analyze_two_stage의 키워드 인자들

    Returns:
        dict: 분석 결과
    """
    analyzer = get_analyzer()
    return analyzer(*args, **kwargs)
