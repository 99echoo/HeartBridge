# TODO: 데이터베이스

**담당 영역**: Supabase, 데이터 모델, 저장소, 캐싱

**마지막 업데이트**: 2025-01-26

---

## 📊 현재 상황

### ✅ 완료된 작업
- [x] 없음 (아직 미착수)

### 🔄 진행 중
- [ ] 없음

### ⏳ 대기 중
- AI 백엔드 완료 대기 중 (Phase 2 완료 후 시작)

---

## 🗄️ Phase 3-1: Supabase 프로젝트 설정

### Supabase 프로젝트 생성
- [ ] **Supabase 계정 생성**
  - https://supabase.com 가입
  - 프로젝트 생성: "heartbridge-ask"

- [ ] **프로젝트 설정**
  - [ ] Region 선택 (Seoul - ap-northeast-2)
  - [ ] Database password 설정
  - [ ] API keys 확인 (anon, service_role)

- [ ] **환경 변수 설정**
  ```env
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

---

## 🏗️ Phase 3-2: 데이터베이스 스키마 설계

### 테이블 설계

#### 1. users 테이블
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 이메일 인덱스
CREATE INDEX idx_users_email ON users(email);
```

#### 2. dogs 테이블
```sql
CREATE TABLE dogs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    age VARCHAR(20),  -- 'puppy', 'young', 'adult', 'senior', 'unknown'
    size VARCHAR(20),  -- 'tiny', 'small', 'medium', 'large', 'giant'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 사용자별 강아지 조회 인덱스
CREATE INDEX idx_dogs_user_id ON dogs(user_id);
```

#### 3. surveys 테이블
```sql
CREATE TABLE surveys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dog_id UUID REFERENCES dogs(id) ON DELETE CASCADE,
    responses JSONB NOT NULL,  -- 설문 응답 (q1-q7)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- JSONB 인덱스 (빠른 검색)
CREATE INDEX idx_surveys_responses ON surveys USING GIN (responses);
```

#### 4. analyses 테이블
```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id UUID REFERENCES surveys(id) ON DELETE CASCADE,
    image_url VARCHAR(500),  -- Supabase Storage URL
    behavior_summary TEXT,
    expert_opinion TEXT,
    action_plan JSONB,  -- 배열 형태
    confidence_score FLOAT,
    additional_notes TEXT,
    processing_time_ms INTEGER,
    api_cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 설문별 분석 조회 인덱스
CREATE INDEX idx_analyses_survey_id ON analyses(survey_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
```

#### 5. analytics 테이블 (경영진 대시보드용)
```sql
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    avg_confidence_score FLOAT,
    problem_type_counts JSONB,  -- {'barking': 10, 'separation_anxiety': 5, ...}
    api_cost_total_usd DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 날짜별 조회 인덱스
CREATE UNIQUE INDEX idx_analytics_date ON analytics(date);
```

### RLS (Row Level Security) 설정
- [ ] **users 테이블 RLS**
  ```sql
  ALTER TABLE users ENABLE ROW LEVEL SECURITY;

  -- 사용자는 자신의 데이터만 조회 가능
  CREATE POLICY "Users can view own data"
      ON users FOR SELECT
      USING (auth.uid() = id);
  ```

- [ ] **dogs, surveys, analyses 테이블 RLS**
  - 각 테이블에 대해 소유자만 접근 가능하도록 설정

---

## 📦 Phase 3-3: Pydantic 데이터 모델

### 모델 정의
- [ ] **`src/database/models.py` 생성**
  ```python
  from pydantic import BaseModel, EmailStr, Field
  from typing import Optional, List
  from datetime import datetime
  import uuid

  class BasicInfo(BaseModel):
      dog_name: str = Field(..., min_length=2, max_length=100)
      owner_email: Optional[EmailStr] = None
      dog_age: str  # 'puppy', 'young', 'adult', 'senior', 'unknown'
      dog_size: str  # 'tiny', 'small', 'medium', 'large', 'giant'

  class SurveyResponse(BaseModel):
      responses: dict  # {q1: 'barking', q2: 'often', ...}

      class Config:
          json_schema_extra = {
              "example": {
                  "responses": {
                      "q1": "barking",
                      "q2": "often",
                      "q3": "when_alone",
                      "q4": "few_months",
                      "q5": "scold",
                      "q6": "half_day",
                      "q7": "sometimes"
                  }
              }
          }

  class AnalysisResult(BaseModel):
      behavior_summary: str
      expert_opinion: str
      action_plan: List[str]
      confidence_score: float = Field(..., ge=0.0, le=1.0)
      additional_notes: Optional[str] = None

  class AnalysisRecord(BaseModel):
      id: uuid.UUID
      survey_id: uuid.UUID
      image_url: Optional[str] = None
      behavior_summary: str
      expert_opinion: str
      action_plan: List[str]
      confidence_score: float
      additional_notes: Optional[str] = None
      processing_time_ms: int
      api_cost_usd: float
      created_at: datetime
  ```

### 모델 검증
- [ ] **입력 검증 함수**
  ```python
  def validate_basic_info(data: dict) -> BasicInfo:
      """기본 정보 검증"""
      return BasicInfo(**data)

  def validate_survey_response(data: dict) -> SurveyResponse:
      """설문 응답 검증"""
      return SurveyResponse(**data)
  ```

---

## 🔌 Phase 3-4: Supabase 클라이언트 구현

### 클라이언트 초기화
- [ ] **`src/database/supabase_client.py` 생성**
  ```python
  from supabase import create_client, Client
  from config.settings import settings

  _supabase_client: Client = None

  def get_supabase_client() -> Client:
      """Supabase 클라이언트 싱글톤"""
      global _supabase_client
      if _supabase_client is None:
          _supabase_client = create_client(
              settings.SUPABASE_URL,
              settings.SUPABASE_KEY
          )
      return _supabase_client
  ```

### CRUD 작업
- [ ] **사용자 관리**
  ```python
  def create_or_get_user(email: str) -> dict:
      """이메일로 사용자 생성 또는 조회"""
      pass

  def get_user_by_id(user_id: str) -> dict:
      """사용자 ID로 조회"""
      pass
  ```

- [ ] **강아지 정보 관리**
  ```python
  def create_dog(user_id: str, basic_info: BasicInfo) -> dict:
      """강아지 정보 생성"""
      pass

  def get_dog_by_id(dog_id: str) -> dict:
      """강아지 정보 조회"""
      pass
  ```

- [ ] **설문 관리**
  ```python
  def create_survey(dog_id: str, survey_response: SurveyResponse) -> dict:
      """설문 응답 저장"""
      pass
  ```

- [ ] **분석 결과 관리**
  ```python
  def create_analysis(
      survey_id: str,
      image_url: str,
      analysis_result: AnalysisResult,
      processing_time_ms: int,
      api_cost_usd: float
  ) -> dict:
      """분석 결과 저장"""
      pass

  def get_analysis_by_id(analysis_id: str) -> dict:
      """분석 결과 조회"""
      pass

  def get_user_analyses(user_id: str, limit: int = 10) -> list:
      """사용자의 분석 결과 목록"""
      pass
  ```

---

## 📁 Phase 3-5: Supabase Storage (이미지 저장)

### Storage Bucket 생성
- [ ] **Supabase Dashboard에서 Bucket 생성**
  - Bucket 이름: `dog-images`
  - Public 여부: Private (signed URL 사용)
  - File size limit: 5MB

### 이미지 업로드 함수
- [ ] **`src/database/storage.py` 생성**
  ```python
  def upload_dog_image(
      image_bytes: bytes,
      filename: str,
      content_type: str = "image/jpeg"
  ) -> str:
      """
      이미지를 Supabase Storage에 업로드

      Returns:
          str: 업로드된 이미지의 public URL
      """
      supabase = get_supabase_client()

      # 파일명 생성 (UUID + 확장자)
      file_extension = filename.split('.')[-1]
      unique_filename = f"{uuid.uuid4()}.{file_extension}"

      # 업로드
      response = supabase.storage.from_("dog-images").upload(
          unique_filename,
          image_bytes,
          {"content-type": content_type}
      )

      # Public URL 생성
      public_url = supabase.storage.from_("dog-images").get_public_url(unique_filename)

      return public_url
  ```

### 이미지 조회 함수
- [ ] **Signed URL 생성**
  ```python
  def get_signed_image_url(filepath: str, expires_in: int = 3600) -> str:
      """
      임시 접근 가능한 Signed URL 생성

      Args:
          filepath: Storage 내 파일 경로
          expires_in: URL 유효 시간 (초)

      Returns:
          str: Signed URL
      """
      supabase = get_supabase_client()
      return supabase.storage.from_("dog-images").create_signed_url(
          filepath,
          expires_in
      )
  ```

---

## 🔄 Phase 3-6: app.py 통합

### 데이터 저장 플로우
- [ ] **page_result() 수정**
  ```python
  # 분석 완료 후 데이터베이스에 저장
  from src.database.supabase_client import (
      create_or_get_user,
      create_dog,
      create_survey,
      create_analysis
  )
  from src.database.storage import upload_dog_image

  # 1. 사용자 생성/조회
  user = create_or_get_user(st.session_state.basic_info['owner_email'])

  # 2. 강아지 정보 저장
  dog = create_dog(user['id'], st.session_state.basic_info)

  # 3. 이미지 업로드
  image_url = upload_dog_image(
      st.session_state.uploaded_image.read(),
      st.session_state.uploaded_image.name
  )

  # 4. 설문 저장
  survey = create_survey(dog['id'], st.session_state.survey_responses)

  # 5. 분석 결과 저장
  analysis = create_analysis(
      survey['id'],
      image_url,
      st.session_state.analysis_result,
      processing_time_ms,
      api_cost_usd
  )
  ```

### 과거 분석 결과 조회 (선택)
- [ ] **사이드바에 과거 분석 목록**
  - 이메일 입력 시 과거 분석 결과 표시
  - 클릭하면 해당 분석 결과 페이지로 이동

---

## 📊 Phase 3-7: Analytics 데이터 수집

### 일일 통계 수집
- [ ] **`src/database/analytics.py` 생성**
  ```python
  def collect_daily_analytics(date: str) -> dict:
      """
      특정 날짜의 통계 수집

      Returns:
          {
              'total_analyses': int,
              'total_users': int,
              'avg_confidence_score': float,
              'problem_type_counts': dict,
              'api_cost_total_usd': float
          }
      """
      supabase = get_supabase_client()

      # SQL 쿼리로 통계 집계
      # ...

      return stats
  ```

- [ ] **일일 배치 작업 (선택)**
  - Supabase Edge Functions 사용
  - 매일 자정에 analytics 테이블 업데이트

---

## 🧪 Phase 3-8: 테스트

### 단위 테스트
- [ ] **`tests/test_supabase_client.py`**
  ```python
  def test_create_user():
      # 사용자 생성 테스트
      pass

  def test_create_dog():
      # 강아지 정보 저장 테스트
      pass
  ```

- [ ] **`tests/test_storage.py`**
  - 이미지 업로드 테스트
  - Signed URL 생성 테스트

### 통합 테스트
- [ ] **전체 플로우 테스트**
  - 사용자 생성 → 강아지 등록 → 설문 → 이미지 업로드 → 분석 → 저장

---

## 🔧 Phase 3-9: 데이터 마이그레이션

### 초기 데이터 설정
- [ ] **`scripts/init_db.sql`**
  - 모든 테이블 생성 스크립트
  - 인덱스 생성
  - RLS 정책 설정

### 마이그레이션 도구
- [ ] **Supabase Migration 사용**
  ```bash
  supabase migration new create_tables
  supabase db reset
  ```

---

## 🚀 우선순위

### 🔥 긴급 (AI 완료 후 즉시)
1. Supabase 프로젝트 생성
2. 테이블 스키마 설계 및 생성
3. Pydantic 모델 정의

### ⚡ 중요 (1주차)
1. Supabase 클라이언트 구현
2. CRUD 작업 구현
3. Storage 통합

### 📌 보통 (2주차)
1. Analytics 데이터 수집
2. 테스트 작성
3. 최적화

---

## 📝 메모

### Supabase 무료 티어 제한
- Storage: 1GB
- Database: 500MB
- Bandwidth: 5GB/월
- **예상**: 이미지당 평균 500KB → 약 2,000개 이미지 저장 가능

### 데이터 보관 정책
- 분석 결과: 영구 보관
- 이미지: 90일 후 자동 삭제 (선택)
- 사용자 데이터: GDPR 준수

---

## ✅ 완료 기준

데이터베이스 작업은 다음 조건을 만족하면 완료:

- [ ] Supabase 프로젝트 생성 및 설정 완료
- [ ] 모든 테이블 생성 및 RLS 설정
- [ ] Pydantic 모델 정의 및 검증
- [ ] Supabase 클라이언트 구현
- [ ] Storage 통합 (이미지 업로드/조회)
- [ ] app.py 통합 완료
- [ ] 테스트 통과
- [ ] Analytics 데이터 수집 가능

→ 완료 시 [TODO_INTEGRATION.md](TODO_INTEGRATION.md)로 이동

---

**다음 작업**: AI 백엔드 완료 대기 중
