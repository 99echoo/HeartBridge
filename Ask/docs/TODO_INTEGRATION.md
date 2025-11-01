# TODO: 외부 서비스 연동

**담당 영역**: 이메일, 인스타그램, Google Sheets, PDF 생성

**마지막 업데이트**: 2025-01-26

---

## 📊 현재 상황

### ✅ 완료된 작업
- [x] 공유 버튼 UI (기능 없음)

### 🔄 진행 중
- [ ] 없음

### ⏳ 대기 중
- 데이터베이스 완료 대기 중 (Phase 3 완료 후 시작)

---

## 📧 Phase 4-1: 이메일 전송 (SendGrid)

### SendGrid 설정
- [ ] **SendGrid 계정 생성**
  - https://sendgrid.com 가입
  - 무료 티어: 100통/일

- [ ] **API Key 생성**
  - Settings → API Keys → Create API Key
  - Full Access 권한

- [ ] **환경 변수 설정**
  ```env
  SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
  SENDGRID_FROM_EMAIL=noreply@heartbridge.com
  SENDGRID_FROM_NAME=HeartBridge Ask
  ```

- [ ] **발신자 인증**
  - Single Sender Verification
  - 또는 도메인 인증 (나중에)

### 이메일 서비스 구현
- [ ] **`src/services/email_service.py` 생성**
  ```python
  from sendgrid import SendGridAPIClient
  from sendgrid.helpers.mail import Mail, Email, To, Content
  from config.settings import settings

  def send_analysis_email(
      to_email: str,
      dog_name: str,
      analysis_result: dict
  ) -> bool:
      """
      분석 결과를 이메일로 전송

      Args:
          to_email: 수신자 이메일
          dog_name: 강아지 이름
          analysis_result: 분석 결과 딕셔너리

      Returns:
          bool: 전송 성공 여부
      """
      try:
          message = Mail(
              from_email=Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
              to_emails=To(to_email),
              subject=f"🐶 {dog_name}의 행동 분석 결과",
              html_content=generate_email_html(dog_name, analysis_result)
          )

          sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
          response = sg.send(message)

          return response.status_code == 202

      except Exception as e:
          print(f"Email send error: {e}")
          return False
  ```

### 이메일 템플릿
- [ ] **HTML 이메일 템플릿 작성**
  - [ ] `src/templates/email_template.html` 생성
  - [ ] 따뜻한 오렌지/베이지 디자인
  - [ ] 마리 이미지 포함
  - [ ] 분석 결과 요약
  - [ ] 액션 플랜 4단계
  - [ ] HeartBridge 로고 및 링크

- [ ] **템플릿 렌더링 함수**
  ```python
  from jinja2 import Template

  def generate_email_html(dog_name: str, analysis_result: dict) -> str:
      """
      Jinja2 템플릿으로 HTML 생성
      """
      with open("src/templates/email_template.html") as f:
          template = Template(f.read())

      return template.render(
          dog_name=dog_name,
          behavior_summary=analysis_result['behavior_summary'],
          expert_opinion=analysis_result['expert_opinion'],
          action_plan=analysis_result['action_plan'],
          confidence_score=analysis_result['confidence_score']
      )
  ```

### app.py 통합
- [ ] **page_result() 수정**
  ```python
  # "📧 이메일 전송" 버튼 클릭 시
  if st.button("📧 이메일 전송", use_container_width=True):
      email = st.session_state.basic_info.get('owner_email')
      if email:
          success = send_analysis_email(
              email,
              st.session_state.basic_info['dog_name'],
              st.session_state.analysis_result
          )
          if success:
              st.success(f"✅ {email}로 전송되었습니다!")
          else:
              st.error("❌ 전송 실패. 다시 시도해주세요.")
      else:
          st.warning("이메일 주소가 필요합니다.")
  ```

---

## 📸 Phase 4-2: 인스타그램 카드 생성

### 카드 디자인
- [ ] **Figma/Canva로 템플릿 디자인**
  - 크기: 1080x1080px (인스타그램 정사각형)
  - 배경: 따뜻한 오렌지/베이지 그라데이션
  - 마리 마스코트 포함
  - 강아지 이름 + 주요 분석 결과 요약

### 이미지 생성 구현
- [ ] **Pillow 라이브러리 사용**
  - `requirements.txt`에 `Pillow>=10.2.0` 추가

- [ ] **`src/services/instagram_card.py` 생성**
  ```python
  from PIL import Image, ImageDraw, ImageFont
  import io

  def create_instagram_card(
      dog_name: str,
      problem_type: str,
      confidence_score: float,
      top_action: str
  ) -> bytes:
      """
      인스타그램 공유용 카드 이미지 생성

      Args:
          dog_name: 강아지 이름
          problem_type: 문제 유형 (한글)
          confidence_score: 신뢰도 점수
          top_action: 주요 액션 플랜 1개

      Returns:
          bytes: PNG 이미지 바이트
      """
      # 1080x1080 캔버스 생성
      img = Image.new('RGB', (1080, 1080), color='#FFFAF0')
      draw = ImageDraw.Draw(img)

      # 폰트 로드
      font_title = ImageFont.truetype("assets/fonts/NotoSansKR-Bold.ttf", 60)
      font_body = ImageFont.truetype("assets/fonts/NotoSansKR-Regular.ttf", 40)

      # 마리 이미지 삽입
      mari = Image.open("assets/images/Mari_image_normal_1.png")
      mari = mari.resize((300, 300))
      img.paste(mari, (390, 100), mari)

      # 텍스트 그리기
      draw.text((540, 450), f"{dog_name}의 분석 결과", fill='#3E2723', font=font_title, anchor='mm')
      draw.text((540, 550), f"문제 유형: {problem_type}", fill='#5D4037', font=font_body, anchor='mm')
      draw.text((540, 620), f"신뢰도: {int(confidence_score*100)}%", fill='#5D4037', font=font_body, anchor='mm')

      # 액션 플랜 (줄바꿈)
      draw.text((540, 750), "첫 번째 액션:", fill='#F4A460', font=font_body, anchor='mm')
      draw.text((540, 820), top_action[:30] + "...", fill='#5D4037', font=font_body, anchor='mm')

      # 로고/워터마크
      draw.text((540, 1000), "HeartBridge Ask 🐾", fill='#F4A460', font=font_body, anchor='mm')

      # 바이트로 변환
      img_bytes = io.BytesIO()
      img.save(img_bytes, format='PNG')
      img_bytes.seek(0)

      return img_bytes.getvalue()
  ```

### 다운로드 기능
- [ ] **app.py 통합**
  ```python
  # "📸 인스타그램 공유" 버튼 클릭 시
  if st.button("📸 인스타그램 카드 생성", use_container_width=True):
      card_image = create_instagram_card(
          dog_name=st.session_state.basic_info['dog_name'],
          problem_type="과도한 짖음",  # 실제로는 매핑 필요
          confidence_score=st.session_state.analysis_result['confidence_score'],
          top_action=st.session_state.analysis_result['action_plan'][0][:50]
      )

      st.download_button(
          label="💾 이미지 다운로드",
          data=card_image,
          file_name=f"{st.session_state.basic_info['dog_name']}_분석결과.png",
          mime="image/png"
      )

      st.image(card_image, caption="생성된 카드", use_container_width=True)
  ```

### 폰트 준비
- [ ] **한글 폰트 다운로드**
  - Noto Sans KR (Google Fonts)
  - `assets/fonts/` 폴더에 저장
  - `NotoSansKR-Regular.ttf`
  - `NotoSansKR-Bold.ttf`

---

## 📊 Phase 4-3: Google Sheets 대시보드

### Google Sheets API 설정
- [ ] **Google Cloud Console 설정**
  - 프로젝트 생성: "heartbridge-ask"
  - Google Sheets API 활성화
  - Service Account 생성
  - JSON 키 파일 다운로드

- [ ] **환경 변수 설정**
  ```env
  GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google-sheets-service-account.json
  GOOGLE_SHEETS_SPREADSHEET_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
  ```

- [ ] **Google Sheets 생성**
  - 스프레드시트 이름: "HeartBridge Ask Analytics"
  - Service Account 이메일에 편집 권한 부여

### Sheets 클라이언트 구현
- [ ] **`src/database/sheets_client.py` 생성**
  ```python
  from google.oauth2.service_account import Credentials
  from googleapiclient.discovery import build
  from config.settings import settings

  def get_sheets_client():
      """Google Sheets API 클라이언트 생성"""
      creds = Credentials.from_service_account_file(
          settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
          scopes=['https://www.googleapis.com/auth/spreadsheets']
      )
      return build('sheets', 'v4', credentials=creds)

  def append_analysis_to_sheet(analysis_data: dict):
      """
      분석 결과를 Google Sheets에 추가

      Args:
          analysis_data: {
              'date': '2025-01-26',
              'dog_name': '마리',
              'problem_type': 'barking',
              'confidence_score': 0.85,
              'processing_time_ms': 5000,
              'api_cost_usd': 0.02
          }
      """
      service = get_sheets_client()
      spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID

      values = [[
          analysis_data['date'],
          analysis_data['dog_name'],
          analysis_data['problem_type'],
          analysis_data['confidence_score'],
          analysis_data['processing_time_ms'],
          analysis_data['api_cost_usd']
      ]]

      body = {'values': values}

      service.spreadsheets().values().append(
          spreadsheetId=spreadsheet_id,
          range='분석기록!A:F',
          valueInputOption='RAW',
          body=body
      ).execute()
  ```

### 시트 구조
- [ ] **Sheet 1: 분석 기록**
  - A: 날짜
  - B: 강아지 이름
  - C: 문제 유형
  - D: 신뢰도 점수
  - E: 처리 시간 (ms)
  - F: API 비용 (USD)

- [ ] **Sheet 2: 일일 통계**
  - A: 날짜
  - B: 총 분석 수
  - C: 총 사용자 수
  - D: 평균 신뢰도
  - E: 총 API 비용

- [ ] **Sheet 3: 문제 유형별 통계**
  - A: 문제 유형
  - B: 발생 횟수
  - C: 비율 (%)

### app.py 통합
- [ ] **분석 완료 시 자동 기록**
  ```python
  # page_analyzing() 또는 page_result()에서
  from src.database.sheets_client import append_analysis_to_sheet

  append_analysis_to_sheet({
      'date': datetime.now().strftime('%Y-%m-%d'),
      'dog_name': st.session_state.basic_info['dog_name'],
      'problem_type': st.session_state.survey_responses['q1'],
      'confidence_score': st.session_state.analysis_result['confidence_score'],
      'processing_time_ms': processing_time,
      'api_cost_usd': api_cost
  })
  ```

---

## 📄 Phase 4-4: PDF 리포트 생성

### PDF 라이브러리 선택
- [ ] **reportlab 또는 weasyprint**
  - reportlab: 코드로 PDF 생성 (유연함)
  - weasyprint: HTML → PDF (쉬움)
  - **선택**: weasyprint (HTML 템플릿 재사용)

- [ ] **requirements.txt 추가**
  ```
  weasyprint>=60.0
  ```

### PDF 생성 구현
- [ ] **`src/services/report_generator.py` 생성**
  ```python
  from weasyprint import HTML
  from jinja2 import Template
  import io

  def generate_pdf_report(
      dog_name: str,
      basic_info: dict,
      analysis_result: dict
  ) -> bytes:
      """
      분석 결과를 PDF로 생성

      Returns:
          bytes: PDF 바이트
      """
      # HTML 템플릿 로드
      with open("src/templates/pdf_template.html") as f:
          template = Template(f.read())

      html_content = template.render(
          dog_name=dog_name,
          basic_info=basic_info,
          analysis_result=analysis_result
      )

      # HTML → PDF
      pdf_bytes = HTML(string=html_content).write_pdf()

      return pdf_bytes
  ```

### PDF 템플릿
- [ ] **`src/templates/pdf_template.html` 생성**
  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <meta charset="UTF-8">
      <style>
          body {
              font-family: 'Noto Sans KR', sans-serif;
              color: #3E2723;
              background: #FFFAF0;
          }
          h1 { color: #F4A460; }
          .section { margin: 20px 0; }
      </style>
  </head>
  <body>
      <h1>🐾 {{ dog_name }}의 행동 분석 리포트</h1>

      <div class="section">
          <h2>📋 기본 정보</h2>
          <p>이름: {{ dog_name }}</p>
          <p>나이: {{ basic_info.dog_age }}</p>
          <p>크기: {{ basic_info.dog_size }}</p>
      </div>

      <div class="section">
          <h2>📊 분석 결과</h2>
          {{ analysis_result.behavior_summary }}
      </div>

      <div class="section">
          <h2>👨‍⚕️ 전문가 의견</h2>
          {{ analysis_result.expert_opinion }}
      </div>

      <div class="section">
          <h2>🎯 훈련 플랜</h2>
          {% for step in analysis_result.action_plan %}
              <p>{{ step }}</p>
          {% endfor %}
      </div>

      <footer>
          <p>생성일: {{ now.strftime('%Y-%m-%d') }}</p>
          <p>HeartBridge Ask - AI 기반 반려견 행동 분석</p>
      </footer>
  </body>
  </html>
  ```

### app.py 통합
- [ ] **"💾 PDF 저장" 버튼**
  ```python
  if st.button("💾 PDF 저장", use_container_width=True):
      pdf_bytes = generate_pdf_report(
          dog_name=st.session_state.basic_info['dog_name'],
          basic_info=st.session_state.basic_info,
          analysis_result=st.session_state.analysis_result
      )

      st.download_button(
          label="📥 PDF 다운로드",
          data=pdf_bytes,
          file_name=f"{st.session_state.basic_info['dog_name']}_분석리포트.pdf",
          mime="application/pdf"
      )
  ```

---

## 🧪 Phase 4-5: 테스트

### 이메일 테스트
- [ ] **SendGrid Sandbox 모드**
  - 실제 이메일 전송 전 샌드박스 테스트

- [ ] **테스트 케이스**
  - [ ] 정상 이메일 전송
  - [ ] 잘못된 이메일 주소
  - [ ] SendGrid API 오류 처리

### 이미지 생성 테스트
- [ ] **다양한 입력 테스트**
  - [ ] 긴 강아지 이름 (20자)
  - [ ] 특수문자 포함
  - [ ] 다양한 문제 유형

### Google Sheets 테스트
- [ ] **권한 테스트**
  - Service Account 접근 확인

- [ ] **데이터 추가 테스트**
  - 100개 데이터 추가 성능 확인

### PDF 생성 테스트
- [ ] **한글 폰트 렌더링**
  - 한글 깨짐 확인

- [ ] **이미지 포함 테스트**
  - 마리 이미지가 PDF에 포함되는지

---

## 🔒 Phase 4-6: 보안 및 에러 처리

### API 키 보호
- [ ] **환경 변수 검증**
  ```python
  # config/settings.py에서
  if not settings.SENDGRID_API_KEY:
      raise ValueError("SENDGRID_API_KEY is required")
  ```

### Rate Limiting
- [ ] **이메일 전송 제한**
  - 동일 이메일로 하루 3회까지만
  - Session state로 카운트

### 에러 메시지
- [ ] **사용자 친화적 메시지**
  - "이메일 전송 실패" → "잠시 후 다시 시도해주세요"
  - 에러 로그는 서버에만 기록

---

## 🚀 우선순위

### 🔥 긴급 (DB 완료 후)
1. 이메일 전송 구현
2. PDF 리포트 생성

### ⚡ 중요 (2주차)
1. 인스타그램 카드 생성
2. Google Sheets 연동

### 📌 보통 (여유 있을 때)
1. 디자인 개선
2. 추가 템플릿

---

## 📝 메모

### SendGrid 무료 티어
- 100통/일 → 충분함 (초기 사용자 < 100명/일)
- 유료 전환 시 $19.95/월 (50,000통)

### 인스타그램 자동 포스팅?
- Instagram Graph API 필요 (복잡함)
- 현재는 **이미지 다운로드만** 제공
- 사용자가 직접 인스타에 업로드

---

## ✅ 완료 기준

외부 서비스 연동 작업은 다음 조건을 만족하면 완료:

- [ ] 이메일 전송 기능 작동
- [ ] 인스타그램 카드 생성 및 다운로드
- [ ] Google Sheets 자동 기록
- [ ] PDF 리포트 생성 및 다운로드
- [ ] 모든 기능 에러 핸들링 완비
- [ ] 테스트 통과

→ 완료 시 [TODO_DEPLOYMENT.md](TODO_DEPLOYMENT.md)로 이동

---

**다음 작업**: 데이터베이스 완료 대기 중
