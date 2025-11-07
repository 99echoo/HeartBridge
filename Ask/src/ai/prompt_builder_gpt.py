"""
파일명: prompt_builder_gpt.py
목적: GPT-4o 기반 2단계 AI 시스템의 프롬프트 생성 로직
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


# ===== GPT-4o 전용 페르소나 (더 직접적, 명확한 규칙) =====

GPT_EXPERT_PERSONA = """You are a professional dog behavior trainer with 10+ years of experience.

## Your Task
Analyze the dog's behavior based on:
1. GPT-4 Vision image analysis results (if provided)
2. Survey responses from the owner

## Analysis Framework
**Image Analysis (Priority):**
- Breed & physical appearance
- Emotional state (tension, alertness, calmness)
- Posture & body language (ears, tail position)
- Behavioral cues (stress signals, positive indicators)

**Survey Analysis:**
- Problem frequency, intensity, context
- Owner's hardest challenge (key focus)
- Environmental factors (living situation, family, schedule)

**Final Diagnosis:**
- Combine image + survey data
- Extract 3-5 key characteristics
- Provide prioritized solutions

## Critical Output Rules (MUST FOLLOW)
1. **solutions_best_fit**: EXACTLY 3 items (no more, no less)
2. **future_guidance**: EXACTLY 3 items (no more, no less)
3. **Specific numbers required**: Include concrete values
   - Distance: "3-5m" or "10m"
   - Time: "5 minutes daily" or "10-15 minutes"
   - Frequency: "3 times per day" or "twice a week"
   - Duration: "2 weeks" or "1 month"
4. **Confidence score**: 0.0-1.0 (based on information completeness)
   - 0.8-1.0: Complete information + clear problem
   - 0.5-0.7: Basic information + moderate clarity
   - 0.0-0.4: Limited information + complex problem

## Output Format
- Language: Korean (한국어)
- Format: JSON only (no markdown, no explanations)
- Style: Professional, objective, specific

## JSON Schema (STRICT)
```json
{
    "analysis_summary": {
        "core_issue": "핵심 문제 진단 (2-3 문장)",
        "root_cause": "근본 원인 분석 (2-3 문장)",
        "key_characteristics": ["특징 1", "특징 2", "특징 3-5"]
    },
    "solutions_best_fit": [
        {
            "title": "솔루션 제목",
            "content": "핵심 설명 (구체적 수치 포함)",
            "details": ["방법 1", "방법 2", "방법 3"],
            "expected_outcome": "기대 효과"
        },
        {}, {}  // EXACTLY 3 solutions
    ],
    "future_guidance": [
        {
            "principle": "핵심 원칙",
            "content": "설명",
            "action": "구체적 행동 (수치 포함)"
        },
        {}, {}  // EXACTLY 3 guidance items
    ],
    "core_message": "훈련 철학 메시지 (1-2 문장)",
    "confidence_score": 0.85
}
```

CRITICAL: Output ONLY valid JSON matching the schema above. No markdown blocks, no explanations.
"""


# ===== 1차 AI: 전문가 분석 프롬프트 (GPT-4o 최적화) =====

def build_expert_analysis_prompt(
    responses: dict,
    dog_photo: bytes,
    behavior_media: Optional[bytes] = None,
    vision_analysis: Optional[dict] = None
) -> dict:
    """
    1차 AI(전문가 분석)용 프롬프트를 생성합니다 (GPT-4o 최적화).

    Args:
        responses: st.session_state.responses (설문 응답 딕셔너리)
        dog_photo: 강아지 사진 바이트 데이터 (사용하지 않음, vision_analysis로 대체)
        behavior_media: 행동 영상/사진 바이트 데이터 (선택)
        vision_analysis: GPT-4 Vision 분석 결과 (필수)

    Returns:
        dict: {
            "system": GPT_EXPERT_PERSONA,
            "user": "구조화된 분석 요청 텍스트 (vision_analysis 포함)",
            "images": None
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

    # vision_analysis 섹션 (GPT-4o는 더 간결하게)
    vision_section = ""
    if vision_analysis:
        vision_section = f"""
## Image Analysis Results (GPT-4 Vision)
**Breed & Appearance:** {vision_analysis.get("breed_analysis", "N/A")}
**Emotional State:** {vision_analysis.get("emotional_state", "N/A")}
**Posture & Body Language:** {vision_analysis.get("posture_body_language", "N/A")}
**Environment:** {vision_analysis.get("environment", "N/A")}
**Behavioral Cues:** {vision_analysis.get("behavioral_cues", "N/A")}
**Overall Assessment:** {vision_analysis.get("overall_assessment", "N/A")}
"""

    # GPT-4o는 짧고 직접적인 프롬프트 선호
    user_prompt = f"""Analyze {dog_info["name"]}'s behavior and output JSON.
{vision_section}

## Dog Information
- **Name:** {dog_info["name"]}
- **Age:** {dog_info["age"]}
- **Breed:** {dog_info["breed"]}
- **Gender:** {dog_info["gender"]}
- **Neutered:** {dog_info["neutered"]}
- **Other Pets:** {dog_info["other_pets"]}

## Personality Traits
- **Usual Traits:** {", ".join(personality["traits"]) if personality["traits"] else "Unknown"}
- **Most Active Time:** {personality["activity_time"]}

## Problem Behavior (CRITICAL - PRIMARY FOCUS)
- **Main Concerns:** {", ".join(problem["main_concerns"]) if problem["main_concerns"] else "Unknown"}
- **When Started:** {problem["start_time"]}
- **Trigger Situations:** {problem["situation"]}
- **Already Tried:** {problem["tried_solutions"]}
- **⚠️ OWNER'S BIGGEST CHALLENGE (FOCUS HERE):** "{problem["hardest_part"]}"

## Living Environment
- **Housing Type:** {environment["living"]}
- **Family Members:** {environment["family"]}
- **Daily Outing Schedule:** {environment["outing_time"]}

---

## Your Task (STRICT REQUIREMENTS)
1. **Analyze** {dog_info["name"]}'s behavior comprehensively
2. **Prioritize** the owner's biggest challenge: "{problem["hardest_part"]}"
3. **Include** specific, actionable numbers in all solutions:
   - Distances (e.g., "3-5m", "10m")
   - Time durations (e.g., "5 minutes", "10-15 minutes")
   - Frequencies (e.g., "3 times daily", "twice a week")
   - Training periods (e.g., "2 weeks", "1 month")
4. **Output** EXACTLY 3 solutions and EXACTLY 3 guidance items
5. **Format** JSON only (no markdown, no explanations)

**Begin analysis now. Output JSON only.**
"""

    return {
        "system": GPT_EXPERT_PERSONA,
        "user": user_prompt,
        "images": None,  # GPT-4 Vision이 이미 분석했으므로 이미지 전송 불필요
    }


# ===== 2차 AI: 마리 페르소나 변환 프롬프트 (GPT-4o 최적화) =====

def build_mari_conversion_prompt(
    raw_json: dict,
    dog_name: str,
    dog_age: str,
    hardest_part: str
) -> dict:
    """
    2차 AI(마리 변환)용 프롬프트를 생성합니다 (GPT-4o 최적화).

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
[SYSTEM PROMPT (GPT-4o)]
{GPT_EXPERT_PERSONA[:200]}...

[USER PROMPT]
Dog Info:
- Name: {dog_info["name"]}
- Age: {dog_info["age"]}
- Breed: {dog_info["breed"]}

Problem:
- Main Concerns: {", ".join(problem["main_concerns"]) if problem["main_concerns"] else "Unknown"}
- Hardest Part: {problem["hardest_part"]}

Environment:
- Living: {environment["living"]}
- Family: {environment["family"]}
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
Convert expert analysis to Mari's warm tone
- Dog Name: {dog_name}
- Solutions: {len(raw_json.get("solutions_best_fit", []))}
- Guidance: {len(raw_json.get("future_guidance", []))}
"""

    return preview
