CREATE SCHEMA IF NOT EXISTS analytics;

DROP MATERIALIZED VIEW IF EXISTS analytics.orders_features;

CREATE MATERIALIZED VIEW analytics.orders_features AS WITH geo_avg AS (
    SELECT
        geolocation_zip_code_prefix,
        AVG(geolocation_lat) AS lat,
        AVG(geolocation_lng) AS lng
    FROM
        olist.geolocation
    GROUP BY
        geolocation_zip_code_prefix
),
payments_agg AS (
    SELECT
        order_id,
        MAX(payment_sequential) AS total_payment_steps,
        STRING_AGG(DISTINCT payment_type, ', ') AS payment_types,
        MAX(payment_installments) AS max_installments,
        SUM(payment_value) AS total_payment_value
    FROM
        olist.payments
    GROUP BY
        order_id
),
reviews_agg AS (
    SELECT
        order_id,
        AVG(review_score)::NUMERIC(3, 2) AS review_score
    FROM
        olist.order_reviews
    GROUP BY
        order_id
)
SELECT
    -- Orders
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    -- Customers
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    c.customer_zip_code_prefix,
    c_geo.lat AS customer_lat,
    c_geo.lng AS customer_lon,
    -- Reviews and Payments
    r.review_score,
    p.payment_types,
    p.max_installments,
    p.total_payment_value,
    -- Items and Products
    i.order_item_id,
    i.product_id,
    i.price,
    i.freight_value,
    pr.product_category_name,
    pr.product_photos_qty,
    pr.product_weight_g,
    pr.product_length_cm,
    pr.product_height_cm,
    pr.product_width_cm,
    -- Sellers
    s.seller_id,
    s.seller_city,
    s.seller_state,
    s.seller_zip_code_prefix,
    s_geo.lat AS seller_lat,
    s_geo.lng AS seller_lon
FROM
    olist.orders AS o
    LEFT JOIN olist.customers AS c ON o.customer_id = c.customer_id
    LEFT JOIN geo_avg AS c_geo ON c.customer_zip_code_prefix = c_geo.geolocation_zip_code_prefix
    LEFT JOIN reviews_agg AS r ON o.order_id = r.order_id
    LEFT JOIN payments_agg AS p ON o.order_id = p.order_id
    LEFT JOIN olist.order_items AS i ON o.order_id = i.order_id
    LEFT JOIN olist.products AS pr ON i.product_id = pr.product_id
    LEFT JOIN olist.sellers AS s ON i.seller_id = s.seller_id
    LEFT JOIN geo_avg AS s_geo ON s.seller_zip_code_prefix = s_geo.geolocation_zip_code_prefix;

CREATE UNIQUE INDEX idx_orders_features_pk ON analytics.orders_features (order_id, order_item_id);
