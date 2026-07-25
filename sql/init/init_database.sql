CREATE SCHEMA IF NOT EXISTS olist;

-- GEOLOCATION 
CREATE TABLE IF NOT EXISTS olist.geolocation (
    geolocation_zip_code_prefix VARCHAR(5) NOT NULL,
    geolocation_lat DOUBLE PRECISION NOT NULL,
    geolocation_lng DOUBLE PRECISION NOT NULL,
    geolocation_city VARCHAR(100) NOT NULL,
    geolocation_state CHAR(2) NOT NULL
);

-- CUSTOMERS
CREATE TABLE IF NOT EXISTS olist.customers (
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_zip_code_prefix VARCHAR(5) NOT NULL, 
    customer_city VARCHAR(100) NOT NULL,
    customer_state CHAR(2) NOT NULL,

    PRIMARY KEY (customer_id)
);

-- SELLERS
CREATE TABLE IF NOT EXISTS olist.sellers (
    seller_id VARCHAR(32) NOT NULL,
    seller_zip_code_prefix VARCHAR(5) NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state CHAR(2) NOT NULL,

    PRIMARY KEY (seller_id)
);

-- PRODUCTS
CREATE TABLE IF NOT EXISTS olist.products (
    product_id VARCHAR(32) NOT NULL,
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,

    PRIMARY KEY (product_id)
);

-- CATEGORY TRANSLATION
CREATE TABLE IF NOT EXISTS olist.category_translation (
    product_category_name VARCHAR(100) NOT NULL,
    product_category_name_english VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_category_name)
);

-- ORDERS
CREATE TABLE IF NOT EXISTS olist.orders (
    order_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP NOT NULL,

    PRIMARY KEY (order_id)
);

-- ORDER REVIEWS
CREATE TABLE IF NOT EXISTS olist.order_reviews (
    review_id VARCHAR(32) NOT NULL,
    order_id VARCHAR(32) NOT NULL,
    review_score SMALLINT NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP NOT NULL,
    review_answer_timestamp TIMESTAMP NOT NULL,

    PRIMARY KEY (review_id, order_id)
);

-- ORDER ITEMS
CREATE TABLE IF NOT EXISTS olist.order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id SMALLINT NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    shipping_limit_date TIMESTAMP NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    freight_value NUMERIC(10,2) NOT NULL,

    PRIMARY KEY (order_id, order_item_id)
);

-- PAYMENTS
CREATE TABLE IF NOT EXISTS olist.payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential SMALLINT NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    payment_installments SMALLINT NOT NULL,
    payment_value NUMERIC(10,2) NOT NULL,

    PRIMARY KEY (order_id, payment_sequential)
);

-- ============================================================================

-- Customers & Sellers
CREATE INDEX IF NOT EXISTS idx_customers_unique_id 
    ON olist.customers (customer_unique_id);

CREATE INDEX IF NOT EXISTS idx_customers_zip_code 
    ON olist.customers (customer_zip_code_prefix);

CREATE INDEX IF NOT EXISTS idx_sellers_zip_code 
    ON olist.sellers (seller_zip_code_prefix);

CREATE INDEX IF NOT EXISTS idx_geolocation_zip_code 
    ON olist.geolocation (geolocation_zip_code_prefix);

-- Orders 
CREATE INDEX IF NOT EXISTS idx_order_items_product_id 
    ON olist.order_items (product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id 
    ON olist.order_items (seller_id);

CREATE INDEX IF NOT EXISTS idx_order_items_shipping_limit 
    ON olist.order_items (shipping_limit_date);

-- Reviews & Products
CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id 
    ON olist.order_reviews (order_id);

CREATE INDEX IF NOT EXISTS idx_products_category_name 
    ON olist.products (product_category_name);
