# Asia Cup Cricket — EDA Script (mirrors the notebook)
# Run:  pip install -r requirements.txt  &&  python EDA_Notebook.py

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", 100)
sns.set_theme(style="whitegrid")

# -------- 1) Locate & load CSV --------
CANDIDATES = [
    "asiacup.csv",
    "./asiacup.csv",
    "/content/asiacup.csv",
    "sample_data/asiacup.csv",
]
path = next((p for p in CANDIDATES if os.path.exists(p)), None)
if path is None:
    raise FileNotFoundError(
        "asiacup.csv not found. Place it next to this script or update CANDIDATES."
    )

df = pd.read_csv(path, encoding="utf-8", low_memory=False)
print(f"[INFO] Loaded: {path}, shape={df.shape}")
print(df.head(), "\n")

# -------- 2) Light cleanup --------
df.columns = [c.strip() for c in df.columns]
numeric_like = [
    "Year", "Run Scored", "Wicket Lost", "Fours", "Sixes", "Extras",
    "Run Rate", "Avg Bat Strike Rate", "Highest Score",
    "Wicket Taken", "Given Extras", "Highest Individual wicket"
]
for col in numeric_like:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("[INFO] dtypes:")
print(df.dtypes, "\n")

# -------- 3) Quick dictionary (printed once) --------
desc = {
    "Team":"Team/country", "Opponent":"Opposing team", "Format":"Match type (e.g., ODI)",
    "Ground":"Stadium/location", "Year":"Year of match", "Toss":"Coin toss result",
    "Selection":"Decision after toss (Bat/Bowl first)", "Run Scored":"Team runs",
    "Wicket Lost":"Dismissals", "Fours":"4-run shots", "Sixes":"6-run shots",
    "Extras":"Bonus runs conceded by opponent", "Run Rate":"Runs per over",
    "Avg Bat Strike Rate":"Runs/100 balls", "Highest Score":"Top individual batter score",
    "Wicket Taken":"Opponent wickets taken", "Given Extras":"Extras conceded by this team",
    "Highest Individual wicket":"Most wickets by one bowler", "Player Of The Match":"MVP",
    "Result":"Win/Lose"
}
print("[INFO] Data dictionary:")
print(pd.DataFrame.from_dict(desc, orient="index", columns=["Meaning"]), "\n")

# -------- 4) Descriptive summaries --------
print("[INFO] Numeric summary:")
print(df.describe(include=[np.number]).T, "\n")

for c in ["Team", "Opponent", "Format", "Ground", "Toss", "Selection", "Result"]:
    if c in df.columns:
        print(f"[INFO] Top 10 values for {c}:")
        print(df[c].value_counts().head(10), "\n")

# -------- 5) Win rate KPIs --------
df["is_win"] = df["Result"].str.lower().eq("win")
win_rate = df.groupby("Team")["is_win"].mean().sort_values(ascending=False)
print("[INFO] Top 15 win rates by team:")
print(win_rate.head(15), "\n")

plt.figure(figsize=(10, 6))
win_rate.plot(kind="bar")
plt.title("Win Rate by Team")
plt.ylabel("Win Rate")
plt.xlabel("Team")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("fig_win_rate_by_team.png", dpi=150)
plt.close()

# -------- 6) Do more runs -> higher win chance? --------
tmp = df.dropna(subset=["Run Scored", "is_win"]).copy()
bins = pd.interval_range(
    start=tmp["Run Scored"].min(), end=tmp["Run Scored"].max(), periods=8
)
tmp["run_bin"] = pd.cut(tmp["Run Scored"], bins=bins)
win_by_runs = tmp.groupby("run_bin")["is_win"].mean().reset_index()
print("[INFO] Win probability by runs (binned):")
print(win_by_runs, "\n")

plt.figure(figsize=(8, 5))
plt.plot(win_by_runs["run_bin"].astype(str), win_by_runs["is_win"], marker="o")
plt.title("Win Probability by Runs Scored (binned)")
plt.ylabel("Win Probability")
plt.xlabel("Runs Scored (binned)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("fig_win_prob_by_runs.png", dpi=150)
plt.close()

# -------- 7) Toss & selection effects --------
toss_win = df.groupby("Toss")["is_win"].mean().sort_values(ascending=False)
sel_win = df.groupby("Selection")["is_win"].mean().sort_values(ascending=False)
print("[INFO] Win rate by Toss result:\n", toss_win, "\n")
print("[INFO] Win rate by Selection:\n", sel_win, "\n")

plt.figure(figsize=(6, 4))
sns.barplot(x=toss_win.index, y=toss_win.values)
plt.title("Win Rate by Toss Result")
plt.ylim(0, 1)
plt.ylabel("Win Rate")
plt.xlabel("Toss")
plt.tight_layout()
plt.savefig("fig_win_rate_by_toss.png", dpi=150)
plt.close()

plt.figure(figsize=(6, 4))
sns.barplot(x=sel_win.index, y=sel_win.values)
plt.title("Win Rate by Selection (Bat/Bowl First)")
plt.ylim(0, 1)
plt.ylabel("Win Rate")
plt.xlabel("Selection")
plt.tight_layout()
plt.savefig("fig_win_rate_by_selection.png", dpi=150)
plt.close()

# -------- 8) Distributions & simple relationship --------
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.histplot(df["Run Scored"].dropna(), bins=20, ax=axes[0])
axes[0].set_title("Runs Scored")

sns.histplot(df["Wicket Lost"].dropna(), bins=11, ax=axes[1])
axes[1].set_title("Wickets Lost")

sns.scatterplot(x="Run Scored", y="Run Rate", data=df, ax=axes[2])
axes[2].set_title("Runs vs Run Rate")

plt.tight_layout()
plt.savefig("fig_distributions_and_relation.png", dpi=150)
plt.close()

# -------- 9) Yearly trends --------
yearly = df.groupby("Year").agg(
    matches=("Team", "count"),
    avg_runs=("Run Scored", "mean"),
    avg_wkts=("Wicket Lost", "mean"),
    win_rate=("is_win", "mean"),
).reset_index()
print("[INFO] Yearly head():")
print(yearly.head(), "\n")

fig, ax = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
sns.lineplot(data=yearly, x="Year", y="matches", ax=ax[0])
ax[0].set_title("Matches per Year")
sns.lineplot(data=yearly, x="Year", y="avg_runs", ax=ax[1])
ax[1].set_title("Average Runs per Team/Match")
sns.lineplot(data=yearly, x="Year", y="win_rate", ax=ax[2])
ax[2].set_title("Win Rate Over Time")
plt.tight_layout()
plt.savefig("fig_yearly_trends.png", dpi=150)
plt.close()

# -------- 10) Grounds: high-scoring venues --------
ground_stats = (
    df.groupby("Ground")
    .agg(n=("Team", "count"), avg_runs=("Run Scored", "mean"), avg_rr=("Run Rate", "mean"))
    .sort_values("avg_runs", ascending=False)
)
top_grounds = ground_stats.query("n >= 8").head(15)
print("[INFO] Top grounds (min 8 matches) by avg runs:")
print(top_grounds, "\n")

# -------- 11) Player of the Match leaders --------
pom = df["Player Of The Match"].dropna().value_counts().head(15)
print("[INFO] Top 'Player of the Match' winners:")
print(pom, "\n")

plt.figure(figsize=(8, 6))
pom.sort_values().plot(kind="barh")
plt.title("Top 'Player of the Match' Winners")
plt.xlabel("Count")
plt.tight_layout()
plt.savefig("fig_pom_leaders.png", dpi=150)
plt.close()

print("[DONE] Figures saved to current folder:")
for f in [
    "fig_win_rate_by_team.png",
    "fig_win_prob_by_runs.png",
    "fig_win_rate_by_toss.png",
    "fig_win_rate_by_selection.png",
    "fig_distributions_and_relation.png",
    "fig_yearly_trends.png",
    "fig_pom_leaders.png",
]:
    print(" -", f)
