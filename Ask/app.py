"""
파일명: app.py
목적: HeartBridge Ask - AI 기반 반려견 행동 분석 Streamlit 앱
작성일: 2025-01-26
"""

import streamlit as st
import time
from pathlib import Path

# 설정 파일 임포트
from config.survey_questions import (
    get_basic_info_fields,
    get_behavior_survey_questions,
)
from src.utils.mock_data import get_mock_result_by_problem

# 페이지 설정
st.set_page_config(
    page_title="HeartBridge Ask - 반려견 행동 분석",
    page_icon="🐶",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 세션 스테이트 초기화
if "page" not in st.session_state:
    st.session_state.page = 0
if "basic_info" not in st.session_state:
    st.session_state.basic_info = {}
if "survey_responses" not in st.session_state:
    st.session_state.survey_responses = {}
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# 헬퍼 함수
def next_page():
    """다음 페이지로 이동"""
    st.session_state.page += 1


def prev_page():
    """이전 페이지로 이동"""
    if st.session_state.page > 0:
        st.session_state.page -= 1


def show_progress_bar(step, total=5):
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


# ===== 페이지 1: 랜딩 페이지 =====
def page_landing():
    st.title("🐾 HeartBridge Ask")
    st.subheader("AI와 함께하는 반려견 행동 분석")

    # 마리 이미지 표시
    mari_image = load_mari_image("Mari_image_normal_1.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, caption="안녕하세요! 저는 마리예요 🐶", width=300)

    st.markdown("---")

    st.markdown(
        """
    ### 🤔 이런 고민 있으신가요?

    - 🔊 우리 강아지가 너무 짖어요
    - 😭 혼자 두면 울고 물건을 파괴해요
    - 😠 다른 사람이나 강아지에게 공격적이에요
    - 🚽 배변 훈련이 잘 안돼요

    ### ✨ HeartBridge Ask가 도와드릴게요!

    1. 📋 **간단한 설문** - 5분이면 충분해요
    2. 📸 **사진 업로드** - 우리 강아지 모습을 보여주세요
    3. 🤖 **AI 분석** - 전문가 수준의 행동 분석
    4. 📊 **맞춤 솔루션** - 단계별 훈련 플랜 제공

    """
    )

    st.markdown("---")

    if st.button("🚀 시작하기", use_container_width=True, type="primary"):
        next_page()


# ===== 페이지 2: 기본 정보 입력 =====
def page_basic_info():
    st.title("📝 기본 정보 입력")
    show_progress_bar(1, 5)

    st.markdown("### 우리 강아지에 대해 알려주세요")

    fields = get_basic_info_fields()

    # 강아지 이름
    dog_name = st.text_input(
        "🐶 강아지 이름",
        value=st.session_state.basic_info.get("dog_name", ""),
        placeholder="예: 마리",
    )

    # 이메일 (선택)
    owner_email = st.text_input(
        "📧 이메일 (선택사항)",
        value=st.session_state.basic_info.get("owner_email", ""),
        placeholder="결과를 이메일로 받고 싶으시면 입력해주세요",
    )

    # 강아지 나이
    st.markdown("### 🎂 강아지 나이")
    age_options = fields[2]["options"]
    dog_age = st.radio(
        "나이를 선택해주세요",
        options=[opt["value"] for opt in age_options],
        format_func=lambda x: next(opt["label"] for opt in age_options if opt["value"] == x),
        index=0
        if "dog_age" not in st.session_state.basic_info
        else [opt["value"] for opt in age_options].index(st.session_state.basic_info["dog_age"]),
        horizontal=True,
    )

    # 강아지 크기
    st.markdown("### 📏 강아지 크기")
    size_options = fields[3]["options"]
    dog_size = st.radio(
        "크기를 선택해주세요",
        options=[opt["value"] for opt in size_options],
        format_func=lambda x: next(opt["label"] for opt in size_options if opt["value"] == x),
        index=0
        if "dog_size" not in st.session_state.basic_info
        else [opt["value"] for opt in size_options].index(st.session_state.basic_info["dog_size"]),
        horizontal=True,
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            prev_page()
    with col2:
        if st.button("다음 ➡️", use_container_width=True, type="primary"):
            if dog_name.strip():
                st.session_state.basic_info = {
                    "dog_name": dog_name,
                    "owner_email": owner_email,
                    "dog_age": dog_age,
                    "dog_size": dog_size,
                }
                next_page()
            else:
                st.error("강아지 이름을 입력해주세요!")


# ===== 페이지 3: 행동 분석 설문 =====
def page_survey():
    st.title("🔍 행동 분석 설문")
    show_progress_bar(2, 5)

    # 마리 질문 이미지
    mari_image = load_mari_image("Mari_image_Question.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, width=200)

    st.markdown(f"### {st.session_state.basic_info.get('dog_name', '강아지')}의 행동에 대해 알려주세요")

    questions = get_behavior_survey_questions()

    responses = {}

    for q in questions:
        st.markdown(f"### {q['question']}")
        if q.get("description"):
            st.caption(q["description"])

        response = st.radio(
            f"질문 {q['id']}",
            options=[opt["value"] for opt in q["options"]],
            format_func=lambda x, opts=q["options"]: next(
                f"{opt['label']} - {opt['description']}" for opt in opts if opt["value"] == x
            ),
            index=0
            if q["id"] not in st.session_state.survey_responses
            else [opt["value"] for opt in q["options"]].index(
                st.session_state.survey_responses[q["id"]]
            ),
            key=q["id"],
            label_visibility="collapsed",
        )
        responses[q["id"]] = response

        st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            prev_page()
    with col2:
        if st.button("다음 ➡️", use_container_width=True, type="primary"):
            st.session_state.survey_responses = responses
            next_page()


# ===== 페이지 4: 이미지 업로드 =====
def page_image_upload():
    st.title("📸 사진 업로드")
    show_progress_bar(3, 5)

    st.markdown(f"### {st.session_state.basic_info.get('dog_name', '강아지')}의 사진을 업로드해주세요")
    st.caption("문제 행동을 보이는 상황의 사진이면 더 좋아요!")

    uploaded_file = st.file_uploader(
        "이미지 업로드 (JPG, PNG, 최대 5MB)",
        type=["jpg", "jpeg", "png"],
        help="드래그 앤 드롭 또는 클릭해서 업로드하세요",
    )

    if uploaded_file is not None:
        st.success("✅ 이미지가 업로드되었습니다!")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)
        st.session_state.uploaded_image = uploaded_file

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            prev_page()
    with col2:
        if st.button("분석 시작 🚀", use_container_width=True, type="primary"):
            if uploaded_file is not None or st.session_state.uploaded_image is not None:
                next_page()
            else:
                st.error("이미지를 업로드해주세요!")


# ===== 페이지 5: AI 분석 중 =====
def page_analyzing():
    st.title("🤖 AI 분석 중...")
    show_progress_bar(4, 5)

    # 마리 이미지
    mari_image = load_mari_image("Mari_image_in_bag.png")
    if mari_image:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(mari_image, width=300)

    st.markdown("### 잠시만 기다려주세요!")
    st.info(
        f"""
    🔍 {st.session_state.basic_info.get('dog_name', '강아지')}의 행동을 분석하고 있어요...

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
        problem_type = st.session_state.survey_responses.get("q1", "barking")
        st.session_state.analysis_result = get_mock_result_by_problem(problem_type)

        status_text.text("✅ 분석 완료!")
        time.sleep(1)
        next_page()
        st.rerun()


# ===== 페이지 6: 분석 결과 =====
def page_result():
    st.title("📊 분석 결과")
    show_progress_bar(5, 5)

    result = st.session_state.analysis_result

    if result:
        st.success(f"✅ {st.session_state.basic_info.get('dog_name', '강아지')}의 행동 분석이 완료되었습니다!")

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
            st.session_state.basic_info = {}
            st.session_state.survey_responses = {}
            st.session_state.uploaded_image = None
            st.session_state.analysis_result = None
            st.rerun()


# ===== 메인 앱 =====
def main():
    # 페이지 라우팅
    pages = [
        page_landing,
        page_basic_info,
        page_survey,
        page_image_upload,
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
