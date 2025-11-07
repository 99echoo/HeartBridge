"""
파일명: survey_questions.py
목적: 반려견 행동 분석을 위한 설문 항목 정의
작성일: 2025-01-26
수정일: 2025-01-26 - 새로운 5개 섹션 구조로 재작성
"""

from typing import List, Dict

# ===== ① 기본 정보 섹션 =====

BASIC_INFO_QUESTIONS: List[Dict] = [
    {
        "id": "dog_name",
        "question": "반려견의 이름을 알려주세요",
        "type": "text",
        "placeholder": "예: 마루, 코코, 구름 등",
        "required": True,
    },
    {
        "id": "dog_birth",
        "question": "반려견의 나이를 알려주세요. 정확하지 않아도 괜찮아요😄",
        "type": "select_year_month",
        "required": True,
    },
    {
        "id": "dog_breed",
        "question": "반려견의 품종이 어떻게 되나요?",
        "type": "text",
        "placeholder": "예: 포메라니안 / 말티즈 / 믹스견",
        "required": True,
    },
    {
        "id": "dog_gender",
        "question": "반려견의 성별은 무엇인가요?",
        "type": "radio_horizontal",
        "options": [
            {"value": "male", "label": "남아"},
            {"value": "female", "label": "여아"},
        ],
        "required": True,
    },
    {
        "id": "dog_neutered",
        "question": "중성화를 진행했나요?",
        "type": "radio_horizontal",
        "options": [
            {"value": "yes", "label": "예"},
            {"value": "no", "label": "아니요"},
        ],
        "required": False,
    },
    {
        "id": "other_pets",
        "question": "다른 반려동물과 함께 살고 있나요? (선택)",
        "type": "checkbox_multiple",
        "options": [
            {"value": "dog", "label": "강아지"},
            {"value": "cat", "label": "고양이"},
            {"value": "other", "label": "기타"},
        ],
        "required": False,
    },
]


# ===== ② 성향 파악 섹션 =====

PERSONALITY_QUESTIONS: List[Dict] = [
    {
        "id": "personality_traits",
        "question": "반려견의 평소 성향을 가장 잘 나타내는 문장을 골라주세요 (복수 선택 가능)",
        "type": "checkbox_grid",
        "options": [
            {"value": "shy", "label": "낯가림이 심해요"},
            {"value": "social", "label": "사람을 좋아하고 활발해요"},
            {"value": "fearful", "label": "겁이 많아요"},
            {"value": "active_hard_control", "label": "산책을 좋아하지만 통제가 어려워요"},
            {"value": "calm_inside_nervous_outside", "label": "집에서는 얌전하지만 밖에서는 예민해요"},
            {"value": "separation_anxiety", "label": "분리불안이 있어요"},
            {"value": "dependent", "label": "보호자에게 의존적이에요"},
            {"value": "hard_to_socialize", "label": "다른 반려견과 어울리기 어려워요"},
        ],
        "required": True,
    },
    {
        "id": "activity_time",
        "question": "반려견이 활발히 활동하는 시간은 얼마나 되나요?",
        "type": "radio_horizontal",
        "options": [
            {"value": "under_30min", "label": "30분 이내"},
            {"value": "30min_to_1h", "label": "30분에서 1시간"},
            {"value": "over_1h", "label": "1시간 이상"},
        ],
        "required": True,
    },
]


# ===== ③ 문제 행동 관련 섹션 =====

BEHAVIOR_PROBLEM_QUESTIONS: List[Dict] = [
    {
        "id": "main_concerns",
        "question": "현재 반려견의 가장 큰 고민거리는 무엇인가요? (복수선택 가능)",
        "type": "checkbox_grid",
        "options": [
            {"value": "barking", "label": "짖음"},
            {"value": "toilet", "label": "배변"},
            {"value": "biting", "label": "입질"},
            {"value": "walk_aggression", "label": "산책 시 공격성"},
            {"value": "stranger_anxiety", "label": "낯선 사람에 대한 불안"},
        ],
        "other_option": True,  # 기타 옵션 활성화
        "required": True,
    },
    {
        "id": "problem_start_time",
        "question": "해당 문제 행동이 시작된 시점은 언제인가요?",
        "type": "radio_horizontal",
        "options": [
            {"value": "within_1month", "label": "최근 1개월 이내"},
            {"value": "over_3months", "label": "3개월 이상"},
            {"value": "over_6months", "label": "6개월 이상 지속"},
        ],
        "required": True,
    },
    {
        "id": "problem_situation",
        "question": "문제 행동이 주로 발생하는 상황을 구체적으로 알려주세요",
        "type": "text",
        "placeholder": "예: 보호자가 외출할 때 / 초인종이 울릴 때 / 다른 개를 만났을 때 등",
        "required": True,
    },
    {
        "id": "tried_solutions",
        "question": "보호자가 지금까지 시도해본 해결 방법이 있다면 알려주세요",
        "type": "text",
        "placeholder": "예: 훈련 영상 시청 / 훈련소 방문 / 간식으로 보상 / 무시하기 등",
        "required": False,
    },
    {
        "id": "hardest_part",
        "question": "문제 행동으로 인해 가장 힘든 점은 무엇인가요?",
        "type": "text",
        "placeholder": "예: 이웃 민원 / 스트레스 / 산책이 어렵다 / 가족 간 갈등 등",
        "required": True,
    },
]


# ===== ④ 환경 정보 섹션 =====

ENVIRONMENT_QUESTIONS: List[Dict] = [
    {
        "id": "living_environment",
        "question": "반려견이 생활하는 환경은 어떤가요?",
        "type": "radio_horizontal",
        "options": [
            {"value": "apartment", "label": "아파트"},
            {"value": "officetel_villa", "label": "오피스텔/빌라/원룸"},
            {"value": "house", "label": "단독주택"},
        ],
        "other_option": True,
        "required": True,
    },
    {
        "id": "family_members",
        "question": "반려견과 함께 사는 가족의 구성원 인원을 알려주세요",
        "type": "radio_horizontal",
        "options": [
            {"value": "1", "label": "1인"},
            {"value": "2-3", "label": "2~3인"},
            {"value": "4+", "label": "4인 이상"},
        ],
        "required": True,
    },
    {
        "id": "has_fixed_outing",
        "question": "고정적인 외출 시간이 있으시면(출근 등), 알려주세요",
        "type": "radio_horizontal",
        "options": [
            {"value": "no", "label": "없음"},
            {"value": "yes", "label": "있음"},
        ],
        "required": True,
    },
    {
        "id": "outing_time_range",
        "question": "외출 시간대를 선택해주세요",
        "type": "time_range",
        "description": "외출 시작 시간과 종료 시간을 선택해주세요",
        "min": 0,
        "max": 24,
        "required": False,
        "conditional": True,  # 조건부 표시
        "depends_on": "has_fixed_outing",  # 이 질문에 의존
        "show_when": "yes",  # 이 값일 때만 표시
    },
]


# ===== ⑤ 사진 및 참고자료 섹션 =====

PHOTO_QUESTIONS: List[Dict] = [
    {
        "id": "dog_photo",
        "question": "반려견의 최근 사진을 업로드해주세요",
        "type": "image",
        "description": "얼굴이 잘 보이는 정면 사진이 좋아요",
        "required": True,
    },
    {
        "id": "behavior_media",
        "question": "행동문제가 나타나는 순간의 영상이나 사진이 있다면 첨부해주세요(준비중인 기능이에요 !)",
        "type": "media",
        "description": "사진 또는 영상을 업로드할 수 있어요",
        "required": False,
    },
]


# ===== 헬퍼 함수들 =====

def get_basic_info_questions() -> List[Dict]:
    """
    기본 정보 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 기본 정보 질문 리스트
    """
    return BASIC_INFO_QUESTIONS


def get_personality_questions() -> List[Dict]:
    """
    성향 파악 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 성향 질문 리스트
    """
    return PERSONALITY_QUESTIONS


def get_behavior_problem_questions() -> List[Dict]:
    """
    문제 행동 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 문제 행동 질문 리스트
    """
    return BEHAVIOR_PROBLEM_QUESTIONS


def get_environment_questions() -> List[Dict]:
    """
    환경 정보 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 환경 정보 질문 리스트
    """
    return ENVIRONMENT_QUESTIONS


def get_photo_questions() -> List[Dict]:
    """
    사진/자료 질문 목록을 반환합니다.

    Returns:
        List[Dict]: 사진 질문 리스트
    """
    return PHOTO_QUESTIONS


def get_all_sections() -> List[Dict]:
    """
    모든 섹션 정보를 반환합니다.

    Returns:
        List[Dict]: 섹션 정보 리스트
    """
    return [
        {
            "id": "basic_info",
            "title": "① 기본 정보",
            "questions": BASIC_INFO_QUESTIONS,
        },
        {
            "id": "personality",
            "title": "② 성향 파악",
            "questions": PERSONALITY_QUESTIONS,
        },
        {
            "id": "behavior_problem",
            "title": "③ 문제 행동 관련",
            "questions": BEHAVIOR_PROBLEM_QUESTIONS,
        },
        {
            "id": "environment",
            "title": "④ 환경 정보",
            "questions": ENVIRONMENT_QUESTIONS,
        },
        {
            "id": "photos",
            "title": "⑤ 사진 및 참고자료",
            "questions": PHOTO_QUESTIONS,
        },
    ]


def validate_responses(responses: Dict, section_id: str) -> tuple[bool, str]:
    """
    특정 섹션의 응답이 유효한지 검증합니다.

    Args:
        responses: 응답 딕셔너리
        section_id: 섹션 ID

    Returns:
        tuple[bool, str]: (유효 여부, 오류 메시지)
    """
    sections = get_all_sections()
    section = next((s for s in sections if s["id"] == section_id), None)

    if not section:
        return False, "섹션을 찾을 수 없습니다."

    for q in section["questions"]:
        if q.get("required", False):
            if q["id"] not in responses or not responses[q["id"]]:
                return False, f"'{q['question']}'에 답변해주세요."

    return True, ""


# 예시 데이터 (테스트용)
EXAMPLE_RESPONSES = {
    # 기본 정보
    "dog_name": "마루",
    "dog_birth": "2022년 5월",
    "dog_breed": "포메라니안",
    "dog_gender": "male",
    "dog_neutered": ["yes"],
    "other_pets": [],
    # 성향
    "personality_traits": ["social", "active_hard_control"],
    "activity_time": "30min_to_1h",
    # 문제 행동
    "main_concerns": ["barking", "walk_aggression"],
    "main_concerns_other": "",
    "problem_start_time": "over_3months",
    "problem_situation": "산책 중 다른 개를 만났을 때 짖어요",
    "tried_solutions": "훈련 영상 시청, 간식으로 보상",
    "hardest_part": "산책이 어렵고 스트레스 받아요",
    # 환경
    "living_environment": "apartment",
    "family_members": "2-3",
    "has_fixed_outing": "yes",
    "outing_time_range": [9, 18],
    # 사진
    "dog_photo": None,
    "behavior_media": None,
}
