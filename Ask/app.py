"""
파일명: app.py
목적: HeartBridge Ask - AI 기반 반려견 행동 분석 Streamlit 앱
작성일: 2025-01-26
수정일: 2025-01-26 - 5개 섹션 구조로 재작성
"""

import streamlit as st
import time
import asyncio
from pathlib import Path

# 설정 파일 임포트
from config.survey_questions import (
    get_all_sections,
    get_basic_info_questions,
    get_personality_questions,
    get_behavior_problem_questions,
    get_environment_questions,
    get_photo_questions,
)
from src.utils.mock_data import get_mock_result_by_problem
from src.ai.analyzer import analyze_two_stage

# 페이지 설정
st.set_page_config(
    page_title="HeartBridge Ask - 반려견 행동 분석",
    page_icon="🐶",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 커스텀 CSS - 전체 스타일
st.markdown("""
    <style>
    /* 다크모드 비활성화 및 흰색 배경 고정 */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f5f5f5 !important;
    }

    /* 전체 앱 배경 */
    .main {
        background-color: #ffffff !important;
    }

    /* 상단 패딩 축소 (모바일 최적화) */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }

    /* 텍스트 색상 강제 */
    .stMarkdown, p, span, div {
        color: #333333 !important;
    }

    /* 텍스트 입력 필드 테두리 스타일 - 반응형 */
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0 !important;
        border-radius: clamp(6px, 2vw, 8px) !important;
        padding: clamp(10px, 2.5vw, 12px) !important;
        font-size: clamp(14px, 3.5vw, 16px) !important;
        background-color: #ffffff !important;
        color: #333333 !important;
    }

    /* 포커스 시 테두리 색상 */
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 1px #1f77b4 !important;
    }

    /* placeholder 스타일 */
    .stTextInput > div > div > input::placeholder {
        color: #a0a0a0 !important;
        font-style: italic !important;
    }

    /* 랜딩 페이지 스타일 - 반응형 */
    .landing-title {
        font-size: clamp(32px, 8vw, 56px) !important;
        font-weight: bold !important;
        color: #E8826B !important;
        text-align: center !important;
        margin-top: clamp(5px, 2vw, 20px) !important;
        margin-bottom: clamp(10px, 3vw, 25px) !important;
    }

    .landing-subtitle {
        font-size: clamp(14px, 4vw, 18px) !important;
        font-weight: bold !important;
        color: #333333 !important;
        text-align: center !important;
        line-height: 1.6 !important;
        margin-bottom: clamp(5px, 1.5vw, 10px) !important;
    }

    .landing-description {
        font-size: clamp(13px, 3.5vw, 16px) !important;
        font-weight: bold !important;
        color: #666666 !important;
        text-align: center !important;
        line-height: 1.6 !important;
        margin-bottom: clamp(8px, 2vw, 15px) !important;
    }

    /* 랜딩 페이지 모바일 최적화 */
    @media (max-width: 768px) {
        .landing-title {
            margin-top: 0 !important;
            margin-bottom: 8px !important;
        }
        .landing-subtitle {
            line-height: 1.5 !important;
            margin-bottom: 5px !important;
        }
        .landing-description {
            line-height: 1.5 !important;
            margin-bottom: 8px !important;
        }
    }

    /* 버튼 스타일 - 산호색 (질문 답변용) - 반응형 */
    .stButton > button {
        background-color: #E8826B !important;
        color: #333333 !important;
        border: none !important;
        border-radius: clamp(15px, 4vw, 25px) !important;
        padding: clamp(12px, 3vw, 15px) clamp(20px, 5vw, 30px) !important;
        font-size: clamp(14px, 4vw, 18px) !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button p {
        color: #333333 !important;
        font-weight: bold !important;
    }

    .stButton > button:hover {
        background-color: #D67159 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(232, 130, 107, 0.3) !important;
    }

    /* Primary 버튼 (선택된 질문 답변) - 흰색 텍스트 */
    .stButton > button[kind="primary"] {
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
    }

    /* Secondary 버튼 (선택 안 된 질문 답변) - 검정색 텍스트 */
    .stButton > button[kind="secondary"] {
        background-color: #f5f5f5 !important;
        color: #333333 !important;
        border: 2px solid #e0e0e0 !important;
        font-weight: bold !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #FFEAE6 !important;
        border-color: #E8826B !important;
        color: #E8826B !important;
    }

    .stButton > button[kind="secondary"] p {
        color: #333333 !important;
    }

    /* 네비게이션 버튼 스타일 - Key 기반 (수정됨) */
    .st-key-nav_start button,
    .st-key-nav_prev button,
    .st-key-nav_next button,
    .st-key-nav_restart button {
        background-color: #E8826B !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: clamp(6px, 2vw, 8px) !important;
        padding: clamp(10px, 2.5vw, 12px) clamp(16px, 4vw, 24px) !important;
        font-size: clamp(14px, 3.5vw, 16px) !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }

    .st-key-nav_start button:hover,
    .st-key-nav_prev button:hover,
    .st-key-nav_next button:hover,
    .st-key-nav_restart button:hover {
        background-color: #D67159 !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }

    .st-key-nav_start button p,
    .st-key-nav_prev button p,
    .st-key-nav_next button p,
    .st-key-nav_restart button p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* 이미지 중앙 정렬 및 반응형 크기 */
    .stImage {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .stImage > img {
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: 100% !important;
        height: auto !important;
    }

    /* 모바일에서 이미지 크기 제한 - 더 작게 */
    @media (max-width: 768px) {
        .stImage > img {
            max-width: 40% !important;
            width: 40% !important;
        }

        /* 컬럼 안의 이미지도 강제 */
        div[data-testid="column"] .stImage > img {
            max-width: 40% !important;
            width: 40% !important;
        }
    }

    /* 태블릿에서 이미지 크기 제한 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stImage > img {
            max-width: 60% !important;
        }
    }

    /* 섹션 제목 반응형 */
    h1, .stMarkdown h1 {
        font-size: clamp(24px, 6vw, 32px) !important;
    }

    h2, .stMarkdown h2 {
        font-size: clamp(20px, 5vw, 28px) !important;
    }

    h3, .stMarkdown h3 {
        font-size: clamp(16px, 4vw, 20px) !important;
    }

    /* 일반 텍스트 반응형 */
    p, .stMarkdown p {
        font-size: clamp(13px, 3.5vw, 16px) !important;
    }

    /* 캡션 텍스트 반응형 */
    .stMarkdown small, .stCaption {
        font-size: clamp(11px, 3vw, 14px) !important;
    }
    </style>
""", unsafe_allow_html=True)


# 헬퍼 함수
def initialize_session_state():
    """세션 스테이트 초기화"""
    if "page" not in st.session_state:
        st.session_state.page = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "dog_photo" not in st.session_state:
        st.session_state.dog_photo = None
    if "behavior_media" not in st.session_state:
        st.session_state.behavior_media = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None


def next_page():
    """다음 페이지로 이동"""
    st.session_state.page += 1
    st.rerun()


def prev_page():
    """이전 페이지로 이동"""
    if st.session_state.page > 0:
        st.session_state.page -= 1
        st.rerun()


def show_progress_bar(step, total=7):
    """진행 바 표시"""
    progress = step / total
    st.progress(progress)
    st.caption(f"진행률: {int(progress * 100)}% (Step {step}/{total})")


def load_mari_image(image_name):
    """마리 이미지 로드"""
    image_path = Path("assets/images") / image_name
    if image_path.exists():
        return str(image_path)
    return None


def render_question(q: dict):
    """
    질문 타입에 맞는 UI를 렌더링하고 응답을 반환합니다.

    Args:
        q: 질문 딕셔너리

    Returns:
        응답 값
    """
    st.markdown(f"### {q['question']}")

    # 설명이 있으면 표시
    if q.get("description"):
        st.caption(q["description"])

    st.markdown("")

    q_type = q["type"]
    q_id = q["id"]

    # 기존 응답 가져오기
    default_value = st.session_state.responses.get(q_id)

    # 텍스트 입력
    if q_type == "text":
        return st.text_input(
            f"{q_id}_input",
            value=default_value or "",
            placeholder=q.get("placeholder", ""),
            label_visibility="collapsed",
        )

    # 라디오 버튼
    elif q_type == "radio":
        options = q["options"]

        # "기타" 옵션 처리
        if q.get("other_option"):
            options = options + [{"value": "other", "label": "기타"}]

        # 기본 선택 인덱스
        if default_value:
            try:
                default_index = [opt["value"] for opt in options].index(default_value)
            except ValueError:
                default_index = 0
        else:
            default_index = 0

        # 버튼 형식으로 표시
        selected = None
        for opt in options:
            is_selected = (default_value == opt["value"])
            button_type = "primary" if is_selected else "secondary"

            if st.button(
                opt["label"],
                key=f"{q_id}_{opt['value']}",
                use_container_width=True,
                type=button_type,
            ):
                selected = opt["value"]
                st.session_state.responses[q_id] = selected
                st.rerun()

            st.markdown("")

        # "기타" 선택 시 텍스트 입력
        if default_value == "other" and q.get("other_option"):
            other_text = st.text_input(
                "기타 내용을 입력해주세요",
                value=st.session_state.responses.get(f"{q_id}_other", ""),
                key=f"{q_id}_other_input",
            )
            st.session_state.responses[f"{q_id}_other"] = other_text

        return default_value

    # 라디오 버튼 (가로 나열)
    elif q_type == "radio_horizontal":
        options = q["options"]

        # "기타" 옵션 처리
        if q.get("other_option"):
            options = options + [{"value": "other", "label": "기타"}]

        # 가로 나열
        num_options = len(options)
        cols = st.columns(num_options)

        for idx, opt in enumerate(options):
            is_selected = (default_value == opt["value"])
            button_type = "primary" if is_selected else "secondary"

            with cols[idx]:
                if st.button(
                    opt["label"],
                    key=f"{q_id}_{opt['value']}",
                    use_container_width=True,
                    type=button_type,
                ):
                    st.session_state.responses[q_id] = opt["value"]
                    st.rerun()

        # "기타" 선택 시 텍스트 입력
        if default_value == "other" and q.get("other_option"):
            other_text = st.text_input(
                "기타 내용을 입력해주세요",
                value=st.session_state.responses.get(f"{q_id}_other", ""),
                key=f"{q_id}_other_input",
            )
            st.session_state.responses[f"{q_id}_other"] = other_text

        return default_value

    # 단일 체크박스
    elif q_type == "checkbox":
        checked_values = default_value if isinstance(default_value, list) else []
        selected = []

        # 버튼 형식으로 표시 (가로 나열)
        num_options = len(q["options"])
        cols = st.columns(num_options)

        for idx, opt in enumerate(q["options"]):
            is_checked = opt["value"] in checked_values
            button_type = "primary" if is_checked else "secondary"

            with cols[idx]:
                if st.button(
                    opt["label"],
                    key=f"{q_id}_{opt['value']}",
                    use_container_width=True,
                    type=button_type,
                ):
                    # 토글 방식
                    if opt["value"] in checked_values:
                        checked_values.remove(opt["value"])
                    else:
                        selected.append(opt["value"])
                    st.session_state.responses[q_id] = checked_values if opt["value"] not in checked_values else checked_values + [opt["value"]]
                    st.rerun()

        return checked_values

    # 복수 선택 체크박스
    elif q_type == "checkbox_multiple":
        checked_values = default_value if isinstance(default_value, list) else []

        # 버튼 형식으로 표시 (가로 나열)
        num_options = len(q["options"])
        if q.get("other_option"):
            num_options += 1

        cols = st.columns(num_options)

        for idx, opt in enumerate(q["options"]):
            is_checked = opt["value"] in checked_values
            button_type = "primary" if is_checked else "secondary"

            with cols[idx]:
                if st.button(
                    opt["label"],
                    key=f"{q_id}_{opt['value']}",
                    use_container_width=True,
                    type=button_type,
                ):
                    # 토글 방식
                    if opt["value"] in checked_values:
                        checked_values.remove(opt["value"])
                    else:
                        checked_values.append(opt["value"])
                    st.session_state.responses[q_id] = checked_values
                    st.rerun()

        # "기타" 옵션 처리
        if q.get("other_option"):
            other_checked = "other" in checked_values
            button_type = "primary" if other_checked else "secondary"

            with cols[num_options - 1]:
                if st.button(
                    "기타",
                    key=f"{q_id}_other_checkbox",
                    use_container_width=True,
                    type=button_type,
                ):
                    # 토글 방식
                    if "other" in checked_values:
                        checked_values.remove("other")
                    else:
                        checked_values.append("other")
                    st.session_state.responses[q_id] = checked_values
                    st.rerun()

        # "기타" 선택 시 텍스트 입력
        if "other" in checked_values:
            other_text = st.text_input(
                "기타 내용을 입력해주세요",
                value=st.session_state.responses.get(f"{q_id}_other", ""),
                key=f"{q_id}_other_input",
            )
            st.session_state.responses[f"{q_id}_other"] = other_text

        return checked_values

    # 체크박스 그리드 (세로 나열, 체크박스 형태)
    elif q_type == "checkbox_grid":
        checked_values = default_value if isinstance(default_value, list) else []

        for opt in q["options"]:
            is_checked = opt["value"] in checked_values
            if st.checkbox(opt["label"], value=is_checked, key=f"{q_id}_{opt['value']}"):
                if opt["value"] not in checked_values:
                    checked_values.append(opt["value"])
            else:
                if opt["value"] in checked_values:
                    checked_values.remove(opt["value"])

        # "기타" 옵션 처리
        if q.get("other_option"):
            other_checked = "other" in checked_values
            if st.checkbox("기타", value=other_checked, key=f"{q_id}_other_checkbox"):
                if "other" not in checked_values:
                    checked_values.append("other")
            else:
                if "other" in checked_values:
                    checked_values.remove("other")

            # "기타" 선택 시 텍스트 입력
            if "other" in checked_values:
                other_text = st.text_input(
                    "기타 내용을 입력해주세요",
                    value=st.session_state.responses.get(f"{q_id}_other", ""),
                    key=f"{q_id}_other_input",
                )
                st.session_state.responses[f"{q_id}_other"] = other_text

        # 세션에 저장
        st.session_state.responses[q_id] = checked_values

        return checked_values

    # 시간 범위 슬라이더
    elif q_type == "time_range":
        default_range = default_value if default_value else [9, 18]

        time_range = st.slider(
            q.get("description", "시간을 선택해주세요"),
            min_value=q.get("min", 0),
            max_value=q.get("max", 24),
            value=tuple(default_range),
            key=f"{q_id}_slider",
        )

        st.caption(f"외출 시간: {time_range[0]}시 ~ {time_range[1]}시")

        return list(time_range)

    # 이미지 업로드
    elif q_type == "image":
        uploaded_file = st.file_uploader(
            q.get("description", "이미지를 업로드해주세요"),
            type=["jpg", "jpeg", "png"],
            key=f"{q_id}_uploader",
        )

        if uploaded_file:
            st.success("✅ 이미지가 업로드되었습니다!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)

        return uploaded_file

    # 미디어 (사진/영상) 업로드
    elif q_type == "media":
        uploaded_file = st.file_uploader(
            q.get("description", "사진 또는 영상을 업로드해주세요"),
            type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
            key=f"{q_id}_uploader",
        )

        if uploaded_file:
            st.success("✅ 파일이 업로드되었습니다!")
            file_type = uploaded_file.type.split("/")[0]

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if file_type == "image":
                    st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)
                else:
                    st.video(uploaded_file)

        return uploaded_file

    return None


# ===== 페이지 0: 랜딩 페이지 =====
def page_landing():
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

    # 마리 이미지 표시 (중앙 정렬)
    mari_image = load_mari_image("Mari_image_normal_1.png")
    if mari_image:
        # 중앙 정렬
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)
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
    questions = get_basic_info_questions()

    st.markdown("## 우리 강아지에 대해 알려주세요")
    st.markdown("<br>", unsafe_allow_html=True)

    show_progress_bar(1, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_1.png")
    if mari_image:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
    questions = get_personality_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 평소 성향을 알려주세요")
    st.markdown("<br>", unsafe_allow_html=True)

    show_progress_bar(2, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_2.png")
    if mari_image:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
    questions = get_behavior_problem_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 문제 행동에 대해 알려주세요")
    st.markdown("<br>", unsafe_allow_html=True)

    show_progress_bar(3, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_3.png")
    if mari_image:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
    questions = get_environment_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 생활 환경을 알려주세요")
    st.markdown("<br>", unsafe_allow_html=True)

    show_progress_bar(4, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_normal_4.png")
    if mari_image:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
    questions = get_photo_questions()
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown(f"## {dog_name}의 사진을 업로드해주세요")
    st.markdown("<br>", unsafe_allow_html=True)

    show_progress_bar(5, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_Answer.png")
    if mari_image:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.image(mari_image, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
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
    # 마리 이미지 애니메이션 CSS
    st.markdown("""
        <style>
        /* 마리 이미지 펄스 애니메이션 */
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }

        /* 마리 이미지 흔들림 애니메이션 */
        @keyframes shake {
            0%, 100% {
                transform: rotate(0deg);
            }
            25% {
                transform: rotate(-5deg);
            }
            75% {
                transform: rotate(5deg);
            }
        }

        /* 분석 중 페이지의 이미지에만 애니메이션 적용 */
        .analyzing-page .stImage > img {
            animation: pulse 2s ease-in-out infinite, shake 3s ease-in-out infinite;
        }

        /* 동적 메시지 페이드인 애니메이션 */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* 깜빡거리는 애니메이션 */
        @keyframes blink {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.3;
            }
        }

        .dynamic-message {
            animation: fadeIn 0.5s ease-in-out;
            font-size: clamp(16px, 4vw, 20px) !important;
            font-weight: bold !important;
            color: #E8826B !important;
            text-align: center !important;
            margin: 20px 0 !important;
        }

        .dynamic-message.blinking {
            animation: fadeIn 0.5s ease-in-out, blink 1s ease-in-out infinite;
        }

        /* 완료 메시지 스타일 */
        .completion-message {
            animation: fadeIn 0.8s ease-in-out;
            font-size: clamp(18px, 5vw, 24px) !important;
            font-weight: bold !important;
            color: #4CAF50 !important;
            text-align: center !important;
            margin: 20px 0 !important;
            text-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="analyzing-page">', unsafe_allow_html=True)

    st.title("🤖 AI 분석 중...")
    show_progress_bar(6, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_in_bag.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, width=300)

    dog_name = st.session_state.responses.get("dog_name", "강아지")

    # 동적 메시지 리스트
    dynamic_messages = [
        f"🐶 {dog_name}의 행동을 꼼꼼히 분석하고 있어요!",
        "🔍 마리가 열심히 생각 중이에요...",
        "💭 전문가 의견을 모으고 있어요!",
        "✨ 맞춤 솔루션을 준비하고 있어요!",
        "⏳ 조금만 기다려주세요, 거의 다 됐어요!",
    ]

    # 동적 메시지 표시 영역
    message_placeholder = st.empty()

    st.markdown("### 분석 진행 중...")

    # 로딩 바
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 실제 AI 분석 수행
    if st.session_state.analysis_result is None:
        try:
            import random

            # 필수 데이터 확인
            dog_photo = st.session_state.get("dog_photo")
            behavior_media = st.session_state.get("behavior_media")

            if dog_photo is None:
                st.error("강아지 사진이 업로드되지 않았습니다.")
                st.markdown('</div>', unsafe_allow_html=True)
                return

            # 이미지를 bytes로 변환 (UploadedFile 객체인 경우)
            if hasattr(dog_photo, 'read'):
                dog_photo_bytes = dog_photo.read()
            else:
                dog_photo_bytes = dog_photo

            behavior_media_bytes = None
            if behavior_media:
                if hasattr(behavior_media, 'read'):
                    behavior_media_bytes = behavior_media.read()
                else:
                    behavior_media_bytes = behavior_media

            # 분석 단계 정의 (동적 프로그레스) - 90%까지만
            analysis_steps = [
                (8, "📋 설문 응답 데이터 처리 중...", 0),
                (12, "📊 응답 패턴 분석 중...", 0),
                (18, "🖼️ 이미지 로딩 중...", 1),
                (25, "🔍 이미지 특징 추출 중...", 1),
                (35, "🤖 1차 AI 전문가 분석 시작...", 2),
                (50, "💭 행동 패턴 분석 중...", 2),
                (65, "🎯 문제 원인 파악 중...", 3),
                (75, "✨ 2차 AI 마리 변환 중...", 3),
                (85, "📝 맞춤 솔루션 생성 중...", 4),
                (90, "✅ 최종 검토 중...", 4),
            ]

            # 단계별 업데이트 (깜빡거리는 효과)
            for progress, status, msg_idx in analysis_steps:
                progress_bar.progress(progress)
                status_text.text(status)

                # 동적 메시지 업데이트 (깜빡거리는 효과 추가)
                message_placeholder.markdown(
                    f'<div class="dynamic-message blinking">{dynamic_messages[msg_idx]}</div>',
                    unsafe_allow_html=True
                )

                # 속도를 늦춤 (0.8초 대기)
                time.sleep(0.8)

            # 2단계 AI 분석 실행 (실제 분석)
            status_text.text("🚀 AI 분석 진행 중...")
            message_placeholder.markdown(
                f'<div class="dynamic-message blinking">💫 마리가 최선을 다하고 있어요!</div>',
                unsafe_allow_html=True
            )

            # 실제 AI 분석 실행
            result = asyncio.run(
                analyze_two_stage(
                    responses=st.session_state.responses,
                    dog_photo=dog_photo_bytes,
                    behavior_media=behavior_media_bytes
                )
            )

            # AI 분석 완료 시그널 받음!
            st.session_state.analysis_result = result

            # 완료 시그널 받은 후 100% + 완료 메시지
            progress_bar.progress(100)
            status_text.text("✅ 분석 완료!")
            message_placeholder.markdown(
                f'<div class="completion-message">🎉 결과가 완료됐어요!</div>',
                unsafe_allow_html=True
            )
            time.sleep(2.0)

            st.markdown('</div>', unsafe_allow_html=True)
            next_page()
            st.rerun()

        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
            st.error("Mock 데이터를 사용합니다.")

            # Mock 데이터로 폴백 (동적 애니메이션 유지)
            dog_name = st.session_state.responses.get("dog_name", "강아지")

            # Mock 모드 프로그레스 (깜빡거리는 효과)
            mock_steps = [
                (15, 0),
                (30, 1),
                (50, 2),
                (70, 3),
                (85, 4),
            ]

            for progress, msg_idx in mock_steps:
                progress_bar.progress(progress)
                message_placeholder.markdown(
                    f'<div class="dynamic-message blinking">{dynamic_messages[msg_idx]}</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.8)

            # 폴백: Mock 데이터
            main_concerns = st.session_state.responses.get("main_concerns", [])
            problem_type = main_concerns[0] if main_concerns else "barking"
            mock_result = get_mock_result_by_problem(problem_type)

            # Mock 데이터를 새 형식으로 변환
            st.session_state.analysis_result = {
                "final_text": f"""**"{dog_name}의 행동 분석 결과예요!"**

{mock_result.get('behavior_summary', '')}

---

{mock_result.get('expert_opinion', '')}

---

## 맞춤 훈련 플랜

""" + "\n\n".join([f"**{i+1}. {step}**" for i, step in enumerate(mock_result.get('action_plan', []))]),
                "confidence_score": mock_result.get("confidence_score", 0.5),
                "raw_json": {}
            }

            # Mock 데이터 완료 시그널
            progress_bar.progress(100)
            status_text.text("✅ 분석 완료!")
            message_placeholder.markdown(
                f'<div class="completion-message">🎉 결과가 완료됐어요!</div>',
                unsafe_allow_html=True
            )
            time.sleep(2.0)

            st.markdown('</div>', unsafe_allow_html=True)
            next_page()
            st.rerun()


# ===== 페이지 7: 분석 결과 =====
def page_result():
    st.title("📊 분석 결과")
    show_progress_bar(7, 7)

    result = st.session_state.analysis_result
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    if result:
        st.success(f"✅ {dog_name}의 행동 분석이 완료되었습니다!")

        # 신뢰도 점수
        confidence = result.get("confidence_score", 0.8)
        st.metric("분석 신뢰도", f"{int(confidence * 100)}%")

        st.markdown("---")

        # 강아지 이미지 표시
        dog_photo = st.session_state.get("dog_photo")
        if dog_photo:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(dog_photo, caption=f"{dog_name}의 사진", use_container_width=True)
            st.markdown("---")

        # 마리의 최종 분석 결과 (Markdown 전체)
        final_text = result.get("final_text", "")
        if final_text:
            st.markdown(final_text)
        else:
            # 하위 호환성: 구 형식 지원
            st.markdown("## 📝 행동 분석 요약")
            st.markdown(result.get("behavior_summary", ""))

            st.markdown("---")

            st.markdown("## 👨‍⚕️ 전문가 의견")
            st.markdown(result.get("expert_opinion", ""))

            st.markdown("---")

            st.markdown("## 🎯 맞춤 훈련 플랜")
            action_plan = result.get("action_plan", [])
            for i, step in enumerate(action_plan, 1):
                with st.expander(f"단계 {i}", expanded=(i == 1)):
                    st.markdown(step)

            st.markdown("---")

            if result.get("additional_notes"):
                st.warning(f"⚠️ {result['additional_notes']}")

        st.markdown("---")

        # 공유 버튼 (UI만)
        st.markdown("### 📤 결과 공유")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("📸 인스타그램 공유", use_container_width=True)
        with col2:
            st.button("📧 이메일 전송", use_container_width=True)
        with col3:
            st.button("💾 PDF 저장", use_container_width=True)

        st.markdown("---")

        # 새로운 분석 시작 버튼 (네비게이션 스타일)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("새로운 분석 시작", key="nav_restart", use_container_width=True, type="primary"):
                # 세션 초기화
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
