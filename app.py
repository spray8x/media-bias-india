import streamlit as st
import pandas as pd
import os
from fetcher import fetch_all
from sentiment import analyze_sentiment
from datetime import datetime, timedelta

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
    st.subheader("Overview")
    st.dataframe(df[["outlet", "lean", "title", "sentiment_label", "sentiment_compound"]].head(20))

elif view == "Topic Explorer":
    st.subheader("Topic Explorer")
    st.info("Coming soon")

elif view == "Outlet Profile":
    st.subheader("Outlet Profile")
    st.info("Coming soon")
