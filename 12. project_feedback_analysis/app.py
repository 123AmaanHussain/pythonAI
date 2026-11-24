import sqlite3
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/analyze"
DB_PATH = "reviews.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            review TEXT NOT NULL,
            label TEXT NOT NULL,
            score INTEGER NOT NULL,
            theme TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


st.set_page_config(page_title="Review Analysis", layout="wide")
st.title("Customer Review Analysis")

reviews_text = st.text_area(
    "Paste customer reviews (one per line)",
    height=250,
    placeholder="The food was great but delivery was slow...\nTerrible experience, never again.",
)

if st.button("Analyze", type="primary"):
    reviews = [r.strip() for r in reviews_text.splitlines() if r.strip()]

    if not reviews:
        st.warning("Please paste at least one review.")
    else:
        results = []
        progress = st.progress(0, text="Analyzing reviews...")

        conn = get_connection()
        now = datetime.now().isoformat(timespec="seconds")

        for i, text in enumerate(reviews):
            try:
                resp = requests.post(API_URL, json={"text": text}, timeout=60)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                data = {"label": "error", "score": 0, "theme": "-"}
                st.warning(f"Failed to analyze review {i + 1}: {e}")

            conn.execute(
                "INSERT INTO analyses (created_at, review, label, score, theme) VALUES (?, ?, ?, ?, ?)",
                (now, text, data["label"], data["score"], data["theme"]),
            )
            results.append({"review": text, **data})
            progress.progress((i + 1) / len(reviews))

        conn.commit()
        conn.close()
        progress.empty()

        df = pd.DataFrame(results)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reviews", len(df))
        col2.metric("Positive", int((df["label"] == "positive").sum()))
        col3.metric("Negative", int((df["label"] == "negative").sum()))

        st.dataframe(df[["review", "label", "score", "theme"]], width="stretch")
        st.success("Results saved to reviews.db")

st.divider()
st.subheader("Analysis History")

conn = get_connection()
history = pd.read_sql_query(
    "SELECT created_at, review, label, score, theme FROM analyses ORDER BY id DESC LIMIT 100",
    conn,
)
conn.close()

if history.empty:
    st.info("No analyses yet.")
else:
    st.dataframe(history, width="stretch")
