# Ask - AI 기반 반려견 훈련 문답 솔루션

HeartBridge 프로젝트의 첫 번째 서브 프로젝트입니다.

---

## 개요

**Ask**는 AI를 활용하여 반려견의 문제 행동을 분석하고, 전문적인 훈련 솔루션을 제공하는 서비스입니다.

### 핵심 기능
- 📸 **이미지 분석**: 반려견 사진을 통한 품종, 표정, 자세 분석
- 📋 **맞춤 설문**: 5개 섹션 20+ 항목의 상세 설문으로 정확한 문제 진단
- 🤖 **2단계 AI 분석**: Claude Sonnet 4.5 기반
  - **1차**: 전문가 수준의 객관적 행동 분석 (구조화된 JSON)
  - **2차**: 마리 페르소나로 따뜻한 대화체 변환
- 📊 **맞춤 리포트**: "마리의 솔루션" + "앞으로 이렇게 해보세요" 제공
- 📤 **공유 기능**: PDF 저장, 인스타그램 공유, 이메일 전송 (예정)

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
│   └── survey_questions.py  # 설문 20+ 항목 정의 (5개 섹션)
├── src/
│   ├── ai/
│   │   ├── analyzer.py      # 2단계 AI 분석 핵심 로직
│   │   ├── prompt_builder.py    # 1차/2차 프롬프트 생성
│   │   ├── mari_persona.py      # 마리 페르소나 정의
│   │   └── rag_search.py        # (향후) RAG 검색
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
│       ├── logger.py        # 로깅
│       └── mock_data.py     # Mock 데이터 (테스트용)
├── data/
│   ├── knowledge_base/      # 전문가 지식 (텍스트 파일) - 향후
│   └── vector_db/           # (향후) RAG용 벡터 DB
├── assets/
│   └── images/              # 마리 이미지 리소스
├── tests/                   # 테스트 코드
├── app.py                   # Streamlit 메인 앱
├── requirements.txt         # 패키지 의존성
├── .env.example             # 환경 변수 템플릿
├── README.md                # 프로젝트 개요
├── AI_ARCHITECTURE.md       # 2단계 AI 시스템 상세 설계
└── TODO.md                  # 작업 진행 상황
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

### 4. 런타임 산출물 위치
- 모든 CSV/로그 파일은 `runtime/{APP_ENV}/` 하위에 생성됩니다.
- `runtime/{APP_ENV}/data/` : 설문 CSV 등의 사용자 데이터
- `runtime/{APP_ENV}/logs/` : Vision/GPT 분석 로그, 성능 계측(`performance.log`)
- `.gitignore`에 포함되어 있어 로컬 개발 산출물이 레포에 섞이지 않습니다.

---

## 사용자 플로우

```
페이지 0: 랜딩 페이지 ("마리에게 물어보기")
  ↓
페이지 1: 기본 정보 (이름, 나이, 품종, 성별 등)
  ↓
페이지 2: 성향 파악 (평소 성향, 활동 시간)
  ↓
페이지 3: 문제 행동 관련 (고민거리, 발생 상황 등)
  ↓
페이지 4: 환경 정보 (주거 형태, 가족 구성, 외출 시간)
  ↓
페이지 5: 사진 업로드 (강아지 사진 필수, 행동 영상 선택)
  ↓
페이지 6: AI 분석 중 (로딩 애니메이션)
  ├─ 1차 AI: 전문가 분석 (5-8초)
  └─ 2차 AI: 마리 페르소나 변환 (3-5초)
  ↓
페이지 7: 최종 리포트
  ├─ "코코의 행동 분석 결과예요!"
  ├─ "이런 솔루션이 가장 잘 맞아요!" (3개)
  ├─ "앞으로 이렇게 해보세요!" (격려 메시지)
  └─ 공유 기능 (PDF 저장, 인스타그램, 이메일)
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

### SurveyResponse (st.session_state.responses)
```python
{
    # 기본 정보
    "dog_name": str,
    "dog_birth": str,           # "2022년 5월"
    "dog_breed": str,
    "dog_gender": str,          # "male" | "female"
    "dog_neutered": str,        # "yes" | "no"
    "other_pets": list[str],

    # 성향
    "personality_traits": list[str],
    "activity_time": str,

    # 문제 행동
    "main_concerns": list[str],
    "problem_start_time": str,
    "problem_situation": str,
    "tried_solutions": str,
    "hardest_part": str,

    # 환경
    "living_environment": str,
    "family_members": str,
    "outing_time": str
}
```

### AnalysisResult (st.session_state.analysis_result)
```python
{
    # 2차 AI 최종 출력 (사용자에게 표시)
    "final_text": str,           # Markdown 형식의 마리 답변 전체

    # 메타 정보
    "confidence_score": float,   # 0.0-1.0

    # 1차 AI 원본 (디버깅/로깅용)
    "raw_json": {
        "analysis_summary": {...},
        "solutions_best_fit": [...],  # 3개 고정
        "future_guidance": [...],     # 3개 고정
        "core_message": str
    }
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

**Claude Sonnet 4.5 기준 (2단계 AI)**
- 입력: $3/MTok
- 출력: $15/MTok

### 1회 분석 비용 상세
- **1차 AI (전문가 분석)**: ~2,000 토큰 (입력) + ~1,500 토큰 (출력) = $0.03
- **2차 AI (마리 변환)**: ~1,500 토큰 (입력) + ~800 토큰 (출력) = $0.02
- **총 비용**: 약 $0.05/회

**30,000원 예산으로 약 400-500회 분석 가능**

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
