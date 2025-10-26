# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## PROJECT OVERVIEW

**HeartBridge (마음다리)** 는 AI 기반 반려견 케어 통합 플랫폼입니다.

### 프로젝트 구조
```
HeartBridge/
├── Ask/          # 훈련 문답 기능 (AI 행동 분석 및 솔루션 제공)
├── (미래)        # 추가 기능 확장 예정 (건강 관리, 커뮤니티 등)
└── CLAUDE.md     # 전체 프로젝트 가이드
```

### Ask (훈련 문답 서브 프로젝트)
- **목적**: 이미지, 설문 데이터를 분석해 문제 행동 파악 및 훈련 솔루션 제공
- **사용자**: 문제 행동을 가진 반려견 보호자 (오프라인 훈련 비용/시간 부담)
- **현재 상태**: 프로토타입 단계 - 확장 가능성을 고려하되 과도한 사전 준비 지양

---

## TECH STACK (Ask 기준)

```
Frontend:     Streamlit 1.30+
AI Model:     Claude Sonnet 4.5 (anthropic==0.18.1)
Database:     Supabase (PostgreSQL + Storage)
Analytics:    Google Sheets API (경영진 대시보드)
Email:        SendGrid (무료 100통/일)
Knowledge:    로컬 텍스트 파일 (향후 RAG/벡터DB 확장 가능)
Python:       3.11+
```

---

## ARCHITECTURE (Ask 기준)

### Data Flow
```
사용자 입력 (설문 + 이미지)
  ↓
Ask/app.py (Streamlit UI)
  ↓
Ask/src/ai/analyzer.py (AI 분석 + 프롬프트 조합)
  ↓
Claude API (이미지 Vision + 컨텍스트)
  ↓
Ask/src/database/supabase_client.py (결과 저장)
  ↓
Ask/src/services/report_generator.py (리포트 생성)
  ↓
Ask/src/services/share_service.py (인스타/이메일 공유)
```

### Key Design Patterns
1. **설정 관리**: Pydantic Settings (`Ask/config/settings.py`) - .env 자동 로드
2. **데이터 검증**: Pydantic Models (`Ask/src/database/models.py`)
3. **UI/로직 분리**: Streamlit UI는 `Ask/app.py`에만, 비즈니스 로직은 `Ask/src/`
4. **전문가 컨텍스트**: `Ask/data/knowledge_base/*.md` 파일을 프롬프트에 포함
5. **확장성**: 동영상/RAG 기능은 폴더만 준비 (`Ask/data/vector_db/`)

---

## DEVELOPMENT COMMANDS

### 환경 설정 (Ask 프로젝트)
```bash
# Ask 디렉토리로 이동
cd Ask

# 가상환경 생성 및 활성화 (Windows)
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 실제 API 키 입력 필요
```

### 실행
```bash
# Ask 디렉토리에서 Streamlit 앱 실행
cd Ask
streamlit run app.py

# 특정 포트로 실행
streamlit run app.py --server.port 8080
```

### 테스트
```bash
# Ask 디렉토리에서 실행
cd Ask

# 전체 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_analyzer.py

# 커버리지 포함
pytest --cov=src --cov-report=html

# 단일 테스트 함수 실행
pytest tests/test_analyzer.py::test_analyze_behavior_success -v
```

---

## CODING CONVENTIONS

### 네이밍
```python
# 변수/함수: snake_case
user_input = "..."
def analyze_dog_behavior(image, survey_data):
    pass

# 클래스: PascalCase
class BehaviorAnalyzer:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_IMAGE_SIZE_MB = 5

# Private: _snake_case
def _prepare_prompt(data):
    pass
```

### Docstring 규칙 (필수)
```python
def analyze_behavior(image: bytes, survey: dict) -> dict:
    """
    반려견 행동 분석을 수행합니다.

    Args:
        image: 업로드된 이미지 바이트
        survey: 설문 응답 딕셔너리 (10개 항목)

    Returns:
        dict: {
            'behavior_summary': str,
            'expert_opinion': str,
            'action_plan': list[str],
            'confidence_score': float
        }

    Raises:
        ValueError: 이미지가 유효하지 않을 때
    """
    pass
```

### 파일 헤더
```python
"""
파일명: analyzer.py
목적: AI 기반 반려견 행동 분석 핵심 로직
작성일: YYYY-MM-DD
"""
```

---

## CRITICAL RULES

### 절대 금지 사항
- ❌ API 키를 코드에 하드코딩
- ❌ Streamlit UI 코드와 비즈니스 로직 혼재
- ❌ 사용자 업로드 이미지를 로컬 저장 (Supabase Storage 사용)
- ❌ 타입 힌트 없는 함수 작성
- ❌ 에러 메시지를 사용자에게 직접 노출

### 필수 사항
- ✅ 모든 외부 API 호출은 try-except로 감싸기
- ✅ 환경 변수는 `.env` + `config/settings.py` 사용
- ✅ 데이터베이스 작업은 Pydantic 모델 사용
- ✅ 함수 구현 시 테스트 코드 동시 작성
- ✅ 설명은 두괄식 (결론 → 이유)

### 검증 원칙 (기존 유지)
- NEVER guess model/field/function names
- ALWAYS verify actual code before writing
- Use Task/Grep/Read/Glob tools extensively
- NEVER reduce user's requested scope without permission

---

## IMPORT PATTERNS (Ask 프로젝트 내부)

```python
# 설정 가져오기
from config.settings import settings

# 데이터 모델 사용
from src.database.models import SurveyResponse, AnalysisResult

# Supabase 클라이언트
from src.database.supabase_client import get_supabase_client

# AI 분석
from src.ai.analyzer import analyze_behavior
```

---

## KEY FILES

### 전체 프로젝트
- `CLAUDE.md`: 전체 프로젝트 가이드
- `Ask/`: 훈련 문답 서브 프로젝트

### Ask 프로젝트
- `Ask/config/settings.py`: 전역 설정 (Pydantic Settings)
- `Ask/config/prompts.py`: AI 프롬프트 템플릿
- `Ask/config/survey_questions.py`: 설문 10개 정의
- `Ask/src/database/models.py`: Pydantic 데이터 모델
- `Ask/src/ai/analyzer.py`: AI 분석 핵심 로직
- `Ask/app.py`: Streamlit 메인 앱
- `Ask/data/knowledge_base/*.md`: 전문가 지식 (프롬프트 컨텍스트)
- `Ask/README.md`: Ask 프로젝트 상세 문서

---

## EXPANSION PATHS

### Ask 프로젝트 내 확장 (미구현)
- **RAG**: `Ask/data/vector_db/` + langchain + chromadb
- **동영상 분석**: `Ask/src/ai/vision_processor.py` 확장 + opencv
- **Google Sheets 대시보드**: `Ask/src/database/sheets_client.py` 구현

### HeartBridge 전체 확장
- 건강 관리 기능 (예: Health/)
- 커뮤니티 기능 (예: Community/)
- 통합 대시보드

---

**원칙: 빠른 프로토타입, 확장 가능한 설계, 철저한 검증**