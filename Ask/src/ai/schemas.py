"""
파일명: schemas.py
목적: GPT-5 Responses API용 JSON Schema 정의
작성일: 2025-01-26
"""

from typing import Dict, Any


# ===== Vision 분석 JSON Schema =====

VISION_SCHEMA: Dict[str, Any] = {
    "name": "VisionBehaviorReport",
    "schema": {
        "type": "object",
        "required": [
            "breed_analysis",
            "emotional_state",
            "posture_body_language",
            "environment",
            "behavioral_cues",
            "overall_assessment"
        ],
        "properties": {
            "breed_analysis": {
                "type": "string",
                "description": "품종 및 외형적 특징 (2-3 문장)",
                "maxLength": 500
            },
            "emotional_state": {
                "type": "string",
                "description": "표정과 감정 상태 분석 (2-3 문장)",
                "maxLength": 500
            },
            "posture_body_language": {
                "type": "string",
                "description": "자세 및 신체 언어 (2-3 문장)",
                "maxLength": 500
            },
            "environment": {
                "type": "string",
                "description": "주변 환경 및 맥락 (1-2 문장)",
                "maxLength": 300
            },
            "behavioral_cues": {
                "type": "string",
                "description": "행동적 단서 및 스트레스 신호 (2-3 문장)",
                "maxLength": 500
            },
            "overall_assessment": {
                "type": "string",
                "description": "전체적인 평가 (1-2 문장)",
                "maxLength": 300
            }
        },
        "additionalProperties": False
    },
    "strict": True
}


# ===== 전문가 분석 JSON Schema =====

EXPERT_ANALYSIS_SCHEMA: Dict[str, Any] = {
    "name": "ExpertAnalysis",
    "schema": {
        "type": "object",
        "required": [
            "analysis_summary",
            "solutions_best_fit",
            "future_guidance",
            "core_message",
            "confidence_score"
        ],
        "properties": {
            "analysis_summary": {
                "type": "object",
                "required": ["core_issue", "root_cause", "key_characteristics"],
                "properties": {
                    "core_issue": {
                        "type": "string",
                        "description": "문제의 핵심 진단",
                        "maxLength": 300
                    },
                    "root_cause": {
                        "type": "string",
                        "description": "근본 원인 분석",
                        "maxLength": 400
                    },
                    "key_characteristics": {
                        "type": "array",
                        "description": "핵심 특징 3-5개",
                        "items": {"type": "string", "maxLength": 200},
                        "minItems": 3,
                        "maxItems": 5
                    }
                },
                "additionalProperties": False
            },
            "solutions_best_fit": {
                "type": "array",
                "description": "정확히 3개의 맞춤 솔루션",
                "items": {
                    "type": "object",
                    "required": ["title", "content", "details"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "솔루션 제목",
                            "maxLength": 80
                        },
                        "content": {
                            "type": "string",
                            "description": "핵심 설명",
                            "maxLength": 500
                        },
                        "details": {
                            "type": "array",
                            "description": "구체적 실행 방법",
                            "items": {"type": "string", "maxLength": 300},
                            "minItems": 1,
                            "maxItems": 5
                        }
                    },
                    "additionalProperties": False
                },
                "minItems": 3,
                "maxItems": 3
            },
            "future_guidance": {
                "type": "array",
                "description": "정확히 3개의 미래 가이던스",
                "items": {
                    "type": "object",
                    "required": ["principle", "content"],
                    "properties": {
                        "principle": {
                            "type": "string",
                            "description": "핵심 원칙",
                            "maxLength": 80
                        },
                        "content": {
                            "type": "string",
                            "description": "설명",
                            "maxLength": 400
                        }
                    },
                    "additionalProperties": False
                },
                "minItems": 3,
                "maxItems": 3
            },
            "core_message": {
                "type": "string",
                "description": "핵심 메시지 1개 (훈련 철학)",
                "maxLength": 300
            },
            "confidence_score": {
                "type": "number",
                "description": "신뢰도 점수 (0.0-1.0)",
                "minimum": 0.0,
                "maximum": 1.0
            }
        },
        "additionalProperties": False
    },
    "strict": True
}

MARI_NARRATIVE_SCHEMA: Dict[str, Any] = {
    "name": "MariNarrative",
    "schema": {
        "type": "object",
        "required": ["header", "solutions", "guidance", "mari_closing"],
        "properties": {
            "header": {
                "type": "object",
                "required": ["title", "summary"],
                "properties": {
                    "title": {"type": "string", "maxLength": 120},
                    "summary": {"type": "string", "maxLength": 800},
                },
                "additionalProperties": False,
            },
            "solutions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["title", "content", "steps"],
                    "properties": {
                        "title": {"type": "string", "maxLength": 80},
                        "content": {"type": "string", "maxLength": 500},
                        "steps": {
                            "type": "array",
                            "items": {"type": "string", "maxLength": 300},
                            "minItems": 2,
                            "maxItems": 4,
                        },
                    },
                    "additionalProperties": False,
                },
                "minItems": 3,
                "maxItems": 3,
            },
            "guidance": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["principle", "description"],
                    "properties": {
                        "principle": {"type": "string", "maxLength": 80},
                        "description": {"type": "string", "maxLength": 400},
                    },
                    "additionalProperties": False,
                },
                "minItems": 3,
                "maxItems": 3,
            },
            "mari_closing": {
                "type": "object",
                "required": ["core_message"],
                "properties": {
                    "core_message": {"type": "string", "maxLength": 300},
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    },
    "strict": True,
}


# ===== Normalization용 기본값 =====

DEFAULT_SOLUTION = {
    "title": "추가 솔루션",
    "content": "정보가 부족하여 자동 생성된 솔루션입니다.",
    "details": ["보호자님의 상황에 맞게 조정해주세요."],
    "expected_outcome": "점진적인 개선이 기대됩니다."
}

DEFAULT_GUIDANCE = {
    "principle": "일관성 유지",
    "content": "훈련은 일관되게 진행하는 것이 중요합니다.",
    "action": "매일 같은 시간에 짧게라도 훈련을 반복하세요."
}


# ===== Normalization 함수 =====

def normalize_array_to_length(
    items: list,
    target_length: int,
    default_item: Dict[str, Any]
) -> list:
    """
    배열을 목표 길이로 정규화합니다 (부족하면 채우고, 초과하면 자름).

    Args:
        items: 원본 배열
        target_length: 목표 길이
        default_item: 부족할 때 채울 기본 아이템

    Returns:
        list: 정규화된 배열
    """
    items = list(items or [])

    # 초과하면 자르기
    if len(items) > target_length:
        items = items[:target_length]

    # 부족하면 채우기
    while len(items) < target_length:
        items.append(default_item.copy())

    return items


def normalize_expert_json(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    전문가 분석 JSON을 정규화합니다 (정확히 3개 보장).

    Args:
        raw_json: 원본 JSON

    Returns:
        dict: 정규화된 JSON
    """
    # solutions_best_fit 정규화
    raw_json["solutions_best_fit"] = normalize_array_to_length(
        raw_json.get("solutions_best_fit", []),
        target_length=3,
        default_item=DEFAULT_SOLUTION
    )

    # future_guidance 정규화
    raw_json["future_guidance"] = normalize_array_to_length(
        raw_json.get("future_guidance", []),
        target_length=3,
        default_item=DEFAULT_GUIDANCE
    )

    return raw_json


# ===== Schema 검증 함수 =====

def validate_expert_json(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    전문가 분석 JSON이 스키마를 만족하는지 검증합니다.

    Args:
        data: 검증할 JSON

    Returns:
        tuple: (성공 여부, 에러 메시지)
    """
    try:
        # 필수 필드 확인
        required_fields = ["analysis_summary", "solutions_best_fit", "future_guidance", "core_message", "confidence_score"]
        for field in required_fields:
            if field not in data:
                return False, f"필수 필드 누락: {field}"

        # solutions_best_fit 개수 확인
        solutions = data.get("solutions_best_fit", [])
        if not isinstance(solutions, list) or len(solutions) != 3:
            return False, f"solutions_best_fit는 정확히 3개여야 합니다 (현재: {len(solutions)}개)"

        # future_guidance 개수 확인
        guidance = data.get("future_guidance", [])
        if not isinstance(guidance, list) or len(guidance) != 3:
            return False, f"future_guidance는 정확히 3개여야 합니다 (현재: {len(guidance)}개)"

        # confidence_score 범위 확인
        score = data.get("confidence_score", 0)
        if not (0.0 <= score <= 1.0):
            return False, f"confidence_score는 0.0-1.0 범위여야 합니다 (현재: {score})"

        return True, ""

    except Exception as e:
        return False, f"검증 중 오류: {str(e)}"
