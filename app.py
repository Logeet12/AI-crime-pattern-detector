from flask import Flask, render_template, jsonify
import random
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# ── Global storage so /generate and /analyze share data ──
_dataset = []
_cleaned_df = None


def build_dataset():
    """Generate and preprocess 20 suspects. Returns raw list and cleaned DataFrame."""
    suspects = []
    for i in range(20):
        suspects.append({
            "suspect_name": f"Suspect_{i+1}",
            "distance_from_scene": round(random.uniform(0.1, 10), 2),
            "motive_strength": random.randint(0, 10),
            "alibi_strength": random.randint(0, 10),
            "evidence_score": random.randint(0, 10),
            "witness_reports": random.randint(0, 5),
        })

    df_raw = pd.DataFrame(suspects)

    # ── Preprocessing ──
    df = df_raw.copy()
    df.fillna({
        "distance_from_scene": df["distance_from_scene"].mean(),
        "motive_strength": 0,
        "alibi_strength": 0,
        "evidence_score": 0,
        "witness_reports": 0,
    }, inplace=True)

    # Feature Engineering: Suspicion Score
    df["suspicion_score"] = (
        df["motive_strength"] * 0.3
        + df["evidence_score"] * 0.4
        + df["witness_reports"] * 0.2
        - df["alibi_strength"] * 0.3
        - df["distance_from_scene"] * 0.1
    )

    # Normalize
    scaler = MinMaxScaler()
    cols_to_scale = [
        "distance_from_scene",
        "motive_strength",
        "alibi_strength",
        "evidence_score",
        "witness_reports",
        "suspicion_score",
    ]
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

    return suspects, df


# ── Chart generation ──
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor="#000000", edgecolor="none")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def generate_charts(df):
    charts = {}
    DARK_BG  = "#000000"
    PANEL_BG = "#011a10"
    GREEN    = "#00aa55"
    ACCENT   = "#00cc66"
    TEXT     = "#00cc66"

    def base_fig():
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(DARK_BG)
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GREEN)
        return fig, ax

    # 1. Correlation Matrix
    fig, ax = base_fig()
    sns.heatmap(df.corr(numeric_only=True), annot=True, fmt=".2f",
                cmap="Greens", ax=ax, annot_kws={"color": TEXT},
                linecolor=DARK_BG, linewidths=0.5)
    ax.set_title("Correlation Matrix", fontsize=13)
    plt.xticks(color=TEXT, fontsize=8)
    plt.yticks(color=TEXT, fontsize=8)
    charts["correlation"] = fig_to_base64(fig)

    # 2. Top 5 Suspects
    top5 = df.sort_values("suspicion_score", ascending=False).head(5)
    fig, ax = base_fig()
    sns.barplot(x="suspect_name", y="suspicion_score", data=top5, color=ACCENT, ax=ax)
    ax.set_title("Top 5 Suspects by Suspicion Score", fontsize=13)
    ax.set_xlabel("Suspect")
    ax.set_ylabel("Suspicion Score")
    plt.xticks(rotation=30, color=TEXT)
    charts["top_suspects"] = fig_to_base64(fig)

    # 3. Suspicion Score Distribution
    fig, ax = base_fig()
    sns.histplot(df["suspicion_score"], kde=True, color=ACCENT, ax=ax,
                 line_kws={"color": GREEN})
    ax.set_title("Suspicion Score Distribution", fontsize=13)
    ax.set_xlabel("Suspicion Score")
    charts["distribution"] = fig_to_base64(fig)

    # 4. Evidence vs Suspicion Scatter
    fig, ax = base_fig()
    sns.scatterplot(x="evidence_score", y="suspicion_score", data=df,
                    color=ACCENT, ax=ax, s=80)
    ax.set_title("Evidence Score vs Suspicion Score", fontsize=13)
    ax.set_xlabel("Evidence Score")
    ax.set_ylabel("Suspicion Score")
    charts["scatter"] = fig_to_base64(fig)

    return charts


# ── Routes ──

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate")
def generate():
    global _dataset, _cleaned_df
    _dataset, _cleaned_df = build_dataset()
    return jsonify(_dataset)


@app.route("/analyze")
def analyze():
    global _cleaned_df
    if _cleaned_df is None:
        return jsonify({"error": "Generate a dataset first."}), 400
    result = _cleaned_df.round(4).to_dict(orient="records")
    return jsonify(result)


@app.route("/charts")
def charts():
    global _cleaned_df
    if _cleaned_df is None:
        return jsonify({"error": "Generate a dataset first."}), 400
    return jsonify(generate_charts(_cleaned_df))


# ── Entry point (local only — Render uses gunicorn) ──
if __name__ == "__main__":
    from waitress import serve
    host = "127.0.0.1"
    port = 5000
    print(f"\n✅  Server running →  http://{host}:{port}\n")
    serve(app, host=host, port=port)
 