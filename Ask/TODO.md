# HeartBridge Ask - 전체 프로젝트 TODO

**마지막 업데이트**: 2025-11-01

---

## 📊 프로젝트 진행 상황

### ✅ 완료된 작업
- [x] 프로젝트 구조 설계
- [x] 기본 설정 파일 작성
- [x] UI 디자인 방향성 결정
- [x] Mock 데이터 준비
- [x] **프로토타입 완성** (8페이지 전환)
- [x] **설문 구조 개편** (7개 질문 → 5개 섹션 18개 질문)
- [x] **랜딩 페이지 디자인 적용** (산호색 #E8826B)
- [x] **다양한 입력 타입 구현** (text, radio, checkbox, image 등)
- [x] **네비게이션 버튼 스타일링** (산호색 + 흰색 텍스트 + 그림자)

### 🔄 현재 진행 중
- [x] UI 디자인 적용 (CSS 인라인 적용 완료)
- [ ] 프로토타입 테스트 및 피드백 수집

### 📅 다음 단계
- UI 완성 → AI 백엔드 → 데이터베이스 → 외부 연동 → 배포

---

## 📁 세부 TODO 파일

프로젝트가 복잡해져서 기능별로 TODO를 분리했습니다:

1. **[TODO_UI_FRONTEND.md](docs/TODO_UI_FRONTEND.md)**
   - Streamlit UI 개선
   - CSS/디자인 작업
   - 페이지 플로우 개선
   - 현재 상태: 프로토타입 완성, 디자인 적용 예정

2. **[TODO_AI_BACKEND.md](docs/TODO_AI_BACKEND.md)**
   - AI 프롬프트 작성
   - Claude API 연동
   - 이미지 분석 로직
   - 현재 상태: Mock 데이터 사용 중

3. **[TODO_DATABASE.md](docs/TODO_DATABASE.md)**
   - Supabase 설정
   - 테이블 스키마 설계
   - 데이터 모델 정의
   - 현재 상태: 미착수

4. **[TODO_INTEGRATION.md](docs/TODO_INTEGRATION.md)**
   - 이메일 전송
   - 인스타그램 카드 생성
   - Google Sheets 대시보드
   - 현재 상태: UI만 존재

5. **[TODO_DEPLOYMENT.md](docs/TODO_DEPLOYMENT.md)**
   - Streamlit Cloud 배포
   - 환경 변수 관리
   - 모니터링
   - 현재 상태: 로컬 개발 환경

---

## 🎯 마일스톤

### Phase 1: UI 프로토타입 (현재)
- **목표**: Mock 데이터로 완전한 사용자 플로우 구현
- **예상 기간**: 1-2주
- **현재 진행률**: 85%
- **다음 작업**: [TODO_UI_FRONTEND.md](docs/TODO_UI_FRONTEND.md) 참고
- **최근 완료**:
  - 설문 구조 5개 섹션으로 재설계
  - 랜딩 페이지 디자인 적용
  - 네비게이션 버튼 스타일링 완료
  - 다양한 입력 타입 구현 (9가지)

### Phase 2: 백엔드 구현
- **목표**: 실제 AI 분석 기능 구현
- **예상 기간**: 2-3주
- **의존성**: Phase 1 완료 필요
- **다음 작업**: [TODO_AI_BACKEND.md](docs/TODO_AI_BACKEND.md) 참고

### Phase 3: 데이터베이스 연동
- **목표**: Supabase 연동 및 데이터 저장
- **예상 기간**: 1주
- **의존성**: Phase 2 완료 필요
- **다음 작업**: [TODO_DATABASE.md](docs/TODO_DATABASE.md) 참고

### Phase 4: 외부 서비스 연동
- **목표**: 이메일, 인스타그램, Google Sheets
- **예상 기간**: 1-2주
- **의존성**: Phase 3 완료 필요
- **다음 작업**: [TODO_INTEGRATION.md](docs/TODO_INTEGRATION.md) 참고

### Phase 5: 배포 및 운영
- **목표**: 프로덕션 환경 배포
- **예상 기간**: 1주
- **의존성**: Phase 1-4 완료 필요
- **다음 작업**: [TODO_DEPLOYMENT.md](docs/TODO_DEPLOYMENT.md) 참고

---

## 🔑 주요 결정사항

### UI 디자인
- **스타일**: 친근하고 따뜻한 스타일
- **색상 테마**: 산호색 (#E8826B) + 흰색 배경
- **페이지 구조**: 8페이지 (랜딩 → 5개 섹션 설문 → 분석중 → 결과)
  - 랜딩 페이지
  - ① 기본 정보 (6개 질문)
  - ② 성향 파악 (2개 질문)
  - ③ 문제 행동 관련 (5개 질문)
  - ④ 환경 정보 (3개 질문)
  - ⑤ 사진 및 참고자료 (2개 질문)
  - AI 분석 중
  - 분석 결과
- **마스코트**: 마리 (Mari) 이미지 순차 활용 (normal_1~4, Answer, in_bag)

### 기술 스택
- Frontend: Streamlit 1.30+
- AI: Claude Sonnet 4.5
- Database: Supabase
- Analytics: Google Sheets
- Email: SendGrid

### 개발 전략
- UI 우선 개발 (Mock 데이터 사용)
- UI 확정 후 백엔드 구현
- 빠른 프로토타입, 점진적 개선

---

## 📝 다음 액션

1. ✅ **프로토타입 실행 및 테스트**
   ```bash
   cd Ask
   streamlit run app.py
   ```

2. 📋 **피드백 수집**
   - 페이지 전환이 자연스러운가?
   - 마리 이미지가 잘 표시되는가?
   - 설문 항목이 적절한가?

3. 🎨 **디자인 적용**
   - custom.css 적용
   - 컴포넌트 스타일링
   - 애니메이션 추가

4. ✅ **UI 확정**
   - 최종 디자인 결정
   - Phase 2 준비

---

**개발 우선순위**: UI (현재) → AI 백엔드 → 데이터베이스 → 외부 연동 → 배포
