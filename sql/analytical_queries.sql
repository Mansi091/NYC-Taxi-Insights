-- =============================================================================
-- analytical_queries.sql
-- Analytical SQL against the fact_table / dimension star schema in BigQuery.
-- Replace `project.dataset` with your GOOGLE_CLOUD_PROJECT.uber_dataset
-- (see data_pipeline/data_exporters/data_export.py for the destination dataset).
--
-- Covers: joins, CTEs, aggregations, CASE statements, window functions.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Revenue and trip volume by hour of day (joins + aggregation)
-- -----------------------------------------------------------------------------
SELECT
    d.hour,
    d.weekday,
    COUNT(*)                       AS trip_count,
    ROUND(SUM(f.total_amount), 2)  AS total_revenue,
    ROUND(AVG(f.total_amount), 2)  AS avg_fare_per_trip,
    ROUND(AVG(f.trip_distance), 2) AS avg_trip_distance
FROM `project.dataset.fact_table` f
JOIN `project.dataset.datetime_dim` d
    ON f.datetime_key = d.datetime_key
GROUP BY d.hour, d.weekday
ORDER BY d.weekday, d.hour;


-- -----------------------------------------------------------------------------
-- 2. Payment type breakdown with CASE-based revenue tiering
-- -----------------------------------------------------------------------------
SELECT
    p.payment_name,
    COUNT(*)                      AS trip_count,
    ROUND(SUM(f.total_amount), 2) AS total_revenue,
    CASE
        WHEN AVG(f.tip_amount) = 0            THEN 'No tipping'
        WHEN AVG(f.tip_amount) < 1.5          THEN 'Low tipping'
        WHEN AVG(f.tip_amount) BETWEEN 1.5 AND 4 THEN 'Moderate tipping'
        ELSE 'High tipping'
    END AS tipping_behavior
FROM `project.dataset.fact_table` f
JOIN `project.dataset.payment_dim` p
    ON f.payment_key = p.payment_key
GROUP BY p.payment_name
ORDER BY total_revenue DESC;


-- -----------------------------------------------------------------------------
-- 3. Top 10 pickup locations by revenue, with % of total revenue (CTE + window fn)
-- -----------------------------------------------------------------------------
WITH pickup_revenue AS (
    SELECT
        l.location_id                  AS pickup_location_id,
        COUNT(*)                       AS trip_count,
        ROUND(SUM(f.total_amount), 2)  AS revenue
    FROM `project.dataset.fact_table` f
    JOIN `project.dataset.location_dim` l
        ON f.pickup_location_key = l.location_key
    GROUP BY l.location_id
)
SELECT
    pickup_location_id,
    trip_count,
    revenue,
    ROUND(100 * revenue / SUM(revenue) OVER (), 2) AS pct_of_total_revenue,
    RANK() OVER (ORDER BY revenue DESC)             AS revenue_rank
FROM pickup_revenue
QUALIFY revenue_rank <= 10
ORDER BY revenue_rank;


-- -----------------------------------------------------------------------------
-- 4. Month-over-month revenue trend (window function: LAG)
-- -----------------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT
        d.year,
        d.month,
        ROUND(SUM(f.total_amount), 2) AS revenue
    FROM `project.dataset.fact_table` f
    JOIN `project.dataset.datetime_dim` d
        ON f.datetime_key = d.datetime_key
    GROUP BY d.year, d.month
)
SELECT
    year,
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
    ROUND(
        100 * (revenue - LAG(revenue) OVER (ORDER BY year, month))
        / NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0),
        2
    ) AS pct_change_mom
FROM monthly_revenue
ORDER BY year, month;


-- -----------------------------------------------------------------------------
-- 5. Vendor performance ranked within each rate type (CTE + PARTITION BY)
-- -----------------------------------------------------------------------------
WITH vendor_rate_stats AS (
    SELECT
        v.vendor_name,
        r.rate_name,
        COUNT(*)                       AS trip_count,
        ROUND(AVG(f.total_amount), 2)  AS avg_revenue_per_trip
    FROM `project.dataset.fact_table` f
    JOIN `project.dataset.vendor_dim` v ON f.vendor_key = v.vendor_key
    JOIN `project.dataset.rate_dim` r   ON f.rate_code_key = r.rate_code_key
    GROUP BY v.vendor_name, r.rate_name
)
SELECT
    rate_name,
    vendor_name,
    trip_count,
    avg_revenue_per_trip,
    RANK() OVER (PARTITION BY rate_name ORDER BY avg_revenue_per_trip DESC) AS rank_within_rate_type
FROM vendor_rate_stats
ORDER BY rate_name, rank_within_rate_type;


-- -----------------------------------------------------------------------------
-- 6. Data quality spot-check directly in SQL (mirrors data_quality_check.py)
--    Useful as a scheduled monitoring query on the warehouse itself.
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*)                                              AS total_rows,
    COUNTIF(fare_amount < 0)                               AS negative_fare_count,
    COUNTIF(trip_distance <= 0)                            AS zero_distance_count,
    COUNTIF(passenger_count = 0 OR passenger_count IS NULL) AS missing_or_zero_passengers,
    COUNTIF(total_amount < fare_amount)                    AS inconsistent_totals,
    ROUND(100 * COUNTIF(fare_amount < 0 OR trip_distance <= 0) / COUNT(*), 3) AS pct_anomalous_rows
FROM `project.dataset.fact_table`;
