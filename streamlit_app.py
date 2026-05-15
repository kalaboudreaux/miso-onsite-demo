import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

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

# ═══════════════════════════════════════════════
# PAGE 1: INTERACTIVE DEMO
# ═══════════════════════════════════════════════
if "Interactive demo" in page:
    st.markdown('<p class="hero-title">Grid intelligence, powered by Snowflake</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Interactive demonstration of AI-driven grid operations for MISO</p>', unsafe_allow_html=True)

    demo_tab = st.segmented_control(
        "Select demo",
        ["Dynamic line rating", "Study anomaly detection", "What-if scenario modeling"],
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

                st.markdown('<div class="callout-box"><b>What you\'re seeing:</b> Engineers adjust parameters and see predicted outcomes <b>in seconds</b> — before committing to full PowerGem/GE study runs that take weeks. Data + AI + application in one platform.</div>', unsafe_allow_html=True)
            else:
                st.info("Adjust scenario parameters and click **Run scenario** to see predictive results.", icon=":material/tune:")


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
**Primary goal:** Attendees walk away saying *"How soon can we have this?"*

**By stakeholder:**
- **Tim** leaves confident Snowflake doesn't duplicate Fabric — it accelerates its ROI
- **Amber** sees strategic fit for forward market operations and planning
- **Bonnie** validates technical compatibility with Azure, AD, and existing security
- **Ben** has executive buy-in to move forward with 90-day evaluation
""")

    st.markdown('<p class="section-header">Logistics</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Snowflake team**\n- Kala Boudreaux — Account Executive\n- Jordan Ude — Solutions Engineer\n- Eric Szenderski — District Manager")
    with c2:
        st.markdown("**Requirements**\n- Conference room with screen/projector\n- Wi-Fi access for demo\n- No MISO data or security approvals needed")

    st.markdown("**Pre-session checklist:**")
    st.markdown("1. Ben reviews and approves this agenda\n2. Snowflake prepares demo environments with public energy data\n3. Ben confirms attendee availability and room booking\n4. Kala sends calendar invite with session overview")
