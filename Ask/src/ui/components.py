"""
공통 UI 컴포넌트 및 질문 렌더링 유틸.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

import streamlit as st
import streamlit.components.v1 as components

from src.ui.media import fix_image_orientation


def scroll_to_top() -> None:
    """페이지 스크롤을 맨 위로 이동."""
    components.html(
        """
        <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
        """,
        height=0,
    )


def show_progress_bar(step: int, total: int = 7) -> None:
    """진행률 표시."""
    progress = step / total
    st.progress(progress)
    st.caption(f"진행률: {int(progress * 100)}% (Step {step}/{total})")


def load_mari_image(image_name: str) -> str | None:
    """assets/images 경로에서 마리 이미지를 찾습니다."""
    script_dir = Path(__file__).resolve().parents[2]
    image_path = script_dir / "assets" / "images" / image_name
    return str(image_path) if image_path.exists() else None


def get_image_base64(image_path: str) -> str:
    """이미지를 base64 문자열로 변환."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def render_question(q: Dict[str, Any]) -> Any:
    """질문 타입별 컴포넌트를 렌더링하고 응답을 반환."""
    st.markdown(f"### {q['question']}")
    if q.get("description"):
        st.caption(q["description"])
    st.markdown("")

    q_type = q["type"]
    q_id = q["id"]
    default_value = st.session_state.responses.get(q_id)

    if q_type == "text":
        return st.text_input(
            f"{q_id}_input",
            value=default_value or "",
            placeholder=q.get("placeholder", ""),
            label_visibility="collapsed",
        )

    if q_type == "radio":
        options = q["options"]
        if q.get("other_option"):
            options = options + [{"value": "other", "label": "기타"}]

        if default_value:
            try:
                default_index = [opt["value"] for opt in options].index(default_value)
            except ValueError:
                default_index = 0
        else:
            default_index = 0

        selected = None
        for opt in options:
            is_selected = default_value == opt["value"]
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

        if default_value == "other" and q.get("other_option"):
            other_text = st.text_input(
                "기타 내용을 입력해주세요",
                value=st.session_state.responses.get(f"{q_id}_other", ""),
                key=f"{q_id}_other_input",
            )
            st.session_state.responses[f"{q_id}_other"] = other_text

        return default_value

    if q_type == "radio_horizontal":
        options = q["options"]
        if q.get("other_option"):
            options = options + [{"value": "other", "label": "기타"}]

        cols = st.columns(len(options))
        for idx, opt in enumerate(options):
            is_selected = default_value == opt["value"]
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

        if default_value == "other" and q.get("other_option"):
            other_text = st.text_input(
                "기타 내용을 입력해주세요",
                value=st.session_state.responses.get(f"{q_id}_other", ""),
                key=f"{q_id}_other_input",
            )
            st.session_state.responses[f"{q_id}_other"] = other_text

        return default_value

    if q_type == "checkbox":
        checked_values = default_value if isinstance(default_value, list) else []
        selected = []
        cols = st.columns(len(q["options"]))

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
                    if is_checked:
                        selected = [v for v in checked_values if v != opt["value"]]
                    else:
                        selected = checked_values + [opt["value"]]
                    st.session_state.responses[q_id] = selected
                    st.rerun()

        return checked_values

    if q_type == "checkbox_button":
        current = default_value if isinstance(default_value, list) else []
        cols = st.columns(len(q["options"]))
        for idx, opt in enumerate(q["options"]):
            is_selected = opt["value"] in current
            button_type = "primary" if is_selected else "secondary"
            with cols[idx]:
                if st.button(
                    opt["label"],
                    key=f"{q_id}_{opt['value']}_btn",
                    use_container_width=True,
                    type=button_type,
                ):
                    if is_selected:
                        current = [v for v in current if v != opt["value"]]
                    else:
                        current = current + [opt["value"]]
                    st.session_state.responses[q_id] = current
                    st.rerun()
        return current

    if q_type in ("checkbox_multiple", "checkbox_grid"):
        current = set(default_value or [])
        columns = q.get("columns")
        if columns is None:
            columns = 2 if q_type == "checkbox_grid" else 1
        columns = max(1, min(columns, len(q["options"])))
        cols = st.columns(columns) if columns > 1 else None

        updated_values = []
        for idx, opt in enumerate(q["options"]):
            key = f"{q_id}_{opt['value']}_checkbox"
            is_checked = opt["value"] in current
            if cols:
                container = cols[idx % columns]
                checked = container.checkbox(opt["label"], value=is_checked, key=key)
            else:
                checked = st.checkbox(opt["label"], value=is_checked, key=key)
            if checked:
                updated_values.append(opt["value"])
        return updated_values

    if q_type == "multiselect":
        options = [opt["label"] for opt in q["options"]]
        default_labels = []
        if default_value:
            value_to_label = {opt["value"]: opt["label"] for opt in q["options"]}
            default_labels = [value_to_label.get(val, "") for val in default_value]

        selected_labels = st.multiselect(
            f"{q_id}_multiselect",
            options,
            default=default_labels,
            label_visibility="collapsed",
        )
        label_to_value = {opt["label"]: opt["value"] for opt in q["options"]}
        return [label_to_value[label] for label in selected_labels]

    if q_type == "selectbox":
        options = q["options"]
        index = options.index(default_value) if default_value in options else 0
        return st.selectbox(
            f"{q_id}_selectbox",
            options,
            index=index,
            label_visibility="collapsed",
        )

    if q_type == "chips":
        selected = default_value or []
        cols = st.columns(len(q["options"]))
        for idx, opt in enumerate(q["options"]):
            is_selected = opt["value"] in selected
            button_type = "primary" if is_selected else "secondary"
            with cols[idx]:
                if st.button(
                    opt["label"],
                    key=f"{q_id}_{opt['value']}",
                    use_container_width=True,
                    type=button_type,
                ):
                    if is_selected:
                        selected.remove(opt["value"])
                    else:
                        if q.get("max_select") and len(selected) >= q["max_select"]:
                            st.warning(f"최대 {q['max_select']}개까지 선택할 수 있어요.")
                        else:
                            selected.append(opt["value"])
                    st.session_state.responses[q_id] = selected
                    st.rerun()
        return selected

    if q_type == "time_range":
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

    if q_type == "select_year_month":
        if isinstance(default_value, dict):
            default_year = default_value.get("year", "2020")
            default_month = default_value.get("month", "1")
        else:
            default_year = "2020"
            default_month = "1"

        col1, col2 = st.columns(2)
        with col1:
            year_options = list(range(2024, 2009, -1)) + ["모름"]
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
                key=f"{q_id}_year",
            )

        with col2:
            month_options = list(range(1, 13)) + ["모름"]
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
                key=f"{q_id}_month",
            )

        return {"year": str(year), "month": str(month)}

    if q_type == "image":
        uploaded_file = st.file_uploader(
            q.get("description", "이미지를 업로드해주세요"),
            type=["jpg", "jpeg", "png"],
            key=f"{q_id}_uploader",
        )
        if uploaded_file:
            st.success("✅ 이미지가 업로드되었습니다!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                fixed_image = fix_image_orientation(uploaded_file)
                if fixed_image:
                    st.image(fixed_image, caption="업로드된 이미지", use_container_width=True)
                else:
                    st.error("이미지를 표시할 수 없습니다. 다른 이미지를 업로드해주세요.")
        return uploaded_file

    if q_type == "media":
        st.markdown(
            """
            <style>
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
            """,
            unsafe_allow_html=True,
        )
        st.file_uploader(
            q.get("description", "사진 또는 영상을 업로드해주세요"),
            type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
            key=f"{q_id}_uploader",
            disabled=True,
        )
        return None

    return None
