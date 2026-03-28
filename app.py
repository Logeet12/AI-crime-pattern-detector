from flask import Flask, render_template, jsonify
import random
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from waitress import serve
 
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
 
 
# ── Routes ──
 
@app.route("/")
def index():
    return render_template("index.html")
 
 
@app.route("/generate")
def generate():
    """Return raw dataset as JSON and cache cleaned data for /analyze."""
    global _dataset, _cleaned_df
    _dataset, _cleaned_df = build_dataset()
    return jsonify(_dataset)
 
 
@app.route("/analyze")
def analyze():
    """Return cleaned + scored dataset as JSON."""
    global _cleaned_df
    if _cleaned_df is None:
        return jsonify({"error": "Generate a dataset first."}), 400
    # Round floats for readability
    result = _cleaned_df.round(4).to_dict(orient="records")
    return jsonify(result)
 
 
# ── Entry point (local only — Render uses gunicorn) ──
if __name__ == "__main__":
    from waitress import serve
    host = "127.0.0.1"
    port = 5000
    print(f"\n✅  Server running →  http://{host}:{port}\n")
    serve(app, host=host, port=port)