# 변경 이력 (Changelog)

## [2025-11-01] - 주요 UI 개편 및 설문 구조 변경

### ✅ 추가됨 (Added)
- **새로운 설문 구조**: 7개 단일 질문 → 5개 섹션 18개 질문으로 확장
  - ① 기본 정보: 반려견 이름, 나이, 품종, 성별, 중성화, 다른 반려동물
  - ② 성향 파악: 성향 체크리스트, 활동 시간
  - ③ 문제 행동 관련: 고민거리, 시작 시점, 상황, 시도한 해결책, 힘든 점
  - ④ 환경 정보: 주거 환경, 가족 구성, 외출 시간
  - ⑤ 사진 및 참고자료: 반려견 사진(필수), 행동 영상/사진(선택)

- **다양한 입력 타입 구현**: 총 9가지 타입
  - `text`: 텍스트 입력
  - `radio`: 버튼형 라디오 (세로 나열)
  - `radio_horizontal`: 가로 나열 라디오 버튼
  - `checkbox`: 단일 체크박스
  - `checkbox_multiple`: 복수 선택 버튼형
  - `checkbox_grid`: 체크박스 세로 나열
  - `image`: 이미지 업로드
  - `media`: 사진/영상 업로드
  - ~~`time_range`: 시간 범위 슬라이더~~ (제거)

- **네비게이션 버튼 스타일링**
  - 산호색 배경 (#E8826B)
  - 흰색 텍스트
  - 그림자 효과 (0 4px 6px rgba(0,0,0,0.1))
  - 호버 시 그림자 증가 및 위치 이동 애니메이션

- **랜딩 페이지 디자인**
  - 마음다리 큰 제목 (56px, 산호색)
  - 서비스 소개 텍스트 (18px/16px, bold)
  - 마리 이미지 중앙 정렬
  - 시작 버튼 (산호색 배경 + 흰색 텍스트)

### 🔄 변경됨 (Changed)
- **색상 테마**: #F4A460 → #E8826B (산호색)
- **페이지 구조**: 6페이지 → 8페이지 (설문이 5개 섹션으로 분리)
- **진행률 표시**: 20%/40%/60%... → Step 1/7, 2/7...
- **마리 이미지 사용 방식**:
  - 페이지 1-4: normal_1.png → normal_4.png (순차적)
  - 페이지 5: Mari_image_Answer.png
  - 분석 중: Mari_image_in_bag.png
- **섹션 제목 위치**: 진행바 하단 → 상단 (더 큰 폰트 크기: ##)
- **버튼 스타일 분리**:
  - 네비게이션 버튼 (이전/다음): 흰색 텍스트
  - 질문 답변 버튼: 검정색 텍스트
- **다크모드 비활성화**: 흰색 배경 고정 (모든 테마에서)

### 🗑️ 제거됨 (Removed)
- 기존 7개 질문 단일 페이지 구조
- 시간 범위 슬라이더 (`time_range` 타입)

### 🐛 수정됨 (Fixed)
- 텍스트 입력 필드 테두리 표시 (2px solid #e0e0e0)
- 체크박스 버튼 투명도 문제 (회색 배경 + 테두리 추가)
- 이미지 중앙 정렬 CSS
- 네비게이션 버튼 텍스트 색상 우선순위 (흰색 강제 적용)
- Placeholder 스타일링 (회색 + italic)

### 📝 설문 세부 변경사항

#### 기본 정보 섹션
- 반려견 이름: text
- 나이: text (생년월 또는 추정 나이)
- 품종: text
- 성별: radio_horizontal (남아/여아)
- 중성화: radio_horizontal (예/아니요) - 이전에는 checkbox
- 다른 반려동물: checkbox_multiple (강아지/고양이/기타) - "네" 접두사 제거

#### 성향 파악 섹션
- 평소 성향: checkbox_grid (8개 옵션, 복수 선택) - 이전에는 checkbox_multiple
- 활동 시간: radio (30분 이내 ~ 3시간 이상)

#### 문제 행동 섹션
- 고민거리: checkbox_grid (짖음/배변/입질/산책 공격성/낯선 사람 불안 + 기타) - 이전에는 checkbox_multiple
- 문제 시작 시점: radio (1개월 이내 ~ 6개월 이상)
- 발생 상황: text (구체적 설명)
- 시도한 해결책: text (선택)
- 가장 힘든 점: text

#### 환경 정보 섹션
- 주거 환경: radio (아파트/오피스텔/단독주택 + 기타)
- 가족 구성: radio (1인/2-3인/4인 이상)
- 외출 시간: radio (없음/오전/오후/저녁/종일) - 이전에는 time_range 슬라이더

#### 사진 섹션
- 반려견 사진: image (필수)
- 행동 영상/사진: media (선택)

### 🎨 CSS 스타일링 세부사항

```css
/* 주요 색상 */
--primary-color: #E8826B (산호색)
--secondary-color: #D67159 (어두운 산호색, 호버)
--background: #ffffff (흰색)
--text-color: #333333 (검정)

/* 버튼 */
- 네비게이션: background #E8826B, color #ffffff, shadow 0 4px 6px
- 질문 답변: background #E8826B, color #333333
- Secondary: background #f5f5f5, border 2px #e0e0e0

/* 텍스트 입력 */
- border: 2px solid #e0e0e0
- border-radius: 8px
- padding: 12px
- focus: border-color #1f77b4
```

### 📊 통계
- 총 페이지 수: 6 → 8
- 총 질문 수: 7 → 18
- 입력 타입: 4가지 → 9가지
- CSS 라인 수: ~50 → ~180

### 🚀 성능
- 앱 실행: http://localhost:8501
- 초기 로딩: 정상
- 페이지 전환: 정상 (session state 유지)

### 📝 참고
- 설문 정의: `Ask/config/survey_questions.py`
- 메인 앱: `Ask/app.py`
- 진행 상황: `Ask/TODO.md`, `Ask/docs/TODO_UI_FRONTEND.md`

---

## [2025-01-26] - 초기 프로토타입

### ✅ 추가됨
- 기본 프로젝트 구조
- 6페이지 프로토타입
- Session state 관리
- Mock 데이터
- 마리 이미지 통합

### 📝 초기 설정
- Streamlit 1.30+
- Python 3.11+
- Pydantic 설정
