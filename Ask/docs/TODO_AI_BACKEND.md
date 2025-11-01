# TODO: AI/백엔드

**담당 영역**: Claude API, 이미지 분석, 프롬프트 엔지니어링, 비즈니스 로직

**마지막 업데이트**: 2025-01-26

---

## 📊 현재 상황

### ✅ 완료된 작업
- [x] Mock 데이터 작성 (4가지 케이스)
- [x] 설문 구조 정의 (7개 질문)
- [x] 기본 정보 필드 정의

### 🔄 진행 중
- [ ] 없음 (UI 작업 우선)

### ⏳ 대기 중
- UI 확정 대기 중 (Phase 1 완료 후 시작)

---

## 🤖 Phase 2-1: AI 프롬프트 엔지니어링

### 프롬프트 템플릿 작성
- [ ] **`config/prompts.py` 파일 생성**
  ```python
  SYSTEM_PROMPT = """
  당신은 15년 경력의 반려견 행동 전문가입니다...
  """

  ANALYSIS_PROMPT_TEMPLATE = """
  다음 정보를 바탕으로 반려견 행동을 분석해주세요:
  - 강아지 정보: {dog_info}
  - 설문 응답: {survey_responses}
  - 이미지 분석: {image_analysis}
  """
  ```

- [ ] **프롬프트 구성 요소**
  - [ ] System Prompt (역할 정의)
  - [ ] Analysis Prompt (분석 요청)
  - [ ] Image Description Prompt (이미지 설명)
  - [ ] Action Plan Prompt (솔루션 생성)

- [ ] **프롬프트 최적화**
  - [ ] Few-shot examples 추가
  - [ ] Chain-of-Thought 프롬프팅
  - [ ] 출력 형식 명확화 (JSON)

### 전문가 지식 베이스
- [ ] **`data/knowledge_base/` 파일 작성**
  - [ ] `barking.md` - 짖음 행동 전문 지식
  - [ ] `separation_anxiety.md` - 분리불안 전문 지식
  - [ ] `aggression.md` - 공격성 전문 지식
  - [ ] `destruction.md` - 파괴 행동 전문 지식
  - [ ] `toilet_training.md` - 배변 훈련 전문 지식

- [ ] **지식 베이스 구조**
  ```markdown
  # 과도한 짖음 행동

  ## 원인
  - ...

  ## 증상 패턴
  - ...

  ## 권장 솔루션
  - ...
  ```

- [ ] **프롬프트에 지식 통합**
  - 설문 응답 → 관련 지식 파일 선택 → 프롬프트에 포함

---

## 🔍 Phase 2-2: 이미지 분석

### Vision API 연동
- [ ] **`src/ai/vision_processor.py` 생성**
  ```python
  def analyze_image(image_bytes: bytes) -> dict:
      """이미지를 분석하여 강아지 상태를 파악합니다."""
      pass
  ```

- [ ] **이미지 분석 항목**
  - [ ] 강아지 표정 (불안, 공격적, 편안함 등)
  - [ ] 주변 환경 (실내/실외, 정돈 상태)
  - [ ] 자세 (긴장, 이완)
  - [ ] 가시적 행동 징후

- [ ] **Claude Vision API 호출**
  ```python
  import anthropic

  client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

  message = client.messages.create(
      model="claude-sonnet-4-20250514",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "image",
                      "source": {
                          "type": "base64",
                          "media_type": "image/jpeg",
                          "data": base64_image,
                      },
                  },
                  {
                      "type": "text",
                      "text": "이 강아지의 상태를 분석해주세요."
                  }
              ],
          }
      ],
  )
  ```

- [ ] **이미지 전처리**
  - [ ] 파일 크기 검증 (max 5MB)
  - [ ] 이미지 리사이징 (max 1568px)
  - [ ] Base64 인코딩
  - [ ] 형식 검증 (JPEG, PNG)

### 이미지 품질 검증
- [ ] **이미지 품질 체크**
  - [ ] 흐릿함 감지
  - [ ] 강아지 존재 확인
  - [ ] 너무 어둡거나 밝은 이미지 경고

---

## 🧠 Phase 2-3: AI 분석 로직

### 핵심 분석 함수
- [ ] **`src/ai/analyzer.py` 생성**
  ```python
  def analyze_behavior(
      basic_info: dict,
      survey_responses: dict,
      image_bytes: bytes
  ) -> dict:
      """
      반려견 행동을 종합 분석합니다.

      Returns:
          {
              'behavior_summary': str,
              'expert_opinion': str,
              'action_plan': list[str],
              'confidence_score': float,
              'additional_notes': str
          }
      """
      pass
  ```

- [ ] **분석 단계**
  1. 이미지 분석 (vision_processor)
  2. 설문 응답 분석
  3. 관련 지식 베이스 로드
  4. 프롬프트 조합
  5. Claude API 호출
  6. 응답 파싱 및 검증
  7. 결과 반환

### 프롬프트 조합 로직
- [ ] **`src/ai/prompt_builder.py` 생성**
  ```python
  def build_analysis_prompt(
      basic_info: dict,
      survey_responses: dict,
      image_description: str,
      knowledge_base: str
  ) -> str:
      """모든 정보를 조합하여 최종 프롬프트 생성"""
      pass
  ```

- [ ] **컨텍스트 구성**
  - 강아지 기본 정보 (이름, 나이, 크기)
  - 설문 응답 (7개 질문)
  - 이미지 분석 결과
  - 관련 전문가 지식

### 응답 파싱
- [ ] **JSON 출력 강제**
  - 프롬프트에서 JSON 형식 요청
  - Claude 응답 → JSON 파싱
  - 검증 (필수 필드 확인)

- [ ] **에러 핸들링**
  - [ ] API 호출 실패 (retry 로직)
  - [ ] 잘못된 응답 형식 (재요청)
  - [ ] Rate limit 처리
  - [ ] Timeout 처리

---

## 📊 Phase 2-4: 신뢰도 점수 계산

### 신뢰도 로직
- [ ] **`src/ai/confidence_scorer.py` 생성**
  ```python
  def calculate_confidence(
      survey_responses: dict,
      image_quality: float,
      response_consistency: float
  ) -> float:
      """분석 신뢰도 점수 계산 (0-1)"""
      pass
  ```

- [ ] **신뢰도 요소**
  - [ ] 설문 응답 완전성 (모든 질문 응답했는가)
  - [ ] 이미지 품질 (흐릿하지 않은가)
  - [ ] AI 응답 일관성
  - [ ] 지식 베이스 매칭 정도

- [ ] **신뢰도별 처리**
  - 90% 이상: "매우 정확한 분석입니다"
  - 70-90%: "신뢰할 만한 분석입니다"
  - 50-70%: "참고용으로 활용하세요"
  - 50% 미만: "전문가 상담을 권장합니다"

---

## 🔧 Phase 2-5: API 비용 관리

### 토큰 사용 최적화
- [ ] **프롬프트 길이 최소화**
  - 불필요한 설명 제거
  - 핵심 정보만 포함

- [ ] **이미지 리사이징**
  - 최대 1568px (Claude 권장)
  - 품질 유지하며 파일 크기 감소

- [ ] **캐싱 활용**
  - 동일 설문 → 캐싱 (같은 질문은 재사용)
  - 지식 베이스 캐싱

### 비용 모니터링
- [ ] **사용량 추적**
  - 각 분석당 토큰 수 기록
  - 월별 API 비용 계산

- [ ] **예산 알림**
  - 일일 한도 설정
  - 초과 시 알림 (Streamlit UI)

---

## 🧪 Phase 2-6: 테스트

### 단위 테스트
- [ ] **`tests/test_analyzer.py`**
  ```python
  def test_analyze_behavior_success():
      # Mock API 응답으로 테스트
      pass

  def test_analyze_behavior_api_failure():
      # API 실패 시나리오
      pass
  ```

- [ ] **`tests/test_vision_processor.py`**
  - 이미지 분석 테스트
  - 다양한 이미지 형식 테스트

- [ ] **`tests/test_prompt_builder.py`**
  - 프롬프트 조합 테스트
  - 지식 베이스 통합 테스트

### 통합 테스트
- [ ] **실제 API 호출 테스트**
  - [ ] 정상 케이스 5개
  - [ ] 엣지 케이스 (흐릿한 이미지, 이상한 응답 등)

- [ ] **성능 테스트**
  - 분석 속도 측정 (목표: 10초 이내)
  - API 응답 시간 모니터링

---

## 🔄 Phase 2-7: Mock → Real AI 전환

### app.py 수정
- [ ] **page_analyzing() 함수 수정**
  ```python
  # Before (Mock)
  st.session_state.analysis_result = get_mock_result_by_problem(problem_type)

  # After (Real AI)
  from src.ai.analyzer import analyze_behavior

  result = analyze_behavior(
      basic_info=st.session_state.basic_info,
      survey_responses=st.session_state.survey_responses,
      image_bytes=st.session_state.uploaded_image.read()
  )
  st.session_state.analysis_result = result
  ```

- [ ] **로딩 상태 개선**
  - 실제 API 호출 중임을 표시
  - 예상 소요 시간 안내
  - 취소 버튼 고려

### 환경 변수 설정
- [ ] **`.env` 파일 업데이트**
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  USE_MOCK_DATA=false  # Mock 사용 여부
  ```

- [ ] **`config/settings.py` 수정**
  - USE_MOCK_DATA 설정 추가
  - 개발 환경에서는 Mock 사용 가능하도록

---

## 🚀 우선순위

### 🔥 긴급 (UI 완료 후 즉시)
1. 프롬프트 템플릿 작성
2. analyzer.py 핵심 로직 구현
3. Claude API 연동

### ⚡ 중요 (1주차)
1. 이미지 분석 구현
2. 전문가 지식 베이스 작성
3. 에러 핸들링
### 📌 보통 (2주차)
1. 신뢰도 점수 계산
2. 비용 최적화
3. 테스트 작성

---

## 📝 메모

### API 예상 비용
- 입력: 이미지 (1568px) + 텍스트 (설문 + 지식)
- 출력: 약 500-1000 토큰
- **예상 비용**: 분석당 약 $0.02 (약 30원)
- **월 예산 30,000원**: 약 1,000회 분석 가능

### 기술적 고민
- [ ] 이미지 없이 설문만으로도 분석 가능한가?
- [ ] 동영상 분석은 어떻게 할 것인가? (Phase 4)
- [ ] RAG 도입 시점은 언제? (Phase 4)

---

## ✅ 완료 기준

AI/백엔드 작업은 다음 조건을 만족하면 완료:

- [ ] Claude API 연동 성공
- [ ] 이미지 + 설문 → 분석 결과 생성
- [ ] 4가지 문제 유형 모두 테스트 통과
- [ ] 에러 핸들링 완비
- [ ] 신뢰도 점수 계산 구현
- [ ] 단위 테스트 80% 이상 커버리지
- [ ] 비용 모니터링 시스템 구축

→ 완료 시 [TODO_DATABASE.md](TODO_DATABASE.md)로 이동

---

**다음 작업**: UI 확정 대기 중
