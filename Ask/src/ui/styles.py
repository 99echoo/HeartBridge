"""
스타일 관련 헬퍼.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st


def inject_base_styles() -> None:
    """assets/styles/app.css 내용을 Streamlit에 삽입."""
    assets_root = Path(__file__).resolve().parents[2] / "assets" / "styles"
    css_path = assets_root / "app.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
