"""
파일명: app.py
목적: HeartBridge Ask - AI 기반 반려견 행동 분석 Streamlit 앱
작성일: 2025-01-26
수정일: 2025-01-26 - 5개 섹션 구조로 재작성
"""

# UTF-8 인코딩 강제 (Windows CP949 환경 대응)
import sys
import io as _io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time

import streamlit as st

# 설정 파일 임포트
from config.survey_questions import (
    get_all_sections,
    get_basic_info_questions,
    get_personality_questions,
    get_behavior_problem_questions,
    get_environment_questions,
    get_photo_questions,
)
from config.settings import settings
from src.utils.mock_data import get_mock_result_by_problem
from src.utils.csv_logger import save_to_csv
from src.ui.state import initialize_session_state, next_page, prev_page
from src.ui.components import (
    scroll_to_top,
    show_progress_bar,
    load_mari_image,
    get_image_base64,
    render_question,
)
from src.ui.media import fix_image_orientation, convert_image_to_bytes
from src.ui.styles import inject_base_styles
from src.services.analysis_service import (
    AnalysisJob,
    start_analysis_job,
    job_done,
    job_result,
)
from src.ui.messages import build_empathy_message
from src.ui.result_sections import (
    render_summary_card,
    render_solutions,
    render_guidance,
    render_core_message,
    render_confidence_badge,
)

# 페이지 설정
st.set_page_config(
    page_title="HeartBridge Ask - 반려견 행동 분석",
    page_icon="🐶",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 커스텀 CSS - 전체 스타일
inject_base_styles()

# 페이지 전환 시 스크롤 맨 위로 이동
st.markdown("""
    <script>
    // 페이지 로드 시 스크롤을 맨 위로
    window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
""", unsafe_allow_html=True)


# ===== 페이지 0: 랜딩 페이지 =====
def page_landing():
    scroll_to_top()

    # 랜딩 페이지 전용 스타일 (버튼 텍스트 흰색)
    st.markdown("""
        <style>
        .landing-page .stButton > button {
            color: #ffffff !important;
        }
        .landing-page .stButton > button p {
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="landing-page">', unsafe_allow_html=True)

    # 큰 제목: 마음다리
    st.markdown('<div class="landing-title">마음다리</div>', unsafe_allow_html=True)

    # 첫 번째 설명
    st.markdown(
        '<div class="landing-subtitle">'
        '반려견의 행동이 고민될 때,<br>'
        '훈련사에게 바로 묻기엔 부담스럽다면?<br>'
        '마리가 도와드릴게요'
        '</div>',
        unsafe_allow_html=True
    )

    # 두 번째 설명
    st.markdown(
        '<div class="landing-description">'
        '일상 속 작은 문제부터 훈련이 필요한 상황까지,<br>'
        '반려견의 상황에 맞춰 솔루션을 쉽고 따뜻한 언어로 알려드려요'
        '</div>',
        unsafe_allow_html=True
    )

    # 마리 이미지 표시 (중앙 정렬 박스)
    mari_image = load_mari_image("Mari_image_normal_1.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        # 이미지가 없을 경우 이모지 표시
        st.markdown(
            '<div style="text-align: center; font-size: 100px;">🐶❤️</div>',
            unsafe_allow_html=True
        )

    # 마리에게 물어보기 버튼 (중앙 정렬)
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("마리에게 물어보기", key="nav_start", use_container_width=True, type="primary"):
            next_page()
    st.markdown('</div>', unsafe_allow_html=True)  # nav-button-container 닫기

    st.markdown('</div>', unsafe_allow_html=True)  # landing-page div 닫기


# ===== 페이지 1: 기본 정보 =====
def page_basic_info():
    scroll_to_top()

    questions = get_basic_info_questions()

    st.markdown("## 우리 강아지에 대해 알려주세요")

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_1.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 각 질문 렌더링
    for q in questions:
        response = render_question(q)

        # 이미지 업로드가 아닌 경우에만 세션에 저장
        if q["type"] not in ["image", "media"]:
            if response is not None:
                st.session_state.responses[q["id"]] = response

        st.markdown("---")

    # 네비게이션 버튼
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="nav_prev", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", key="nav_next", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("모든 필수 항목을 입력해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 2: 성향 파악 =====
def page_personality():
    scroll_to_top()

    questions = get_personality_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 평소 성향을 알려주세요")

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_2.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 각 질문 렌더링
    for q in questions:
        response = render_question(q)

        if q["type"] not in ["image", "media"]:
            if response is not None:
                st.session_state.responses[q["id"]] = response

        st.markdown("---")

    # 네비게이션 버튼
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="nav_prev", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", key="nav_next", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("모든 필수 항목을 입력해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 3: 문제 행동 관련 =====
def page_behavior_problem():
    scroll_to_top()

    questions = get_behavior_problem_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 문제 행동에 대해 알려주세요")

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_3.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 각 질문 렌더링
    for q in questions:
        response = render_question(q)

        if q["type"] not in ["image", "media"]:
            if response is not None:
                st.session_state.responses[q["id"]] = response

        st.markdown("---")

    # 네비게이션 버튼
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="nav_prev", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", key="nav_next", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("모든 필수 항목을 입력해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 4: 환경 정보 =====
def page_environment():
    scroll_to_top()

    questions = get_environment_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 생활 환경을 알려주세요")

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_4.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 각 질문 렌더링 (조건부 처리)
    for q in questions:
        # 조건부 질문 처리
        if q.get("conditional", False):
            depends_on = q.get("depends_on")
            show_when = q.get("show_when")

            # 의존하는 질문의 응답 확인
            parent_response = st.session_state.responses.get(depends_on)

            # 조건이 맞을 때만 표시
            if parent_response != show_when:
                continue

        response = render_question(q)

        if q["type"] not in ["image", "media"]:
            if response is not None:
                st.session_state.responses[q["id"]] = response

        st.markdown("---")

    # 네비게이션 버튼
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="nav_prev", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증 (조건부 필드 고려)
        required_fields = []
        for q in questions:
            if q.get("required", False):
                # 조건부 질문인 경우 조건 확인
                if q.get("conditional", False):
                    depends_on = q.get("depends_on")
                    show_when = q.get("show_when")
                    parent_response = st.session_state.responses.get(depends_on)

                    # 조건이 맞을 때만 필수
                    if parent_response == show_when:
                        required_fields.append(q["id"])
                else:
                    required_fields.append(q["id"])

        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", key="nav_next", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("모든 필수 항목을 입력해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 5: 사진 및 참고자료 =====
def page_photos():
    scroll_to_top()

    questions = get_photo_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 사진을 업로드해주세요")

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_Answer.png")
    if mari_image:
        st.markdown(
            f'''
            <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
                <img src="data:image/png;base64,{get_image_base64(mari_image)}" width="200" />
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 각 질문 렌더링
    for q in questions:
        response = render_question(q)

        # 이미지/미디어는 별도로 세션에 저장
        if q["type"] in ["image", "media"]:
            if response is not None:
                if q["id"] == "dog_photo":
                    st.session_state.dog_photo = response
                elif q["id"] == "behavior_media":
                    st.session_state.behavior_media = response

        st.markdown("---")

    # 네비게이션 버튼
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="nav_prev", use_container_width=True):
            prev_page()
    with col2:
        # dog_photo는 필수
        if st.session_state.dog_photo is not None:
            if st.button("분석 시작 🚀", key="nav_next", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("반려견 사진을 업로드해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 6: AI 분석 중 =====
def page_analyzing():
    scroll_to_top()

    if st.session_state.analysis_result is not None:
        next_page()
        return

    st.markdown("""
        <style>
        @keyframes pulse { 0%,100%{transform:scale(1);} 50%{transform:scale(1.05);} }
        @keyframes shake { 0%,100%{transform:rotate(0deg);} 25%{transform:rotate(-5deg);} 75%{transform:rotate(5deg);} }
        .analyzing-page .stImage > img { animation: pulse 2s ease-in-out infinite, shake 3s ease-in-out infinite; }
        @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
        .dynamic-message { font-size: clamp(16px,4vw,20px); font-weight: bold; color:#E8826B; text-align:center; margin:20px 0; }
        .dynamic-message.blinking { animation: blink 1s ease-in-out infinite; }
        .completion-message { font-size: clamp(18px,5vw,24px); font-weight:bold; color:#4CAF50; text-align:center; margin:20px 0; }
        .empathy-card {
            background: #fff6f2;
            border: 1px solid #ffd6c9;
            border-radius: 18px;
            padding: 18px;
            margin: 10px 0 25px 0;
            box-shadow: 0 4px 12px rgba(232, 130, 107, 0.15);
            text-align: center;
            font-size: clamp(15px, 4vw, 18px);
            line-height: 1.5;
            color: #cc5b3f;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="analyzing-page">', unsafe_allow_html=True)
    st.title("AI 분석 중...")

    mari_image = load_mari_image("Mari_image_in_bag.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, width=300)

    dog_name = st.session_state.responses.get("dog_name", "강아지")
    dynamic_messages = [
        f"🐶 {dog_name}의 행동을 꼼꼼히 분석하고 있어요!",
        "🔍 마리가 열심히 생각 중이에요...",
        "💭 전문가 의견을 모으고 있어요!",
        "✨ 맞춤 솔루션을 준비하고 있어요!",
        "⏳ 조금만 기다려주세요, 거의 다 됐어요!",
    ]
    if "empathy_message" not in st.session_state:
        st.session_state.empathy_message = build_empathy_message(
            dog_name,
            st.session_state.responses.get("dog_breed"),
        )
    message_placeholder = st.empty()
    st.markdown("### 분석 진행 중...")
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    st.markdown(
        f"""
        <div class="empathy-card">
            {st.session_state.empathy_message}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "analysis_inputs" not in st.session_state:
        dog_photo = st.session_state.get("dog_photo")
        if dog_photo is None:
            st.error("강아지 사진이 업로드되지 않았습니다.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        fixed_dog_photo = fix_image_orientation(dog_photo)
        dog_photo_bytes = convert_image_to_bytes(fixed_dog_photo)
        if dog_photo_bytes is None:
            st.error("이미지 처리 중 오류가 발생했습니다. 다른 이미지를 업로드해주세요.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        behavior_media = st.session_state.get("behavior_media")
        behavior_media_bytes = None
        if behavior_media:
            fixed = fix_image_orientation(behavior_media)
            behavior_media_bytes = convert_image_to_bytes(fixed)

        st.session_state.analysis_inputs = {
            "dog_photo_bytes": dog_photo_bytes,
            "behavior_media_bytes": behavior_media_bytes,
        }

    inputs = st.session_state.analysis_inputs

    if "analysis_job" not in st.session_state:
        st.session_state.analysis_job = start_analysis_job(
            responses=st.session_state.responses,
            dog_photo=inputs["dog_photo_bytes"],
            behavior_media=inputs["behavior_media_bytes"],
        )

    job: AnalysisJob = st.session_state.analysis_job
    elapsed = max(time.time() - job.started_at, 0.0)
    expected = max(settings.ANALYSIS_EXPECTED_SECONDS, 1.0)
    progress_ratio = min(elapsed / expected, 0.95)
    progress_bar.progress(progress_ratio)

    status_timeline = [
        (0.05, "📋 설문 응답 데이터 처리 중..."),
        (0.15, "📊 응답 패턴 분석 중..."),
        (0.3, "🖼️ 이미지 로딩 및 특징 추출 중..."),
        (0.5, "🤖 1차 AI 전문가 분석 시작..."),
        (0.7, "🎯 문제 원인 파악 중..."),
        (0.85, "✨ 2차 AI 마리 변환 중..."),
    ]
    current_status = status_timeline[-1][1]
    for threshold, message in status_timeline:
        if progress_ratio <= threshold:
            current_status = message
            break
    status_text.text(current_status)

    msg_index = min(int(progress_ratio * len(dynamic_messages)), len(dynamic_messages) - 1)
    message_placeholder.markdown(
        f'<div class="dynamic-message blinking">{dynamic_messages[msg_index]}</div>',
        unsafe_allow_html=True,
    )

    if not job_done(job):
        time.sleep(0.8)
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()
        return

    try:
        result = job_result(job)
    except Exception as exc:
        st.error(f"분석 중 오류가 발생했습니다: {exc}")
        st.warning("임시 분석 결과를 생성합니다.")
        result = build_mock_analysis_result(st.session_state.responses)

    st.session_state.analysis_result = result

    try:
        save_to_csv(
            responses=st.session_state.responses,
            analysis_result=result,
        )
    except Exception as csv_error:
        st.warning(f"CSV 저장 실패: {csv_error}")

    st.session_state.pop("analysis_job", None)
    st.session_state.pop("analysis_inputs", None)
    st.session_state.pop("empathy_message", None)

    progress_bar.progress(1.0)
    status_text.text("✅ 분석 완료!")
    message_placeholder.markdown(
        '<div class="completion-message">🎉 결과가 완료됐어요!</div>',
        unsafe_allow_html=True,
    )
    time.sleep(1.5)
    st.markdown('</div>', unsafe_allow_html=True)
    next_page()


def build_mock_analysis_result(responses: dict) -> dict:
    """API 오류 시 사용할 임시 분석 결과 생성."""
    dog_name = responses.get("dog_name", "강아지")
    main_concerns = responses.get("main_concerns", [])
    problem_type = main_concerns[0] if main_concerns else "barking"
    mock_result = get_mock_result_by_problem(problem_type)

    final_text = f"""**"{dog_name}의 행동 분석 결과예요!"**

{mock_result.get('behavior_summary', '')}

---

{mock_result.get('expert_opinion', '')}

---

## 맞춤 훈련 플랜

""" + "\n\n".join(
        [f"**{i + 1}. {step}**" for i, step in enumerate(mock_result.get("action_plan", []))]
    )

    return {
        "final_text": final_text,
        "confidence_score": mock_result.get("confidence_score", 0.5),
        "raw_json": {},
    }


def extract_structured_sections(result: dict) -> dict:
    """raw_json 기반 구조화된 결과 추출."""
    raw = result.get("raw_json") or {}
    summary = raw.get("analysis_summary") or {}
    solutions = raw.get("solutions_best_fit") or []
    guidance = raw.get("future_guidance") or []
    return {
        "summary": summary,
        "solutions": solutions,
        "guidance": guidance,
        "core_message": raw.get("core_message"),
        "confidence": raw.get("confidence_score", result.get("confidence_score")),
        "has_structured": bool(summary and solutions and guidance),
    }


# ===== 페이지 7: 분석 결과 =====
def page_result():
    scroll_to_top()

    st.title("분석 결과")

    result = st.session_state.analysis_result
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    if not result:
        st.info("아직 분석 결과가 준비되지 않았어요.")
        return

    sections = extract_structured_sections(result)

    st.markdown(
        f"""
        <div style='text-align: center; margin-bottom: 14px;'>
            <p style='color: #333333; font-size: clamp(16px, 4vw, 20px); font-weight: bold; margin: 0;'>
                {dog_name}의 행동 분석이 완료되었습니다!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_confidence_badge(sections["confidence"])

    dog_photo = st.session_state.get("dog_photo")
    if dog_photo:
        fixed_image = fix_image_orientation(dog_photo)
        if fixed_image:
            st.image(fixed_image, caption=f"{dog_name}의 사진", width=260)

    if sections["has_structured"]:
        render_summary_card(sections["summary"], dog_name)
        render_core_message(sections.get("core_message"))
        if sections["solutions"]:
            render_solutions(sections["solutions"])
        if sections["guidance"]:
            render_guidance(sections["guidance"])

        final_text = result.get("final_text")
        if final_text:
            st.markdown("### 💬 마리의 이야기")
            render_mari_story(final_text)
    else:
        final_text = result.get("final_text", "")
        if final_text:
            st.markdown("### 💬 마리의 이야기")
            render_mari_story(final_text)
        else:
            summary = result.get("behavior_summary")
            if summary:
                st.markdown("### 행동 요약")
                st.markdown(summary)
            action_plan = result.get("action_plan", [])
            for i, step in enumerate(action_plan, 1):
                with st.expander(f"단계 {i}", expanded=(i == 1)):
                    st.markdown(step)
            if result.get("additional_notes"):
                st.warning(f"{result['additional_notes']}")

    st.markdown("---")

    st.markdown("### 📤 결과 공유")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("📸 인스타그램 공유", use_container_width=True)
    with col2:
        st.button("📧 이메일 전송", use_container_width=True)
    with col3:
        st.button("💾 PDF 저장", use_container_width=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("새로운 분석 시작", key="nav_restart", use_container_width=True, type="primary"):
            st.session_state.page = 0
            st.session_state.responses = {}
            st.session_state.dog_photo = None
            st.session_state.behavior_media = None
            st.session_state.analysis_result = None
            st.rerun()


# ===== 메인 앱 =====
def main():
    # 세션 스테이트 초기화
    initialize_session_state()

    # 페이지 라우팅
    pages = [
        page_landing,
        page_basic_info,
        page_personality,
        page_behavior_problem,
        page_environment,
        page_photos,
        page_analyzing,
        page_result,
    ]

    # 현재 페이지 표시
    if 0 <= st.session_state.page < len(pages):
        pages[st.session_state.page]()
    else:
        st.error("페이지를 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
