"""
분석 결과를 카드형 UI로 렌더링하는 컴포넌트 모음.
"""

from __future__ import annotations

from typing import Dict, List
import html

import streamlit as st


def render_summary_card(summary: Dict[str, str], dog_name: str) -> None:
    """핵심 진단 카드."""
    root_cause = summary.get("root_cause", "")
    characteristics = summary.get("key_characteristics", [])

    # HTML 태그 이스케이프 처리
    root_cause_escaped = html.escape(root_cause)
    characteristics_escaped = [html.escape(str(item)) for item in characteristics]

    st.markdown(
        f"""
        <div class="result-card emphasis-card">
            <p class="card-caption">{root_cause_escaped}</p>
            <ul>
                {''.join(f'<li>{item}</li>' for item in characteristics_escaped)}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_solutions(solutions: List[Dict[str, str]]) -> None:
    """맞춤 솔루션 카드 리스트 (세로)."""
    st.markdown("### 🧩 맞춤 솔루션 2가지")
    for idx, sol in enumerate(solutions[:2], start=1):
        # HTML 태그 이스케이프 처리
        title = html.escape(sol.get('title', '솔루션'))
        content = html.escape(sol.get('content', ''))
        details = [html.escape(str(d)) for d in sol.get('details', [])]

        st.markdown(
            f"""
            <div class="result-card solution-card">
                <h4>{title}</h4>
                <p>{content}</p>
                <ul>
                    {''.join(f'<li>{detail}</li>' for detail in details)}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_guidance(guidance: List[Dict[str, str]]) -> None:
    """앞으로의 가이드 섹션."""
    st.markdown("### 🌱 앞으로 이렇게 해보세요")
    for guide in guidance:
        # HTML 태그 이스케이프 처리
        principle = html.escape(guide.get('principle', ''))
        content = html.escape(guide.get('content', ''))

        st.markdown(
            f"""
            <div class="guidance-item">
                <div class="guidance-title">{principle}</div>
                <p>{content}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_core_message(message: str | None) -> None:
    if not message:
        return
    st.markdown("### 💛 마리의 한마디")
    # HTML 태그 이스케이프 처리
    message_escaped = html.escape(message)
    st.markdown(
        f"""
        <div class="core-message-card">
            <p>{message_escaped}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_confidence_badge(score: float | None) -> None:
    if score is None:
        return

    # 점수 구간별 텍스트 및 색상 설정
    if score >= 0.8:
        level_text = "높음"
        color = "#4CAF50"  # 초록색
    elif score >= 0.6:
        level_text = "중간"
        color = "#FF9800"  # 오렌지색
    else:
        level_text = "낮음"
        color = "#757575"  # 회색

    st.markdown(
        f"""
        <div class="confidence-badge" style="background-color: {color};">
            신뢰도 <span>{level_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mari_story(story: dict | str | None) -> None:
    if not story:
        return

    if isinstance(story, str):
        # HTML 태그 이스케이프 처리
        story_escaped = html.escape(story)
        st.markdown(
            f"""
            <div class="result-card mari-card">
                {story_escaped}
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    header = story.get("header", {})
    closing = story.get("mari_closing", {})

    # HTML 태그 이스케이프 처리
    title = html.escape(header.get('title', '마리의 이야기'))
    summary = html.escape(header.get('summary', ''))
    core_message = html.escape(closing.get('core_message', ''))
    final_quote = html.escape(closing.get('final_quote', ''))

    st.markdown(
        f"""
        <div class="result-card mari-card">
            <h4>{title}</h4>
            <p>{summary}</p>
            <div class="mari-core-message">{core_message}</div>
            <div class="mari-final-quote">{final_quote}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
