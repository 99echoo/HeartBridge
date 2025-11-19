"""
세션 상태 및 페이지 네비게이션 헬퍼.
"""

from __future__ import annotations

import streamlit as st


def initialize_session_state() -> None:
    """Streamlit 세션 스테이트 기본값 설정."""
    default_values = {
        "page": 0,
        "responses": {},
        "dog_photo": None,
        "behavior_media": None,
        "analysis_result": None,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def next_page() -> None:
    """다음 페이지로 이동."""
    st.session_state.page += 1
    st.rerun()


def prev_page() -> None:
    """이전 페이지로 이동."""
    if st.session_state.page > 0:
        st.session_state.page -= 1
        st.rerun()
