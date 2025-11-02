# 변경 이력 (Changelog)

## [2025-11-02] - 모바일 반응형 최적화 및 버튼 스타일 분리

### ✅ 추가됨 (Added)
- **모바일 반응형 CSS (clamp 함수)**
  - 모든 텍스트/버튼 크기가 화면 너비에 맞춰 자동 조정
  - 랜딩 제목: `clamp(32px, 8vw, 56px)` - 모바일에서 32px, 데스크톱에서 56px
  - 버튼 폰트: `clamp(14px, 4vw, 18px)`
  - 버튼 패딩: `clamp(12px, 3vw, 15px) clamp(20px, 5vw, 30px)`
  - 섹션 제목: h1 `clamp(24px, 6vw, 32px)`, h2 `clamp(20px, 5vw, 28px)`

- **Key 기반 버튼 스타일 분리**
  - 네비게이션 버튼에 `key="nav_start"`, `key="nav_prev"`, `key="nav_next"` 추가
  - CSS에서 `.st-key-nav_*` 선택자로 타겟팅
  - 질문 선택 버튼과 네비게이션 버튼 스타일 완전 분리

### 🔄 변경됨 (Changed)
- **모바일 이미지 크기 최적화**
  - 모바일 (768px 이하): 40%로 축소
  - 태블릿 (769-1024px): 60%
  - 데스크톱 (1025px 이상): 100% (기존 유지)
  - iPhone SE 기준: 이미지 크기 약 38px

- **상단 패딩 축소 (모바일 최적화)**
  - 컨테이너 패딩: 데스크톱 2rem → 모바일 1rem
  - 랜딩 제목 상단 마진: 20px → 모바일에서 0px
  - 총 상단 여백: 약 99px → 32px (67% 감소)
  - 모바일에서 스크롤 없이 전체 랜딩 페이지 표시 가능

- **버튼 스타일 명확화**
  - 네비게이션 버튼 (이전/다음/시작): 흰색 텍스트 (#ffffff) ✅
  - 질문 선택 버튼: 검정색 텍스트 (#333333) ✅
  - CSS 우선순위 문제 해결 (key 기반 선택자 사용)

### 🐛 수정됨 (Fixed)
- **CSS 선택자 문제 해결**
  - 기존: `.nav-button-container .stButton > button` (작동 안함)
  - 수정: `.st-key-nav_* button` (작동함)
  - Streamlit의 HTML 구조로 인한 선택자 불일치 문제 해결

- **텍스트 줄간격 조정 (모바일)**
  - 랜딩 서브타이틀: `line-height: 1.8 → 1.5`
  - 랜딩 설명: `line-height: 1.8 → 1.5`
  - 모바일에서 더 컴팩트한 레이아웃

### 📊 성능 개선
- **모바일 화면 활용도**: 약 67% 여백 감소로 한 화면에 더 많은 콘텐츠 표시
- **iPhone SE (375px) 기준**:
  - 랜딩 제목: 56px → 30px (46% 축소)
  - 마리 이미지: 화면의 10% 정도로 적정 크기
  - 스크롤 없이 "마리에게 물어보기" 버튼까지 표시

### 🎨 CSS 세부 변경사항
```css
/* 모바일 반응형 */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;  /* 기존 2rem */
    }
    .stImage > img {
        max-width: 40% !important;  /* 기존 60% */
    }
    .landing-title {
        margin-top: 0 !important;
        margin-bottom: 8px !important;
    }
}

/* Key 기반 버튼 타겟팅 */
.st-key-nav_start button,
.st-key-nav_prev button,
.st-key-nav_next button {
    color: #ffffff !important;  /* 네비게이션만 흰색 */
}
```

---

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
