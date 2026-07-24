# 🚕 NYC Taxi Insights: End-to-End Data Engineering Pipeline

📊 **[View Interactive Dashboard Here](https://datastudio.google.com/reporting/1bb78609-0d06-4a9b-a945-969de96fddc7)**

## 📖 Project Overview
**NYC Taxi Insights** is a robust, end-to-end Data Engineering pipeline designed to process, clean, model, and visualize large-scale NYC TLC Yellow Taxi trip data. The primary objective of this project is to transform a massive, flat, raw dataset into a highly optimized **Star Schema** within Google BigQuery, ultimately powering an interactive Looker Studio dashboard for business intelligence reporting.

## 🏗️ Architecture & Pipeline Flow
1. **Data Extraction**: Raw `yellow_tripdata` Parquet files are loaded into Python via Pandas.
2. **Data Transformation**: Python & Pandas are used to clean the data (removing missing values/duplicates) and transform the flat structure into a relational **Star Schema**.
3. **Orchestration**: **Mage AI** is used to orchestrate the data pipeline, ensuring modular block execution and dependency management.
4. **Data Warehousing**: The transformed Dimension and Fact tables are loaded into **Google Cloud BigQuery** for high-performance OLAP querying.
5. **Data Visualization**: BigQuery is connected to **Looker Studio** to create an interactive dashboard translating complex data into actionable business insights.

## 🗄️ Data Modeling (Star Schema)
The core of this project revolves around architecting a relational data model by decomposing the flat dataset into a highly efficient Star Schema. 
- **Fact Table**: `fact_table` (Contains quantitative metrics like `fare_amount`, `tip_amount`, `total_amount`, and foreign keys to all dimension tables)
- **Dimension Tables**: 
  - `datetime_dim`
  - `passenger_count_dim`
  - `trip_distance_dim`
  - `rate_code_dim`
  - `pickup_location_dim`
  - `dropoff_location_dim`
  - `payment_type_dim`

## 🛠️ Tech Stack & Tools
* **Language:** Python 3.12
* **Data Processing:** Pandas, PyArrow, Numpy
* **Orchestration:** Mage AI
* **Cloud Data Warehouse:** Google Cloud BigQuery
* **Data Visualization:** Looker Studio (Google Data Studio)

## 📁 Dataset
* **Dataset Link:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
* **Data Dictionary:** A cheatsheet explaining all the dataset columns is included in this repository as `data_dictionary_trip_records_yellow.pdf`.
