"""
Healthcare Patient Readmission Risk Scoring Engine
Author: Puneet Goswami
Description: Builds a clinical risk classifier to flag inpatient cases with elevated
             probabilities of 30-day post-discharge readmission for care coordination.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


def generate_clinical_cohort(n_patients: int = 15000) -> pd.DataFrame:
    """Generates synthetic electronic health records (EHR) cohort data."""
    np.random.seed(42)

    patient_ids = [f"PT-{100000 + i}" for i in range(n_patients)]
    age = np.random.normal(loc=64, scale=12, size=n_patients).clip(20, 95).astype(int)
    gender = np.random.choice(["Male", "Female"], size=n_patients)
    
    # Clinical Features
    length_of_stay = np.random.poisson(lam=4.2, size=n_patients).clip(1, 28)
    charlson_comorbidity_score = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=n_patients, p=[0.25, 0.28, 0.20, 0.14, 0.08, 0.03, 0.02])
    prior_emergency_visits_6m = np.random.choice([0, 1, 2, 3, 4], size=n_patients, p=[0.60, 0.22, 0.11, 0.05, 0.02])
    num_prescribed_medications = np.random.poisson(lam=7.5, size=n_patients).clip(1, 25)

    # Realistic Readmission Risk Function (CMS Benchmark ~15-18%)
    logits = (
        -2.5
        + 0.025 * (age - 50)
        + 0.08 * length_of_stay
        + 0.35 * charlson_comorbidity_score
        + 0.45 * prior_emergency_visits_6m
        + 0.04 * (num_prescribed_medications - 5)
    )
    probabilities = 1 / (1 + np.exp(-logits))
    is_readmitted = (np.random.rand(n_patients) < probabilities).astype(int)

    return pd.DataFrame({
        "patient_id": patient_ids,
        "age": age,
        "gender": gender,
        "length_of_stay": length_of_stay,
        "charlson_comorbidity_score": charlson_comorbidity_score,
        "prior_emergency_visits_6m": prior_emergency_visits_6m,
        "num_prescribed_medications": num_prescribed_medications,
        "is_readmitted_30d": is_readmitted
    })


def run_pipeline():
    print("Loading inpatient clinical records...")
    df = generate_clinical_cohort(15000)
    print(f"Total Discharges Analyzed: {len(df):,} | Baseline 30-Day Readmission Rate: {df['is_readmitted_30d'].mean()*100:.2f}%\n")

    features = [
        "age", 
        "length_of_stay", 
        "charlson_comorbidity_score", 
        "prior_emergency_visits_6m", 
        "num_prescribed_medications"
    ]
    
    X = df[features]
    y = df["is_readmitted_30d"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:, 1]

    print("--- Clinical Stratification Performance ---")
    print(classification_report(y_test, preds, target_names=["Discharged-Safe", "Readmitted-30D"]))
    print(f"Stratification ROC-AUC: {roc_auc_score(y_test, probs):.4f}")

    importance = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
    print("\nPrimary Clinical Readmission Drivers:")
    for feat, imp in importance.items():
        print(f" - {feat:28s}: {imp*100:.1f}%")


if __name__ == "__main__":
    run_pipeline()