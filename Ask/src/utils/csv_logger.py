"""
파일명: csv_logger.py
목적: 설문 응답 및 AI 분석 결과를 CSV 파일로 저장
작성일: 2025-01-26
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.paths import get_csv_output_path, get_csv_log_path


# ===== 로깅 설정 =====

def setup_csv_logger():
    """
    CSV 로거를 설정합니다.
    로그는 runtime/{APP_ENV}/logs/csv_logger.log 파일에 저장됩니다.

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger("csv_logger")
    logger.setLevel(logging.DEBUG)

    # 기존 핸들러 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()

    # 로그 파일 경로
    log_dir = get_csv_log_path().parent
    log_file = get_csv_log_path()

    # 부모 디렉토리 생성 (AWS 환경 대응)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 파일 핸들러 (UTF-8 인코딩, append 모드)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 포맷터 설정
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# 로거 초기화
logger = setup_csv_logger()


def save_to_csv(
    responses: Dict[str, Any],
    analysis_result: Dict[str, Any],
    csv_path: Optional[str] = None
) -> str:
    """
    설문 응답과 AI 분석 결과를 CSV 파일로 저장합니다.

    Args:
        responses: 설문 응답 딕셔너리 (st.session_state.responses)
        analysis_result: AI 분석 결과 딕셔너리 (st.session_state.analysis_result)
        csv_path: CSV 파일 경로 (기본값: Ask/result/survey_results.csv)

    Returns:
        str: 저장된 CSV 파일 경로

    Raises:
        IOError: 파일 저장 실패 시
    """
    # CSV 파일 경로 설정
    if csv_path is None:
        csv_path = get_csv_output_path()
    else:
        csv_path = Path(csv_path)

    # 절대 경로로 변환 (AWS 환경에서 상대 경로 문제 방지)
    csv_path = csv_path.resolve()

    # 부모 디렉토리가 없으면 생성 (AWS 환경 대응)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"CSV 파일 저장 경로: {csv_path}")

    # 타임스탬프
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 생년월일 처리 (딕셔너리 → 문자열)
    dog_birth = responses.get("dog_birth", "")
    if isinstance(dog_birth, dict):
        year = dog_birth.get("year", "")
        month = dog_birth.get("month", "")
        dog_birth_str = f"{year}년 {month}월"
    else:
        dog_birth_str = str(dog_birth)

    # CSV 행 데이터 준비
    row_data = {
        "timestamp": timestamp,
        # 기본 정보
        "dog_name": responses.get("dog_name", ""),
        "dog_birth": dog_birth_str,
        "dog_breed": responses.get("dog_breed", ""),
        "dog_gender": responses.get("dog_gender", ""),
        "dog_neutered": responses.get("dog_neutered", ""),
        "other_pets": json.dumps(responses.get("other_pets", []), ensure_ascii=False),

        # 성향
        "personality_traits": json.dumps(responses.get("personality_traits", []), ensure_ascii=False),
        "activity_time": responses.get("activity_time", ""),

        # 문제 행동
        "main_concerns": json.dumps(responses.get("main_concerns", []), ensure_ascii=False),
        "problem_start_time": responses.get("problem_start_time", ""),
        "problem_situation": responses.get("problem_situation", ""),
        "tried_solutions": responses.get("tried_solutions", ""),
        "hardest_part": responses.get("hardest_part", ""),

        # 환경
        "living_environment": responses.get("living_environment", ""),
        "family_members": responses.get("family_members", ""),
        "outing_time": responses.get("outing_time", ""),

        # 기타 응답 (other 텍스트)
        "other_responses": json.dumps({
            k: v for k, v in responses.items()
            if k.endswith("_other") and v
        }, ensure_ascii=False),

        # AI 분석 결과
        "confidence_score": analysis_result.get("confidence_score", 0.0),
        "final_text": analysis_result.get("final_text", ""),

        # Raw JSON (디버깅용)
        "raw_json": json.dumps(analysis_result.get("raw_json", {}), ensure_ascii=False),
    }

    # CSV 파일 존재 여부 확인 (헤더 작성용)
    file_exists = csv_path.exists()

    # CSV 파일에 추가
    try:
        with open(csv_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())

            # 파일이 없으면 헤더 작성
            if not file_exists:
                writer.writeheader()

            # 데이터 행 작성
            writer.writerow(row_data)

        saved_path = str(csv_path)
        logger.info(f"CSV 파일 저장 성공: {saved_path}")
        return saved_path

    except OSError as e:
        error_msg = f"CSV 파일 저장 실패 (경로: {csv_path}): {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise IOError(error_msg) from e
    except Exception as e:
        error_msg = f"CSV 파일 저장 실패 (경로: {csv_path}): {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise IOError(error_msg) from e


def get_csv_path() -> Path:
    """
    CSV 파일 경로를 반환합니다.

    Returns:
        Path: CSV 파일 경로
    """
    return get_csv_output_path()
