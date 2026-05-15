import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import json
import re
from datetime import datetime

NAVY = "#11224F"
BLUE = "#29B5E8"
LIGHT_BLUE = "#E8F4FD"
WHITE = "#FFFFFF"
GRAY = "#6B7280"
GREEN = "#10B981"
RED = "#EF4444"
ORANGE = "#F59E0B"

st.set_page_config(
    page_title="MISO x Snowflake — Onsite Experience",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "comments" not in st.session_state:
    st.session_state["comments"] = {}

def render_comments(section_key: str, section_label: str):
    if section_key not in st.session_state["comments"]:
        st.session_state["comments"][section_key] = []
    comments = st.session_state["comments"][section_key]
    with st.expander(f":material/comment: Notes & comments — {section_label} ({len(comments)})", expanded=False):
        for i, c in enumerate(comments):
            with st.container(border=True):
                hcol1, hcol2 = st.columns([4, 1])
                with hcol1:
                    st.caption(f"{c['author']} — {c['time']}")
                with hcol2:
                    if st.button(":material/delete:", key=f"del_{section_key}_{i}", help="Delete"):
                        st.session_state["comments"][section_key].pop(i)
                        st.rerun()
                st.markdown(c["text"])
        with st.container(border=True):
            author = st.text_input("Your name", value=st.session_state.get("comment_author", ""), key=f"author_{section_key}", placeholder="e.g. Tim Aliff")
            new_comment = st.text_area("Add a note or comment", key=f"text_{section_key}", placeholder="Type your thoughts, questions, or feedback here...")
            if st.button("Save comment", key=f"save_{section_key}", type="primary", icon=":material/save:"):
                if new_comment.strip():
                    st.session_state["comment_author"] = author
                    st.session_state["comments"][section_key].append({
                        "author": author or "Anonymous",
                        "time": datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        "text": new_comment.strip(),
                        "section": section_label,
                    })
                    st.rerun()
                else:
                    st.warning("Please enter a comment before saving.")

def render_export_all():
    all_comments = []
    for section_key, comments in st.session_state.get("comments", {}).items():
        all_comments.extend(comments)
    if all_comments:
        export_md = "# MISO x Snowflake — Session Notes\n\n"
        for c in all_comments:
            export_md += f"### {c['section']}\n**{c['author']}** — {c['time']}\n\n{c['text']}\n\n---\n\n"
        st.download_button(":material/download: Export all notes", export_md, "miso_session_notes.md", "text/markdown")

st.markdown(f"""
<style>
    .main .block-container {{ padding-top: 1.5rem; }}
    [data-testid="stSidebar"] {{ background-color: {NAVY}; }}
    [data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
    [data-testid="stSidebar"] .stSelectbox label {{ color: {BLUE} !important; }}
    .hero-title {{ font-size: 2.2rem; font-weight: 700; color: {NAVY}; margin-bottom: 0; }}
    .hero-sub {{ font-size: 1.1rem; color: {GRAY}; margin-top: 0.2rem; }}
    .section-header {{ font-size: 1.5rem; font-weight: 600; color: {NAVY}; border-bottom: 3px solid {BLUE}; padding-bottom: 0.3rem; margin-top: 1.5rem; }}
    .callout-box {{ background: {LIGHT_BLUE}; border-left: 4px solid {BLUE}; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; margin: 1rem 0; }}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### :material/bolt: MISO x Snowflake")
    st.caption("Onsite Demo Experience")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            ":material/play_circle: Interactive demo",
            ":material/summarize: Executive overview",
            ":material/analytics: Business value analysis",
            ":material/calendar_today: Onsite agenda",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("**Attendees**")
    st.caption("Tim Aliff — Exec Dir, Market Ops")
    st.caption("Amber Alewine — Dir, Forward Markets")
    st.caption("Bonnie Matthews — IT Architecture")
    st.caption("Ben Boutwell — Principal Engineer")
    st.markdown("---")
    st.caption("Prepared by Kala Boudreaux")
    st.caption("kala.boudreaux@snowflake.com")
    st.markdown("---")
    render_export_all()

# ═══════════════════════════════════════════════
# PAGE 1: INTERACTIVE DEMO
# ═══════════════════════════════════════════════
if "Interactive demo" in page:
    st.markdown('<p class="hero-title">Grid intelligence, powered by Snowflake</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Interactive demonstration of AI-driven grid operations for MISO</p>', unsafe_allow_html=True)

    demo_tab = st.segmented_control(
        "Select demo",
        ["Dynamic line rating", "Study anomaly detection", "What-if scenario modeling", "Ask the data (LLM)", "ML recommendations"],
        default="Dynamic line rating",
    )

    if demo_tab == "Dynamic line rating":
        st.markdown('<p class="section-header">Dynamic line rating — from seasonal to real-time</p>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.markdown("**Simulation controls**")
                ambient_temp = st.slider("Ambient temperature (°F)", 20, 105, 52)
                wind_speed = st.slider("Wind speed (mph)", 0, 40, 12)
                solar_radiation = st.slider("Solar radiation (W/m²)", 0, 1200, 300)
                line_voltage = st.selectbox("Transmission line", ["345 kV — Midwest Corridor", "230 kV — South Hub", "138 kV — Metro Feed"])
                st.caption("Adjust conditions to see how dynamic ratings respond in real time")

        static_rating = 1200
        temp_factor = max(0.4, 1.0 - (ambient_temp - 40) * 0.008)
        wind_factor = 1.0 + wind_speed * 0.015
        solar_factor = max(0.85, 1.0 - solar_radiation * 0.0001)
        dynamic_rating = static_rating * temp_factor * wind_factor * solar_factor
        aar_rating = static_rating * temp_factor * solar_factor
        capacity_gain_aar = ((aar_rating - static_rating) / static_rating) * 100
        capacity_gain_dlr = ((dynamic_rating - static_rating) / static_rating) * 100

        with col2:
            with st.container(horizontal=True):
                st.metric("Static rating (SLR)", f"{static_rating} MW", help="Worst-case seasonal assumption", border=True)
                st.metric("AAR (Phase 1)", f"{aar_rating:.0f} MW", f"{capacity_gain_aar:+.1f}%", border=True)
                st.metric("DLR (Phase 2)", f"{dynamic_rating:.0f} MW", f"{capacity_gain_dlr:+.1f}%", border=True)

            hours = list(range(24))
            np.random.seed(42)
            temps_h = [ambient_temp + 15 * np.sin((h - 6) * np.pi / 12) + np.random.normal(0, 2) for h in hours]
            winds_h = [max(0, wind_speed + 5 * np.sin((h - 14) * np.pi / 12) + np.random.normal(0, 3)) for h in hours]
            dlr_h, aar_h = [], []
            for h in hours:
                tf = max(0.4, 1.0 - (temps_h[h] - 40) * 0.008)
                wf = 1.0 + winds_h[h] * 0.015
                sf = max(0.85, 1.0 - (solar_radiation * max(0, np.sin((h - 6) * np.pi / 12))) * 0.0001)
                dlr_h.append(static_rating * tf * wf * sf)
                aar_h.append(static_rating * tf * sf)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hours, y=[static_rating]*24, name="Static (SLR)", line=dict(color=RED, dash="dash", width=2)))
            fig.add_trace(go.Scatter(x=hours, y=aar_h, name="AAR (Phase 1)", line=dict(color=ORANGE, width=2)))
            fig.add_trace(go.Scatter(x=hours, y=dlr_h, name="DLR (Phase 2)", line=dict(color=GREEN, width=3), fill="tonexty", fillcolor="rgba(16,185,129,0.1)"))
            fig.update_layout(title="24-hour line capacity comparison", xaxis_title="Hour of day", yaxis_title="Capacity (MW)", height=380, margin=dict(t=40, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        unlocked = max(0, dynamic_rating - static_rating)
        render_comments("demo_dlr", "Dynamic Line Rating Demo")
        st.markdown(f'<div class="callout-box"><b>What you\'re seeing:</b> The green shaded area represents <b>capacity that exists today but goes unused</b> under seasonal ratings. On this simulated day, DLR unlocks an additional <b>{unlocked:.0f} MW</b> — equivalent to powering <b>~{unlocked * 500:,.0f} homes</b> — without building a single new line.</div>', unsafe_allow_html=True)

        with st.expander("How it works — Snowflake + Siemens architecture", icon=":material/architecture:"):
            c1, c2, c3 = st.columns(3)
            with c1:
                with st.container(border=True):
                    st.markdown("**:material/database: Data layer**")
                    st.markdown("Snowflake Unified Namespace")
                    st.caption("Grid sensor data, weather forecasts from Marketplace, study I/O from PowerGem/GE")
            with c2:
                with st.container(border=True):
                    st.markdown("**:material/model_training: AI/ML layer**")
                    st.markdown("Siemens xDT + Cortex AI")
                    st.caption("Executable Digital Twin models convective cooling via CFD. Cortex powers AAR/DLR calculations")
            with c3:
                with st.container(border=True):
                    st.markdown("**:material/web: Application layer**")
                    st.markdown("Streamlit + scenarios")
                    st.caption("Engineers run what-if scenarios and view real-time ratings — all in one platform")

    elif demo_tab == "Study anomaly detection":
        st.markdown('<p class="section-header">AI-powered anomaly detection in study input data</p>', unsafe_allow_html=True)
        st.markdown("Simulating Cortex AI scanning 12 months of reliability study input data for statistical anomalies.")

        np.random.seed(123)
        dates = pd.date_range("2025-01-01", periods=365, freq="D")
        base_load = 85000 + 15000 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 2000, 365)
        anomaly_indices = [45, 46, 122, 123, 124, 200, 278, 279, 340]
        anomaly_mask = np.zeros(365, dtype=bool)
        for idx in anomaly_indices:
            base_load[idx] += np.random.choice([-1, 1]) * np.random.uniform(8000, 18000)
            anomaly_mask[idx] = True

        study_df = pd.DataFrame({"date": dates, "load_mw": base_load, "anomaly": anomaly_mask})
        sensitivity = st.select_slider("AI detection sensitivity", options=["Conservative", "Balanced", "Aggressive"], value="Balanced")
        threshold = {"Conservative": 2.5, "Balanced": 2.0, "Aggressive": 1.5}[sensitivity]
        rolling_mean = study_df["load_mw"].rolling(30, center=True).mean()
        rolling_std = study_df["load_mw"].rolling(30, center=True).std()
        z_scores = (study_df["load_mw"] - rolling_mean) / rolling_std
        detected = z_scores.abs() > threshold

        with st.container(horizontal=True):
            st.metric("Data points scanned", f"{len(study_df):,}", border=True)
            st.metric("Anomalies detected", f"{detected.sum()}", border=True)
            st.metric("True anomalies caught", f"{(detected & anomaly_mask).sum()} / {anomaly_mask.sum()}", border=True)
            st.metric("Processing time", "2.3 sec", help="vs. ~2-3 weeks manual review", border=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=study_df["date"], y=study_df["load_mw"], name="Study input (load MW)", line=dict(color=BLUE, width=1.5)))
        fig2.add_trace(go.Scatter(x=study_df["date"], y=rolling_mean, name="30-day rolling mean", line=dict(color=GRAY, dash="dash", width=1)))
        fig2.add_trace(go.Scatter(x=study_df.loc[detected, "date"], y=study_df.loc[detected, "load_mw"], name="AI-detected anomalies", mode="markers", marker=dict(color=RED, size=12, symbol="x", line=dict(width=2))))
        fig2.update_layout(title="Cortex AI anomaly detection — 12-month study input scan", xaxis_title="Date", yaxis_title="Load (MW)", height=420, margin=dict(t=40, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02), hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

        render_comments("demo_anomaly", "Study Anomaly Detection Demo")

        st.markdown('<div class="callout-box"><b>What you\'re seeing:</b> Cortex AI scanned a year of study data in <b>2.3 seconds</b> and flagged anomalies that would take engineers <b>weeks to find manually</b>. Each red marker is a data point deviating from expected patterns — the "needles buried in haystacks made of needles."</div>', unsafe_allow_html=True)

        with st.expander("Detected anomaly details", icon=":material/table_chart:"):
            detail = study_df[detected][["date", "load_mw"]].copy()
            detail["z_score"] = z_scores[detected].values
            detail["severity"] = detail["z_score"].abs().apply(lambda x: "Critical" if x > 3 else "Warning" if x > 2 else "Info")
            detail.columns = ["Date", "Load (MW)", "Z-Score", "Severity"]
            st.dataframe(detail, hide_index=True, use_container_width=True)

    elif demo_tab == "What-if scenario modeling":
        st.markdown('<p class="section-header">Predictive what-if scenario modeling</p>', unsafe_allow_html=True)
        st.markdown("Run predictive scenarios on study data before committing to full engineering studies.")

        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container(border=True):
                st.markdown("**Scenario parameters**")
                load_growth = st.slider("Load growth (%)", -10, 30, 5)
                renewable_pen = st.slider("Renewable penetration (%)", 10, 60, 25)
                gen_retirement = st.slider("Generation retirements (MW)", 0, 5000, 1000, step=500)
                weather_scenario = st.selectbox("Weather scenario", ["Normal", "Extreme heat", "Polar vortex", "High wind"])
                run_btn = st.button("Run scenario", type="primary", icon=":material/play_arrow:", use_container_width=True)
                if run_btn:
                    st.session_state["scenario_run"] = True

        with col2:
            if st.session_state.get("scenario_run"):
                with st.spinner("Running predictive model..."):
                    time.sleep(1.5)
                weather_mult = {"Normal": 1.0, "Extreme heat": 1.35, "Polar vortex": 1.45, "High wind": 0.85}
                base_demand = 120000
                adjusted_demand = base_demand * (1 + load_growth / 100) * weather_mult[weather_scenario]
                renewable_supply = adjusted_demand * renewable_pen / 100
                conventional_supply = 95000 - gen_retirement
                total_supply = conventional_supply + renewable_supply
                reserve_margin = ((total_supply - adjusted_demand) / adjusted_demand) * 100
                congestion_risk = max(0, min(100, 50 + load_growth * 2 - renewable_pen * 0.5 + gen_retirement / 100))

                with st.container(horizontal=True):
                    st.metric("Projected peak demand", f"{adjusted_demand:,.0f} MW", f"{load_growth:+d}% growth", border=True)
                    st.metric("Available supply", f"{total_supply:,.0f} MW", f"-{gen_retirement:,} MW retired", border=True)
                    rm_color = "normal" if reserve_margin > 15 else "inverse" if reserve_margin < 5 else "off"
                    st.metric("Reserve margin", f"{reserve_margin:.1f}%", "Adequate" if reserve_margin > 15 else "At risk" if reserve_margin > 5 else "Critical", delta_color=rm_color, border=True)
                    st.metric("Congestion risk", f"{congestion_risk:.0f}%", border=True)

                hours = list(range(24))
                demand_curve = [adjusted_demand * (0.6 + 0.4 * np.sin((h - 4) * np.pi / 14)) for h in hours]
                supply_curve = [total_supply * (0.7 + 0.3 * np.sin((h - 6) * np.pi / 16)) for h in hours]
                renewable_curve = [renewable_supply * max(0, np.sin((h - 6) * np.pi / 12)) for h in hours]

                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=hours, y=demand_curve, name="Projected demand", line=dict(color=RED, width=3)))
                fig3.add_trace(go.Scatter(x=hours, y=supply_curve, name="Available supply", line=dict(color=GREEN, width=2)))
                fig3.add_trace(go.Scatter(x=hours, y=renewable_curve, name="Renewable generation", fill="tozeroy", fillcolor="rgba(41,181,232,0.2)", line=dict(color=BLUE, width=1)))
                fig3.update_layout(title=f"Scenario: {weather_scenario} | +{load_growth}% load | {renewable_pen}% renewable | -{gen_retirement} MW retired", xaxis_title="Hour of day", yaxis_title="MW", height=400, margin=dict(t=50, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02), hovermode="x unified")
                st.plotly_chart(fig3, use_container_width=True)

                if reserve_margin < 5:
                    st.error("**Critical:** Reserve margin below 5%. Potential reliability risk requiring immediate engineering review.", icon=":material/error:")
                elif reserve_margin < 15:
                    st.warning("**Caution:** Reserve margin below target. Consider accelerating generation interconnection or transmission upgrades.", icon=":material/warning:")
                else:
                    st.success("**Adequate:** Reserve margin within acceptable range under this scenario.", icon=":material/check_circle:")

                render_comments("demo_whatif", "What-If Scenario Modeling Demo")

                st.markdown('<div class="callout-box"><b>What you\'re seeing:</b> Engineers adjust parameters and see predicted outcomes <b>in seconds</b> — before committing to full PowerGem/GE study runs that take weeks. Data + AI + application in one platform.</div>', unsafe_allow_html=True)
            else:
                st.info("Adjust scenario parameters and click **Run scenario** to see predictive results.", icon=":material/tune:")

    elif demo_tab == "Ask the data (LLM)":
        st.markdown('<p class="section-header">Natural language grid analytics — powered by Cortex AI</p>', unsafe_allow_html=True)
        st.markdown("Ask questions about MISO grid data in plain English. Snowflake Cortex translates your question into analytics and returns insights instantly.")

        np.random.seed(77)
        dates = pd.date_range("2025-01-01", periods=365, freq="D")
        grid_df = pd.DataFrame({
            "date": dates,
            "load_mw": 85000 + 15000 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 2000, 365),
            "congestion_cost_m": np.clip(3 + 4 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 1.5, 365), 0.5, 12),
            "wind_gen_mw": np.clip(15000 + 8000 * np.sin(np.arange(365) * 2 * np.pi / 365 + 1) + np.random.normal(0, 3000, 365), 2000, 30000),
            "solar_gen_mw": np.clip(8000 * np.maximum(0, np.sin(np.arange(365) * 2 * np.pi / 365)) + np.random.normal(0, 1500, 365), 0, 15000),
            "line_utilization_pct": np.clip(55 + 20 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 8, 365), 25, 95),
            "reserve_margin_pct": np.clip(18 - 8 * np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 3, 365), 3, 35),
            "region": np.random.choice(["Midwest", "South", "Central", "North"], 365),
        })
        grid_df["month"] = grid_df["date"].dt.month_name()
        grid_df["quarter"] = "Q" + grid_df["date"].dt.quarter.astype(str)

        suggested = [
            "What were the top 5 highest congestion cost days?",
            "Show me average load by quarter",
            "Which month had the lowest reserve margin?",
            "Compare wind vs solar generation by month",
            "When did line utilization exceed 85%?",
            "What is the correlation between wind generation and congestion costs?",
        ]

        st.caption("Try one of these or type your own:")
        cols = st.columns(3)
        for i, q in enumerate(suggested):
            with cols[i % 3]:
                if st.button(q, key=f"sq_{i}", use_container_width=True):
                    st.session_state["nlq"] = q

        user_q = st.chat_input("Ask a question about the grid data...")
        if user_q:
            st.session_state["nlq"] = user_q

        if st.session_state.get("nlq"):
            query = st.session_state["nlq"]
            with st.chat_message("user"):
                st.markdown(query)

            with st.chat_message("assistant", avatar=":material/bolt:"):
                with st.spinner("Cortex AI is analyzing..."):
                    time.sleep(1.2)

                ql = query.lower()
                if "highest congestion" in ql or "top" in ql and "congestion" in ql:
                    result = grid_df.nlargest(5, "congestion_cost_m")[["date", "congestion_cost_m", "load_mw", "region"]].copy()
                    result.columns = ["Date", "Congestion Cost ($M)", "Load (MW)", "Region"]
                    result["Congestion Cost ($M)"] = result["Congestion Cost ($M)"].round(1)
                    st.markdown("**Top 5 highest congestion cost days:**")
                    st.dataframe(result, hide_index=True, use_container_width=True)
                    st.markdown(f"The highest congestion day was **{result.iloc[0]['Date'].strftime('%B %d, %Y')}** at **${result.iloc[0]['Congestion Cost ($M)']}M** in the **{result.iloc[0]['Region']}** region. These peaks correlate with high load periods and constrained transmission corridors.")

                elif "average load" in ql and "quarter" in ql:
                    result = grid_df.groupby("quarter")["load_mw"].mean().reset_index()
                    result.columns = ["Quarter", "Avg Load (MW)"]
                    result["Avg Load (MW)"] = result["Avg Load (MW)"].round(0).astype(int)
                    fig = go.Figure(go.Bar(x=result["Quarter"], y=result["Avg Load (MW)"], marker_color=BLUE, text=result["Avg Load (MW)"].apply(lambda x: f"{x:,}"), textposition="outside"))
                    fig.update_layout(title="Average load by quarter", yaxis_title="MW", height=350)
                    st.plotly_chart(fig, use_container_width=True)
                    peak_q = result.loc[result["Avg Load (MW)"].idxmax()]
                    st.markdown(f"**{peak_q['Quarter']}** had the highest average load at **{peak_q['Avg Load (MW)']:,} MW**, driven by seasonal cooling/heating demand.")

                elif "lowest reserve margin" in ql:
                    monthly = grid_df.groupby("month")["reserve_margin_pct"].mean().reset_index()
                    monthly.columns = ["Month", "Avg Reserve Margin (%)"]
                    monthly["Avg Reserve Margin (%)"] = monthly["Avg Reserve Margin (%)"].round(1)
                    month_order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
                    monthly["sort"] = monthly["Month"].apply(lambda x: month_order.index(x))
                    monthly = monthly.sort_values("sort").drop(columns="sort")
                    colors = [RED if v < 10 else ORANGE if v < 15 else GREEN for v in monthly["Avg Reserve Margin (%)"]]
                    fig = go.Figure(go.Bar(x=monthly["Month"], y=monthly["Avg Reserve Margin (%)"], marker_color=colors, text=monthly["Avg Reserve Margin (%)"].apply(lambda x: f"{x}%"), textposition="outside"))
                    fig.update_layout(title="Average reserve margin by month", yaxis_title="%", height=380)
                    st.plotly_chart(fig, use_container_width=True)
                    lowest = monthly.loc[monthly["Avg Reserve Margin (%)"].idxmin()]
                    st.markdown(f"**{lowest['Month']}** had the lowest average reserve margin at **{lowest['Avg Reserve Margin (%)']}%**. Months below 15% (orange/red) indicate potential reliability stress and warrant proactive study review.")

                elif "wind" in ql and "solar" in ql:
                    monthly = grid_df.groupby(grid_df["date"].dt.month).agg({"wind_gen_mw": "mean", "solar_gen_mw": "mean"}).reset_index()
                    monthly.columns = ["Month", "Wind (MW)", "Solar (MW)"]
                    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="Wind", x=months, y=monthly["Wind (MW)"], marker_color=BLUE))
                    fig.add_trace(go.Bar(name="Solar", x=months, y=monthly["Solar (MW)"], marker_color=ORANGE))
                    fig.update_layout(title="Wind vs Solar generation by month", yaxis_title="Avg MW", height=380, barmode="group")
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("Wind generation peaks in spring/fall with seasonal wind patterns. Solar peaks in summer. Together they provide complementary renewable coverage across the year.")

                elif "utilization" in ql and ("85" in ql or "exceed" in ql or "above" in ql):
                    high_util = grid_df[grid_df["line_utilization_pct"] > 85][["date", "line_utilization_pct", "load_mw", "region"]].copy()
                    high_util.columns = ["Date", "Utilization (%)", "Load (MW)", "Region"]
                    high_util["Utilization (%)"] = high_util["Utilization (%)"].round(1)
                    st.markdown(f"**{len(high_util)} days** exceeded 85% line utilization:")
                    st.dataframe(high_util.head(20), hide_index=True, use_container_width=True)
                    if len(high_util) > 20:
                        st.caption(f"Showing 20 of {len(high_util)} days.")
                    st.markdown("High utilization days are prime candidates for DLR deployment — these are the corridors where dynamic ratings would have the most immediate impact on congestion relief.")

                elif "correlation" in ql or ("wind" in ql and "congestion" in ql):
                    corr = grid_df["wind_gen_mw"].corr(grid_df["congestion_cost_m"])
                    fig = go.Figure(go.Scatter(x=grid_df["wind_gen_mw"], y=grid_df["congestion_cost_m"], mode="markers", marker=dict(color=BLUE, size=4, opacity=0.5)))
                    fig.update_layout(title=f"Wind generation vs congestion cost (r = {corr:.2f})", xaxis_title="Wind Generation (MW)", yaxis_title="Congestion Cost ($M)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    direction = "positive" if corr > 0 else "negative"
                    st.markdown(f"The correlation is **{corr:.2f}** ({direction}). {'Higher wind can increase congestion when transmission constraints prevent power delivery to load centers — exactly the problem DLR solves by unlocking more line capacity.' if corr > 0 else 'Higher wind tends to reduce congestion costs by displacing more expensive generation.'}")

                else:
                    monthly_summary = grid_df.groupby("quarter").agg({"load_mw": "mean", "congestion_cost_m": "sum", "reserve_margin_pct": "mean", "line_utilization_pct": "mean"}).round(1).reset_index()
                    monthly_summary.columns = ["Quarter", "Avg Load (MW)", "Total Congestion ($M)", "Avg Reserve Margin (%)", "Avg Line Utilization (%)"]
                    st.markdown(f"Here's a quarterly summary of the grid data that's relevant to your question:")
                    st.dataframe(monthly_summary, hide_index=True, use_container_width=True)
                    st.markdown(f"""Based on the data, the grid shows clear seasonal patterns:
- **Peak load and congestion** occur in summer (Q3) when cooling demand drives utilization up
- **Reserve margins tighten** during peak periods, increasing reliability risk
- **Line utilization** averages {grid_df['line_utilization_pct'].mean():.0f}% but spikes to {grid_df['line_utilization_pct'].max():.0f}% — DLR would unlock significant headroom on those peak days

Try asking a more specific question like "What were the top 5 highest congestion cost days?" for deeper analysis.""")

        render_comments("demo_llm", "Ask the Data (LLM)")

        st.markdown('<div class="callout-box"><b>What you\'re seeing:</b> This demonstrates <b>Cortex Analyst</b> — Snowflake\'s natural language query engine. In production, MISO engineers would ask questions about study data, market data, and grid operations in plain English. No SQL. No waiting for reports. No submitting tickets to the data team.</div>', unsafe_allow_html=True)

    elif demo_tab == "ML recommendations":
        st.markdown('<p class="section-header">ML-driven grid recommendations — real-time decision support</p>', unsafe_allow_html=True)
        st.markdown("Snowflake's ML models continuously analyze current grid conditions and generate actionable recommendations for operators.")

        st.markdown("#### Set current grid conditions")
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            cur_temp = st.number_input("Temperature (°F)", 0, 120, 58, key="ml_temp")
        with rc2:
            cur_wind = st.number_input("Wind speed (mph)", 0, 50, 14, key="ml_wind")
        with rc3:
            cur_load = st.number_input("System load (GW)", 50, 150, 95, key="ml_load")
        with rc4:
            cur_season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"], key="ml_season")

        if st.button("Generate ML recommendations", type="primary", icon=":material/model_training:", use_container_width=True):
            with st.spinner("ML model evaluating conditions..."):
                time.sleep(2)

            static_cap = 1200
            tf = max(0.4, 1.0 - (cur_temp - 40) * 0.008)
            wf = 1.0 + cur_wind * 0.015
            sf = 0.92
            aar_cap = static_cap * tf * sf
            dlr_cap = static_cap * tf * wf * sf
            aar_gain = ((aar_cap - static_cap) / static_cap) * 100
            dlr_gain = ((dlr_cap - static_cap) / static_cap) * 100

            load_ratio = cur_load / 120
            season_risk = {"Spring": 0.3, "Summer": 0.9, "Fall": 0.4, "Winter": 0.7}[cur_season]
            congestion_prob = min(95, max(5, load_ratio * 60 + season_risk * 25 - cur_wind * 0.5))
            reliability_score = min(100, max(20, 85 - (load_ratio - 0.7) * 80 + cur_wind * 0.3 - season_risk * 10))
            anomaly_risk = min(90, max(5, abs(cur_temp - 65) * 0.8 + (cur_load - 85) * 0.3 + season_risk * 15))

            st.markdown('<p class="section-header">Model output: Current conditions assessment</p>', unsafe_allow_html=True)

            with st.container(horizontal=True):
                st.metric("Congestion probability", f"{congestion_prob:.0f}%", "High" if congestion_prob > 60 else "Moderate" if congestion_prob > 35 else "Low", border=True)
                st.metric("Reliability score", f"{reliability_score:.0f}/100", "Good" if reliability_score > 70 else "At risk" if reliability_score > 50 else "Critical", border=True)
                st.metric("Study anomaly risk", f"{anomaly_risk:.0f}%", "Elevated" if anomaly_risk > 50 else "Normal", border=True)
                st.metric("DLR capacity available", f"{dlr_cap:.0f} MW", f"{dlr_gain:+.0f}% vs static", border=True)

            st.markdown('<p class="section-header">AI recommendations</p>', unsafe_allow_html=True)

            recs = []
            if dlr_gain > 10:
                recs.append({
                    "priority": "High",
                    "category": "Capacity optimization",
                    "icon": ":material/trending_up:",
                    "title": f"Activate DLR on constrained corridors — {dlr_gain:+.0f}% capacity available",
                    "detail": f"Current conditions (temp: {cur_temp}°F, wind: {cur_wind} mph) support a DLR rating of **{dlr_cap:.0f} MW** vs the static rating of {static_cap} MW. This unlocks **{dlr_cap - static_cap:.0f} MW** of additional transfer capability on the Midwest Corridor alone.",
                    "action": "Apply dynamic rating to top 10 constrained flowgates. Estimated congestion savings: $2.1M today.",
                })
            elif aar_gain > 3:
                recs.append({
                    "priority": "Medium",
                    "category": "Capacity optimization",
                    "icon": ":material/trending_up:",
                    "title": f"AAR adjustment recommended — {aar_gain:+.0f}% above static",
                    "detail": f"Ambient conditions support an AAR of **{aar_cap:.0f} MW**. Even without DLR sensors, this provides incremental capacity.",
                    "action": "Update ambient-adjusted ratings for temperature-sensitive corridors.",
                })

            if congestion_prob > 50:
                recs.append({
                    "priority": "High",
                    "category": "Congestion management",
                    "icon": ":material/warning:",
                    "title": f"Elevated congestion risk detected — {congestion_prob:.0f}% probability",
                    "detail": f"Load at {cur_load} GW during {cur_season.lower()} creates transmission bottlenecks. Historical patterns show {congestion_prob:.0f}% probability of significant congestion events under these conditions.",
                    "action": "Pre-position reserves on constrained interfaces. Consider accelerating planned outage returns.",
                })

            if anomaly_risk > 45:
                recs.append({
                    "priority": "Medium",
                    "category": "Study data quality",
                    "icon": ":material/search:",
                    "title": f"Elevated anomaly risk in study inputs — {anomaly_risk:.0f}% likelihood",
                    "detail": f"Current conditions deviate from seasonal norms. ML model flags a {anomaly_risk:.0f}% probability that today's study inputs contain statistical anomalies that manual review would miss.",
                    "action": "Run Cortex AI anomaly scan on today's study inputs before executing scheduled reliability studies.",
                })

            if reliability_score < 65:
                recs.append({
                    "priority": "Critical" if reliability_score < 50 else "High",
                    "category": "Reliability",
                    "icon": ":material/error:" if reliability_score < 50 else ":material/shield:",
                    "title": f"Reliability score below threshold — {reliability_score:.0f}/100",
                    "detail": f"System conditions suggest tightening margins. Load-to-capacity ratio is elevated for {cur_season.lower()} conditions.",
                    "action": "Review contingency plans. Validate study assumptions against current operating conditions. Consider conservative operating posture.",
                })

            recs.append({
                "priority": "Info",
                "category": "Continuous learning",
                "icon": ":material/auto_awesome:",
                "title": "Model confidence: Updated with latest 30-day operational data",
                "detail": "Recommendations incorporate historical patterns, real-time weather, and the most recent study results. Each study run feeds back into the model, improving prediction accuracy over time.",
                "action": "No action required. Model retrains continuously on Snowflake's elastic compute.",
            })

            for rec in recs:
                priority_colors = {"Critical": "red", "High": "orange", "Medium": "blue", "Info": "gray"}
                badge_color = priority_colors.get(rec["priority"], "gray")
                with st.container(border=True):
                    header_cols = st.columns([3, 1])
                    with header_cols[0]:
                        st.markdown(f"{rec['icon']} **{rec['title']}**")
                    with header_cols[1]:
                        st.badge(rec["priority"], color=badge_color)
                    st.caption(rec["detail"])
                    st.markdown(f"**Recommended action:** {rec['action']}")

            render_comments("demo_ml", "ML Recommendations")

            st.markdown('<div class="callout-box"><b>What you\'re seeing:</b> This is <b>Cortex ML</b> generating real-time, condition-based recommendations. In production, these models run continuously on Snowflake — ingesting weather, load, and study data to provide operators with proactive guidance. No manual analysis. No waiting. The grid tells you what it needs.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE 2: EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════
elif "Executive overview" in page:
    st.markdown('<p class="hero-title">Why Snowflake for MISO</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Executive overview — Market Operations leadership</p>', unsafe_allow_html=True)

    with st.container(horizontal=True):
        st.metric("Annual market value", ">$40B", help="Annual energy transactions managed by MISO", border=True)
        st.metric("People served", "42M", help="Across 15 U.S. states + 1 Canadian province", border=True)
        st.metric("Member utilities", "~400", border=True)
        st.metric("Annual member benefits", "$5.1B", "15:1 ROI", border=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        ":material/target: What we're solving",
        ":material/bolt: What Snowflake unlocks",
        ":material/compare_arrows: Current vs. future state",
        ":material/people: Value to members",
        ":material/format_quote: 30-second pitch",
    ])

    with tab1:
        st.markdown("### What we're solving for")
        st.markdown("""
MISO runs grid reliability studies daily using specialized engines (PowerGem, GE) — but study inputs, outputs, and insights are **siloed across disconnected systems**.

- **Anomaly detection is manual** — engineers spend weeks hunting for statistical abnormalities in study data
- **The low-hanging fruit is already picked** — what remains requires AI at scale to detect
- **Cloud-containerized studies** (PowerGem/GE) are creating new orchestration demands no current tool addresses
- **No single platform** exists to build predictive models, deploy them, and let engineers interact with results
""")
        st.markdown("### Why it matters now")
        st.markdown("""
- MISO's **$1.8B-$3.7B/year** in congestion costs are driven partly by stale seasonal ratings and undetected anomalies
- The interconnection queue has **~216 projects / 32 GW backlogged**, averaging ~2.5 years behind schedule
- **FERC Order 881** is mandating the move from static to ambient-adjusted ratings
- Peer RTOs (ERCOT, PJM) and utilities (AEP) are already running production AI workloads on Snowflake
""")

    with tab2:
        st.markdown("### What Snowflake unlocks that MISO can't do today")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**:material/speed: Study acceleration**")
                st.markdown("Studies that take weeks run in hours. AI scans historical runs and surfaces anomalies in seconds.")
            with st.container(border=True):
                st.markdown("**:material/psychology: Predictive what-if modeling**")
                st.markdown("Engineers run scenarios in real time before committing to full study runs. Catch issues earlier, eliminate reruns.")
        with c2:
            with st.container(border=True):
                st.markdown("**:material/dynamic_feed: Dynamic line ratings**")
                st.markdown("Move from quarterly static ratings to hourly dynamic ratings using ML + weather data. Unlock 30-50% more capacity.")
            with st.container(border=True):
                st.markdown("**:material/hub: One platform**")
                st.markdown("Data + AI + applications in a single environment. No more stitching across five tools.")

        st.markdown("### Current vs. future state")
        improvements = pd.DataFrame({
            "Capability": ["Line ratings", "Anomaly detection", "Study turnaround", "Data architecture", "Grid modeling", "Operations mode", "Engineer workflow"],
            "Today": ["Quarterly/seasonal static", "Weeks of manual review", "Weeks per cycle", "5+ disconnected tools", "Quarterly static updates", "Reactive (find after)", "Wait for reports"],
            "With Snowflake": ["Hourly dynamic (AAR then DLR)", "Seconds with Cortex AI", "Hours per cycle", "One unified platform", "Real-time digital twin", "Proactive (predict before)", "Self-service scenarios"],
        })
        st.dataframe(improvements, hide_index=True, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### :red[Today]")
            with st.container(border=True):
                st.markdown("""
- :red-badge[Static] Line ratings updated quarterly — worst-case assumptions
- :red-badge[Manual] Engineers spend weeks hunting anomalies by hand
- :red-badge[Siloed] PowerGem, GE, and market data in separate systems
- :red-badge[Reactive] Issues found after they happen
- :red-badge[Wasted] 40-50% capacity unused on favorable days
- :red-badge[Slow] Studies take weeks per cycle
- :red-badge[Fragmented] Data here, models there, dashboards somewhere else
""")
        with c2:
            st.markdown("#### :green[With Snowflake]")
            with st.container(border=True):
                st.markdown("""
- :green-badge[Dynamic] Hourly ratings via AAR then DLR (5-50% capacity gain)
- :green-badge[AI-driven] Cortex AI scans studies in seconds
- :green-badge[Unified] One platform — data + AI + applications
- :green-badge[Proactive] Predict and prevent before impact
- :green-badge[Optimized] 85-100% of safe capacity utilized
- :green-badge[Fast] Studies run in hours, not weeks
- :green-badge[Integrated] Snowflake + Siemens xDT + Data Fabric
""")

    with tab4:
        st.markdown("### Value delivered to MISO's members & operations")
        st.markdown("""
MISO is a nonprofit — every improvement flows directly to ~400 member utilities and 42 million ratepayers.

- **Lower delivered energy costs** — Less congestion + less curtailment = lower costs to utilities and ratepayers
- **Higher grid reliability** — Proactive anomaly detection means fewer surprise events and more stable service
- **Faster interconnection** — Faster study turnaround means members connect new generation to the grid sooner
- **Greater transparency** — Unified analytics enables richer data sharing with members
- **Capital efficiency** — DLR unlocks existing capacity before spending billions on new transmission ($32.1B LRTP approved)
""")

    with tab5:
        st.markdown("### The 30-second pitch for Tim")
        with st.container(border=True):
            st.markdown("""
> *"MISO is modernizing data with Azure and Data Fabric — great move. Snowflake sits on top of that Azure investment and does what Data Fabric can't: elastic AI, predictive modeling, and real-time analytics at scale.*
>
> *Your team already spends weeks hunting anomalies in study data. With Snowflake, those same studies run faster, AI surfaces the needles in the haystack automatically, and every insight traces back to measurable grid reliability improvements.*
>
> *It doesn't replace anything you're building — it makes what you're building deliver value 10x faster."*
""")
        st.markdown("""
- Runs on Azure, consumes MISO's existing credits — no new cloud contracts
- Connects to Data Fabric via Apache Iceberg / OneLake — doesn't replace or slow it
- Starts as one isolated use case — 90-day evaluation, zero disruption
- ERCOT, PJM, and AEP are already running production workloads on Snowflake
""")

    render_comments("exec_overview", "Executive Overview")


# ═══════════════════════════════════════════════
# PAGE 3: BUSINESS VALUE ANALYSIS
# ═══════════════════════════════════════════════
elif "Business value" in page:
    st.markdown('<p class="hero-title">Business value analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Quantified impact on grid operations, market efficiency & member value</p>', unsafe_allow_html=True)

    with st.container(horizontal=True):
        st.metric("Annual congestion costs", "$1.8B-$3.7B", help="2022 peak driven by gas prices + Winter Storm Elliott", border=True)
        st.metric("Queue backlog", "~32 GW", "~216 projects", border=True)
        st.metric("LRTP approved capex", "$32.1B", "42 projects", border=True)
        st.metric("FERC max penalty", "$1M/day", "per violation", border=True)

    st.markdown('<p class="section-header">Value by category</p>', unsafe_allow_html=True)

    val_tab = st.segmented_control("Value category", ["Congestion reduction", "Study efficiency", "Reliability risk", "Capital deferral", "Summary"], default="Summary")

    if val_tab == "Congestion reduction":
        st.markdown("### Congestion cost reduction")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["2022", "2023", "2024"], y=[3.7, 1.8, 2.0], marker_color=[RED, BLUE, BLUE], text=["$3.7B", "$1.8B", "$2.0B"], textposition="outside"))
        fig.update_layout(title="MISO annual congestion costs ($B)", yaxis_title="$ Billions", height=350, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Root causes:**")
            st.markdown("- Stale seasonal line ratings (40-50% waste on favorable days)\n- Undetected anomalies in study input data\n- Reactive grid management\n- $350M from Winter Storm Elliott alone (2 days)")
        with c2:
            st.markdown("**Snowflake impact:**")
            st.markdown("- DLR + ML: **30-50% capacity increase** (NREL 2024)\n- AAR Phase 1: **5-15% gain**, no sensors\n- MISO/SPP study: GETs delivered **$175M/yr** (Brattle)\n- **Conservative: 2-5% reduction = $36M-$185M/yr**")

    elif val_tab == "Study efficiency":
        st.markdown("### Study efficiency & engineering productivity")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Current state:**\n- ~216 projects / 32 GW backlogged\n- Average delay: **~2.5 years** (900+ days)\n- Only **~13%** of queued projects reach commercial operation\n- Anomaly detection takes **weeks per cycle**")
        with c2:
            st.markdown("**With Snowflake:**\n- AI anomaly detection: **weeks to seconds**\n- Study cycle: **weeks to hours**\n- Predictive what-if eliminates unnecessary runs\n- **Savings: $2M-$5M/yr** in engineering efficiency")
        comparison = pd.DataFrame({"Metric": ["Anomaly detection", "Study cycle", "Reruns", "Engineer workflow"], "Today": ["2-3 weeks", "Weeks/cycle", "Frequent", "Reactive review"], "With Snowflake": ["2-3 seconds", "Hours/cycle", "Rare (AI pre-screen)", "Proactive scenarios"]})
        st.dataframe(comparison, hide_index=True, use_container_width=True)

    elif val_tab == "Reliability risk":
        st.markdown("### Reliability risk mitigation")
        st.markdown("- FERC can levy **$1M/day/violation** for reliability failures\n- FY2025 enforcement settlements: **$36.6M**\n- Undetected study anomalies can cause load shedding for **42M people**")
        st.markdown("**Snowflake reduces risk by:**\n- AI scanning study data at scale\n- Shifting from post-event to **pre-event prevention**\n- Strengthening NERC/FERC compliance\n- **Avoided costs: $5M-$20M/yr**")

    elif val_tab == "Capital deferral":
        st.markdown("### Transmission capital deferral")
        st.markdown(f"MISO has **$32.1B** in approved new builds. New transmission: **$2M-$5M/mile**, **7-10 years** to build.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("- DLR unlocks **30-50%** more capacity from existing lines\n- Single DLR project < **1 mile of new transmission** cost (Brattle)\n- PPL: **$64M savings year one**, 30% capacity gain\n- **Conservative: $50M-$200M/yr** deferred capex")
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=["New transmission\n(per mile)", "DLR deployment\n(per segment)"], y=[3.5, 0.125], marker_color=[RED, GREEN], text=["$2M-$5M", "$50K-$200K"], textposition="outside"))
            fig.update_layout(title="Cost comparison", yaxis_title="$ Millions", height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    elif val_tab == "Summary":
        st.markdown("### Annual value summary")
        categories = ["Congestion\nreduction", "Study\nefficiency", "Reliability\nrisk", "Capital\ndeferral"]
        low = [36, 2, 5, 50]
        high = [185, 5, 20, 200]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Conservative", x=categories, y=low, marker_color=BLUE, text=[f"${v}M" for v in low], textposition="outside"))
        fig.add_trace(go.Bar(name="High estimate", x=categories, y=high, marker_color=NAVY, text=[f"${v}M" for v in high], textposition="outside"))
        fig.update_layout(title="Estimated annual value ($M)", yaxis_title="$ Millions/Year", height=420, barmode="group", margin=dict(t=40, b=80), legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        with st.container(horizontal=True):
            st.metric("Total annual value", "$93M - $410M", border=True)
            st.metric("Snowflake investment", "~$100K - $500K/yr", border=True)
            st.metric("Implied ROI", "186x - 4,100x", border=True)

        st.markdown('<div class="callout-box"><b>Bottom line:</b> MISO sells reliability, efficiency, and market fairness. Snowflake makes MISO measurably better at all three. Conservative annual value: <b>$93M-$410M</b> against a $100K-$500K investment.</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-header">Why less-technical executives should care</p>', unsafe_allow_html=True)
    st.markdown("""
- **Faster decisions, fewer surprises** — Leadership gets answers in hours, not weeks
- **Reduced congestion costs** — Proactive detection catches problems before costly curtailments
- **More capacity from existing infrastructure** — 30-50% more on favorable days, no new lines
- **No new budget required** — Runs on Azure credits MISO already owns
- **Protects existing investments** — Accelerates Data Fabric ROI, doesn't replace it
- **Grid reliability = MISO's mission** — Every improvement = more reliable electricity for 42M people
""")

    with st.expander("Sources & references", icon=":material/link:"):
        st.markdown("""
- [Potomac Economics — 2023 MISO State of the Market](https://www.potomaceconomics.com/wp-content/uploads/2024/06/2023-MISO-SOM_Report_Body-Final.pdf)
- [Potomac Economics — 2024 MISO State of the Market](https://www.potomaceconomics.com/wp-content/uploads/2025/06/2024-MISO-SOM_Report_Body_Final.pdf)
- [NREL — Hourly Dynamic Line Ratings (2024)](https://docs.nrel.gov/docs/fy25osti/91599.pdf)
- [WATT Coalition — About Dynamic Line Ratings](https://watt-transmission.org/about-dynamic-line-ratings/)
- [Brattle Group — GETs Could Save >$100B (2026)](https://www.brattle.com/insights-events/news/new-brattle-report-finds-better-utilization-of-existing-power-grid-could-save-us-consumers-more-than-100-billion-in-the-next-decade/)
- [PPL DLR Deployment Results](https://www.powermag.com/why-utilities-cant-afford-to-wait-to-deploy-dlr/)
- [Lawrence Berkeley National Lab — Queued Up 2024](https://emp.lbl.gov/publications/queued-2024-edition-characteristics)
- [MISO 2024 Value Proposition ($5.1B)](https://electricenergyonline.com/article/energy/category/financial/51/1131280/miso-annual-benefits-top-5-billion.html)
- [FERC FY2025 Enforcement Report](https://www.ferc.gov/sites/default/files/2025-11/FY2025%20Report%20on%20Enforcement.pdf)
- [FERC — Explainer on Dynamic Line Ratings](https://www.ferc.gov/explainer-implementation-dynamic-line-ratings)
""")

    render_comments("biz_value", "Business Value Analysis")


# ═══════════════════════════════════════════════
# PAGE 4: ONSITE AGENDA
# ═══════════════════════════════════════════════
elif "Onsite agenda" in page:
    st.markdown('<p class="hero-title">Snowflake Day at MISO — onsite plan</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Proposed agenda for executive working session</p>', unsafe_allow_html=True)

    with st.container(horizontal=True):
        st.metric("Duration", "3 hours", border=True)
        st.metric("Format", "Executive briefing + live demo", border=True)
        st.metric("Location", "MISO conference room", border=True)
        st.metric("Cost to MISO", "$0", border=True)

    st.markdown("### Attendees")
    attendees = pd.DataFrame({
        "Name": ["Tim Aliff", "Amber Alewine", "Bonnie Matthews", "Ben Boutwell"],
        "Title": ["Executive Director, Market Operations", "Director, Forward Markets", "IT Architecture", "Principal Engineer"],
        "Role in session": ["Decision maker — needs the 'why should we care' answer", "Incoming stakeholder — assess strategic fit", "Technical gatekeeper — validate Azure/Fabric compatibility", "Champion — validate use case fit and technical depth"],
    })
    st.dataframe(attendees, hide_index=True, use_container_width=True)

    st.markdown('<p class="section-header">Proposed agenda</p>', unsafe_allow_html=True)

    agenda = [
        ("0:00 - 0:15", "Welcome & context setting", "Introductions, MISO priorities recap, session objectives. Frame: what Snowflake adds to Azure/Fabric — not what it replaces.", "Kala Boudreaux"),
        ("0:15 - 0:35", "Executive value overview", "Why Snowflake, why now, why MISO should care. Complement to Data Fabric. 30-second pitch. Industry peers already on Snowflake.", "Kala + Jordan"),
        ("0:35 - 0:50", "Use case deep-dive: Study orchestration", "MISO's priority use case. How study I/O processing, anomaly detection, and what-if modeling converge on one platform.", "Jordan Ude"),
        ("0:50 - 1:20", "Live demo: DLR + anomaly detection + what-if", "Interactive demonstration. Attendees adjust parameters, see AI in action. The 'wow' moment.", "Jordan + Eric"),
        ("1:20 - 1:30", "Break", "", ""),
        ("1:30 - 1:50", "Snowflake + Siemens: AAR to DLR architecture", "Phased approach. Unified Namespace, Executable Digital Twin, Cortex AI. Runs on existing Azure credits.", "Jordan Ude"),
        ("1:50 - 2:10", "Business value & ROI", "Quantified value: congestion ($36M-$185M/yr), study efficiency, reliability risk, capital deferral. $93M-$410M annual estimate.", "Kala Boudreaux"),
        ("2:10 - 2:30", "Azure & Data Fabric compatibility", "For Bonnie: Apache Iceberg, OneLake, Azure AD/RBAC, security. How Snowflake connects without disrupting Fabric.", "Eric Szenderski"),
        ("2:30 - 2:50", "Open discussion & Q&A", "Address concerns, explore additional use cases, discuss IDEA Group and AI CoP broader engagement.", "All"),
        ("2:50 - 3:00", "Next steps & 90-day evaluation proposal", "One use case, existing Azure credits, parallel to Fabric. Align on timeline and success criteria.", "Kala Boudreaux"),
    ]

    for t, item, detail, owner in agenda:
        if not detail:
            st.caption(f"**{t}** — {item}")
            continue
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"**{t}**")
                if owner:
                    st.caption(owner)
            with c2:
                st.markdown(f"**{item}**")
                st.caption(detail)

    st.markdown('<p class="section-header">Session goals</p>', unsafe_allow_html=True)
    st.markdown("""
**Primary goal:** MISO leadership has a clear, confident understanding of how Snowflake accelerates grid reliability, reduces congestion costs, and complements the existing Data Fabric investment — with a defined path to evaluate.

**By stakeholder:**
- **Tim** has confidence that Snowflake strengthens (not duplicates) the Azure/Fabric strategy and delivers measurable operational ROI
- **Amber** sees how Snowflake supports forward market planning and aligns with her team's priorities
- **Bonnie** confirms Snowflake integrates cleanly with Azure AD, Iceberg, OneLake, and existing security policies
- **Ben** has the executive alignment needed to move forward with a focused 90-day evaluation
""")

    st.markdown('<p class="section-header">Logistics</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Snowflake team**\n- Kala Boudreaux — Account Executive\n- Jordan Ude — Solutions Engineer\n- Eric Szenderski — District Manager")
    with c2:
        st.markdown("**Requirements**\n- Conference room with screen/projector\n- Wi-Fi access for demo\n- No MISO data or security approvals needed")

    st.markdown('<p class="section-header">Next steps: Solution accelerator</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
**Solution Accelerator** — Snowflake creates an accelerator to show real-time load forecasting, weather impacts, and risk assessment capabilities that is built with synthetic data to demonstrate value quickly.

The goal is demonstrating tangible business value to MISO's decision-makers. The typical solution accelerator approach uses simulated data first, followed by potential deployment with real data.

**Phase 1 — Synthetic data accelerator**
1. Snowflake builds a working solution accelerator using simulated MISO-like grid data
2. Demonstrates load forecasting, anomaly detection, DLR, and what-if scenario capabilities
3. No MISO data or security approvals required — ready to demo within weeks

**Phase 2 — Real data deployment**
4. With executive approval, connect to MISO's actual study data and grid operations
5. Validate results against real operational outcomes
6. Scale from proof-of-value to production capability
""")

    render_comments("onsite_agenda", "Onsite Agenda")
