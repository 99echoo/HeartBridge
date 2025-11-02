"""
파일명: analyzer.py
목적: 2단계 AI 분석 핵심 로직
작성일: 2025-01-26
"""

import json
import re
import time
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
import anthropic

from config.settings import settings
from src.ai.prompt_builder import (
    build_expert_analysis_prompt,
    build_mari_conversion_prompt,
)
from src.ai.gpt4_vision import (
    analyze_dog_image_with_gpt4,
    get_fallback_vision_analysis,
)
from src.utils.mock_data import get_mock_result_by_problem


# ===== 로깅 설정 =====

def setup_logger():
    """
    analyzer.py 전용 로거를 설정합니다.

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger("analyzer")
    logger.setLevel(logging.DEBUG)

    # 기존 핸들러 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()

    # 로그 파일 경로 (Ask/logs/ 디렉토리)
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "analyzer.log"

    # 파일 핸들러 (UTF-8 인코딩)
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
logger = setup_logger()


# ===== Claude API 호출 =====

async def call_claude_api(
    system: str,
    user: str,
    images: Optional[List[Dict]] = None,
    max_retries: int = 2,
    model: str = "claude-sonnet-4-5-20250929"
) -> str:
    """
    Claude API를 호출합니다 (재시도 로직 포함).

    Args:
        system: 시스템 프롬프트
        user: 사용자 프롬프트
        images: 이미지 리스트 (Optional) - [{"type": "base64", "media_type": "image/jpeg", "data": "..."}]
        max_retries: 최대 재시도 횟수
        model: Claude 모델명

    Returns:
        str: AI 응답 텍스트

    Raises:
        Exception: API 호출 실패 시
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    logger.info(f"Claude API 호출 시작 (model={model}, images={len(images) if images else 0}개)")
    logger.debug(f"System prompt 길이: {len(system)} chars")
    logger.debug(f"User prompt 길이: {len(user)} chars")

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"API 호출 시도 {attempt + 1}/{max_retries + 1}")

            # 이미지가 있을 경우 Vision API 사용
            if images:
                content_blocks = []

                # 이미지 추가
                for img in images:
                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": img["type"],
                            "media_type": img["media_type"],
                            "data": img["data"],
                        }
                    })

                # 텍스트 프롬프트 추가
                content_blocks.append({
                    "type": "text",
                    "text": user
                })

                message = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=system,
                    messages=[
                        {"role": "user", "content": content_blocks}
                    ]
                )
            else:
                # 텍스트만 사용
                message = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=system,
                    messages=[
                        {"role": "user", "content": user}
                    ]
                )

            # 응답 추출
            response_text = message.content[0].text
            logger.info(f"Claude API 호출 성공 (응답 길이: {len(response_text)} chars)")
            return response_text

        except anthropic.APIError as e:
            logger.error(f"Anthropic API 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            if attempt < max_retries:
                # 재시도 (exponential backoff)
                wait_time = 2 ** attempt
                logger.warning(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                # 최종 실패
                error_msg = f"Claude API 호출 실패 (시도 {max_retries + 1}회): {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"예기치 않은 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.warning(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                error_msg = f"예기치 않은 오류: {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)


# ===== JSON 파싱 및 검증 =====

def parse_json_response(response: str) -> dict:
    """
    AI 응답에서 JSON을 파싱하고 검증합니다.

    Args:
        response: AI 응답 텍스트

    Returns:
        dict: 파싱된 JSON 딕셔너리

    Raises:
        ValueError: JSON 파싱 실패 또는 필수 필드 누락
    """
    # JSON 블록 추출 (```json ... ``` 형식 지원)
    json_match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # JSON 블록 없으면 전체를 JSON으로 파싱 시도
        json_str = response

    # JSON 파싱
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {str(e)}")

    # 필수 필드 검증
    required_fields = [
        "analysis_summary",
        "solutions_best_fit",
        "future_guidance",
        "core_message",
        "confidence_score"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"필수 필드 누락: {field}")

    # solutions_best_fit가 정확히 3개인지 확인
    if len(result["solutions_best_fit"]) != 3:
        raise ValueError(f"solutions_best_fit는 3개여야 합니다 (현재: {len(result["solutions_best_fit"])}개)")

    # future_guidance가 정확히 3개인지 확인
    if len(result["future_guidance"]) != 3:
        raise ValueError(f"future_guidance는 3개여야 합니다 (현재: {len(result["future_guidance"])}개)")

    return result


# ===== 2단계 AI 분석 메인 함수 =====

async def analyze_two_stage(
    responses: dict,
    dog_photo: bytes,
    behavior_media: Optional[bytes] = None
) -> dict:
    """
    2단계 AI 분석을 실행합니다.

    Args:
        responses: st.session_state.responses (설문 응답)
        dog_photo: 강아지 사진 바이트
        behavior_media: 행동 영상/사진 바이트 (Optional)

    Returns:
        dict: {
            "final_text": str,           # 마리의 최종 Markdown 텍스트
            "confidence_score": float,   # 0.0-1.0
            "raw_json": dict            # 1차 AI 원본 (디버깅/로깅용)
        }
    """
    # 강아지 정보 추출
    dog_name = responses.get("dog_name", "강아지")
    dog_age = responses.get("dog_birth", "알 수 없음")
    hardest_part = responses.get("hardest_part", "알 수 없음")
    main_concerns = responses.get("main_concerns", [])

    # ===== 0단계: GPT-4 Vision 이미지 전처리 =====
    logger.info(f"=== GPT-4 Vision 이미지 전처리 시작 (강아지: {dog_name}) ===")
    logger.debug(f"dog_photo 크기: {len(dog_photo) if dog_photo else 0} bytes")
    logger.debug(f"behavior_media 크기: {len(behavior_media) if behavior_media else 0} bytes")

    vision_analysis = None
    try:
        # GPT-4 Vision으로 이미지 분석
        vision_analysis = await analyze_dog_image_with_gpt4(
            image_bytes=dog_photo,
            max_retries=2
        )
        logger.info("GPT-4 Vision 이미지 분석 성공!")
        logger.debug(f"Vision 분석 결과: {vision_analysis.keys()}")

    except Exception as e:
        # GPT-4 Vision 실패 시: Fallback 사용
        logger.error(f"GPT-4 Vision 실패, Fallback 사용: {str(e)}")
        vision_analysis = get_fallback_vision_analysis(dog_name=dog_name)

    # ===== 1차 AI: 전문가 분석 =====
    logger.info(f"=== 1차 AI 분석 시작 (강아지: {dog_name}) ===")

    try:
        # 프롬프트 생성 (vision_analysis 포함)
        logger.debug("1차 AI 프롬프트 생성 중...")
        expert_prompt = build_expert_analysis_prompt(
            responses=responses,
            dog_photo=dog_photo,
            behavior_media=behavior_media,
            vision_analysis=vision_analysis  # ← GPT-4 Vision 결과 전달
        )
        logger.debug(f"프롬프트 생성 완료 (이미지 전송: {expert_prompt['images'] is not None})")

        # API 호출
        logger.info("1차 AI Claude API 호출 시작...")
        raw_response = await call_claude_api(
            system=expert_prompt["system"],
            user=expert_prompt["user"],
            images=expert_prompt["images"],  # None이어야 함
            max_retries=2
        )

        # JSON 파싱
        logger.debug("1차 AI 응답 JSON 파싱 중...")
        raw_json = parse_json_response(raw_response)
        logger.info("1차 AI 분석 성공!")

    except Exception as e:
        # 1차 AI 실패 시: Mock 데이터 사용
        logger.error(f"===== 1차 AI 실패 - Mock 데이터 폴백 =====")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full traceback:", exc_info=True)

        # Mock 데이터 가져오기
        problem_type = main_concerns[0] if main_concerns else "barking"
        mock_result = get_mock_result_by_problem(problem_type)

        # Mock 데이터를 1차 JSON 형식으로 변환
        raw_json = {
            "analysis_summary": {
                "core_issue": "분석 실패로 인한 기본 응답",
                "root_cause": "API 오류",
                "key_characteristics": ["정보 부족"]
            },
            "solutions_best_fit": [
                {"title": "솔루션 1", "content": "기본 솔루션", "details": [], "expected_outcome": "개선 기대"},
                {"title": "솔루션 2", "content": "기본 솔루션", "details": [], "expected_outcome": "개선 기대"},
                {"title": "솔루션 3", "content": "기본 솔루션", "details": [], "expected_outcome": "개선 기대"}
            ],
            "future_guidance": [
                {"principle": "원칙 1", "content": "내용", "action": "행동"},
                {"principle": "원칙 2", "content": "내용", "action": "행동"},
                {"principle": "원칙 3", "content": "내용", "action": "행동"}
            ],
            "core_message": "일시적인 오류가 발생했습니다. 다시 시도해주세요.",
            "confidence_score": 0.3
        }

    # ===== 2차 AI: 마리 페르소나 변환 =====
    logger.info(f"=== 2차 AI 변환 시작 (강아지: {dog_name}) ===")

    try:
        # 프롬프트 생성
        logger.debug("2차 AI 프롬프트 생성 중...")
        mari_prompt = build_mari_conversion_prompt(
            raw_json=raw_json,
            dog_name=dog_name,
            dog_age=dog_age,
            hardest_part=hardest_part
        )

        # API 호출
        logger.info("2차 AI Claude API 호출 시작...")
        final_text = await call_claude_api(
            system=mari_prompt["system"],
            user=mari_prompt["user"],
            images=None,  # 2차는 텍스트만
            max_retries=2
        )
        logger.info("2차 AI 변환 성공!")

    except Exception as e:
        # 2차 AI 실패 시: 간단한 템플릿 변환
        logger.error(f"===== 2차 AI 실패 - simple_template_conversion 폴백 =====")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full traceback:", exc_info=True)
        final_text = simple_template_conversion(raw_json, dog_name, dog_age)

    # 결과 반환
    return {
        "final_text": final_text,
        "confidence_score": raw_json.get("confidence_score", 0.5),
        "raw_json": raw_json
    }


# ===== 폴백: 간단한 템플릿 변환 =====

def simple_template_conversion(raw_json: dict, dog_name: str, dog_age: str) -> str:
    """
    2차 AI 실패 시 사용할 간단한 템플릿 변환.

    Args:
        raw_json: 1차 AI 결과
        dog_name: 강아지 이름
        dog_age: 강아지 나이

    Returns:
        str: Markdown 텍스트
    """
    summary = raw_json.get("analysis_summary", {})
    solutions = raw_json.get("solutions_best_fit", [])
    guidance = raw_json.get("future_guidance", [])
    core_message = raw_json.get("core_message", "")

    text = f"""**"{dog_name}({dog_age})의 행동 분석 결과예요!"**

{summary.get("core_issue", "분석 결과")}

---

🐾 **이런 솔루션이 {dog_name}에게 가장 잘 맞아요!**

"""

    # 솔루션 3개 추가
    for i, sol in enumerate(solutions[:3], 1):
        text += f"""**{i}. {sol.get("title", f"솔루션 {i}")}**

{sol.get("content", "내용 없음")}

"""

    # 코어 메시지
    if core_message:
        text += f"""🌱 **마리의 한마디:**

"{core_message}"

---

"""

    # 미래 가이던스
    text += f"""🐾 **앞으로 이렇게 해보세요!**

"""

    for g in guidance[:3]:
        text += f"- {g.get('principle', '원칙')}: {g.get('action', '행동')}\n"

    text += f"""

**{dog_name}는 잘하고 있어요. 보호자님도 너무 잘하고 계세요 💛**
"""

    return text
