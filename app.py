import streamlit as st
import pandas as pd
import os
from fetcher import fetch_all
from sentiment import analyze_sentiment
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(
    page_title="Indian Media Bias Dashboard",
    page_icon="📰",
    layout="wide"
)

CACHE_FILE = "data/articles.csv"
CACHE_HOURS = 6


def load_data():
    # check if cache exists and is fresh
    if os.path.exists(CACHE_FILE):
        df = pd.read_csv(CACHE_FILE)
        last_fetched = pd.to_datetime(df["fetched_at"].iloc[0])
        age = datetime.now() - last_fetched
        if age < timedelta(hours=CACHE_HOURS):
            return df, last_fetched

    # cache is stale or missing — refetch
    with st.spinner("Fetching latest articles..."):
        df = fetch_all()
        df = analyze_sentiment(df)
        df.to_csv(CACHE_FILE, index=False)

    return df, datetime.now()


# ── Load data ─────────────────────────────────────────────────────────────────
df, last_fetched = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📰 Indian Media Bias & Sentiment Dashboard")
st.caption(f"Last updated: {last_fetched.strftime('%d %b %Y, %I:%M %p')}")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Navigation")
view = st.sidebar.radio("Go to", ["Overview", "Topic Explorer", "Outlet Profile"])

if st.sidebar.button("🔄 Refresh Data"):
    os.remove(CACHE_FILE)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total articles:** {len(df)}")
st.sidebar.markdown(f"**Outlets:** {df['outlet'].nunique()}")

# ── Placeholder views ─────────────────────────────────────────────────────────
if view == "Overview":
    st.subheader("🗺️ Overview — The Big Picture")

    # ── Row 1: summary metrics ─────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Articles", len(df))
    col2.metric("Outlets Tracked", df["outlet"].nunique())
    col3.metric("Most Negative Lean", df.groupby("lean")["sentiment_compound"].mean().idxmin())
    col4.metric("Most Positive Lean", df.groupby("lean")["sentiment_compound"].mean().idxmax())

    st.markdown("---")

    # ── Row 2: article volume by lean ──────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📊 Article Volume by Lean")
        lean_order = ["Far Right", "Moderate Right", "Centre", "Moderate Left", "Far Left"]
        volume = df["lean"].value_counts().reindex(lean_order).reset_index()
        volume.columns = ["Lean", "Count"]

        import plotly.express as px
        fig_vol = px.bar(
            volume,
            x="Lean",
            y="Count",
            color="Lean",
            color_discrete_map={
                "Far Right":      "#d62728",
                "Moderate Right": "#ff7f0e",
                "Centre":         "#7f7f7f",
                "Moderate Left":  "#1f77b4",
                "Far Left":       "#00008b",
            },
            template="plotly_dark",
        )
        fig_vol.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Row 2: avg sentiment by lean ───────────────────────────────────────
    with col_right:
        st.markdown("#### 🎭 Average Sentiment by Lean")
        sentiment_avg = (
            df.groupby("lean")["sentiment_compound"]
            .mean()
            .reindex(lean_order)
            .reset_index()
        )
        sentiment_avg.columns = ["Lean", "Avg Compound Score"]

        fig_sent = px.bar(
            sentiment_avg,
            x="Lean",
            y="Avg Compound Score",
            color="Lean",
            color_discrete_map={
                "Far Right":      "#d62728",
                "Moderate Right": "#ff7f0e",
                "Centre":         "#7f7f7f",
                "Moderate Left":  "#1f77b4",
                "Far Left":       "#00008b",
            },
            template="plotly_dark",
        )
        fig_sent.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("---")

    # ── Row 3: sentiment label distribution by lean ────────────────────────
    st.markdown("#### 🔵 Sentiment Distribution Across the Spectrum")
    dist = (
        df.groupby(["lean", "sentiment_label"])
        .size()
        .reset_index(name="count")
    )
    dist["lean"] = pd.Categorical(dist["lean"], categories=lean_order, ordered=True)
    dist = dist.sort_values("lean")

    fig_dist = px.bar(
        dist,
        x="lean",
        y="count",
        color="sentiment_label",
        barmode="group",
        color_discrete_map={
            "Positive": "#2ca02c",
            "Negative": "#d62728",
            "Neutral":  "#7f7f7f",
        },
        template="plotly_dark",
        labels={"lean": "Lean", "count": "Articles", "sentiment_label": "Sentiment"},
    )
    fig_dist.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")

    # ── Row 4: raw data table ──────────────────────────────────────────────
    st.markdown("#### 🗞️ Raw Articles")
    st.dataframe(
        df[["outlet", "lean", "title", "sentiment_label", "sentiment_compound"]]
        .sort_values("sentiment_compound"),
        use_container_width=True,
    )

elif view == "Topic Explorer":
    st.subheader("🔍 Topic Explorer")
    st.markdown("Search a keyword and see how different sides of the spectrum covered it.")

    query = st.text_input("Enter a keyword", placeholder="e.g. Modi, inflation, Pakistan, election")

    if query:
        mask = (
            df["title"].str.contains(query, case=False, na=False) |
            df["description"].str.contains(query, case=False, na=False)
        )
        results = df[mask].copy()

        if len(results) == 0:
            st.warning(f"No articles found for '{query}'. Try a different keyword.")
        else:
            st.markdown(f"**{len(results)} articles found for '{query}'**")
            st.markdown("---")

            # ── Row 1: metrics ─────────────────────────────────────────────
            col1, col2, col3 = st.columns(3)
            col1.metric("Articles Found", len(results))
            col2.metric("Most Coverage From", results["lean"].value_counts().idxmax())
            col3.metric("Avg Sentiment", round(results["sentiment_compound"].mean(), 3))

            st.markdown("---")

            # ── Row 2: volume and sentiment by lean ────────────────────────
            lean_order = ["Far Right", "Moderate Right", "Centre", "Moderate Left", "Far Left"]
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("#### 📊 Coverage Volume by Lean")
                vol = results["lean"].value_counts().reindex(lean_order).fillna(0).reset_index()
                vol.columns = ["Lean", "Count"]
                fig_vol = px.bar(
                    vol, x="Lean", y="Count", color="Lean",
                    color_discrete_map={
                        "Far Right":      "#d62728",
                        "Moderate Right": "#ff7f0e",
                        "Centre":         "#7f7f7f",
                        "Moderate Left":  "#1f77b4",
                        "Far Left":       "#00008b",
                    },
                    template="plotly_dark",
                )
                fig_vol.update_layout(showlegend=False, margin=dict(t=20, b=20))
                st.plotly_chart(fig_vol, use_container_width=True)

            with col_right:
                st.markdown("#### 🎭 Sentiment by Lean")
                sent = (
                    results.groupby("lean")["sentiment_compound"]
                    .mean()
                    .reindex(lean_order)
                    .reset_index()
                )
                sent.columns = ["Lean", "Avg Compound Score"]
                fig_sent = px.bar(
                    sent, x="Lean", y="Avg Compound Score", color="Lean",
                    color_discrete_map={
                        "Far Right":      "#d62728",
                        "Moderate Right": "#ff7f0e",
                        "Centre":         "#7f7f7f",
                        "Moderate Left":  "#1f77b4",
                        "Far Left":       "#00008b",
                    },
                    template="plotly_dark",
                )
                fig_sent.update_layout(showlegend=False, margin=dict(t=20, b=20))
                st.plotly_chart(fig_sent, use_container_width=True)

            st.markdown("---")

            # ── Row 3: side by side headline comparison ────────────────────
            st.markdown("#### 📰 How Each Side Framed It")
            left_leans  = ["Far Left", "Moderate Left"]
            right_leans = ["Far Right", "Moderate Right"]

            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown("##### 🔵 Left Leaning")
                left_articles = results[results["lean"].isin(left_leans)][
                    ["outlet", "lean", "title", "sentiment_label", "url"]
                ]
                if len(left_articles) == 0:
                    st.info("No left-leaning articles found for this topic.")
                else:
                    for _, row in left_articles.iterrows():
                        sentiment_color = {"Positive": "🟢", "Negative": "🔴", "Neutral": "⚪"}.get(row["sentiment_label"], "⚪")
                        st.markdown(f"{sentiment_color} **{row['outlet']}** — [{row['title']}]({row['url']})")

            with col_r:
                st.markdown("##### 🔴 Right Leaning")
                right_articles = results[results["lean"].isin(right_leans)][
                    ["outlet", "lean", "title", "sentiment_label", "url"]
                ]
                if len(right_articles) == 0:
                    st.info("No right-leaning articles found for this topic.")
                else:
                    for _, row in right_articles.iterrows():
                        sentiment_color = {"Positive": "🟢", "Negative": "🔴", "Neutral": "⚪"}.get(row["sentiment_label"], "⚪")
                        st.markdown(f"{sentiment_color} **{row['outlet']}** — [{row['title']}]({row['url']})")

            st.markdown("---")

            # ── Row 4: centre coverage ─────────────────────────────────────
            st.markdown("##### ⚪ Centre")
            centre_articles = results[results["lean"] == "Centre"][
                ["outlet", "title", "sentiment_label", "url"]
            ]
            if len(centre_articles) == 0:
                st.info("No centre articles found for this topic.")
            else:
                for _, row in centre_articles.iterrows():
                    sentiment_color = {"Positive": "🟢", "Negative": "🔴", "Neutral": "⚪"}.get(row["sentiment_label"], "⚪")
                    st.markdown(f"{sentiment_color} **{row['outlet']}** — [{row['title']}]({row['url']})")

elif view == "Outlet Profile":
    st.subheader("Outlet Profile")
    st.info("Coming soon")
