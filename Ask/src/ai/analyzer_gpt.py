"""
파일명: analyzer_gpt.py
목적: GPT-4o 기반 2단계 AI 분석 (JSON Schema + Self-Healing)
작성일: 2025-01-26
수정일: 2025-01-26 - JSON Schema 강제, Self-Healing 로직, asyncio 개선
"""

import json
import re
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from openai import OpenAI, APIError

from config.settings import settings
from src.ai.prompt_builder_gpt import (
    build_expert_analysis_prompt,
    build_mari_conversion_prompt,
)
from src.ai.gpt4_vision import (
    analyze_dog_image_with_gpt4,
    get_fallback_vision_analysis,
)
from src.ai.schemas import (
    EXPERT_ANALYSIS_SCHEMA,
    normalize_expert_json,
    validate_expert_json,
)
from src.utils.mock_data import get_mock_result_by_problem


# ===== 로깅 설정 =====

def setup_logger():
    """analyzer_gpt.py 전용 로거를 설정합니다."""
    logger = logging.getLogger("analyzer_gpt")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "analyzer_gpt.log"

    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


# ===== GPT-4o API 호출 (JSON Schema 강제) =====

async def call_gpt4_api(
    system: str,
    user: str,
    max_retries: int = 3,
    model: str = "gpt-4o",
    use_json_schema: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    temperature: float = 0.7
) -> str:
    """
    GPT-4o API를 호출합니다 (JSON Schema 강제 지원, 비동기 재시도).

    Args:
        system: 시스템 프롬프트
        user: 사용자 프롬프트
        max_retries: 최대 재시도 횟수
        model: GPT 모델명
        use_json_schema: JSON Schema 강제 사용 여부
        json_schema: JSON Schema 객체
        temperature: 온도 (창의성)

    Returns:
        str: AI 응답 텍스트

    Raises:
        Exception: API 호출 실패 시
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    logger.info(f"GPT-4o API 호출 시작 (model={model}, json_schema={use_json_schema}, temp={temperature})")
    logger.debug(f"System prompt 길이: {len(system)} chars")
    logger.debug(f"User prompt 길이: {len(user)} chars")

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"API 호출 시도 {attempt + 1}/{max_retries + 1}")

            # 메시지 구성
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]

            # API 호출
            if use_json_schema and json_schema:
                # JSON Schema 강제 모드
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4096,
                    temperature=temperature,
                    response_format={
                        "type": "json_schema",
                        "json_schema": json_schema
                    }
                )
            else:
                # 일반 모드
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4096,
                    temperature=temperature
                )

            response_text = response.choices[0].message.content
            logger.info(f"GPT-4o API 호출 성공 (응답 길이: {len(response_text)} chars)")

            # 사용량 로깅
            if hasattr(response, 'usage'):
                logger.info(f"토큰 사용량: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")

            return response_text

        except APIError as e:
            logger.error(f"OpenAI API 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            if attempt < max_retries:
                wait_time = (2 ** attempt) * 0.5  # 지수 백오프: 0.5s, 1s, 2s
                logger.warning(f"{wait_time}초 후 재시도...")
                await asyncio.sleep(wait_time)  # 비동기 sleep
                continue
            else:
                error_msg = f"GPT-4o API 호출 실패 (시도 {max_retries + 1}회): {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"예기치 않은 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            if attempt < max_retries:
                wait_time = (2 ** attempt) * 0.5
                logger.warning(f"{wait_time}초 후 재시도...")
                await asyncio.sleep(wait_time)
                continue
            else:
                error_msg = f"예기치 않은 오류: {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)


# ===== JSON 파싱 및 검증 =====

def parse_json_response(response: str) -> dict:
    """
    AI 응답에서 JSON을 파싱합니다.

    Args:
        response: AI 응답 텍스트

    Returns:
        dict: 파싱된 JSON

    Raises:
        ValueError: JSON 파싱 실패
    """
    # JSON 블록 추출 시도
    json_match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response

    try:
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {str(e)}")


# ===== Self-Healing: 수정 프롬프트 =====

async def fix_json_with_prompt(
    broken_json: dict,
    error_message: str,
    original_prompt: str
) -> dict:
    """
    JSON이 스키마를 위반한 경우, GPT에게 수정을 요청합니다.

    Args:
        broken_json: 문제가 있는 JSON
        error_message: 검증 실패 메시지
        original_prompt: 원래 프롬프트 (컨텍스트)

    Returns:
        dict: 수정된 JSON

    Raises:
        Exception: 수정 실패 시
    """
    logger.info("=== Self-Healing: JSON 수정 프롬프트 시도 ===")

    fix_prompt = f"""아래 JSON이 규칙을 위반했습니다. 정확히 수정해주세요.

**원래 요구사항:**
{original_prompt[:500]}...

**문제가 있는 JSON:**
```json
{json.dumps(broken_json, ensure_ascii=False, indent=2)}
```

**검증 실패 사유:**
{error_message}

**수정 요구사항:**
1. solutions_best_fit는 정확히 3개여야 합니다.
2. future_guidance는 정확히 3개여야 합니다.
3. 모든 필수 필드를 포함해야 합니다.
4. JSON만 출력하세요 (설명 불필요).
"""

    try:
        fixed_response = await call_gpt4_api(
            system="너는 JSON 검증 전문가다. 규칙을 정확히 따른 JSON만 출력한다.",
            user=fix_prompt,
            max_retries=1,
            use_json_schema=True,
            json_schema=EXPERT_ANALYSIS_SCHEMA,
            temperature=0.3  # 낮은 온도로 정확성 확보
        )

        fixed_json = parse_json_response(fixed_response)
        logger.info("JSON 수정 성공!")
        return fixed_json

    except Exception as e:
        logger.error(f"JSON 수정 실패: {str(e)}")
        raise


# ===== 2단계 AI 분석 메인 함수 =====

async def analyze_two_stage(
    responses: dict,
    dog_photo: bytes,
    behavior_media: Optional[bytes] = None
) -> dict:
    """
    2단계 AI 분석을 실행합니다 (GPT-4o, JSON Schema, Self-Healing).

    Args:
        responses: st.session_state.responses (설문 응답)
        dog_photo: 강아지 사진 바이트
        behavior_media: 행동 영상/사진 바이트 (Optional)

    Returns:
        dict: {
            "final_text": str,
            "confidence_score": float,
            "raw_json": dict
        }
    """
    dog_name = responses.get("dog_name", "강아지")
    dog_age = responses.get("dog_birth", "알 수 없음")
    hardest_part = responses.get("hardest_part", "알 수 없음")
    main_concerns = responses.get("main_concerns", [])

    # ===== 0단계: GPT-4 Vision 이미지 전처리 =====
    logger.info(f"=== GPT-4 Vision 이미지 전처리 시작 (강아지: {dog_name}) ===")

    vision_analysis = None
    try:
        vision_analysis = await analyze_dog_image_with_gpt4(
            image_bytes=dog_photo,
            max_retries=2
        )
        logger.info("GPT-4 Vision 이미지 분석 성공!")

    except Exception as e:
        logger.error(f"GPT-4 Vision 실패, Fallback 사용: {str(e)}")
        vision_analysis = get_fallback_vision_analysis(dog_name=dog_name)

    # ===== 1차 AI: 전문가 분석 (JSON Schema 강제) =====
    logger.info(f"=== 1차 AI 분석 시작 (GPT-4o + JSON Schema, 강아지: {dog_name}) ===")

    raw_json = None
    try:
        # 프롬프트 생성
        logger.debug("1차 AI 프롬프트 생성 중...")
        expert_prompt = build_expert_analysis_prompt(
            responses=responses,
            dog_photo=dog_photo,
            behavior_media=behavior_media,
            vision_analysis=vision_analysis
        )

        # GPT-4o API 호출 (JSON Schema 강제)
        logger.info("1차 AI GPT-4o API 호출 시작 (JSON Schema 강제)...")
        raw_response = await call_gpt4_api(
            system=expert_prompt["system"],
            user=expert_prompt["user"],
            max_retries=3,
            model="gpt-4o",
            use_json_schema=True,
            json_schema=EXPERT_ANALYSIS_SCHEMA,
            temperature=0.4  # 낮은 온도로 정확성 확보
        )

        # JSON 파싱
        logger.debug("1차 AI 응답 JSON 파싱 중...")
        raw_json = parse_json_response(raw_response)

        # ===== Self-Healing: Schema 검증 =====
        is_valid, error_msg = validate_expert_json(raw_json)

        if not is_valid:
            logger.warning(f"Schema 검증 실패: {error_msg}")
            logger.info("=== Self-Healing 단계 1: Normalize 시도 ===")

            # 1) Normalize (자동 보정)
            raw_json = normalize_expert_json(raw_json)
            logger.info("Normalize 완료")

            # 2) 재검증
            is_valid, error_msg = validate_expert_json(raw_json)

            if not is_valid:
                logger.warning(f"Normalize 후에도 검증 실패: {error_msg}")
                logger.info("=== Self-Healing 단계 2: 수정 프롬프트 시도 ===")

                # 3) 수정 프롬프트
                try:
                    raw_json = await fix_json_with_prompt(
                        broken_json=raw_json,
                        error_message=error_msg,
                        original_prompt=expert_prompt["user"]
                    )

                    # 4) 최종 검증
                    is_valid, error_msg = validate_expert_json(raw_json)

                    if not is_valid:
                        logger.error(f"수정 프롬프트 후에도 검증 실패: {error_msg}")
                        logger.warning("최종 Normalize 적용")
                        raw_json = normalize_expert_json(raw_json)

                except Exception as fix_error:
                    logger.error(f"수정 프롬프트 실패: {str(fix_error)}")
                    logger.warning("Normalize로 복구")
                    raw_json = normalize_expert_json(raw_json)

        logger.info("1차 AI 분석 및 검증 완료!")

    except Exception as e:
        # 최후 폴백: Mock 데이터
        logger.error(f"===== 1차 AI 실패 - Mock 데이터 폴백 =====")
        logger.error(f"Error: {str(e)}", exc_info=True)

        problem_type = main_concerns[0] if main_concerns else "barking"
        mock_result = get_mock_result_by_problem(problem_type)

        raw_json = {
            "analysis_summary": {
                "core_issue": "분석 실패로 인한 기본 응답",
                "root_cause": "API 오류",
                "key_characteristics": ["정보 부족", "임시 응답", "재시도 권장"]
            },
            "solutions_best_fit": [
                {"title": "솔루션 1", "content": "기본 솔루션", "details": ["임시 응답"], "expected_outcome": "개선 기대"},
                {"title": "솔루션 2", "content": "기본 솔루션", "details": ["임시 응답"], "expected_outcome": "개선 기대"},
                {"title": "솔루션 3", "content": "기본 솔루션", "details": ["임시 응답"], "expected_outcome": "개선 기대"}
            ],
            "future_guidance": [
                {"principle": "원칙 1", "content": "내용", "action": "행동"},
                {"principle": "원칙 2", "content": "내용", "action": "행동"},
                {"principle": "원칙 3", "content": "내용", "action": "행동"}
            ],
            "core_message": "일시적인 오류가 발생했습니다. 다시 시도해주세요.",
            "confidence_score": 0.3
        }

    # ===== 2차 AI: 마리 페르소나 변환 (자연어) =====
    logger.info(f"=== 2차 AI 변환 시작 (GPT-4o, 강아지: {dog_name}) ===")

    try:
        mari_prompt = build_mari_conversion_prompt(
            raw_json=raw_json,
            dog_name=dog_name,
            dog_age=dog_age,
            hardest_part=hardest_part
        )

        # GPT-4o API 호출 (텍스트 모드, 높은 temperature)
        logger.info("2차 AI GPT-4o API 호출 시작 (텍스트 모드)...")
        final_text = await call_gpt4_api(
            system=mari_prompt["system"],
            user=mari_prompt["user"],
            max_retries=2,
            model="gpt-4o",
            use_json_schema=False,
            temperature=0.7  # 자연스러운 톤을 위해 높은 온도
        )
        logger.info("2차 AI 변환 성공!")

    except Exception as e:
        logger.error(f"===== 2차 AI 실패 - simple_template_conversion 폴백 =====")
        logger.error(f"Error: {str(e)}", exc_info=True)
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
