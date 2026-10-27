-- =====================================================================
-- HOSPITAL 30-DAY UNPLANNED READMISSION ANALYTICS PIPELINE
-- Author: Puneet Goswami
-- Description: Identifies index admissions, calculates post-discharge
--              re-encounter intervals, and flags 30-day readmission penalities.
-- =====================================================================

WITH inpatient_encounters AS (
    SELECT 
        encounter_id,
        patient_id,
        admission_date,
        discharge_date,
        discharge_disposition,
        primary_diagnosis_code,
        department_name,
        total_incurred_cost_usd,
        -- Calculate length of stay (LOS) in full days
        DATEDIFF('day', admission_date, discharge_date) AS length_of_stay_days
    FROM clinical_dw.patient_encounters
    WHERE admission_type = 'INPATIENT'
      AND discharge_disposition NOT IN ('EXPIRED', 'HOSPICE') -- Exclude non-eligible CMS dispositions
),

encounter_sequence AS (
    SELECT 
        encounter_id AS index_encounter_id,
        patient_id,
        admission_date AS index_admission_date,
        discharge_date AS index_discharge_date,
        department_name,
        primary_diagnosis_code,
        length_of_stay_days,
        total_incurred_cost_usd,
        
        -- Lead to identify next hospital admission for the same patient
        LEAD(admission_date, 1) OVER (
            PARTITION BY patient_id 
            ORDER BY admission_date ASC
        ) AS subsequent_admission_date,

        LEAD(encounter_id, 1) OVER (
            PARTITION BY patient_id 
            ORDER BY admission_date ASC
        ) AS subsequent_encounter_id
    FROM inpatient_encounters
),

readmission_labeled AS (
    SELECT 
        index_encounter_id,
        patient_id,
        department_name,
        primary_diagnosis_code,
        length_of_stay_days,
        total_incurred_cost_usd,
        index_discharge_date,
        subsequent_admission_date,
        
        -- Interval between discharge and next entry
        DATEDIFF('day', index_discharge_date, subsequent_admission_date) AS days_to_readmit,
        
        -- CMS 30-Day Readmission Threshold
        CASE 
            WHEN subsequent_admission_date IS NOT NULL 
             AND DATEDIFF('day', index_discharge_date, subsequent_admission_date) <= 30 
            THEN 1 
            ELSE 0 
        END AS is_30d_readmission
    FROM encounter_sequence
)

SELECT 
    department_name,
    COUNT(index_encounter_id) AS total_discharges,
    SUM(is_30d_readmission) AS total_30d_readmissions,
    ROUND((SUM(is_30d_readmission) * 100.0) / COUNT(index_encounter_id), 2) AS readmission_rate_pct,
    ROUND(AVG(length_of_stay_days), 1) AS avg_index_los_days,
    ROUND(AVG(CASE WHEN is_30d_readmission = 1 THEN days_to_readmit END), 1) AS avg_days_to_unplanned_return,
    ROUND(SUM(CASE WHEN is_30d_readmission = 1 THEN total_incurred_cost_usd ELSE 0 END), 2) AS readmission_cost_burden_usd
FROM readmission_labeled
GROUP BY department_name
ORDER BY readmission_rate_pct DESC;