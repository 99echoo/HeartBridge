"""
파일명: prompt_builder.py
목적: 2단계 AI 시스템의 프롬프트 생성 로직
작성일: 2025-01-26
"""

import base64
import json
from typing import Dict, List, Optional, Any

from src.ai.mari_persona import (
    get_expert_persona,
    get_mari_persona,
    get_mari_conversion_template,
)


# ===== 이미지 처리 =====

def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    이미지 바이트를 base64 문자열로 인코딩합니다.

    Args:
        image_bytes: 이미지 파일의 바이트 데이터

    Returns:
        str: base64로 인코딩된 문자열

    Raises:
        ValueError: image_bytes가 None이거나 비어있을 때
    """
    if not image_bytes:
        raise ValueError("image_bytes는 비어있을 수 없습니다.")

    return base64.b64encode(image_bytes).decode("utf-8")


# ===== 설문 응답 구조화 =====

def structure_survey_responses(responses: dict) -> dict:
    """
    설문 응답을 1차 AI가 이해하기 쉬운 구조화된 dict로 변환합니다.

    Args:
        responses: st.session_state.responses (설문 응답 딕셔너리)

    Returns:
        dict: {
            "dog_info": {...},
            "personality": {...},
            "problem": {...},
            "environment": {...}
        }
    """
    # 기본 정보
    dog_info = {
        "name": responses.get("dog_name", "강아지"),
        "age": responses.get("dog_birth", "알 수 없음"),
        "breed": responses.get("dog_breed", "알 수 없음"),
        "gender": responses.get("dog_gender", "알 수 없음"),
        "neutered": responses.get("dog_neutered", "알 수 없음"),
    }

    # 다른 반려동물 정보 (있을 경우)
    other_pets = responses.get("other_pets", [])
    if other_pets and len(other_pets) > 0 and other_pets[0] != "없음":
        dog_info["other_pets"] = ", ".join(other_pets)
    else:
        dog_info["other_pets"] = "없음"

    # 성격 및 성향
    personality = {
        "traits": responses.get("personality_traits", []),
        "activity_time": responses.get("activity_time", "알 수 없음"),
    }

    # 문제 행동
    problem = {
        "main_concerns": responses.get("main_concerns", []),
        "start_time": responses.get("problem_start_time", "알 수 없음"),
        "situation": responses.get("problem_situation", "알 수 없음"),
        "tried_solutions": responses.get("tried_solutions", "없음"),
        "hardest_part": responses.get("hardest_part", "알 수 없음"),
    }

    # 환경 정보
    environment = {
        "living": responses.get("living_environment", "알 수 없음"),
        "family": responses.get("family_members", "알 수 없음"),
        "outing_time": responses.get("outing_time", "알 수 없음"),
    }

    return {
        "dog_info": dog_info,
        "personality": personality,
        "problem": problem,
        "environment": environment,
    }


# ===== 1차 AI: 전문가 분석 프롬프트 =====

def build_expert_analysis_prompt(
    responses: dict,
    dog_photo: bytes,
    behavior_media: Optional[bytes] = None,
    vision_analysis: Optional[dict] = None
) -> dict:
    """
    1차 AI(전문가 분석)용 프롬프트를 생성합니다.

    Args:
        responses: st.session_state.responses (설문 응답 딕셔너리)
        dog_photo: 강아지 사진 바이트 데이터 (GPT-4 Vision에서만 사용, Claude에는 전달 안 함)
        behavior_media: 행동 영상/사진 바이트 데이터 (선택)
        vision_analysis: GPT-4 Vision 분석 결과 (Optional)

    Returns:
        dict: {
            "system": EXPERT_PERSONA,
            "user": "구조화된 분석 요청 텍스트 (vision_analysis 포함)",
            "images": None  # 더 이상 이미지를 전송하지 않음
        }

    Raises:
        ValueError: dog_photo가 None일 때
    """
    if not dog_photo:
        raise ValueError("dog_photo는 필수입니다.")

    # 설문 응답 구조화
    structured = structure_survey_responses(responses)

    # 사용자 프롬프트 텍스트 생성
    dog_info = structured["dog_info"]
    personality = structured["personality"]
    problem = structured["problem"]
    environment = structured["environment"]

    # vision_analysis가 있으면 이미지 분석 섹션 추가
    vision_section = ""
    if vision_analysis:
        vision_section = f"""

## 이미지 분석 결과 (GPT-4 Vision)
반려견의 사진을 GPT-4 Vision으로 분석한 결과입니다. 이 정보를 참고하여 행동 분석을 수행하세요.

**품종 및 외형:**
{vision_analysis.get("breed_analysis", "정보 없음")}

**표정 및 감정 상태:**
{vision_analysis.get("emotional_state", "정보 없음")}

**자세 및 신체 언어:**
{vision_analysis.get("posture_body_language", "정보 없음")}

**주변 환경:**
{vision_analysis.get("environment", "정보 없음")}

**행동적 단서:**
{vision_analysis.get("behavioral_cues", "정보 없음")}

**전체 평가:**
{vision_analysis.get("overall_assessment", "정보 없음")}
"""

    user_prompt = f"""반려견 행동 분석을 요청합니다.
{vision_section}

## 반려견 기본 정보
- 이름: {dog_info["name"]}
- 나이: {dog_info["age"]}
- 품종: {dog_info["breed"]}
- 성별: {dog_info["gender"]}
- 중성화: {dog_info["neutered"]}
- 다른 반려동물: {dog_info["other_pets"]}

## 성격 및 성향
- 평소 성격: {", ".join(personality["traits"]) if personality["traits"] else "알 수 없음"}
- 활동 시간: {personality["activity_time"]}

## 문제 행동 관련
- 주요 고민: {", ".join(problem["main_concerns"]) if problem["main_concerns"] else "알 수 없음"}
- 발생 시점: {problem["start_time"]}
- 발생 상황: {problem["situation"]}
- 시도한 솔루션: {problem["tried_solutions"]}
- 가장 어려운 점: {problem["hardest_part"]}

## 환경 정보
- 거주 형태: {environment["living"]}
- 가족 구성: {environment["family"]}
- 외출 시간: {environment["outing_time"]}

---

위 정보를 바탕으로 **{dog_info["name"]}의 행동을 전문적으로 분석**하고, **JSON 형식으로 출력**해주세요.

특히 보호자가 가장 힘들어하는 부분("{problem["hardest_part"]}")을 중점적으로 고려해주세요.

{"이미지 분석 결과와 설문 응답을 종합하여 근본 원인을 도출해주세요." if vision_analysis else "설문 응답을 바탕으로 근본 원인을 도출해주세요."}
"""

    return {
        "system": get_expert_persona(),
        "user": user_prompt,
        "images": None,  # 더 이상 이미지를 전송하지 않음 (GPT-4 Vision이 대신 분석)
    }


# ===== 2차 AI: 마리 페르소나 변환 프롬프트 =====

def build_mari_conversion_prompt(
    raw_json: dict,
    dog_name: str,
    dog_age: str,
    hardest_part: str
) -> dict:
    """
    2차 AI(마리 변환)용 프롬프트를 생성합니다.

    Args:
        raw_json: 1차 AI의 JSON 응답 (dict)
        dog_name: 강아지 이름
        dog_age: 강아지 나이
        hardest_part: 보호자가 가장 힘들어하는 점

    Returns:
        dict: {
            "system": MARI_PERSONA,
            "user": "변환 요청 텍스트"
        }
    """
    # raw_json을 문자열로 변환 (예쁘게 포맷)
    raw_analysis_str = json.dumps(raw_json, ensure_ascii=False, indent=2)

    # 템플릿 가져오기 및 포맷팅
    template = get_mari_conversion_template()

    user_prompt = template.format(
        raw_analysis=raw_analysis_str,
        dog_name=dog_name,
        dog_age=dog_age,
        hardest_part=hardest_part,
    )

    return {
        "system": get_mari_persona(),
        "user": user_prompt,
    }


# ===== 디버깅용 헬퍼 함수 =====

def preview_expert_prompt(responses: dict) -> str:
    """
    1차 AI 프롬프트 미리보기 (이미지 제외)

    Args:
        responses: 설문 응답 딕셔너리

    Returns:
        str: 생성될 프롬프트 텍스트
    """
    structured = structure_survey_responses(responses)
    dog_info = structured["dog_info"]
    personality = structured["personality"]
    problem = structured["problem"]
    environment = structured["environment"]

    preview = f"""
[SYSTEM PROMPT]
{get_expert_persona()[:200]}...

[USER PROMPT]
반려견 기본 정보:
- 이름: {dog_info["name"]}
- 나이: {dog_info["age"]}
- 품종: {dog_info["breed"]}

문제 행동:
- 주요 고민: {", ".join(problem["main_concerns"]) if problem["main_concerns"] else "알 수 없음"}
- 가장 어려운 점: {problem["hardest_part"]}

환경:
- 거주 형태: {environment["living"]}
- 가족 구성: {environment["family"]}
"""

    return preview


def preview_mari_prompt(raw_json: dict, dog_name: str) -> str:
    """
    2차 AI 프롬프트 미리보기

    Args:
        raw_json: 1차 AI 결과
        dog_name: 강아지 이름

    Returns:
        str: 생성될 프롬프트 텍스트 (요약)
    """
    preview = f"""
[SYSTEM PROMPT]
{get_mari_persona()[:200]}...

[USER PROMPT]
전문가 분석 결과를 마리의 톤으로 변환 요청
- 강아지 이름: {dog_name}
- 솔루션 개수: {len(raw_json.get("solutions_best_fit", []))}개
- 가이던스 개수: {len(raw_json.get("future_guidance", []))}개
"""

    return preview
