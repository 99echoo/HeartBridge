"""
분석 결과를 카드형 UI로 렌더링하는 컴포넌트 모음.
"""

from __future__ import annotations

from typing import Dict, List

import streamlit as st


def render_summary_card(summary: Dict[str, str], dog_name: str) -> None:
    """핵심 진단 카드."""
    core_issue = summary.get("core_issue", "핵심 이슈 정보가 부족해요.")
    root_cause = summary.get("root_cause", "")
    characteristics = summary.get("key_characteristics", [])

    st.markdown(
        f"""
        <div class="result-card emphasis-card">
            <p class="card-eyebrow">핵심 진단</p>
            <h3>{dog_name}에게 가장 중요한 한 가지</h3>
            <p class="card-highlight">{core_issue}</p>
            <p class="card-caption">{root_cause}</p>
            <ul>
                {''.join(f'<li>{item}</li>' for item in characteristics)}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_solutions(solutions: List[Dict[str, str]]) -> None:
    """맞춤 솔루션 카드 리스트 (세로)."""
    st.markdown("### 🧩 맞춤 솔루션 3가지")
    for idx, sol in enumerate(solutions, start=1):
        st.markdown(
            f"""
            <div class="result-card solution-card">
                <p class="card-eyebrow">솔루션 {idx}</p>
                <h4>{sol.get('title', '솔루션')}</h4>
                <p>{sol.get('content', '')}</p>
                <ul>
                    {''.join(f'<li>{detail}</li>' for detail in sol.get('details', []))}
                </ul>
                <div class="card-badge">{sol.get('expected_outcome', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_guidance(guidance: List[Dict[str, str]]) -> None:
    """앞으로의 가이드 섹션."""
    st.markdown("### 🌱 앞으로 이렇게 해보세요")
    for guide in guidance:
        st.markdown(
            f"""
            <div class="guidance-item">
                <div class="guidance-title">{guide.get('principle', '')}</div>
                <p>{guide.get('content', '')}</p>
                <div class="guidance-action">➡ {guide.get('action', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_core_message(message: str | None) -> None:
    if not message:
        return
    st.markdown(
        f"""
        <div class="core-message-card">
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_confidence_badge(score: float | None) -> None:
    if score is None:
        return
    pct = int(score * 100)
    st.markdown(
        f"""
        <div class="confidence-badge">
            신뢰도 <span>{pct}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mari_story(story: dict | str | None) -> None:
    if not story:
        return

    if isinstance(story, str):
        st.markdown(
            f"""
            <div class="result-card mari-card">
                {story}
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    header = story.get("header", {})
    closing = story.get("mari_closing", {})
    st.markdown(
        f"""
        <div class="result-card mari-card">
            <h4>{header.get('title', '마리의 이야기')}</h4>
            <p>{header.get('summary', '')}</p>
            <div class="mari-core-message">{closing.get('core_message', '')}</div>
            <div class="mari-final-quote">{closing.get('final_quote', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
