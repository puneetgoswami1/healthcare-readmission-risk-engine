# Healthcare Operations & Patient Readmission Risk Analytics

A predictive clinical analytics framework designed to monitor 30-day unplanned hospital readmissions, optimize bed capacity utilization, and satisfy CMS Hospital Readmissions Reduction Program (HRRP) benchmarks.

## Overview
Unplanned hospital readmissions within 30 days of inpatient discharge introduce substantial reimbursement penalties and strain care resources. This project combines SQL window functions to calculate re-encounter deltas with a balanced Random Forest model to risk-stratify patients prior to discharge.

## Project Structure
- `readmission_cohort_pipeline.sql`: Production SQL CTE query tracking patient discharge timelines, excluding CMS-ineligible dispositions, and aggregating 30-day re-encounter rates by clinical department.
- `readmission_risk_engine.py`: Machine learning pipeline evaluating clinical indicators (Charlson Comorbidity Index, prior emergency visits, acute LOS) to generate pre-discharge risk scores.
- `requirements.txt`: Python package dependencies.

## Key Clinical Metrics & Findings
1. **CMS 30-Day Windowing:** Uses windowed `LEAD()` logic partitioned by patient ID to isolate subsequent emergency admissions within a 30-day post-discharge horizon.
2. **Key Risk Indicators:** Demonstrates that chronic comorbidity index and prior 6-month emergency utilization are the strongest leading drivers of post-acute bouncebacks.
3. **Operational Impact:** Identifies high-risk patient cohorts to enable post-discharge telehealth follow-ups and medication reconciliation before day 14.

## How to Run

```bash
# Clone the repository
git clone https://github.com/puneetgoswami1/healthcare-readmission-risk-engine.git
cd healthcare-readmission-risk-engine

# Install dependencies
pip install -r requirements.txt

# Run clinical risk engine
python readmission_risk_engine.py