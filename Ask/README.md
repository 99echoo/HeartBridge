# Ask - AI 기반 반려견 훈련 문답 솔루션

HeartBridge 프로젝트의 첫 번째 서브 프로젝트입니다.

---

## 개요

**Ask**는 AI를 활용하여 반려견의 문제 행동을 분석하고, 전문적인 훈련 솔루션을 제공하는 서비스입니다.

### 핵심 기능
- 📸 **이미지 분석**: 반려견 사진을 통한 행동 패턴 파악
- 📋 **맞춤 설문**: 10개 항목의 상세 설문으로 정확한 문제 진단
- 🤖 **AI 분석**: Claude Sonnet 4.5를 활용한 전문가 수준 행동 분석
- 📊 **맞춤 리포트**: 행동 요약 + 전문가 의견 + 액션 플랜 제공
- 📤 **공유 기능**: 인스타그램 카드 생성 및 이메일 전송

### 타겟 사용자
- 문제 행동을 가진 반려견 보호자
- 높은 오프라인 훈련 비용/시간 부담으로 어려움을 겪는 일반 사용자

---

## 기술 스택

```
Frontend:    Streamlit 1.30+
AI:          Claude Sonnet 4.5 (anthropic API)
Database:    Supabase (PostgreSQL + Storage)
Analytics:   Google Sheets API
Email:       SendGrid
Language:    Python 3.11+
```

---

## 프로젝트 구조

```
Ask/
├── config/
│   ├── settings.py          # 환경 변수 관리 (Pydantic)
│   ├── prompts.py           # AI 프롬프트 템플릿
│   └── survey_questions.py  # 설문 10개 정의
├── src/
│   ├── ai/
│   │   ├── analyzer.py      # AI 분석 핵심 로직
│   │   └── vision_processor.py  # 이미지 처리 (향후 동영상)
│   ├── database/
│   │   ├── models.py        # Pydantic 데이터 모델
│   │   ├── supabase_client.py   # Supabase CRUD
│   │   └── sheets_client.py     # Google Sheets 연동
│   ├── services/
│   │   ├── report_generator.py  # 리포트 생성
│   │   └── share_service.py     # 인스타/이메일 공유
│   └── utils/
│       ├── validators.py    # 입력 검증
│       ├── file_handler.py  # 파일 처리
│       └── logger.py        # 로깅
├── data/
│   ├── knowledge_base/      # 전문가 지식 (텍스트 파일)
│   └── vector_db/           # (향후) RAG용 벡터 DB
├── tests/                   # 테스트 코드
├── app.py                   # Streamlit 메인 앱
├── requirements.txt         # 패키지 의존성
└── .env.example             # 환경 변수 템플릿
```

---

## 빠른 시작

### 1. 환경 설정

```bash
# Ask 디렉토리로 이동
cd Ask

# 가상환경 생성 및 활성화 (Windows)
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집하여 API 키 입력
# - ANTHROPIC_API_KEY: Claude API 키
# - SUPABASE_URL, SUPABASE_KEY: Supabase 프로젝트 정보
# - SENDGRID_API_KEY: 이메일 전송용 (선택)
```

### 3. 실행

```bash
# Streamlit 앱 실행
streamlit run app.py

# 브라우저에서 자동으로 http://localhost:8501 열림
```

---

## 사용자 플로우

```
Step 1: 랜딩 페이지
  ↓
Step 2: 기본 정보 입력 (강아지 이름, 이메일)
  ↓
Step 3: 설문 10개 작성
  ↓
Step 4: 이미지 업로드 (최대 5MB)
  ↓
Step 5: AI 분석 (로딩)
  ↓
Step 6: 초기 결과 표시
  ↓
Step 7: (선택) AI가 추가 정보 요청
  ↓
Step 8: 최종 리포트
  ├─> 인스타그램 카드 생성
  └─> 이메일 전송
```

---

## 개발 가이드

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 파일 테스트
pytest tests/test_analyzer.py

# 커버리지 리포트
pytest --cov=src --cov-report=html
```

### 코딩 컨벤션

- **변수/함수**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **Private**: `_snake_case`
- **Docstring**: 모든 함수에 필수 (Args, Returns, Raises 명시)
- **타입 힌트**: 모든 함수 파라미터 및 리턴 타입 명시

자세한 내용은 상위 디렉토리의 `../CLAUDE.md` 참고

---

## 데이터 모델

### SurveyResponse
```python
{
    "user_id": str,
    "q1_dog_age": int,           # 강아지 나이 (개월)
    "q2_breed": str,             # 견종
    "q3_problem_behavior": list, # 문제 행동
    # ... 10개 항목
}
```

### AnalysisResult
```python
{
    "analysis_id": str,
    "user_id": str,
    "image_url": str,
    "behavior_summary": str,     # AI 분석 요약
    "expert_opinion": str,       # 전문가 의견
    "action_plan": list[str],    # 액션 플랜
    "confidence_score": float,   # 신뢰도
    "created_at": datetime
}
```

---

## 향후 확장 계획

### 단기 (1-2개월)
- [ ] RAG 기반 전문가 지식 검색 (벡터 DB)
- [ ] Google Sheets 경영진 대시보드 구현
- [ ] 동영상 분석 기능 추가

### 중기 (3-6개월)
- [ ] 사용자 피드백 수집 시스템
- [ ] 훈련 진행도 추적 기능
- [ ] 커뮤니티 공유 기능

---

## API 비용 예상

**Claude Sonnet 4.5 기준**
- 입력: $3/MTok
- 출력: $15/MTok
- 1회 분석 (이미지 1장 + 설문): 약 $0.02
- **30,000원 예산으로 약 1,000회 분석 가능**

---

## 문제 해결

### 일반적인 문제

**Q: Streamlit 실행 시 모듈을 찾을 수 없다는 에러**
```bash
# 가상환경이 활성화되어 있는지 확인
# requirements.txt를 다시 설치
pip install -r requirements.txt
```

**Q: Anthropic API 키 에러**
```bash
# .env 파일에 ANTHROPIC_API_KEY가 올바르게 설정되었는지 확인
# API 키는 https://console.anthropic.com/settings/keys 에서 발급
```

**Q: Supabase 연결 실패**
```bash
# .env의 SUPABASE_URL과 SUPABASE_KEY 확인
# Supabase 프로젝트가 활성화되어 있는지 확인
```

---

## 기여 가이드

1. 새로운 기능 추가 시 **테스트 코드 필수**
2. 함수 작성 시 **타입 힌트 및 Docstring 필수**
3. 커밋 전 `pytest` 실행하여 기존 테스트 통과 확인
4. 설명은 **두괄식** (결론 → 이유)

---

## 라이선스

MIT License

---

## 문의

프로젝트 관련 문의: [이메일 주소]

**HeartBridge - Ask**: AI와 함께하는 스마트 반려견 훈련 🐕
