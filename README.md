# Hospital 30-Day Readmission Cohort & Risk Analytics

A clinical operations pipeline tracking 30-day unplanned hospital readmissions and scoring pre-discharge patient risk to prioritize post-acute follow-up.

## Problem Context
Unplanned readmissions within 30 days of inpatient discharge strain bed capacity and trigger reimbursement penalties. This repository tracks re-encounter intervals in SQL and scores discharge risk factors in Python.

## Files
- `readmission_cohort_pipeline.sql`: Uses windowed `LEAD()` over patient encounters to measure days to readmission by clinical department.
- `readmission_risk_engine.py`: Evaluates comorbidity scores, prior emergency visits, and length of stay to flag high-risk discharges.
- `requirements.txt`: Python dependencies.

## How It Works
1. **30-Day Windowing:** Partitions encounters by patient ID to isolate unplanned emergency returns within 30 days of discharge.
2. **Risk Stratification:** Weights chronic comorbidity index and recent ER utilization to rank discharge cohorts.
3. **Care Follow-Up:** Flags high-risk discharges for nurse telehealth check-ins within 14 days.

## Run Locally

    git clone https://github.com/puneetgoswami1/healthcare-readmission-risk-engine.git
    cd healthcare-readmission-risk-engine
    pip install -r requirements.txt
    python readmission_risk_engine.py
