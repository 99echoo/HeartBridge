"""
파일명: survey_questions.py
목적: 반려견 행동 분석을 위한 설문 항목 정의
작성일: 2025-01-26
수정일: 2025-01-26 - 기본 정보와 행동 분석 설문 분리
"""

from typing import List, Dict

# ===== 1. 기본 정보 입력 (간단하고 빠르게) =====

BASIC_INFO_FIELDS: List[Dict] = [
    {
        "id": "dog_name",
        "question": "🐶 강아지 이름",
        "type": "text",
        "placeholder": "예: 마리",
        "required": True,
    },
    {
        "id": "owner_email",
        "question": "📧 이메일 (선택)",
        "type": "text",
        "placeholder": "결과를 이메일로 받고 싶으시면 입력해주세요",
        "required": False,
    },
    {
        "id": "dog_age",
        "question": "🐶 강아지 나이",
        "type": "radio",
        "options": [
            {"value": "puppy", "label": "🍼 퍼피 (0-6개월)"},
            {"value": "young", "label": "🌱 어린 강아지 (7개월-2년)"},
            {"value": "adult", "label": "💪 성견 (3-7년)"},
            {"value": "senior", "label": "👴 노견 (8년 이상)"},
            {"value": "unknown", "label": "❓ 정확히 모름"},
        ],
        "required": True,
    },
    {
        "id": "dog_size",
        "question": "🐕 강아지 크기",
        "type": "radio",
        "options": [
            {"value": "tiny", "label": "🐁 초소형견 (3kg 미만)"},
            {"value": "small", "label": "🐶 소형견 (3-10kg)"},
            {"value": "medium", "label": "🦮 중형견 (10-25kg)"},
            {"value": "large", "label": "🐕 대형견 (25-40kg)"},
            {"value": "giant", "label": "🐺 초대형견 (40kg 이상)"},
        ],
        "required": True,
    },
]


# ===== 2. 행동 분석 설문 (깊이 있는 행동 파악) =====

BEHAVIOR_SURVEY_QUESTIONS: List[Dict] = [
    {
        "id": "q1",
        "question": "😟 현재 가장 걱정되는 문제 행동은 무엇인가요?",
        "description": "여러 개 있다면 가장 심각한 하나를 선택해주세요.",
        "type": "radio",
        "options": [
            {"value": "barking", "label": "🔊 과도한 짖음", "description": "낯선 사람, 소리, 혼자 있을 때 짖음"},
            {"value": "separation_anxiety", "label": "😭 분리불안", "description": "혼자 두면 울거나 물건 파괴"},
            {"value": "aggression", "label": "😠 공격성", "description": "물거나 으르렁거림"},
            {"value": "destruction", "label": "💥 파괴 행동", "description": "가구, 신발 등 물건 파손"},
            {"value": "toilet", "label": "🚽 배변 문제", "description": "정해진 장소에 배변하지 않음"},
        ],
    },
    {
        "id": "q2",
        "question": "⏰ 문제 행동이 얼마나 자주 발생하나요?",
        "description": "최근 1주일을 기준으로 생각해주세요.",
        "type": "radio",
        "options": [
            {"value": "always", "label": "⚠️ 거의 항상 (하루 10회 이상)", "description": "매우 심각한 수준"},
            {"value": "often", "label": "🔴 자주 (하루 5-10회)", "description": "일상생활에 큰 지장"},
            {"value": "sometimes", "label": "🟡 가끔 (하루 2-4회)", "description": "특정 상황에서 발생"},
            {"value": "rarely", "label": "🟢 드물게 (하루 1회 미만)", "description": "가끔씩만 발생"},
            {"value": "recently", "label": "🆕 최근에 시작됨", "description": "1-2주 내에 처음 시작"},
        ],
    },
    {
        "id": "q3",
        "question": "🎯 문제 행동이 주로 언제 발생하나요?",
        "description": "가장 빈번하게 발생하는 상황을 선택해주세요.",
        "type": "radio",
        "options": [
            {"value": "when_alone", "label": "🚪 혼자 있을 때", "description": "보호자가 외출하거나 다른 방에 있을 때"},
            {"value": "with_strangers", "label": "👥 낯선 사람/강아지를 볼 때", "description": "산책 중이나 방문객이 왔을 때"},
            {"value": "specific_sound", "label": "🔔 특정 소리를 들을 때", "description": "초인종, 천둥소리, 청소기 등"},
            {"value": "want_attention", "label": "💭 관심이 필요할 때", "description": "심심하거나 놀아달라고 요구할 때"},
            {"value": "anytime", "label": "🌐 특별한 패턴 없이 무작위", "description": "언제 발생할지 예측하기 어려움"},
        ],
    },
    {
        "id": "q4",
        "question": "📅 이 문제 행동은 언제부터 시작되었나요?",
        "description": "문제를 처음 인식한 시점을 생각해주세요.",
        "type": "radio",
        "options": [
            {"value": "from_puppy", "label": "🍼 어릴 때부터 (퍼피 시절)", "description": "입양 직후부터 계속"},
            {"value": "few_months", "label": "📆 최근 몇 개월 사이", "description": "2-6개월 전부터"},
            {"value": "few_weeks", "label": "🆕 최근 몇 주 사이", "description": "2-4주 전부터"},
            {"value": "sudden_change", "label": "⚡ 갑자기 시작됨", "description": "최근 1-2주, 특정 사건 후"},
            {"value": "gradual", "label": "📈 점점 심해짐", "description": "예전엔 괜찮았는데 점차 악화"},
        ],
    },
    {
        "id": "q5",
        "question": "🤔 문제 행동이 발생했을 때 주로 어떻게 대응하시나요?",
        "description": "평소 가장 자주 하는 반응을 선택해주세요.",
        "type": "radio",
        "options": [
            {"value": "ignore", "label": "🙈 무시한다", "description": "반응하지 않고 그냥 둠"},
            {"value": "scold", "label": "😤 혼낸다", "description": "소리 지르거나 'NO'라고 말함"},
            {"value": "distract", "label": "🎾 주의를 돌린다", "description": "장난감이나 간식으로 관심 전환"},
            {"value": "comfort", "label": "🤗 달랜다", "description": "쓰다듬거나 안아줌"},
            {"value": "inconsistent", "label": "🔀 일정하지 않다", "description": "상황에 따라 다르게 반응"},
        ],
    },
    {
        "id": "q6",
        "question": "⏱️ 우리 강아지가 하루 중 혼자 있는 시간은 얼마나 되나요?",
        "description": "평균적인 평일 기준으로 답변해주세요.",
        "type": "radio",
        "options": [
            {"value": "never_alone", "label": "👨‍👩‍👧‍👦 거의 혼자 있지 않음 (1시간 미만)", "description": "재택근무, 은퇴, 전업주부 등"},
            {"value": "short_time", "label": "⏰ 짧은 시간 (1-4시간)", "description": "짧은 외출, 출퇴근"},
            {"value": "half_day", "label": "🕐 반나절 정도 (4-8시간)", "description": "일반적인 직장인"},
            {"value": "long_time", "label": "🕘 긴 시간 (8-12시간)", "description": "장시간 근무"},
            {"value": "vary", "label": "🔄 매일 다름", "description": "불규칙한 일정"},
        ],
    },
    {
        "id": "q7",
        "question": "🐕‍🦺 다른 사람이나 강아지를 만날 기회가 얼마나 되나요?",
        "description": "사회화 정도를 파악하기 위한 질문입니다.",
        "type": "radio",
        "options": [
            {"value": "very_social", "label": "🌟 매우 자주 (거의 매일)", "description": "강아지 유치원, 공원 자주 방문"},
            {"value": "regular", "label": "👍 정기적으로 (주 3-4회)", "description": "산책 중 다른 강아지 만남"},
            {"value": "sometimes", "label": "🤷 가끔 (주 1-2회)", "description": "주말에만 외출"},
            {"value": "rarely", "label": "🏠 거의 없음 (월 1-2회)", "description": "집에서만 생활"},
            {"value": "isolated", "label": "❌ 거의 격리 상태", "description": "다른 강아지/사람 접촉 극히 드뭄"},
        ],
    },
]


def get_basic_info_fields() -> List[Dict]:
    """
    기본 정보 입력 필드를 반환합니다.

    Returns:
        List[Dict]: 기본 정보 필드 리스트
    """
    return BASIC_INFO_FIELDS


def get_behavior_survey_questions() -> List[Dict]:
    """
    행동 분석 설문 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 행동 분석 설문 리스트
    """
    return BEHAVIOR_SURVEY_QUESTIONS


def get_survey_questions() -> List[Dict]:
    """
    (하위 호환성) 행동 분석 설문 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 설문 질문 리스트
    """
    return BEHAVIOR_SURVEY_QUESTIONS


def get_question_by_id(question_id: str) -> Dict:
    """
    ID로 특정 질문을 가져옵니다.

    Args:
        question_id: 질문 ID (q1, q2, ...)

    Returns:
        Dict: 질문 데이터 또는 None
    """
    for q in BEHAVIOR_SURVEY_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def validate_basic_info(basic_info: Dict) -> bool:
    """
    기본 정보 입력이 유효한지 검증합니다.

    Args:
        basic_info: 기본 정보 딕셔너리

    Returns:
        bool: 유효하면 True, 아니면 False
    """
    required_fields = [field["id"] for field in BASIC_INFO_FIELDS if field.get("required", False)]

    for field_id in required_fields:
        if field_id not in basic_info or not basic_info[field_id]:
            return False

    return True


def validate_survey_response(responses: Dict) -> bool:
    """
    행동 분석 설문 응답이 유효한지 검증합니다.

    Args:
        responses: 설문 응답 딕셔너리 {q1: value, q2: value, ...}

    Returns:
        bool: 유효하면 True, 아니면 False
    """
    # 모든 질문에 답변했는지 확인
    for q in BEHAVIOR_SURVEY_QUESTIONS:
        if q["id"] not in responses or not responses[q["id"]]:
            return False

    # 각 답변이 유효한 옵션인지 확인
    for q in BEHAVIOR_SURVEY_QUESTIONS:
        q_id = q["id"]
        response_value = responses[q_id]
        valid_values = [opt["value"] for opt in q["options"]]

        if response_value not in valid_values:
            return False

    return True


# 예시 데이터 (테스트용)
EXAMPLE_BASIC_INFO = {
    "dog_name": "마리",
    "owner_email": "test@heartbridge.com",
    "dog_age": "young",
    "dog_size": "small",
}

EXAMPLE_SURVEY_RESPONSE = {
    "q1": "barking",  # 과도한 짖음
    "q2": "often",  # 자주 발생
    "q3": "when_alone",  # 혼자 있을 때
    "q4": "few_months",  # 최근 몇 개월
    "q5": "scold",  # 혼낸다
    "q6": "half_day",  # 반나절 혼자
    "q7": "sometimes",  # 가끔 사회화
}
