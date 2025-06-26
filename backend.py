import os
import json
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics.pairwise import cosine_similarity
import joblib

app = Flask(__name__)
CORS(app)

MODEL_PATH = "model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"
DATASET_PATH = "fake_or_real_news.csv"

def train_or_load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
    else:
        print("🔧 Training model...")
        df = pd.read_csv(DATASET_PATH)
        df.dropna(inplace=True)
        X = df["text"]
        y = df["label"]

        vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)
        X_vec = vectorizer.fit_transform(X)

        model = PassiveAggressiveClassifier(max_iter=1000)
        model.fit(X_vec, y)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)

    return model, vectorizer

model, vectorizer = train_or_load_model()

def summarize(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip().split()) > 7]
    if not sentences:
        return []

    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(sentences)

    mean_vector = np.asarray(tfidf_matrix.mean(axis=0))
    scores = cosine_similarity(tfidf_matrix, mean_vector)
    ranked = sorted(zip(scores, sentences), key=lambda x: -x[0].sum())
    top_sentences = [s for _, s in ranked[:3]]
    return top_sentences

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        text = data.get("text", "")
        print("📨 Received text:", text[:200])

        sentences = [s.strip() for s in text.split(".") if len(s.strip().split()) > 7]
        results = []

        for sentence in sentences:
            vec = vectorizer.transform([sentence])
            raw_conf = model.decision_function(vec)[0]
            conf = 1 / (1 + np.exp(-raw_conf))  # sigmoid
            confidence_percent = round(conf * 100, 1)

            if raw_conf < -0.01:
              verdict = "FALSE"
            elif raw_conf > 0.01:
                 verdict = "TRUE"
            else:
               verdict = "UNCERTAIN"

            results.append({
                "sentence": sentence,
                "verdict": verdict,
                "confidence": confidence_percent
            })

        return jsonify({
            "summary": summarize(text),
            "results": results
        })

    except Exception as e:
        import traceback
        print("🔥 Exception in /analyze:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/sources", methods=["GET"])
def sources():
    return jsonify({
        "links": [
            "https://www.snopes.com/",
            "https://www.politifact.com/",
            "https://www.factcheck.org/",
            "https://www.reuters.com/fact-check/",
            "https://www.boomlive.in/"
        ]
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    with open("feedback_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"status": "received"})

if __name__ == "__main__":
    app.run(debug=True)