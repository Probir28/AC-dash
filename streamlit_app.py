import streamlit as st
import sys, platform, subprocess, time
import pandas as pd
import numpy as np

st.set_page_config(page_title="Streamlit Starter Healthcheck", page_icon="✅", layout="centered")
st.title("Streamlit Starter — Healthcheck & Demo")
st.caption("Use this as a clean baseline to get your app deploying on Streamlit Cloud.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Environment")
    st.write({"python": sys.version.split()[0], "platform": platform.platform()})
with col2:
    st.subheader("Key packages")
    def ver(mod):
        try:
            m = __import__(mod)
            return getattr(m, "__version__", "n/a")
        except Exception as e:
            return f"ERR: {e}"
    st.write({
        "streamlit": ver("streamlit"),
        "pandas": ver("pandas"),
        "numpy": ver("numpy"),
        "altair": ver("altair"),
        "plotly": ver("plotly"),
        "protobuf": ver("google.protobuf"),
    })

st.divider()
st.subheader("Cache demo (avoid heavy work at import)")
@st.cache_resource(show_spinner=True)
def heavy_init(seconds: int = 2):
    # simulate loading a model or connecting to a DB
    time.sleep(seconds)
    return {"ok": True, "init_seconds": seconds}

if st.button("Initialize heavy resource"):
    st.success(heavy_init())

@st.cache_data(show_spinner=True)
def compute_summary(n: int = 1000):
    # simulate data processing
    rng = np.random.default_rng(0)
    x = rng.normal(size=n)
    return pd.DataFrame({"x": x, "cum": np.cumsum(x)})

df = compute_summary()
st.line_chart(df["cum"])

st.divider()
st.subheader("Local file example (use pathlib)")
from pathlib import Path
data_path = Path(__file__).parent / "data" / "hello.txt"
if data_path.exists():
    st.code(data_path.read_text())
else:
    st.info("No local data file found. Create one at 'data/hello.txt' if needed.")

st.divider()
st.subheader("Diagnostics")
if st.button("Show first 80 lines of 'pip freeze'"):
    out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    st.code("\n".join(out.splitlines()[:80]))
