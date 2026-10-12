import os
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

from sentiment_utils import analyze_dataframe, fetch_recent_posts, load_demo_data

st.set_page_config(
    page_title="Social Pulse | Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
      [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(88, 125, 255, .12), rgba(25, 190, 160, .08));
        border: 1px solid rgba(128, 128, 128, .20);
        padding: 16px 18px; border-radius: 14px;
      }
      .hero {padding: 1.2rem 1.4rem; border-radius: 18px;
        background: linear-gradient(115deg, rgba(84,112,255,.18), rgba(36,190,170,.12));
        border: 1px solid rgba(128,128,128,.18); margin-bottom: 1rem;}
      .muted {color: #777; font-size: .92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1 style="margin:0">📊 Social Pulse</h1>
      <p style="margin:.4rem 0 0 0">Real-time-ready sentiment analysis for public posts on X</p>
      <p class="muted" style="margin:.35rem 0 0 0">Python · VADER NLP · Pandas · Plotly · Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Data settings")
    source = st.radio(
        "Choose data source",
        ["Demo dataset", "Live X API"],
        help="Demo mode works without API credentials. Live mode needs an X API Bearer Token.",
    )
    keyword = st.text_input("Keyword or hashtag", value="AI", help="Used as the live X search query.")
    max_posts = st.slider("Maximum posts", min_value=10, max_value=100, value=50, step=10)
    refresh = st.button("🔄 Load / refresh data", type="primary", use_container_width=True)
    st.caption("Live recent search availability depends on your X developer account and API limits.")

if "data" not in st.session_state or refresh:
    if source == "Demo dataset":
        st.session_state["data"] = load_demo_data()
        st.session_state["source_label"] = "Demo dataset"
        st.session_state["query_label"] = "AI"
    else:
        token = st.secrets.get("X_BEARER_TOKEN", os.getenv("X_BEARER_TOKEN", "")).strip()
        if not token:
            st.error(
                "No X API Bearer Token found. Add it to `.streamlit/secrets.toml` "
                "as `X_BEARER_TOKEN = \"your_token_here\"`, or set the X_BEARER_TOKEN environment variable."
            )
            st.info("Showing the demo dataset for now. Your token is never stored in this project.")
            st.session_state["data"] = load_demo_data()
            st.session_state["source_label"] = "Demo dataset (live token missing)"
            st.session_state["query_label"] = "AI"
        else:
            with st.spinner(f"Fetching recent public posts for: {keyword}"):
                try:
                    raw = fetch_recent_posts(token, keyword, max_posts)
                    if raw.empty:
                        st.warning("The API returned no posts for this query. Showing the demo dataset.")
                        st.session_state["data"] = load_demo_data()
                        st.session_state["source_label"] = "Demo dataset (no live results)"
                    else:
                        st.session_state["data"] = analyze_dataframe(raw)
                        st.session_state["source_label"] = "Live X API"
                    st.session_state["query_label"] = keyword
                except Exception as exc:
                    st.error(f"Could not fetch live posts: {exc}")
                    st.info("Showing demo data so you can still explore the dashboard.")
                    st.session_state["data"] = load_demo_data()
                    st.session_state["source_label"] = "Demo dataset (API error)"
                    st.session_state["query_label"] = "AI"

df = st.session_state["data"].copy()
source_label = st.session_state.get("source_label", "Demo dataset")
query_label = st.session_state.get("query_label", "AI")

if df.empty:
    st.warning("No data available. Try refreshing or changing your search keyword.")
    st.stop()

df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
df["sentiment"] = df["sentiment"].fillna("Neutral")
df["clean_text"] = df["clean_text"].fillna("")
df["text"] = df["text"].fillna("")

with st.sidebar:
    st.divider()
    st.markdown(f"**Current source:** {source_label}")
    st.markdown(f"**Search:** `{query_label}`")
    st.markdown(f"**Posts loaded:** {len(df):,}")
    st.caption("Sentiment is an automated estimate, not a definitive measure of opinion.")

# Filters
st.subheader("Explore the conversation")
col_filter1, col_filter2 = st.columns([1, 1])
with col_filter1:
    sentiment_options = ["Positive", "Neutral", "Negative"]
    selected_sentiments = st.multiselect(
        "Filter by sentiment",
        options=sentiment_options,
        default=sentiment_options,
    )
with col_filter2:
    search_text = st.text_input("Find text containing", placeholder="e.g. helpful, update, service")

filtered = df[df["sentiment"].isin(selected_sentiments)].copy()
if search_text.strip():
    filtered = filtered[
        filtered["text"].str.contains(search_text.strip(), case=False, na=False)
        | filtered["clean_text"].str.contains(search_text.strip(), case=False, na=False)
    ]

total = len(filtered)
positive = int((filtered["sentiment"] == "Positive").sum())
neutral = int((filtered["sentiment"] == "Neutral").sum())
negative = int((filtered["sentiment"] == "Negative").sum())
positive_pct = positive / total * 100 if total else 0
negative_pct = negative / total * 100 if total else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Posts analyzed", f"{total:,}")
m2.metric("Positive", f"{positive:,}", f"{positive_pct:.1f}% of filtered posts")
m3.metric("Neutral", f"{neutral:,}", f"{neutral / total * 100:.1f}% of filtered posts" if total else "0%")
m4.metric("Negative", f"{negative:,}", f"{negative_pct:.1f}% of filtered posts")

if total == 0:
    st.info("No posts match these filters. Change the filters above.")
    st.stop()

left, right = st.columns([1, 1])
with left:
    st.markdown("### Sentiment mix")
    counts = filtered["sentiment"].value_counts().reindex(sentiment_options, fill_value=0).reset_index()
    counts.columns = ["Sentiment", "Posts"]
    fig = px.pie(
        counts,
        names="Sentiment",
        values="Posts",
        hole=0.58,
        color="Sentiment",
        color_discrete_map={"Positive": "#20A779", "Neutral": "#7C8CA5", "Negative": "#E45B67"},
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("### Post count by sentiment")
    bar = px.bar(
        counts,
        x="Sentiment",
        y="Posts",
        color="Sentiment",
        text="Posts",
        color_discrete_map={"Positive": "#20A779", "Neutral": "#7C8CA5", "Negative": "#E45B67"},
    )
    bar.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="", yaxis_title="Number of posts")
    bar.update_traces(textposition="outside")
    st.plotly_chart(bar, use_container_width=True)

st.markdown("### Sentiment over time")
timeline = filtered.dropna(subset=["created_at"]).copy()
if not timeline.empty:
    timeline["time_bucket"] = timeline["created_at"].dt.floor("h")
    trend = timeline.groupby(["time_bucket", "sentiment"]).size().reset_index(name="posts")
    line = px.line(
        trend, x="time_bucket", y="posts", color="sentiment", markers=True,
        color_discrete_map={"Positive": "#20A779", "Neutral": "#7C8CA5", "Negative": "#E45B67"},
        labels={"time_bucket": "Time (UTC)", "posts": "Posts", "sentiment": "Sentiment"},
    )
    line.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
    st.plotly_chart(line, use_container_width=True)
else:
    st.info("No valid timestamps are available for a timeline.")

st.markdown("### Analyzed posts")
display_cols = [c for c in ["created_at", "text", "sentiment", "compound", "clean_text"] if c in filtered.columns]
display_df = filtered[display_cols].sort_values("created_at", ascending=False, na_position="last")
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "created_at": st.column_config.DatetimeColumn("Created at (UTC)", format="YYYY-MM-DD HH:mm"),
        "compound": st.column_config.NumberColumn("VADER score", format="%.3f"),
        "text": st.column_config.TextColumn("Original post", width="large"),
        "clean_text": st.column_config.TextColumn("Cleaned text", width="large"),
    },
)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download analyzed data as CSV",
    data=csv_bytes,
    file_name="sentiment_analysis_results.csv",
    mime="text/csv",
)

with st.expander("How sentiment is classified"):
    st.write(
        "VADER returns a compound score between -1 and +1. This project uses the common thresholds: "
        "Positive ≥ 0.05, Negative ≤ -0.05, and Neutral between -0.05 and +0.05. "
        "These are heuristic labels and may misread sarcasm, slang, context, or mixed-language posts."
    )

st.caption(
    f"Last dashboard data load: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} · "
    "Demo figures are illustrative and are not live public opinion."
)
