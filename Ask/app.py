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

import streamlit as st
import streamlit.components.v1 as components
import time
import asyncio
import base64
from pathlib import Path
from PIL import Image, ImageOps
import io

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
from src.ai.analyzer_factory import get_analyzer
from src.utils.csv_logger import save_to_csv

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
            padding-top: 2rem !important;
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
        font-size: clamp(16px, 4vw, 18px) !important;
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
        margin-top: clamp(20px, 5vw, 40px) !important;
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
        margin-bottom: clamp(5px, 1vw, 8px) !important;
    }

    /* 랜딩 페이지 이미지 여백 축소 */
    .landing-page .stImage {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* 랜딩 페이지 버튼 컨테이너 여백 축소 */
    .landing-page .nav-button-container {
        margin-top: clamp(5px, 1vw, 10px) !important;
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
            margin-bottom: 5px !important;
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

    /* 모바일/태블릿 이미지 최대 크기 제한 제거 (width 파라미터 사용) */

    /* 섹션 제목 반응형 */
    h1, .stMarkdown h1 {
        font-size: clamp(24px, 6vw, 32px) !important;
    }

    h2, .stMarkdown h2 {
        font-size: clamp(20px, 5vw, 28px) !important;
        margin-top: clamp(15px, 4vw, 30px) !important;
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

    /* 구분선(hr) 마진 축소 - 질문 사이 간격 줄이기 */
    hr {
        margin: 8px 0 !important;
        border: none !important;
        border-bottom: 1px solid #e0e0e0 !important;
    }

    /* Selectbox 스타일 (다크모드 대응) */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }

    .stSelectbox label {
        color: #333333 !important;
        font-weight: 500 !important;
    }

    /* Selectbox 드롭다운 메뉴 */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #333333 !important;
    }

    /* Selectbox 드롭다운 팝업 (listbox) */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="popover"] ul {
        background-color: #ffffff !important;
    }

    /* Selectbox 옵션 항목 */
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #333333 !important;
    }

    .stSelectbox [role="option"]:hover {
        background-color: #f5f5f5 !important;
    }

    /* 드롭다운 리스트 전체 */
    [role="listbox"] {
        background-color: #ffffff !important;
    }

    [role="listbox"] li {
        background-color: #ffffff !important;
        color: #333333 !important;
    }

    [role="listbox"] li:hover {
        background-color: #f5f5f5 !important;
    }

    /* 이미지 중앙 정렬 */
    .stImage {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 페이지 제목 (h2) 중앙 정렬 - 여러 선택자 사용 */
    h2 {
        text-align: center !important;
    }

    .main h2 {
        text-align: center !important;
    }

    .stMarkdown h2 {
        text-align: center !important;
    }

    [data-testid="stMarkdown"] h2 {
        text-align: center !important;
    }

    .main .stMarkdown h2 {
        text-align: center !important;
    }

    /* 파일 업로더 스타일 개선 (다크모드 대응) */
    [data-testid="stFileUploader"] {
        background-color: #FFEAE6 !important;
        border: 2px dashed #E8826B !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    [data-testid="stFileUploader"] label {
        color: #E8826B !important;
        font-weight: bold !important;
    }

    /* 파일 업로더 내부 텍스트 (다크모드 대응) */
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] div {
        color: #333333 !important;
    }

    /* 파일 업로더 드래그 영역 */
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border-color: #E8826B !important;
    }

    /* 파일 업로더 버튼 */
    [data-testid="stFileUploader"] button {
        background-color: #E8826B !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: #D67159 !important;
    }

    /* 파일 업로더 아이콘 색상 */
    [data-testid="stFileUploader"] svg {
        fill: #E8826B !important;
    }

    /* 체크박스 스타일 (다크모드 대응) */
    .stCheckbox {
        background-color: transparent !important;
    }

    /* 체크박스 라벨 텍스트 - 검정색 */
    .stCheckbox label {
        color: #333333 !important;
        font-weight: 500 !important;
    }

    /* 체크박스 라벨 내부 span - 검정색 */
    .stCheckbox label span {
        color: #333333 !important;
    }

    /* 체크박스 input 컨테이너 */
    .stCheckbox > label > div {
        background-color: transparent !important;
    }

    /* 체크박스 input - 내부 흰색 */
    .stCheckbox input[type="checkbox"] {
        background-color: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
    }

    /* 체크박스 전체 div */
    [data-testid="stCheckbox"] {
        background-color: transparent !important;
    }

    /* 체크박스 라벨 (data-testid 사용) - 검정색 */
    [data-testid="stCheckbox"] label {
        color: #333333 !important;
    }

    /* 체크박스 라벨 내부 모든 텍스트 - 검정색 */
    [data-testid="stCheckbox"] label p,
    [data-testid="stCheckbox"] label span,
    [data-testid="stCheckbox"] label div {
        color: #333333 !important;
    }

    /* 체크박스 위젯 전체 배경 */
    [data-baseweb="checkbox"] {
        background-color: transparent !important;
    }

    /* 체크박스 체크마크 배경 - 내부 흰색 */
    [data-baseweb="checkbox"] > div {
        background-color: #ffffff !important;
        border-color: #e0e0e0 !important;
    }

    /* 체크 시 내부도 흰색 유지 */
    [data-baseweb="checkbox"] input:checked + div {
        background-color: #ffffff !important;
        border-color: #e0e0e0 !important;
    }

    /* 체크박스 포커스 시 outline 제거 (산호색 테두리 제거) */
    .stCheckbox input[type="checkbox"]:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    [data-baseweb="checkbox"] input:focus + div {
        outline: none !important;
        box-shadow: none !important;
    }

    /* 체크박스 체크마크 색상 */
    [data-baseweb="checkbox"] svg {
        fill: #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 페이지 전환 시 스크롤 맨 위로 이동
st.markdown("""
    <script>
    // 페이지 로드 시 스크롤을 맨 위로
    window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
""", unsafe_allow_html=True)


# 헬퍼 함수
def scroll_to_top():
    """페이지 스크롤을 맨 위로 이동"""
    components.html("""
        <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """, height=0)


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
    # 현재 스크립트의 디렉토리를 기준으로 절대 경로 설정
    script_dir = Path(__file__).parent
    image_path = script_dir / "assets" / "images" / image_name
    if image_path.exists():
        return str(image_path)
    return None


def get_image_base64(image_path):
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def fix_image_orientation(image_file):
    """
    EXIF orientation 메타데이터를 처리하여 이미지를 올바르게 회전합니다.

    Args:
        image_file: Streamlit UploadedFile 객체 또는 bytes

    Returns:
        PIL.Image: EXIF orientation이 처리된 이미지 (실패 시 None)
    """
    if image_file is None:
        return None

    image_bytes = None

    try:
        # UploadedFile 객체인 경우 읽기
        if hasattr(image_file, 'read'):
            # 현재 파일 포인터 위치 저장
            if hasattr(image_file, 'tell'):
                original_position = image_file.tell()
            else:
                original_position = 0

            # 처음으로 이동
            if hasattr(image_file, 'seek'):
                image_file.seek(0)

            image_bytes = image_file.read()

            # 원래 위치로 복원
            if hasattr(image_file, 'seek'):
                image_file.seek(original_position)
        else:
            image_bytes = image_file

        # 빈 bytes 체크
        if not image_bytes or len(image_bytes) == 0:
            return None

        # PIL Image로 열기
        image = Image.open(io.BytesIO(image_bytes))

        # EXIF orientation 자동 처리
        # 이 함수는 EXIF 메타데이터를 읽고 필요한 경우 이미지를 회전시킴
        # exif_transpose가 None을 반환하면 원본 이미지 반환
        rotated_image = ImageOps.exif_transpose(image)
        return rotated_image if rotated_image is not None else image

    except Exception as e:
        # EXIF 처리 실패 시 원본 이미지 로드 시도
        try:
            if image_bytes and len(image_bytes) > 0:
                return Image.open(io.BytesIO(image_bytes))
        except:
            pass

        # 모든 시도 실패
        return None


def convert_image_to_bytes(image):
    """
    PIL Image를 bytes로 변환합니다.

    Args:
        image: PIL.Image 객체 (None 가능)

    Returns:
        bytes: JPEG 형식의 이미지 바이트 (실패 시 None)
    """
    if image is None:
        return None

    try:
        buffer = io.BytesIO()

        # RGB 모드로 변환 (RGBA나 다른 모드일 경우 JPEG 저장 오류 방지)
        if image.mode in ('RGBA', 'LA', 'P'):
            # 투명 배경을 흰색으로 변환
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # JPEG로 저장
        image.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)

        image_bytes = buffer.read()

        # 빈 bytes 체크
        if not image_bytes or len(image_bytes) == 0:
            return None

        return image_bytes

    except Exception as e:
        # 변환 실패
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

    # 연/월 셀렉트박스
    elif q_type == "select_year_month":
        # 기본값 처리
        if isinstance(default_value, dict):
            default_year = default_value.get("year", "2020")
            default_month = default_value.get("month", "1")
        else:
            default_year = "2020"
            default_month = "1"

        col1, col2 = st.columns(2)

        with col1:
            # 2010년부터 2024년까지 + "모름" 옵션
            year_options = list(range(2024, 2009, -1)) + ["모름"]

            # 기본 인덱스 찾기
            try:
                if default_year == "모름":
                    year_index = year_options.index("모름")
                else:
                    year_index = year_options.index(int(default_year))
            except (ValueError, TypeError):
                year_index = 0

            year = st.selectbox(
                "년도",
                options=year_options,
                index=year_index,
                key=f"{q_id}_year"
            )

        with col2:
            # 1월부터 12월까지 + "모름" 옵션
            month_options = list(range(1, 13)) + ["모름"]

            # 기본 인덱스 찾기
            try:
                if default_month == "모름":
                    month_index = month_options.index("모름")
                else:
                    month_index = month_options.index(int(default_month))
            except (ValueError, TypeError):
                month_index = 0

            month = st.selectbox(
                "월",
                options=month_options,
                index=month_index,
                key=f"{q_id}_month"
            )

        # 딕셔너리로 반환
        return {"year": str(year), "month": str(month)}

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
                # EXIF orientation 처리
                fixed_image = fix_image_orientation(uploaded_file)
                if fixed_image:
                    st.image(fixed_image, caption="업로드된 이미지", use_container_width=True)
                else:
                    st.error("이미지를 표시할 수 없습니다. 다른 이미지를 업로드해주세요.")

        return uploaded_file

    # 미디어 (사진/영상) 업로드 - 준비 중
    elif q_type == "media":
        # Browse files 버튼을 "준비중이에요!"로 변경하는 CSS
        st.markdown("""
            <style>
            /* 파일 업로더 버튼 텍스트 "Browse files"를 "준비중이에요!"로 변경 */
            [data-testid="stFileUploader"]:has(button:disabled) button span {
                visibility: hidden;
                position: relative;
            }
            [data-testid="stFileUploader"]:has(button:disabled) button span::after {
                content: "준비중이에요! 🚧";
                visibility: visible;
                position: absolute;
                left: 0;
                top: 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # 비활성화된 파일 업로더
        uploaded_file = st.file_uploader(
            q.get("description", "사진 또는 영상을 업로드해주세요"),
            type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
            key=f"{q_id}_uploader",
            disabled=True  # 비활성화
        )

        return None  # 준비 중이므로 None 반환

    return None


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

    st.title("AI 분석 중...")

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
            # EXIF orientation을 처리하여 올바른 방향으로 변환
            fixed_dog_photo = fix_image_orientation(dog_photo)
            dog_photo_bytes = convert_image_to_bytes(fixed_dog_photo)

            # 이미지 처리 실패 체크
            if dog_photo_bytes is None:
                st.error("이미지 처리 중 오류가 발생했습니다. 다른 이미지를 업로드해주세요.")
                st.markdown('</div>', unsafe_allow_html=True)
                return

            behavior_media_bytes = None
            if behavior_media:
                fixed_behavior_media = fix_image_orientation(behavior_media)
                behavior_media_bytes = convert_image_to_bytes(fixed_behavior_media)

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

                # 속도를 늦춤 (3초 대기)
                time.sleep(3.0)

            # 2단계 AI 분석 실행 (실제 분석)
            status_text.text("🚀 AI 분석 진행 중...")
            message_placeholder.markdown(
                f'<div class="dynamic-message blinking">💫 마리가 최선을 다하고 있어요!</div>',
                unsafe_allow_html=True
            )

            # 실제 AI 분석 실행 (Factory 패턴으로 analyzer 선택)
            analyze_two_stage = get_analyzer()
            result = asyncio.run(
                analyze_two_stage(
                    responses=st.session_state.responses,
                    dog_photo=dog_photo_bytes,
                    behavior_media=behavior_media_bytes
                )
            )

            # AI 분석 완료 시그널 받음!
            st.session_state.analysis_result = result

            # CSV 저장
            try:
                csv_path = save_to_csv(
                    responses=st.session_state.responses,
                    analysis_result=result
                )
                print(f"CSV 저장 완료: {csv_path}")
            except Exception as csv_error:
                print(f"CSV 저장 실패: {str(csv_error)}")

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
                time.sleep(3.0)

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

            # CSV 저장 (Mock 데이터)
            try:
                csv_path = save_to_csv(
                    responses=st.session_state.responses,
                    analysis_result=st.session_state.analysis_result
                )
                print(f"CSV 저장 완료 (Mock): {csv_path}")
            except Exception as csv_error:
                print(f"CSV 저장 실패 (Mock): {str(csv_error)}")

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
    scroll_to_top()

    st.title("분석 결과")

    result = st.session_state.analysis_result
    dog_name = st.session_state.responses.get("dog_name", "강아지")

    if result:
        # 분석 완료 메시지 (중앙 정렬, 검은색 텍스트)
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <p style='color: #333333; font-size: clamp(16px, 4vw, 20px); font-weight: bold; margin: 0;'>
                    {dog_name}의 행동 분석이 완료되었습니다!
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 강아지 이미지 표시
        dog_photo = st.session_state.get("dog_photo")
        if dog_photo:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # EXIF orientation 처리
                fixed_image = fix_image_orientation(dog_photo)
                if fixed_image:
                    st.image(fixed_image, caption=f"{dog_name}의 사진", use_container_width=True)
            st.markdown("---")

        # 마리의 최종 분석 결과 (Markdown 전체)
        final_text = result.get("final_text", "")
        if final_text:
            st.markdown(final_text)
        else:
            # 하위 호환성: 구 형식 지원
            st.markdown("## 행동 분석 요약")
            st.markdown(result.get("behavior_summary", ""))

            st.markdown("---")

            st.markdown("## 전문가 의견")
            st.markdown(result.get("expert_opinion", ""))

            st.markdown("---")

            st.markdown("## 맞춤 훈련 플랜")
            action_plan = result.get("action_plan", [])
            for i, step in enumerate(action_plan, 1):
                with st.expander(f"단계 {i}", expanded=(i == 1)):
                    st.markdown(step)

            st.markdown("---")

            if result.get("additional_notes"):
                st.warning(f"{result['additional_notes']}")

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
