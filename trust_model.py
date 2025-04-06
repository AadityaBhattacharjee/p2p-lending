import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

MODEL_PATH = "trust_model.pkl"
CSV_PATH = "Trustify.csv"

def train_model():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError("🚫 Trustify.csv not found. Please make sure it exists in the project folder.")

    df = pd.read_csv(CSV_PATH)

    X = df[[
        "Monthly Wallet Transactions (Count)",
        "Utility Bill Timeliness (%)",
        "Digital Social Activity Score (0-10)"
    ]]
    y = df["Predicted Trust Score (0 = Low, 1 = High)"]

    model = make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=100, random_state=42))
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved to", MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    print("Model not found. Training from CSV...")
    train_model()

model = joblib.load(MODEL_PATH)

def predict_trust_score(wallet_txns, bill_timeliness, social_score):
    features = np.array([[wallet_txns, bill_timeliness, social_score]])
    score = model.predict(features)[0]
    return round(score, 2)
