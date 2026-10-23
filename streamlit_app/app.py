"""Multimodal Construction Intelligence Platform - Streamlit application."""

import io
import json
from datetime import datetime

import streamlit as st
from PIL import Image as PILImage

from services.gemini_service import (
    create_chat,
    generate_crack_assessment,
    generate_ppe_assessment,
    is_gemini_configured,
    send_chat,
)
from services.pollination_service import build_image_url, build_visualization_prompt, get_image_bytes
from utils import demo_responses
from utils.config import get_secret
from utils.site_ops import WEATHER_CONDITIONS, get_weather_alerts
from utils.valuation import LOCATION_TIERS, STRUCTURE_TYPES, compute_valuation, format_inr

st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
)

PAGES = [
    "Site Safety & PPE Audit",
    "Crack Diagnostics & Structural Integrity",
    "Planning & Real Estate Valuation",
    "Daily Site Assistant & Weather-Aware Advisory",
]

STATUS_PALETTE = {
    "Compliant": "#16a34a",
    "Needs Attention": "#d97706",
    "Critical": "#dc2626",
}
SEVERITY_PALETTE = {
    "Critical": "#dc2626",
    "High": "#ea580c",
    "Medium": "#d97706",
    "Low": "#2563eb",
}


def _pill(text: str, background: str) -> str:
    return (
        f'<span style="display:inline-block;padding:4px 14px;border-radius:9999px;'
        f'background-color:{background};color:#ffffff;font-size:0.85rem;font-weight:700;">{text}</span>'
    )


def _status_badge(status: str) -> str:
    color = STATUS_PALETTE.get(status, STATUS_PALETTE["Needs Attention"])
    return _pill(status, color)


def _severity_badge(severity: str) -> str:
    color = SEVERITY_PALETTE.get(severity, SEVERITY_PALETTE["Low"])
    return _pill(severity, color)


def _render_custom_css() -> None:
    st.markdown(
        """
        <style>
        h1 { font-size: 2.25rem; font-weight: 800; }
        h2 { font-size: 1.6rem; font-weight: 700; }
        h3 { font-size: 1.25rem; font-weight: 650; }
        [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
        .block-container { max-width: 1200px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> str:
    st.sidebar.title("🏗️ Construction Intelligence")
    st.sidebar.caption("Multimodal Construction Intelligence Platform")

    st.sidebar.divider()
    st.sidebar.subheader("AI Engine Configuration")
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
    if st.sidebar.button("Connect Gemini"):
        if api_key:
            import os

            os.environ["GEMINI_API_KEY"] = api_key
            st.sidebar.success("Gemini connected.")
        else:
            st.sidebar.warning("No API key provided — running in Demonstration Mode.")

    st.sidebar.divider()
    st.sidebar.subheader("Architecture")
    st.sidebar.markdown(
        "- **Multimodal LLM**: Gemini 1.5 Flash — PPE compliance & crack diagnostics\n"
        "- **Cost & Valuation**: INR-based cost estimation & real-estate valuation\n"
        "- **Image Gen**: Pollinations / Flux for 3D architectural renders"
    )
    st.sidebar.divider()
    st.sidebar.subheader("Features")
    return st.sidebar.radio("Navigate", PAGES, index=0)


def render_ppe_tab() -> None:
    st.header("Site Safety & PPE Audit")
    st.caption(
        "Upload a construction site photo to audit worker PPE compliance "
        "(helmets, high-visibility vests, steel-toe boots, safety harnesses) under OSHA and IS 456 standards."
    )

    uploaded_file = st.file_uploader(
        "Construction site photo (JPG / PNG)", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:
        st.info("Upload a construction site photo to run the PPE safety audit.")
        return

    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/jpeg"
    st.image(PILImage.open(io.BytesIO(image_bytes)), caption=uploaded_file.name, use_column_width=True)

    with st.spinner("Gemini multimodal safety analysis in progress..."):
        result = generate_ppe_assessment(
            image_bytes=image_bytes, mime_type=mime_type, filename=uploaded_file.name
        )

    safety_score = int(result.get("safety_score") or 0)
    overall_status = str(result.get("overall_status") or "Needs Attention")
    checklist = result.get("ppe_checklist") or []
    hazards = result.get("hazards") or []

    col_a, col_b = st.columns(2)
    col_a.metric("Safety Score", f"{safety_score} / 100")
    col_b.markdown(f"**Overall Status:** { _status_badge(overall_status) }", unsafe_allow_html=True)

    st.divider()
    st.subheader("PPE Detection Checklist")
    if checklist:
        cols = st.columns(2)
        for idx, item in enumerate(checklist):
            with cols[idx % 2]:
                detected = bool(item.get("detected"))
                required = bool(item.get("required"))
                st.markdown(
                    f"{'✅' if detected else '❌'} **{item.get('item')}** — Required: {'Yes' if required else 'No'}"
                )
    else:
        st.write("No checklist data returned.")

    st.divider()
    st.subheader("Identified Site Hazards")
    if hazards:
        for hazard in hazards:
            severity = str(hazard.get("severity") or "Low")
            remedy = str(hazard.get("remedy") or "Monitor and follow up.")
            st.markdown(f"**{_severity_badge(severity)}** {hazard.get('hazard')} — Remedy: {remedy}")
    else:
        st.write("No hazards identified.")

    st.divider()
    report = {
        "report_type": "PPE_Safety_Audit",
        "generated_at": datetime.utcnow().isoformat(),
        "source_image": uploaded_file.name,
        "safety_score": safety_score,
        "overall_status": overall_status,
        "ppe_checklist": checklist,
        "hazards": hazards,
    }
    st.download_button(
        label="Download Safety Report (JSON)",
        data=json.dumps(report, indent=2),
        file_name="ppe_safety_report.json",
        mime="application/json",
    )


def render_crack_tab() -> None:
    st.header("Crack Diagnostics & Structural Integrity")
    st.caption(
        "Upload a concrete / wall surface photo to classify defect type, estimate crack width, "
        "identify root causes and recommend engineering repairs."
    )

    uploaded_file = st.file_uploader(
        "Concrete / wall surface photo (JPG / PNG)", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:
        st.info("Upload a concrete or wall surface photo to run crack diagnostics.")
        return

    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/jpeg"
    st.image(PILImage.open(io.BytesIO(image_bytes)), caption=uploaded_file.name, use_column_width=True)

    with st.spinner("Gemini structural crack analysis in progress..."):
        result = generate_crack_assessment(
            image_bytes=image_bytes, mime_type=mime_type, filename=uploaded_file.name
        )

    defect_type = str(result.get("defect_type") or "Hairline")
    crack_width_mm = float(result.get("crack_width_mm") or 0.0)
    root_causes = result.get("root_causes") or []
    repairs = result.get("recommended_repairs") or []
    urgency = str(result.get("urgency") or "Medium")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Defect Type", defect_type)
    col_b.metric("Crack Width", f"{crack_width_mm:.2f} mm")
    col_c.markdown(f"**Urgency:** { _severity_badge(urgency) }", unsafe_allow_html=True)

    st.divider()
    st.subheader("Root Causes")
    if root_causes:
        for cause in root_causes:
            st.markdown(f"- {cause}")
    else:
        st.write("No root causes identified.")

    st.subheader("Recommended Engineering Repairs")
    if repairs:
        for repair in repairs:
            st.markdown(f"- {repair}")
    else:
        st.write("No repair recommendations available.")

    st.divider()
    repair_note = (
        "For epoxy injection: structural epoxy injection is suited for non-structural cracks. "
        "For structural shear / settlement / shear defects: engage structural re-grouting or underpinning "
        "assessment before loading restoration."
    )
    st.info(repair_note)


def render_planning_tab() -> None:
    st.header("Planning & Real Estate Valuation")
    st.caption(
        "Estimate construction costs and current market asset valuation in INR (Lakhs / Crores)."
    )

    with st.form("valuation_form"):
        structure_type = st.selectbox("Structure Type", list(STRUCTURE_TYPES.keys()))
        built_up_sqft = st.number_input(
            "Built-up Area (sq ft)", min_value=100.0, value=2000.0, step=100.0
        )
        location_tier = st.selectbox("Location Tier (Indian Cities)", list(LOCATION_TIERS.keys()))
        completion_pct = st.slider("Project Completion (%)", 0, 100, 40, step=5)

        submitted = st.form_submit_button("Generate Plan & Valuation")

    if submitted:
        with st.spinner("Computing construction plan and valuation..."):
            valuation = compute_valuation(
                structure_type=structure_type,
                built_up_sqft=built_up_sqft,
                location_tier=location_tier,
                completion_pct=completion_pct,
            )

        st.divider()
        cols = st.columns(4)
        cols[0].metric("Total Project Budget", format_inr(valuation["total_project_budget_inr"]))
        cols[1].metric("CAPEX Incurred", format_inr(valuation["capital_expenditure_inr"]))
        cols[2].metric("Market Asset Valuation", format_inr(valuation["market_asset_valuation_inr"]))
        cols[3].metric("Steel Required", f"{valuation['steel_requirement_tons']} tons")

        st.metric("Cement Requirement", f"{valuation['cement_requirement_bags']} bags")

        st.divider()
        st.subheader("Milestone Progress")
        st.progress(float(completion_pct) / 100.0)
        for milestone in valuation["milestone_progress"]:
            st.markdown(
                f"- **{milestone['name']}**: {milestone['progress']}% complete (weighted contribution)"
            )

        st.divider()
        st.subheader("Conceptual 3D Architectural Rendering")
        prompt = build_visualization_prompt(
            structure_type=structure_type,
            built_up_sqft=built_up_sqft,
            location_label=LOCATION_TIERS[location_tier]["label"],
        )
        image_url = build_image_url(prompt)
        with st.spinner("Generating 3D architectural visualization via Pollinations / Flux..."):
            try:
                image_bytes = get_image_bytes(image_url)
                st.image(
                    PILImage.open(io.BytesIO(image_bytes)),
                    caption=prompt,
                    use_column_width=True,
                )
            except Exception as exc:
                st.warning(f"3D visualization generation failed: {exc}")


def render_weather_tab() -> None:
    st.header("Daily Site Assistant & Weather-Aware Advisory")
    st.caption("Select today's weather condition to receive dynamic safety protocols.")

    condition = st.selectbox("Weather Condition", list(WEATHER_CONDITIONS.keys()))
    alert = get_weather_alerts(condition)

    st.markdown(f"**{_severity_badge(alert['severity'])}** {alert['title']}")
    st.info(alert["advisory"])
    st.caption(f"Affected activity: {alert['affected_activity']}")

    st.divider()
    st.subheader("Construction Assistant Chatbot")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.gemini_chat = create_chat()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask about safety, cracks, plans, costs, weather...")
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            with st.spinner("Consulting the engineering assistant..."):
                reply = send_chat(st.session_state.gemini_chat, user_prompt)
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})


def main() -> None:
    _render_custom_css()

    page = _render_sidebar()

    st.title("Multimodal Construction Intelligence Platform")
    st.caption(
        "AI-driven construction safety, structural diagnostics, planning, valuation and site intelligence."
    )

    if not is_gemini_configured():
        st.warning(
            "Gemini API key not detected — running in **Demonstration Mode** with fallback analysis results. "
            "Add a Google Gemini API key in the sidebar for live multimodal AI analysis."
        )

    if page == PAGES[0]:
        render_ppe_tab()
    elif page == PAGES[1]:
        render_crack_tab()
    elif page == PAGES[2]:
        render_planning_tab()
    elif page == PAGES[3]:
        render_weather_tab()


if __name__ == "__main__":
    main()
