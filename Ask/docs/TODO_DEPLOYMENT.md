# TODO: 배포 및 운영

**담당 영역**: Streamlit Cloud, 환경 변수, 모니터링, 성능 최적화, 보안

**마지막 업데이트**: 2025-01-26

---

## 📊 현재 상황

### ✅ 완료된 작업
- [x] 로컬 개발 환경 구축

### 🔄 진행 중
- [ ] 없음

### ⏳ 대기 중
- 모든 Phase 완료 대기 중 (Phase 1-4 완료 후 시작)

---

## 🚀 Phase 5-1: Streamlit Community Cloud 배포

### 사전 준비
- [ ] **GitHub 저장소 설정**
  - [ ] HeartBridge 프로젝트를 GitHub에 푸시
  - [ ] Repository: Public 또는 Private (Streamlit Cloud는 둘 다 지원)
  - [ ] `.gitignore` 확인 (`.env`, `venv/`, `*.pyc` 제외)

- [ ] **requirements.txt 최종 확인**
  ```
  streamlit>=1.30.0
  anthropic==0.18.1
  pydantic>=2.6.0
  pydantic-settings>=2.1.0
  supabase>=2.0.0
  python-dotenv>=1.0.0
  Pillow>=10.2.0
  sendgrid>=6.11.0
  google-auth>=2.27.0
  google-auth-oauthlib>=1.2.0
  google-auth-httplib2>=0.2.0
  google-api-python-client>=2.116.0
  weasyprint>=60.0
  jinja2>=3.1.3
  ```

- [ ] **Python 버전 명시**
  - `runtime.txt` 파일 생성
  ```
  python-3.11
  ```

### Streamlit Cloud 설정
- [ ] **Streamlit Cloud 계정 생성**
  - https://streamlit.io/cloud
  - GitHub 계정으로 로그인

- [ ] **앱 배포**
  1. "New app" 클릭
  2. Repository 선택: `yourusername/HeartBridge`
  3. Branch: `main`
  4. Main file path: `Ask/app.py`
  5. App URL: `heartbridge-ask.streamlit.app` (또는 사용 가능한 이름)

### Secrets 관리
- [ ] **`.streamlit/secrets.toml` 설정**
  - Streamlit Cloud 대시보드 → Settings → Secrets
  - 다음 내용 추가:
  ```toml
  # Anthropic API
  ANTHROPIC_API_KEY = "sk-ant-xxxxx"

  # Supabase
  SUPABASE_URL = "https://xxx.supabase.co"
  SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  # SendGrid
  SENDGRID_API_KEY = "SG.xxxxx"
  SENDGRID_FROM_EMAIL = "noreply@heartbridge.com"
  SENDGRID_FROM_NAME = "HeartBridge Ask"

  # Google Sheets (JSON 형식)
  [google_sheets]
  type = "service_account"
  project_id = "heartbridge-ask"
  private_key_id = "xxxxx"
  private_key = "-----BEGIN PRIVATE KEY-----\nxxxxx\n-----END PRIVATE KEY-----\n"
  client_email = "heartbridge-ask@xxx.iam.gserviceaccount.com"
  client_id = "xxxxx"
  auth_uri = "https://accounts.google.com/o/oauth2/auth"
  token_uri = "https://oauth2.googleapis.com/token"
  auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
  client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/xxx"
  ```

### 환경별 설정 분리
- [ ] **`config/settings.py` 수정**
  ```python
  import streamlit as st

  class Settings(BaseSettings):
      # Streamlit Cloud에서는 st.secrets 사용
      @property
      def ANTHROPIC_API_KEY(self) -> str:
          if 'ANTHROPIC_API_KEY' in st.secrets:
              return st.secrets['ANTHROPIC_API_KEY']
          return os.getenv('ANTHROPIC_API_KEY', '')

      # 나머지 변수도 동일하게...

      class Config:
          env_file = ".env"
          case_sensitive = True
  ```

---

## 🔧 Phase 5-2: 성능 최적화

### 캐싱 전략
- [ ] **Streamlit 캐싱 적용**
  ```python
  # app.py 또는 각 모듈에서

  @st.cache_data
  def get_survey_questions():
      """설문 질문 캐싱 (변경 안 됨)"""
      return BEHAVIOR_SURVEY_QUESTIONS

  @st.cache_data(ttl=3600)
  def get_mock_data():
      """Mock 데이터 1시간 캐싱"""
      return MOCK_ANALYSIS_RESULTS

  @st.cache_resource
  def get_supabase_client():
      """Supabase 클라이언트 재사용"""
      return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

  @st.cache_data
  def load_mari_image(image_name: str):
      """마리 이미지 캐싱"""
      return Image.open(f"assets/images/{image_name}")
  ```

### 이미지 최적화
- [ ] **마리 이미지 압축**
  - PNG → WebP (더 작은 파일 크기)
  - 또는 TinyPNG 사용

- [ ] **업로드 이미지 리사이징**
  ```python
  from PIL import Image

  def resize_uploaded_image(image_bytes: bytes, max_size: int = 1568) -> bytes:
      """업로드된 이미지 리사이징"""
      img = Image.open(io.BytesIO(image_bytes))

      # 비율 유지하며 리사이징
      img.thumbnail((max_size, max_size), Image.LANCZOS)

      # 바이트로 변환
      output = io.BytesIO()
      img.save(output, format='JPEG', quality=85, optimize=True)
      return output.getvalue()
  ```

### 코드 최적화
- [ ] **불필요한 임포트 제거**
  - `ruff` 또는 `pylint` 사용

- [ ] **함수 최적화**
  - 반복 계산 제거
  - 리스트 컴프리헨션 사용

---

## 📊 Phase 5-3: 모니터링 및 로깅

### 로깅 시스템
- [ ] **`src/utils/logger.py` 생성**
  ```python
  import logging
  from datetime import datetime

  def setup_logger(name: str) -> logging.Logger:
      """로거 설정"""
      logger = logging.getLogger(name)
      logger.setLevel(logging.INFO)

      # 파일 핸들러
      fh = logging.FileHandler(f'logs/app_{datetime.now():%Y%m%d}.log')
      fh.setLevel(logging.INFO)

      # 포맷터
      formatter = logging.Formatter(
          '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )
      fh.setFormatter(formatter)

      logger.addHandler(fh)
      return logger

  # 사용
  logger = setup_logger(__name__)
  logger.info("App started")
  ```

### 주요 이벤트 로깅
- [ ] **추적할 이벤트**
  - [ ] 앱 시작/종료
  - [ ] 페이지 전환
  - [ ] 분석 요청 (시작/완료/실패)
  - [ ] API 호출 (소요 시간, 비용)
  - [ ] 에러 발생 (스택 트레이스 포함)

- [ ] **app.py에 로깅 추가**
  ```python
  from src.utils.logger import setup_logger

  logger = setup_logger(__name__)

  def page_analyzing():
      logger.info(f"Analysis started for dog: {st.session_state.basic_info['dog_name']}")

      try:
          result = analyze_behavior(...)
          logger.info(f"Analysis completed. Confidence: {result['confidence_score']}")
      except Exception as e:
          logger.error(f"Analysis failed: {e}", exc_info=True)
          st.error("분석 중 오류가 발생했습니다.")
  ```

### 사용량 추적
- [ ] **Google Analytics 연동 (선택)**
  ```python
  # Streamlit에서 GA 추적 코드 삽입
  st.components.v1.html("""
      <!-- Google tag (gtag.js) -->
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
      </script>
  """, height=0)
  ```

### 에러 모니터링
- [ ] **Sentry 연동 (선택)**
  ```python
  import sentry_sdk

  sentry_sdk.init(
      dsn="https://xxxxx@sentry.io/xxxxx",
      traces_sample_rate=1.0,
      profiles_sample_rate=1.0,
  )
  ```

---

## 💰 Phase 5-4: 비용 관리

### API 비용 추적
- [ ] **비용 계산 함수**
  ```python
  def calculate_api_cost(input_tokens: int, output_tokens: int) -> float:
      """
      Claude API 비용 계산

      Sonnet 4.5 기준:
      - Input: $3 / 1M tokens
      - Output: $15 / 1M tokens
      """
      input_cost = (input_tokens / 1_000_000) * 3
      output_cost = (output_tokens / 1_000_000) * 15
      return input_cost + output_cost
  ```

- [ ] **월별 비용 대시보드**
  - Supabase 또는 Google Sheets에서 집계
  - 목표: 월 30,000원 이내 유지

### 사용량 제한
- [ ] **일일 한도 설정**
  ```python
  from datetime import date

  def check_daily_limit() -> bool:
      """하루 분석 횟수 제한 (무료 티어)"""
      today = date.today()
      count = get_today_analysis_count(today)

      MAX_DAILY_ANALYSES = 100  # 무료 티어 한도

      if count >= MAX_DAILY_ANALYSES:
          st.warning("오늘의 무료 분석 횟수를 초과했습니다. 내일 다시 시도해주세요.")
          return False

      return True
  ```

### 비용 알림
- [ ] **예산 초과 시 이메일 알림**
  - 일일 $5 초과 시
  - 월별 $100 초과 시

---

## 🔒 Phase 5-5: 보안

### API 키 보호
- [ ] **.env 파일 절대 커밋 안 함**
  - `.gitignore`에 `.env` 추가 확인

- [ ] **환경 변수 검증**
  ```python
  # config/settings.py
  def validate_settings():
      """필수 환경 변수 확인"""
      required = [
          'ANTHROPIC_API_KEY',
          'SUPABASE_URL',
          'SUPABASE_KEY'
      ]

      for var in required:
          if not getattr(settings, var):
              raise ValueError(f"{var} is not set!")
  ```

### 입력 검증
- [ ] **SQL Injection 방지**
  - Supabase 클라이언트 사용 (자동 방지)

- [ ] **XSS 방지**
  - 사용자 입력 이스케이프
  ```python
  import html

  def sanitize_input(text: str) -> str:
      """사용자 입력 정제"""
      return html.escape(text.strip())
  ```

### HTTPS 강제
- [ ] **Streamlit Cloud는 기본 HTTPS**
  - 추가 설정 불필요

### Rate Limiting
- [ ] **동일 IP 제한 (Streamlit Cloud 제약)**
  - Streamlit Cloud에서 직접 구현 어려움
  - Cloudflare 또는 nginx 리버스 프록시 필요 (고급)

---

## 🧪 Phase 5-6: 배포 전 체크리스트

### 기능 테스트
- [ ] **전체 플로우 테스트 (프로덕션 환경)**
  - [ ] 랜딩 → 기본정보 → 설문 → 이미지 → 분석 → 결과
  - [ ] 이메일 전송
  - [ ] PDF 다운로드
  - [ ] 인스타그램 카드 생성

### 성능 테스트
- [ ] **로딩 속도**
  - 초기 페이지 로드: < 3초
  - 페이지 전환: < 1초
  - AI 분석: < 15초

- [ ] **동시 사용자 테스트**
  - Streamlit Cloud 무료: 1 앱당 1 인스턴스
  - 동시 접속 시 대기 큐 발생 가능

### 브라우저/디바이스 테스트
- [ ] **브라우저**
  - [ ] Chrome (최신)
  - [ ] Safari (최신)
  - [ ] Edge (최신)
  - [ ] Firefox (최신)

- [ ] **디바이스**
  - [ ] iPhone
  - [ ] Android
  - [ ] Tablet
  - [ ] Desktop

### 보안 테스트
- [ ] **환경 변수 노출 확인**
  - 브라우저 개발자 도구에서 API 키 노출 확인

- [ ] **HTTPS 확인**
  - 모든 페이지가 HTTPS로 서빙되는지

---

## 📚 Phase 5-7: 문서화

### 사용자 문서
- [ ] **사용 가이드 작성**
  - 랜딩 페이지에 "사용 방법" 섹션
  - FAQ 추가

- [ ] **개인정보 처리방침**
  - 수집 정보: 이메일, 강아지 이름, 설문 응답, 이미지
  - 보관 기간: 90일 (또는 영구)
  - 삭제 요청 방법

- [ ] **서비스 약관**
  - AI 분석은 참고용
  - 전문가 상담 권장

### 개발자 문서
- [ ] **README.md 업데이트**
  - 배포 환경 정보
  - 환경 변수 설명
  - 로컬 개발 가이드

- [ ] **CHANGELOG.md 작성**
  - 버전별 변경 사항 기록

---

## 🚨 Phase 5-8: 장애 대응

### 에러 시나리오
- [ ] **API 장애 시**
  - Claude API 다운: 사용자에게 안내 메시지
  - Supabase 다운: 로컬 캐시 사용 (가능하다면)

- [ ] **서버 다운 시**
  - Streamlit Cloud 자동 재시작
  - 로그 확인

### 백업 전략
- [ ] **데이터베이스 백업**
  - Supabase 자동 백업 활성화
  - 주간 수동 백업

- [ ] **코드 백업**
  - GitHub에 자동 백업
  - 태그/릴리스 관리

---

## 🔄 Phase 5-9: CI/CD (선택)

### GitHub Actions
- [ ] **자동 테스트**
  ```yaml
  # .github/workflows/test.yml
  name: Test

  on: [push, pull_request]

  jobs:
    test:
      runs-on: ubuntu-latest

      steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd Ask
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd Ask
          pytest
  ```

### 자동 배포
- [ ] **main 브랜치 푸시 시 자동 배포**
  - Streamlit Cloud가 자동으로 감지하여 재배포

---

## 🚀 우선순위

### 🔥 긴급 (배포 직전)
1. Streamlit Cloud 설정
2. Secrets 관리
3. 기능 테스트

### ⚡ 중요 (배포 후 1주)
1. 모니터링 구축
2. 비용 추적
3. 에러 처리 개선

### 📌 보통 (안정화 후)
1. 성능 최적화
2. CI/CD 구축
3. 문서화 보완

---

## 📝 메모

### Streamlit Cloud 제약사항
- 무료 티어: 1 앱, Public 저장소
- 리소스: 제한적 (CPU, 메모리)
- 동시 접속: 제한적
- **유료 전환 시**: $20/월 (프라이빗 저장소, 더 많은 리소스)

### 대안 배포 옵션
1. **Streamlit Cloud** (추천, 간편)
2. **AWS EC2 + Nginx**
3. **Google Cloud Run**
4. **Heroku**
5. **Docker + 자체 서버**

---

## ✅ 완료 기준

배포 작업은 다음 조건을 만족하면 완료:

- [ ] Streamlit Cloud 배포 성공
- [ ] 환경 변수 설정 완료
- [ ] 전체 기능 프로덕션 환경에서 작동
- [ ] 모니터링 시스템 구축
- [ ] 비용 추적 시스템 구축
- [ ] 보안 점검 완료
- [ ] 사용자 문서 작성
- [ ] 장애 대응 계획 수립

→ 완료 시 **정식 출시! 🎉**

---

## 🎯 출시 후 TODO

- [ ] 베타 사용자 모집 (5-10명)
- [ ] 피드백 수집
- [ ] 버그 수정
- [ ] 기능 개선
- [ ] 마케팅 시작

---

**다음 작업**: 모든 Phase 완료 대기 중
