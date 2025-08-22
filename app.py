import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Asia Cup Dashboard", layout="wide")
st.title("🏏 Asia Cup Cricket Dashboard")

uploaded = st.file_uploader("Upload asiacup.csv", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.success(f"Data loaded! {df.shape[0]} rows × {df.shape[1]} cols")

    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Win Rate by Team")
    if "Result" in df.columns and "Team" in df.columns:
        df["is_win"] = df["Result"].str.lower().eq("win")
        win_rate = df.groupby("Team")["is_win"].mean().sort_values(ascending=False)
        st.bar_chart(win_rate)
else:
    st.info("👆 Upload your `asiacup.csv` to get started.")
