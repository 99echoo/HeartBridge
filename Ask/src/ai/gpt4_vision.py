"""
파일명: gpt4_vision.py
목적: GPT-4o를 사용한 반려견 이미지 분석 (전처리)
작성일: 2025-11-02
수정일: 2025-11-02 - GPT-4 Vision → GPT-4o 모델 변경
"""

import base64
import logging
from typing import Dict, Optional
import openai
from openai import OpenAI

from config.settings import settings


# ===== 로깅 설정 =====

logger = logging.getLogger("gpt4_vision")
logger.setLevel(logging.DEBUG)

# analyzer.py와 같은 로거 설정 (같은 파일에 기록)
if not logger.handlers:
    from pathlib import Path
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "analyzer.log"

    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [GPT4] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# ===== GPT-4 Vision 프롬프트 =====

VISION_ANALYSIS_PROMPT = """당신은 반려견 행동 전문가로서 이미지를 분석하는 역할입니다.

아래 이미지를 보고 다음 항목들을 상세히 분석해주세요:

## 분석 항목

1. **품종 및 외형적 특징**
   - 품종 추정 (확실하지 않으면 "추정" 명시)
   - 크기 (소형/중형/대형)
   - 털 색상과 질감
   - 체형 상태 (정상/마른/통통함)

2. **표정 및 감정 상태**
   - 눈의 상태 (크게 뜨여있음/반쯤 감김/경계하는 눈빛 등)
   - 귀의 위치 (앞으로 기울임/뒤로 젖혀짐/중립)
   - 입과 혀의 상태 (헥헥거림/다물고 있음/웃는 표정)
   - 전체적인 감정 (편안함/긴장/흥분/불안/공포)

3. **자세 및 신체 언어**
   - 몸의 자세 (서있음/앉아있음/누워있음/웅크림)
   - 꼬리 위치와 상태 (높이 들림/중립/다리 사이에 숨김/흔들림)
   - 근육 긴장도 (이완/긴장)
   - 특이한 자세나 행동

4. **주변 환경 및 맥락**
   - 촬영 장소 (실내/실외/특정 장소)
   - 주변 사물이나 사람
   - 환경이 강아지에게 미칠 수 있는 영향

5. **행동적 단서**
   - 이미지에서 포착된 행동 (짖음/점프/회피 등)
   - 스트레스 신호 (헥헥거림/하품/눈 피함/코 핥음)
   - 긍정적 신호 (편안한 자세/부드러운 눈빛)

## 출력 형식

반드시 아래 JSON 형식으로만 응답하세요. 주석이나 설명 없이 JSON만 출력하세요.

```json
{
    "breed_analysis": "품종 및 외형 특징 (2-3 문장)",
    "emotional_state": "표정과 감정 상태 분석 (2-3 문장)",
    "posture_body_language": "자세 및 신체 언어 (2-3 문장)",
    "environment": "주변 환경 및 맥락 (1-2 문장)",
    "behavioral_cues": "행동적 단서 및 스트레스 신호 (2-3 문장)",
    "overall_assessment": "전체적인 평가 (1-2 문장)"
}
```

IMPORTANT:
- 한국어로 작성
- 객관적이고 구체적으로 묘사
- 추측은 "~으로 보임", "~일 가능성" 등으로 표현
- JSON 형식 엄수
"""


# ===== GPT-4 Vision API 호출 =====

async def analyze_dog_image_with_gpt4(
    image_bytes: bytes,
    max_retries: int = 2
) -> Dict[str, str]:
    """
    GPT-4o를 사용하여 반려견 이미지를 분석합니다.

    Args:
        image_bytes: 이미지 바이트 데이터 (최대 20MB)
        max_retries: 최대 재시도 횟수

    Returns:
        dict: {
            "breed_analysis": str,
            "emotional_state": str,
            "posture_body_language": str,
            "environment": str,
            "behavioral_cues": str,
            "overall_assessment": str
        }

    Raises:
        Exception: API 호출 실패 시
    """
    logger.info(f"GPT-4o 이미지 분석 시작 (크기: {len(image_bytes)} bytes)")

    # 이미지를 base64로 인코딩
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        logger.debug(f"Base64 인코딩 완료 (인코딩 후: {len(base64_image)} chars)")
    except Exception as e:
        logger.error(f"Base64 인코딩 실패: {str(e)}")
        raise Exception(f"이미지 인코딩 실패: {str(e)}")

    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"GPT-4o API 호출 시도 {attempt + 1}/{max_retries + 1}")

            # GPT-4o API 호출
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": VISION_ANALYSIS_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # 고해상도 분석
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # 일관성 있는 분석을 위해 낮은 temperature
            )

            # 응답 추출
            result_text = response.choices[0].message.content
            logger.info(f"GPT-4o 응답 받음 (길이: {len(result_text)} chars)")
            logger.debug(f"응답 내용: {result_text[:200]}...")

            # JSON 파싱
            import json
            import re

            # JSON 블록 추출 (```json ... ``` 형식 지원)
            json_match = re.search(r"```json\s*\n(.*?)\n```", result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록 없으면 전체를 JSON으로 파싱 시도
                json_str = result_text

            try:
                vision_result = json.loads(json_str)
                logger.info("GPT-4o 분석 성공!")
                return vision_result

            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {str(e)}")
                logger.error(f"파싱 시도한 문자열: {json_str[:200]}...")

                # 재시도할 것이므로 continue
                if attempt < max_retries:
                    continue
                else:
                    raise Exception(f"GPT-4o 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")

        except openai.APIError as e:
            logger.error(f"OpenAI API 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")

            if attempt < max_retries:
                import time
                wait_time = 2 ** attempt
                logger.warning(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                error_msg = f"GPT-4o API 호출 실패 (시도 {max_retries + 1}회): {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"예기치 않은 오류 (시도 {attempt + 1}/{max_retries + 1}): {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")

            if attempt < max_retries:
                import time
                wait_time = 2 ** attempt
                logger.warning(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                error_msg = f"예기치 않은 오류: {str(e)}"
                logger.critical(error_msg)
                raise Exception(error_msg)


# ===== 폴백: 간단한 기본 분석 =====

def get_fallback_vision_analysis(dog_name: str = "강아지") -> Dict[str, str]:
    """
    GPT-4o 실패 시 사용할 기본 분석 결과

    Args:
        dog_name: 강아지 이름

    Returns:
        dict: 기본 vision_analysis 구조
    """
    logger.warning("GPT-4o 폴백 - 기본 분석 사용")

    return {
        "breed_analysis": "이미지 분석을 수행할 수 없어 품종 정보를 확인할 수 없습니다.",
        "emotional_state": "표정 분석이 제한적입니다. 설문 응답을 중심으로 평가합니다.",
        "posture_body_language": "자세 분석이 제한적입니다. 보호자의 설명을 우선합니다.",
        "environment": "환경 정보가 제한적입니다.",
        "behavioral_cues": "이미지 기반 행동 분석이 제한적입니다. 설문 응답을 중심으로 분석합니다.",
        "overall_assessment": f"{dog_name}의 이미지 분석 중 오류가 발생했지만, 설문 응답을 바탕으로 최선의 분석을 제공합니다."
    }
