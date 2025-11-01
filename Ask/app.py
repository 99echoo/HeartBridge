"""
파일명: app.py
목적: HeartBridge Ask - AI 기반 반려견 행동 분석 Streamlit 앱
작성일: 2025-01-26
수정일: 2025-01-26 - 5개 섹션 구조로 재작성
"""

import streamlit as st
import time
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

    /* 텍스트 색상 강제 */
    .stMarkdown, p, span, div {
        color: #333333 !important;
    }

    /* 텍스트 입력 필드 테두리 스타일 */
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
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

    /* 랜딩 페이지 스타일 */
    .landing-title {
        font-size: 56px !important;
        font-weight: bold !important;
        color: #E8826B !important;
        text-align: center !important;
        margin-top: 20px !important;
        margin-bottom: 25px !important;
    }

    .landing-subtitle {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #333333 !important;
        text-align: center !important;
        line-height: 1.8 !important;
        margin-bottom: 10px !important;
    }

    .landing-description {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #666666 !important;
        text-align: center !important;
        line-height: 1.8 !important;
        margin-bottom: 15px !important;
    }

    /* 버튼 스타일 - 산호색 (질문 답변용) */
    .stButton > button {
        background-color: #E8826B !important;
        color: #333333 !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 15px 30px !important;
        font-size: 18px !important;
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

    /* 네비게이션 버튼 스타일 - 더 높은 우선순위로 재정의 */
    div[data-testid="column"] .nav-button-container button[data-testid="baseButton-primary"],
    div[data-testid="column"] .nav-button-container button[data-testid="baseButton-secondary"],
    .nav-button-container button[data-testid="baseButton-primary"],
    .nav-button-container button[data-testid="baseButton-secondary"] {
        background-color: #E8826B !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="column"] .nav-button-container button[data-testid="baseButton-primary"]:hover,
    div[data-testid="column"] .nav-button-container button[data-testid="baseButton-secondary"]:hover,
    .nav-button-container button[data-testid="baseButton-primary"]:hover,
    .nav-button-container button[data-testid="baseButton-secondary"]:hover {
        background-color: #D67159 !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="column"] .nav-button-container button p,
    .nav-button-container button p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* 랜딩 페이지의 네비게이션 버튼도 흰색 텍스트 유지 */
    .landing-page .nav-button-container button p {
        color: #ffffff !important;
    }

    /* 이미지 중앙 정렬 */
    .stImage {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .stImage > img {
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
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


def prev_page():
    """이전 페이지로 이동"""
    if st.session_state.page > 0:
        st.session_state.page -= 1


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

    # 여백
    st.markdown("<br>", unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)

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
        if st.button("마리에게 물어보기", use_container_width=True, type="primary"):
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
        if st.button("이전", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", use_container_width=True, type="primary"):
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
        if st.button("이전", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", use_container_width=True, type="primary"):
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
        if st.button("이전", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", use_container_width=True, type="primary"):
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
        if st.button("이전", use_container_width=True):
            prev_page()
    with col2:
        # 필수 필드 검증 (선택 항목 제외)
        required_fields = [q["id"] for q in questions if q.get("required", False)]
        all_filled = all(
            st.session_state.responses.get(field) for field in required_fields
        )

        if all_filled:
            if st.button("다음", use_container_width=True, type="primary"):
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
        if st.button("이전", use_container_width=True):
            prev_page()
    with col2:
        # dog_photo는 필수
        if st.session_state.dog_photo is not None:
            if st.button("분석 시작 🚀", use_container_width=True, type="primary"):
                next_page()
        else:
            st.button("반려견 사진을 업로드해주세요", use_container_width=True, disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ===== 페이지 6: AI 분석 중 =====
def page_analyzing():
    st.title("🤖 AI 분석 중...")
    show_progress_bar(6, 7)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_in_bag.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, width=300)

    dog_name = st.session_state.responses.get("dog_name", "강아지")

    st.markdown("### 잠시만 기다려주세요!")
    st.info(
        f"""
    🔍 {dog_name}의 행동을 분석하고 있어요...

    - 설문 응답 분석 중
    - 이미지 분석 중
    - 전문가 의견 취합 중
    - 맞춤 솔루션 생성 중
    """
    )

    # 로딩 바
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Mock 분석 수행
    if st.session_state.analysis_result is None:
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 25:
                status_text.text("설문 응답 분석 중...")
            elif i < 50:
                status_text.text("이미지 분석 중...")
            elif i < 75:
                status_text.text("전문가 의견 취합 중...")
            else:
                status_text.text("맞춤 솔루션 생성 중...")
            time.sleep(0.03)

        # Mock 데이터 가져오기
        main_concerns = st.session_state.responses.get("main_concerns", [])
        problem_type = main_concerns[0] if main_concerns else "barking"
        st.session_state.analysis_result = get_mock_result_by_problem(problem_type)

        status_text.text("✅ 분석 완료!")
        time.sleep(1)
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

        # 행동 요약
        st.markdown("## 📝 행동 분석 요약")
        st.markdown(result.get("behavior_summary", ""))

        st.markdown("---")

        # 전문가 의견
        st.markdown("## 👨‍⚕️ 전문가 의견")
        st.markdown(result.get("expert_opinion", ""))

        st.markdown("---")

        # 액션 플랜
        st.markdown("## 🎯 맞춤 훈련 플랜")
        action_plan = result.get("action_plan", [])
        for i, step in enumerate(action_plan, 1):
            with st.expander(f"단계 {i}", expanded=(i == 1)):
                st.markdown(step)

        st.markdown("---")

        # 추가 노트
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

        if st.button("🔄 새로운 분석 시작", use_container_width=True, type="primary"):
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
