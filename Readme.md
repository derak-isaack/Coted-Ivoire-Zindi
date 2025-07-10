# Côte d'Ivoire Crop Classification (Cocoa, Rubber, Oil Palm)

This project focuses on identifying crop types—**cocoa**, **rubber**, and **oil palm**—in Côte d'Ivoire using **multi-temporal Sentinel-2 imagery** and machine learning. The pipeline integrates spatial and temporal feature engineering techniques to exploit phenological patterns and spectral properties of each crop type throughout the year.

## 🌍 Dataset Overview

- **Location:** Côte d'Ivoire
- **Imagery Source:** Sentinel-2 Surface Reflectance (Collection 2)
- **Temporal Range:** February to December 2024
- **Geometry Reference:** `train.geojson` containing 953 labeled crop polygons with metadata (`ID`, `year`, `crop_type`, and `class`)
- **Bands Used:** B3, B4, B5, B6, B7, B8, B8A, B11, B12 

---

## 🧠 Objective

The goal is to **classify crop types** using the temporal and spectral characteristics of Sentinel-2 imagery. We incorporate domain knowledge through feature engineering and handle missing data intelligently using spatial interpolation.

---

## 🧮 Data Processing Pipeline

### 1. **Cloud and Shadow Masking**

To ensure data quality:
- Cloud probabilities from `S2_CLOUD_PROBABILITY` collection were used with a threshold (e.g. 40%).
- Shadows were projected and masked using vector-based heuristics (sun azimuth, geometry, cloud height).
- Masked bands include all relevant reflectance bands.

### 2. **Monthly Aggregation**

- Images were aggregated per polygon **by month** using `reduceRegions` in Earth Engine.
- For each month (Feb–Dec), the **mean reflectance per band** was computed per crop polygon.
- Indices like **NDVI** and **EVI** were added as derived features.

---

## 🔍 Handling Missing Values with KDTree

Some polygons lacked data for specific months due to cloud cover or data gaps.

To address this:
- A **SciPy KDTree** was constructed using spatial centroids of available polygons.
- For any missing `(polygon_id, month)` data, the algorithm:
  1. Found the **nearest neighbor** polygon with valid data for that month.
  2. Copied its band and index values into the missing entry.
  
This **spatial imputation** preserved temporal structure while leveraging spatial similarity.

---

## 📅 Temporal Feature Engineering

To capture **phenological cycles**:
- Features were arranged in a **wide format**: each row = one polygon, columns = spectral values per month.
  - Example: `NDVI_Feb`, `NDVI_Mar`, ..., `B8A_Nov`, etc.
- Temporal **differences** and **ratios** were added:
  - `NDVI_Mar - NDVI_Feb`
  - `B8_Jul / B4_Jul`

This structure helps the model distinguish crops by their **growth patterns over time**.

---

## 🧪 Machine Learning Approach

- Combined **multiple boosting algorithms** in a chained ensemble framework:
  - **XGBoost**, **LightGBM**, and **CatBoost** were stacked or blended to exploit their individual strengths.
- Used **cross-validation** (Stratified K-Fold) to ensure **model robustness** and generalization to unseen data.
- Hyperparameter tuning was performed using tools like `GridSearchCV` and `Optuna` for optimal performance.
- Features used:
  - Raw spectral bands per month
  - NDVI and EVI per month
  - Temporal change metrics (e.g., `NDVI_Mar - NDVI_Feb`)
  - Spatial location features (latitude/longitude centroids, optional)

---

## 📊 Results

> 📊 Final CV Results:  
> Accuracy: 0.9360  
> F1 Score (macro): 0.9404  
>
> | Class | Precision | Recall | F1-score | Support |
> |-------|-----------|--------|----------|---------|
> | 0     | 1.00     | 0.96   | 0.98     | 235     |
> | 1     | 0.89     | 0.95   | 0.92     | 313     |
> | 2     | 0.94     | 0.91   | 0.93     | 405     |
>
> | Average | Precision | Recall | F1-score | Support |
> |---------|-----------|--------|----------|---------|
> | Accuracy | - | - | 0.94 | 953 |
> | Macro avg | 0.94 | 0.94 | 0.94 | 953 |
> | Weighted avg | 0.94 | 0.94 | 0.94 | 953 |

---
## 📝 Conclusion

This project demonstrates the potential of multi-temporal Sentinel-2 data for crop classification in Côte d'Ivoire. By combining spatial and temporal features, we can effectively identify and differentiate cocoa, rubber, and oil palm crops. The model's ability to generalize to unseen data highlights its robustness.
