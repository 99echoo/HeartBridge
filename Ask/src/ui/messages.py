"""
분석 대기 화면 등에서 사용할 감성 메시지 유틸.
"""

from __future__ import annotations

import random
from typing import Sequence


EMPATHY_TEMPLATES: Sequence[str] = [
    "{dog_name}이는 오늘도 {dog_breed} 특유의 따뜻한 눈빛으로 보호자를 기다리고 있을 거예요.",
    "{dog_breed}인 {dog_name}이의 부드러운 털결이 화면 밖에서도 느껴지는 것 같아요!",
    "사랑스러운 {dog_breed} 친구 {dog_name}에게 꼭 맞는 솔루션을 준비하는 중이에요.",
    "{dog_name}이는 {dog_breed}다운 호기심으로 세상을 바라보고 있을 거예요.",
    "{dog_name}의 작은 표정 변화도 소중하죠. {dog_breed} 친구의 마음을 천천히 열어볼게요.",
    "{dog_breed} 친구 {dog_name}과(와) 함께한 모든 순간이 반짝이도록 솔루션을 만드는 중이에요.",
    "{dog_name}이가 안심할 수 있도록 {dog_breed}에게 어울리는 조언을 곧 전해드릴게요.",
]


def build_empathy_message(dog_name: str | None, dog_breed: str | None) -> str:
    """이름/품종을 기반으로 랜덤 감성 문구를 생성."""
    safe_name = dog_name if dog_name else "우리 친구"
    safe_breed = dog_breed if dog_breed else "사랑스러운 친구"
    template = random.choice(EMPATHY_TEMPLATES)
    return template.format(dog_name=safe_name, dog_breed=safe_breed)
