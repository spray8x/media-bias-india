import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))
from fetcher import fetch_all
from sentiment import analyze_sentiment

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Indian Media Bias Dashboard",
    page_icon=None,
    layout="wide",
)

# ── Theme injection ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #0d1b2a;
        background-image:
            linear-gradient(#1a2f4518 1px, transparent 1px),
            linear-gradient(90deg, #1a2f4518 1px, transparent 1px);
        background-size: 24px 24px;
    }

    .main .block-container {
        background: transparent;
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        background-color: #0a1520 !important;
        border-right: 1px solid #1a2f45;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #7a9ab8 !important;
        font-size: 12px;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #c8d8e8 !important;
    }

    h1 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 22px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        letter-spacing: -0.01em;
        margin-bottom: 0.25rem !important;
    }
    h2, h3 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        color: #c8d8e8 !important;
        letter-spacing: -0.01em;
    }
    h3 { font-size: 14px !important; text-transform: uppercase; letter-spacing: 0.08em; color: #7a9ab8 !important; }

    p, li { color: #7a9ab8; font-size: 13px; }
    .stMarkdown p { color: #7a9ab8; }

    [data-testid="stMetric"] {
        background: #0a1520;
        border: 1px solid #1a2f45;
        padding: 1rem 1.25rem;
        border-radius: 0;
    }
    [data-testid="stMetricLabel"] p {
        color: #7a9ab8 !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 22px !important;
    }
    [data-testid="stMetricDelta"] {
        color: #a78bfa !important;
        font-size: 11px !important;
    }

    .stButton button {
        background: transparent;
        border: 1px solid #1a2f45;
        color: #7a9ab8;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.06em;
        border-radius: 0;
        padding: 0.4rem 1rem;
        transition: all 0.15s;
    }
    .stButton button:hover {
        background: #7c3aed22;
        border-color: #7c3aed55;
        color: #c4b5fd;
    }

    .stTextInput input {
        background: #0a1520 !important;
        border: 1px solid #1a2f45 !important;
        border-radius: 0 !important;
        color: #ffffff !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 13px !important;
    }
    .stTextInput input:focus {
        border-color: #7c3aed !important;
        box-shadow: none !important;
    }
    .stTextInput label {
        color: #7a9ab8 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .stSelectbox > label {
        color: #7a9ab8 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .stSelectbox [data-baseweb="select"] {
        background: #0a1520 !important;
        border: 1px solid #1a2f45 !important;
        border-radius: 0 !important;
    }
    .stSelectbox [data-baseweb="select"] * {
        color: #ffffff !important;
        background: #0a1520 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #1a2f45;
    }
    [data-testid="stDataFrame"] th {
        background: #0a1520 !important;
        color: #7a9ab8 !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-bottom: 1px solid #1a2f45 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    [data-testid="stDataFrame"] td {
        background: #0d1b2a !important;
        color: #c8d8e8 !important;
        border-bottom: 1px solid #1a2f4533 !important;
        font-size: 12px !important;
    }

    hr { border-color: #1a2f45 !important; margin: 1.5rem 0 !important; }

    .stAlert {
        background: #0a1520 !important;
        border: 1px solid #1a2f45 !important;
        border-radius: 0 !important;
        color: #7a9ab8 !important;
    }

    .stRadio label { color: #7a9ab8 !important; font-size: 13px !important; }
    .stRadio label:hover { color: #fff !important; }

    .stCaption { color: #4a6a8a !important; font-size: 11px !important; font-family: 'IBM Plex Mono', monospace !important; }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0a1520; }
    ::-webkit-scrollbar-thumb { background: #1a2f45; }
    ::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

    .stSpinner > div { border-top-color: #a78bfa !important; }

    /* hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Dataframe overrides ─────────────────────────────────────────────── */
    [data-testid="stDataFrame"] > div {
        background: transparent !important;
        border: 1px solid #1a2f45 !important;
        border-radius: 0 !important;
    }
    [data-testid="stDataFrame"] iframe {
        background: transparent !important;
    }
    .dvn-scroller {
        background: #0a1520 !important;
    }
    .glideDataEditor {
        background: #0a1520 !important;
    }
    .gdg-style {
        background: #0a1520 !important;
    }
    /* ── Custom table ────────────────────────────────────────────────────── */
    table tr {
        border-bottom: 1px solid #1a2f4533;
        transition: background 0.1s;
    }
    table tr:hover {
        background: #1a2f4544 !important;
    }
    table td {
        padding: 9px 12px;
        color: #7a9ab8;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
CACHE_FILE  = "data/articles.csv"
CACHE_HOURS = 6
LEAN_ORDER  = ["Far Right", "Moderate Right", "Centre", "Moderate Left", "Far Left"]
LEAN_COLORS = {
    "Far Right":      "#c0392b",
    "Moderate Right": "#e67e22",
    "Centre":         "#4a6a8a",
    "Moderate Left":  "#2980b9",
    "Far Left":       "#1a4a8a",
}
SENTIMENT_COLORS = {
    "Positive": "#4ade80",
    "Negative": "#f87171",
    "Neutral":  "#4a6a8a",
}


# ── Plotly theme helper ───────────────────────────────────────────────────────
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="#0a1520",
        plot_bgcolor="#0a1520",
        font=dict(color="#7a9ab8", family="IBM Plex Sans, sans-serif", size=11),
        xaxis=dict(
            gridcolor="#1a2f45",
            linecolor="#1a2f45",
            tickcolor="#1a2f45",
            tickfont=dict(color="#7a9ab8", size=10),
            title_font=dict(color="#7a9ab8", size=11),
        ),
        yaxis=dict(
            gridcolor="#1a2f45",
            linecolor="#1a2f45",
            tickcolor="#1a2f45",
            tickfont=dict(color="#7a9ab8", size=10),
            title_font=dict(color="#7a9ab8", size=11),
        ),
        legend=dict(
            bgcolor="#0a1520",
            bordercolor="#1a2f45",
            borderwidth=1,
            font=dict(color="#7a9ab8", size=10),
        ),
        margin=dict(t=20, b=30, l=10, r=10),
    )
    return fig


# ── Data loading ──────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(CACHE_FILE):
        df = pd.read_csv(CACHE_FILE)
        if "sentiment_compound" in df.columns:
            last_fetched = pd.to_datetime(df["fetched_at"].iloc[0])
            age = datetime.now() - last_fetched
            if age < timedelta(hours=CACHE_HOURS):
                return df, last_fetched

    with st.spinner("Fetching latest articles..."):
        df = fetch_all()
        df = analyze_sentiment(df)
        df.to_csv(CACHE_FILE, index=False)

    return df, datetime.now()


# ── Load ──────────────────────────────────────────────────────────────────────
df, last_fetched = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Navigation")
    view = st.radio("", ["Overview", "Topic Explorer", "Outlet Profile"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("Refresh Data"):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        st.rerun()
    st.markdown("---")
    st.markdown(f"**Articles:** {len(df)}")
    st.markdown(f"**Outlets:** {df['outlet'].nunique()}")
    st.markdown(f"**Updated:** {last_fetched.strftime('%d %b, %I:%M %p')}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Indian Media Bias & Sentiment Dashboard")
st.caption(f"Tracking {df['outlet'].nunique()} Indian news outlets across the political spectrum — data as of {last_fetched.strftime('%d %b %Y, %I:%M %p')}")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if view == "Overview":

    st.markdown("### The Big Picture")

    # metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Articles", len(df))
    col2.metric("Outlets Tracked", df["outlet"].nunique())
    col3.metric(
        "Most Negative Lean",
        df.groupby("lean")["sentiment_compound"].mean().idxmin()
    )
    col4.metric(
        "Most Positive Lean",
        df.groupby("lean")["sentiment_compound"].mean().idxmax()
    )

    st.markdown("---")

    # volume + sentiment side by side
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### Article Volume by Lean")
        volume = (
            df["lean"].value_counts()
            .reindex(LEAN_ORDER)
            .reset_index()
        )
        volume.columns = ["Lean", "Count"]
        fig_vol = px.bar(
            volume, x="Lean", y="Count",
            color="Lean", color_discrete_map=LEAN_COLORS,
        )
        fig_vol.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig_vol), use_container_width=True)

    with col_r:
        st.markdown("### Average Sentiment by Lean")
        sent_avg = (
            df.groupby("lean")["sentiment_compound"]
            .mean()
            .reindex(LEAN_ORDER)
            .reset_index()
        )
        sent_avg.columns = ["Lean", "Avg Compound Score"]
        fig_sent = px.bar(
            sent_avg, x="Lean", y="Avg Compound Score",
            color="Lean", color_discrete_map=LEAN_COLORS,
        )
        fig_sent.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig_sent), use_container_width=True)

    st.markdown("---")

    # sentiment distribution
    st.markdown("### Sentiment Distribution Across the Spectrum")
    dist = (
        df.groupby(["lean", "sentiment_label"])
        .size()
        .reset_index(name="count")
    )
    dist["lean"] = pd.Categorical(dist["lean"], categories=LEAN_ORDER, ordered=True)
    dist = dist.sort_values("lean")
    fig_dist = px.bar(
        dist, x="lean", y="count",
        color="sentiment_label", barmode="group",
        color_discrete_map=SENTIMENT_COLORS,
        labels={"lean": "Lean", "count": "Articles", "sentiment_label": "Sentiment"},
    )
    st.plotly_chart(style_fig(fig_dist), use_container_width=True)

    st.markdown("---")

    # raw table
    st.markdown("### All Articles")
    table_df = (
        df[["outlet", "lean", "title", "sentiment_label", "sentiment_compound"]]
        .sort_values("sentiment_compound")
        .reset_index(drop=True)
    )

    sentiment_colors = {"Positive": "#4ade80", "Negative": "#f87171", "Neutral": "#4a6a8a"}

    rows = []
    for _, row in table_df.iterrows():
        dot  = sentiment_colors.get(row["sentiment_label"], "#4a6a8a")
        lean = LEAN_COLORS.get(row["lean"], "#4a6a8a")
        rows.append(
            f"<tr>"
            f"<td>{row['outlet']}</td>"
            f"<td style='color:{lean}'>{row['lean']}</td>"
            f"<td style='color:#c8d8e8'>{row['title']}</td>"
            f"<td><span style='color:{dot}'>&#9632;</span> {row['sentiment_label']}</td>"
            f"<td style='font-family:IBM Plex Mono,monospace;color:{dot}'>{round(row['sentiment_compound'], 4)}</td>"
            f"</tr>"
        )

    th = "style='text-align:left;padding:10px 12px;color:#7a9ab8;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;border-bottom:1px solid #1a2f45'"
    td_style = "table tr{border-bottom:1px solid #1a2f4533} table tr:hover{background:#1a2f4544} table td{padding:9px 12px;color:#7a9ab8;vertical-align:middle}"

    html = (
        f"<style>{td_style}</style>"
        f"<div style='overflow-x:auto'>"
        f"<table style='width:100%;border-collapse:collapse;font-size:12px;font-family:IBM Plex Sans,sans-serif'>"
        f"<thead><tr>"
        f"<th {th}>Outlet</th>"
        f"<th {th}>Lean</th>"
        f"<th {th}>Title</th>"
        f"<th {th}>Sentiment</th>"
        f"<th {th}>Score</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table></div>"
    )

    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2 — TOPIC EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Topic Explorer":

    st.markdown("### Topic Explorer")
    st.caption("Search a keyword and see how different sides of the spectrum covered it.")

    query = st.text_input("Keyword", placeholder="e.g. Modi, inflation, Pakistan, election")

    if query:
        mask = (
            df["title"].str.contains(query, case=False, na=False) |
            df["description"].str.contains(query, case=False, na=False)
        )
        results = df[mask].copy()

        if len(results) == 0:
            st.warning(f"No articles found for '{query}'. Try a different keyword.")
        else:
            st.caption(f"{len(results)} articles matched")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            col1.metric("Articles Found", len(results))
            col2.metric("Most Coverage From", results["lean"].value_counts().idxmax())
            col3.metric("Avg Sentiment", round(results["sentiment_compound"].mean(), 3))

            st.markdown("---")

            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown("### Coverage Volume by Lean")
                vol = (
                    results["lean"].value_counts()
                    .reindex(LEAN_ORDER).fillna(0)
                    .reset_index()
                )
                vol.columns = ["Lean", "Count"]
                fig_vol = px.bar(
                    vol, x="Lean", y="Count",
                    color="Lean", color_discrete_map=LEAN_COLORS,
                )
                fig_vol.update_layout(showlegend=False)
                st.plotly_chart(style_fig(fig_vol), use_container_width=True)

            with col_r:
                st.markdown("### Sentiment by Lean")
                sent = (
                    results.groupby("lean")["sentiment_compound"]
                    .mean()
                    .reindex(LEAN_ORDER)
                    .reset_index()
                )
                sent.columns = ["Lean", "Avg Compound Score"]
                fig_sent = px.bar(
                    sent, x="Lean", y="Avg Compound Score",
                    color="Lean", color_discrete_map=LEAN_COLORS,
                )
                fig_sent.update_layout(showlegend=False)
                st.plotly_chart(style_fig(fig_sent), use_container_width=True)

            st.markdown("---")

            # side by side headline comparison
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("### Left Leaning")
                left = results[results["lean"].isin(["Far Left", "Moderate Left"])]
                if len(left) == 0:
                    st.info("No left-leaning articles for this topic.")
                else:
                    for _, row in left.iterrows():
                        dot = {"Positive": "green", "Negative": "red", "Neutral": "gray"}.get(row["sentiment_label"], "gray")
                        st.markdown(
                            f'<span style="color:{dot};font-size:10px;">&#9632;</span> '
                            f'<span style="color:#7a9ab8;font-size:11px;">{row["outlet"]}</span> '
                            f'<a href="{row["url"]}" style="color:#c8d8e8;font-size:12px;text-decoration:none;">{row["title"]}</a>',
                            unsafe_allow_html=True
                        )
                        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

            with col_right:
                st.markdown("### Right Leaning")
                right = results[results["lean"].isin(["Far Right", "Moderate Right"])]
                if len(right) == 0:
                    st.info("No right-leaning articles for this topic.")
                else:
                    for _, row in right.iterrows():
                        dot = {"Positive": "green", "Negative": "red", "Neutral": "gray"}.get(row["sentiment_label"], "gray")
                        st.markdown(
                            f'<span style="color:{dot};font-size:10px;">&#9632;</span> '
                            f'<span style="color:#7a9ab8;font-size:11px;">{row["outlet"]}</span> '
                            f'<a href="{row["url"]}" style="color:#c8d8e8;font-size:12px;text-decoration:none;">{row["title"]}</a>',
                            unsafe_allow_html=True
                        )
                        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Centre")
            centre = results[results["lean"] == "Centre"]
            if len(centre) == 0:
                st.info("No centre articles for this topic.")
            else:
                for _, row in centre.iterrows():
                    dot = {"Positive": "green", "Negative": "red", "Neutral": "gray"}.get(row["sentiment_label"], "gray")
                    st.markdown(
                        f'<span style="color:{dot};font-size:10px;">&#9632;</span> '
                        f'<span style="color:#7a9ab8;font-size:11px;">{row["outlet"]}</span> '
                        f'<a href="{row["url"]}" style="color:#c8d8e8;font-size:12px;text-decoration:none;">{row["title"]}</a>',
                        unsafe_allow_html=True
                    )
                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3 — OUTLET PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Outlet Profile":

    st.markdown("### Outlet Profile")
    st.caption("Deep dive into a single outlet's sentiment and coverage patterns.")

    outlets = sorted(df["outlet"].unique().tolist())
    selected = st.selectbox("Select outlet", outlets)

    outlet_df   = df[df["outlet"] == selected].copy()
    outlet_lean = outlet_df["lean"].iloc[0]
    lean_color  = LEAN_COLORS.get(outlet_lean, "#4a6a8a")
    lean_avg    = round(df[df["lean"] == outlet_lean]["sentiment_compound"].mean(), 3)
    outlet_avg  = round(outlet_df["sentiment_compound"].mean(), 3)
    delta       = round(outlet_avg - lean_avg, 3)

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Articles", len(outlet_df))
    col2.metric("Political Lean", outlet_lean)
    col3.metric("Most Common Sentiment", outlet_df["sentiment_label"].value_counts().idxmax())
    col4.metric("vs Lean Average", outlet_avg, delta=delta)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### Sentiment Breakdown")
        sent_counts = outlet_df["sentiment_label"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_pie = px.pie(
            sent_counts, names="Sentiment", values="Count",
            color="Sentiment", color_discrete_map=SENTIMENT_COLORS,
        )
        fig_pie.update_traces(textfont_color="#0a1520")
        st.plotly_chart(style_fig(fig_pie), use_container_width=True)

    with col_r:
        st.markdown("### Compound Score Distribution")
        fig_hist = px.histogram(
            outlet_df, x="sentiment_compound",
            nbins=20,
            color_discrete_sequence=[lean_color],
            labels={"sentiment_compound": "Compound Score"},
        )
        fig_hist.add_vline(
            x=outlet_avg,
            line_dash="dash",
            line_color="#a78bfa",
            annotation_text="mean",
            annotation_font_color="#a78bfa",
            annotation_font_size=10,
        )
        st.plotly_chart(style_fig(fig_hist), use_container_width=True)

    st.markdown("---")

    st.markdown("### Compared to Lean Peers")
    peers = (
        df[df["lean"] == outlet_lean]
        .groupby("outlet")["sentiment_compound"]
        .mean()
        .reset_index()
    )
    peers.columns = ["Outlet", "Avg Sentiment"]
    peers["highlight"] = peers["Outlet"].apply(lambda x: selected if x == selected else "peer")
    fig_peers = px.bar(
        peers, x="Outlet", y="Avg Sentiment",
        color="highlight",
        color_discrete_map={selected: lean_color, "peer": "#1a2f45"},
    )
    fig_peers.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig_peers), use_container_width=True)

    st.markdown("---")

    st.markdown("### Recent Headlines")
    for _, row in outlet_df.head(15).iterrows():
        dot = {"Positive": "green", "Negative": "red", "Neutral": "gray"}.get(row["sentiment_label"], "gray")
        st.markdown(
            f'<span style="color:{dot};font-size:10px;">&#9632;</span> '
            f'<a href="{row["url"]}" style="color:#c8d8e8;font-size:13px;text-decoration:none;">{row["title"]}</a>',
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
