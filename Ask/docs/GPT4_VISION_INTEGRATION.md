# GPT-4 Vision 통합 업데이트 로그

**작업일**: 2025-11-02
**목적**: Claude API의 5MB 이미지 크기 제한 문제 해결
**방법**: GPT-4 Vision으로 이미지 전처리 → 텍스트 변환 → Claude에 전달

---

## 🎯 문제 상황

### 기존 문제
```
사용자 이미지 (6.3 MB)
  ↓
Base64 인코딩 (8.4 MB)
  ↓
Claude Vision API 호출
  ↓
❌ Error: "image exceeds 5 MB maximum"
```

### 에러 로그
```
[ERROR] Anthropic API 오류:
'messages.0.content.0.image.source.base64: image exceeds 5 MB maximum:
8786112 bytes > 5242880 bytes'
```

---

## ✅ 해결 방안

### 새로운 AI 파이프라인
```
사용자 이미지 (최대 20MB 가능)
  ↓
[0단계] GPT-4 Vision 이미지 전처리 (~2초)
  → 품종, 표정, 자세, 환경, 행동 단서 분석
  → 텍스트로 변환
  ↓
[1차 AI] Claude Sonnet 4.5 전문가 분석 (~5초)
  → GPT-4 Vision 분석 결과 + 설문 응답 종합
  → JSON 형식 출력
  ↓
[2차 AI] Claude Sonnet 4.5 마리 변환 (~3초)
  → 따뜻한 톤으로 변환
  → Markdown 출력
  ↓
결과 표시
```

---

## 📁 변경된 파일 목록

### 1. 새로 생성된 파일

#### `src/ai/gpt4_vision.py` (신규)
**목적**: GPT-4 Vision을 사용한 이미지 전처리

**주요 함수**:
- `analyze_dog_image_with_gpt4(image_bytes, max_retries=2)` → dict
  - GPT-4 Vision API 호출
  - 반려견 이미지 분석 (품종, 표정, 자세, 환경, 행동)
  - JSON 구조로 반환

- `get_fallback_vision_analysis(dog_name)` → dict
  - GPT-4 Vision 실패 시 사용할 기본 분석

**반환 구조**:
```python
{
    "breed_analysis": str,
    "emotional_state": str,
    "posture_body_language": str,
    "environment": str,
    "behavioral_cues": str,
    "overall_assessment": str
}
```

**로깅**: `analyzer.log`에 `[GPT4]` 접두사로 기록

---

### 2. 환경 변수 설정

#### `.env`
**변경 내용**:
```diff
# AI API
ANTHROPIC_API_KEY=sk-ant-api03-...
+ OPENAI_API_KEY=sk-proj-5AWFhWMcqLEJ3FPnA2z3Hw9l9...
```

#### `config/settings.py`
**변경 내용**:
```diff
class Settings(BaseSettings):
    # AI API
    ANTHROPIC_API_KEY: str
+   OPENAI_API_KEY: str
```

---

### 3. 프롬프트 빌더 수정

#### `src/ai/prompt_builder.py`
**함수**: `build_expert_analysis_prompt()`

**변경 사항**:
1. **파라미터 추가**:
   ```python
   def build_expert_analysis_prompt(
       responses: dict,
       dog_photo: bytes,
       behavior_media: Optional[bytes] = None,
       vision_analysis: Optional[dict] = None  # ← 추가
   ) -> dict:
   ```

2. **이미지 전송 중단**:
   ```python
   # 기존:
   return {
       "system": get_expert_persona(),
       "user": user_prompt,
       "images": [base64_encoded_images]  # ← 이미지 전송
   }

   # 변경 후:
   return {
       "system": get_expert_persona(),
       "user": user_prompt,
       "images": None  # ← 더 이상 이미지 전송 안 함
   }
   ```

3. **프롬프트에 이미지 분석 결과 추가**:
   ```python
   if vision_analysis:
       vision_section = f"""

   ## 이미지 분석 결과 (GPT-4 Vision)
   반려견의 사진을 GPT-4 Vision으로 분석한 결과입니다.

   **품종 및 외형:**
   {vision_analysis.get("breed_analysis", "정보 없음")}

   **표정 및 감정 상태:**
   {vision_analysis.get("emotional_state", "정보 없음")}

   ... (생략)
   """
   ```

---

### 4. 페르소나 수정

#### `src/ai/mari_persona.py`
**변경 부분**: `EXPERT_PERSONA`

**Before**:
```python
## 분석 기준
1. **이미지 분석**
   - 품종 특성: 설문 응답과 실제 품종 일치 여부 확인
   - 표정 분석: 긴장도, 경계심, 편안함 정도 파악
   - 자세 분석: 귀, 꼬리 위치로 심리 상태 판단
```

**After**:
```python
## 분석 기준
1. **이미지 분석 결과 (GPT-4 Vision)**
   - 이미지 분석 결과가 제공되면, 이를 우선적으로 참고하세요
   - 품종 및 외형: 설문 응답과 비교하여 일치 여부 확인
   - 표정 및 감정 상태: 긴장도, 경계심, 편안함 정도 파악
   - 이미지 분석 결과가 없으면, 설문 응답만으로 분석 진행
```

**변경 부분**: `MARI_CONVERSION_TEMPLATE`

**템플릿 에러 수정** (사용자 직접 수정):
```python
# Line 145 - 수정됨
# Before: "{key_characteristics를 인용한 한 문장}"
# After: [수정된 내용]

# Line 194 - 수정됨
# Before: "{core_message를 마리체로}"
# After: [수정된 내용]
```

---

### 5. 분석 파이프라인 수정

#### `src/ai/analyzer.py`
**함수**: `analyze_two_stage()`

**Import 추가**:
```python
from src.ai.gpt4_vision import (
    analyze_dog_image_with_gpt4,
    get_fallback_vision_analysis,
)
```

**0단계 전처리 추가**:
```python
# ===== 0단계: GPT-4 Vision 이미지 전처리 =====
logger.info(f"=== GPT-4 Vision 이미지 전처리 시작 (강아지: {dog_name}) ===")
logger.debug(f"dog_photo 크기: {len(dog_photo)} bytes")

vision_analysis = None
try:
    # GPT-4 Vision으로 이미지 분석
    vision_analysis = await analyze_dog_image_with_gpt4(
        image_bytes=dog_photo,
        max_retries=2
    )
    logger.info("GPT-4 Vision 이미지 분석 성공!")

except Exception as e:
    # GPT-4 Vision 실패 시: Fallback 사용
    logger.error(f"GPT-4 Vision 실패, Fallback 사용: {str(e)}")
    vision_analysis = get_fallback_vision_analysis(dog_name=dog_name)
```

**1차 AI 호출 수정**:
```python
# 프롬프트 생성 (vision_analysis 포함)
expert_prompt = build_expert_analysis_prompt(
    responses=responses,
    dog_photo=dog_photo,
    behavior_media=behavior_media,
    vision_analysis=vision_analysis  # ← GPT-4 Vision 결과 전달
)
```

---

### 6. 의존성 추가

#### `requirements.txt`
**변경 내용**:
```diff
# AI/ML
anthropic==0.18.1           # Claude Sonnet 4.5 API
+ openai>=1.0.0               # GPT-4 Vision API (이미지 전처리)
pillow>=10.3.0              # 이미지 처리 및 인스타그램 카드 생성
```

**설치**:
```bash
pip install openai==2.6.1
```

---

## 🐛 발견된 버그 및 수정

### Bug #1: 이미지 크기 제한 초과
**원인**: Claude Vision API의 5MB 제한
**해결**: GPT-4 Vision으로 전처리 (20MB까지 지원)

### Bug #2: 템플릿 KeyError
**원인**: `MARI_CONVERSION_TEMPLATE`에서 `{key_characteristics를 인용한 한 문장}` 사용
**해결**: 사용자가 직접 수정 (중괄호 제거 또는 이스케이프)

**에러 로그**:
```
KeyError: 'key_characteristics를 인용한 한 문장'
File: prompt_builder.py:240
template.format(...) 호출 시 발생
```

---

## 📊 성능 및 비용 영향

### 지연 시간
- **기존**: ~8초 (1차 Claude + 2차 Claude)
- **신규**: ~10초 (GPT-4 Vision + 1차 Claude + 2차 Claude)
- **증가**: +2초 (25% 증가)

### 비용
- **GPT-4 Vision**: 약 $0.01/이미지 (고해상도 모드)
- **Claude Vision** (기존): 약 $0.024/이미지 (추정)
- **Claude Text** (신규): 약 $0.003/요청 (이미지 없음)
- **절감**: 약 -$0.011/요청 (약 46% 절감)

### 이미지 크기 제한
- **기존**: 5MB (Base64 인코딩 고려 시 실제 ~3.8MB)
- **신규**: 20MB (GPT-4 Vision 제한)
- **개선**: 5.3배 증가

---

## 🧪 테스트 결과

### 테스트 케이스 1: "보리" (6.3 MB 이미지)
**Before**:
```
❌ Claude API Error: image exceeds 5 MB maximum
→ Mock 데이터 폴백
```

**After**:
```
✅ GPT-4 Vision 분석 성공
✅ 1차 AI 분석 성공 (텍스트만)
✅ 2차 AI 변환 성공
```

### 로그 확인
```
[2025-11-02 19:58:47] [INFO] [GPT4] GPT-4 Vision 이미지 분석 시작 (크기: 6589582 bytes)
[2025-11-02 19:58:48] [INFO] [GPT4] GPT-4 Vision 응답 받음 (길이: 856 chars)
[2025-11-02 19:58:48] [INFO] [GPT4] GPT-4 Vision 분석 성공!
[2025-11-02 19:58:49] [INFO] 1차 AI 분석 시작 (강아지: 보리)
[2025-11-02 19:58:49] [DEBUG] 프롬프트 생성 완료 (이미지 전송: False)
[2025-11-02 19:58:52] [INFO] Claude API 호출 성공 (응답 길이: 1234 chars)
[2025-11-02 19:58:52] [INFO] 1차 AI 분석 성공!
```

---

## 🔍 로그 파일 위치

모든 AI 호출은 다음 파일에 기록됩니다:
```
runtime/{APP_ENV}/logs/analyzer.log
```

**로그 포맷**:
```
[2025-11-02 20:19:55] [LEVEL] [PREFIX] 메시지
```

**PREFIX 구분**:
- `[GPT4]`: GPT-4 Vision 관련 로그
- (없음): Claude API 관련 로그

---

## 📝 향후 개선 사항

### 1. 이미지 리사이징 추가
- 5MB 이하 이미지는 Claude Vision 직접 사용
- 5MB 초과만 GPT-4 Vision 사용
- 비용 및 지연시간 최적화

### 2. GPT-4 Vision 프롬프트 개선
- 더 구체적인 행동 분석 지시
- 스트레스 신호 감지 정확도 향상

### 3. Fallback 로직 강화
- GPT-4 Vision 실패 시 이미지 리사이징 시도
- 리사이징 후 Claude Vision 재시도

### 4. 캐싱 고려
- 동일 이미지 재분석 방지
- 비용 절감

---

## 🔐 보안 고려사항

### API 키 관리
- `.env` 파일은 `.gitignore`에 포함됨
- 환경 변수로 관리
- 코드에 하드코딩 금지

### 이미지 데이터
- 메모리에서만 처리
- 로컬 저장소에 저장 안 함
- API 전송 후 즉시 삭제

---

## 📞 문의 및 이슈

**문제 발생 시 확인 사항**:
1. `runtime/{APP_ENV}/logs/analyzer.log` 확인
2. `.env` 파일의 `OPENAI_API_KEY` 유효성 확인
3. OpenAI 계정 크레딧 잔액 확인

**관련 파일**:
- 설정: `config/settings.py`, `.env`
- 핵심 로직: `src/ai/gpt4_vision.py`, `src/ai/analyzer.py`
- 프롬프트: `src/ai/prompt_builder.py`, `src/ai/mari_persona.py`

---

**작성자**: Claude Code
**최종 업데이트**: 2025-11-02
