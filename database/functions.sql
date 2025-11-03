-- RPC Functions (Stored Procedures) - FIXED TYPE MATCHING

-- Drop existing functions first to allow return type changes
DROP FUNCTION IF EXISTS get_top_selling_products(TEXT, INT, INT);
DROP FUNCTION IF EXISTS get_trending_products(INT, INT);
DROP FUNCTION IF EXISTS search_products_by_description(TEXT);
DROP FUNCTION IF EXISTS get_low_stock_products(INT);
DROP FUNCTION IF EXISTS get_sales_summary_by_category(INT);
DROP FUNCTION IF EXISTS get_product_details(INT, TEXT);
DROP FUNCTION IF EXISTS get_recent_transactions(INT);

-- ============================================================================
-- 1. Get Top Selling Products
-- Returns best-selling products by total quantity sold
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_selling_products(
    p_category TEXT DEFAULT NULL,
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 30
)
RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    total_quantity_sold BIGINT,
    total_revenue NUMERIC,
    current_stock INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.brand,
        c.name AS category,
        SUM(sli.quantity) AS total_quantity_sold,
        SUM(sli.line_total) AS total_revenue,
        COALESCE(i.quantity_on_hand, 0) AS current_stock
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN sales_line_items sli ON p.id = sli.product_id
    INNER JOIN sales_transactions st ON sli.transaction_id = st.id
    LEFT JOIN inventory i ON p.id = i.product_id
    WHERE 
        p.status = 'active'
        AND st.transaction_date >= (CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL)
        AND (p_category IS NULL OR c.name ILIKE p_category)
    GROUP BY p.id, p.name, p.brand, c.name, i.quantity_on_hand
    ORDER BY total_quantity_sold DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_top_selling_products IS 'Get top selling products by quantity sold, optionally filtered by category and time period';


-- ============================================================================
-- 2. Get Trending Products
-- Returns products with highest recent sales velocity (trending up)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_trending_products(
    p_days INT DEFAULT 7,
    p_limit INT DEFAULT 10
)
RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    recent_sales BIGINT,
    sales_velocity NUMERIC,
    current_stock INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.brand,
        c.name AS category,
        SUM(sli.quantity) AS recent_sales,
        ROUND(SUM(sli.quantity)::NUMERIC / p_days, 2) AS sales_velocity,
        COALESCE(i.quantity_on_hand, 0) AS current_stock
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN sales_line_items sli ON p.id = sli.product_id
    INNER JOIN sales_transactions st ON sli.transaction_id = st.id
    LEFT JOIN inventory i ON p.id = i.product_id
    WHERE 
        p.status = 'active'
        AND st.transaction_date >= (CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL)
    GROUP BY p.id, p.name, p.brand, c.name, i.quantity_on_hand
    ORDER BY sales_velocity DESC, recent_sales DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_trending_products IS 'Get trending products based on recent sales velocity';


-- ============================================================================
-- 3. Search Products by Description
-- Searches product names and descriptions for matching terms
-- ============================================================================
CREATE OR REPLACE FUNCTION search_products_by_description(
    p_search_term TEXT
)
RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    description TEXT,
    price NUMERIC,
    current_stock INT,
    relevance_score INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.brand,
        c.name AS category,
        p.description,
        p.retail_price,
        COALESCE(i.quantity_on_hand, 0) AS current_stock,
        -- Simple relevance scoring: name match = 3, description match = 1
        CASE 
            WHEN p.name ILIKE '%' || p_search_term || '%' THEN 3
            ELSE 1
        END AS relevance_score
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    LEFT JOIN inventory i ON p.id = i.product_id
    WHERE 
        p.status = 'active'
        AND (
            p.name ILIKE '%' || p_search_term || '%'
            OR p.description ILIKE '%' || p_search_term || '%'
            OR p.brand ILIKE '%' || p_search_term || '%'
        )
    ORDER BY relevance_score DESC, p.name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_products_by_description IS 'Search products by name, description, or brand with relevance scoring';


-- ============================================================================
-- 4. Get Low Stock Products
-- Returns products that need reordering
-- ============================================================================
CREATE OR REPLACE FUNCTION get_low_stock_products(
    p_limit INT DEFAULT 20
)
RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    current_stock INT,
    reorder_level INT,
    stock_deficit INT,
    reorder_quantity INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.brand,
        c.name AS category,
        i.quantity_on_hand,
        i.reorder_level,
        (i.reorder_level - i.quantity_on_hand) AS stock_deficit,
        i.reorder_quantity
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    INNER JOIN inventory i ON p.id = i.product_id
    WHERE 
        p.status = 'active'
        AND i.quantity_on_hand <= i.reorder_level
    ORDER BY stock_deficit DESC, p.name
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_low_stock_products IS 'Get products with stock at or below reorder level';


-- ============================================================================
-- 5. Get Sales Summary by Category
-- Returns sales performance broken down by category
-- ============================================================================
CREATE OR REPLACE FUNCTION get_sales_summary_by_category(
    p_days INT DEFAULT 30
)
RETURNS TABLE(
    category VARCHAR(100),
    total_units_sold BIGINT,
    total_revenue NUMERIC,
    avg_transaction_value NUMERIC,
    unique_products_sold BIGINT,
    top_product VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    WITH category_sales AS (
        SELECT 
            c.name AS category,
            SUM(sli.quantity) AS total_units,
            SUM(sli.line_total) AS total_rev,
            COUNT(DISTINCT sli.product_id) AS unique_prods
        FROM categories c
        INNER JOIN products p ON c.id = p.category_id
        INNER JOIN sales_line_items sli ON p.id = sli.product_id
        INNER JOIN sales_transactions st ON sli.transaction_id = st.id
        WHERE st.transaction_date >= (CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL)
        GROUP BY c.name
    ),
    top_products AS (
        SELECT DISTINCT ON (c.name)
            c.name AS category,
            p.name AS product_name
        FROM categories c
        INNER JOIN products p ON c.id = p.category_id
        INNER JOIN sales_line_items sli ON p.id = sli.product_id
        INNER JOIN sales_transactions st ON sli.transaction_id = st.id
        WHERE st.transaction_date >= (CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL)
        GROUP BY c.name, p.name, sli.quantity
        ORDER BY c.name, SUM(sli.quantity) DESC
    )
    SELECT 
        cs.category,
        cs.total_units,
        cs.total_rev,
        ROUND(cs.total_rev / NULLIF(cs.total_units, 0), 2) AS avg_transaction_value,
        cs.unique_prods,
        tp.product_name
    FROM category_sales cs
    LEFT JOIN top_products tp ON cs.category = tp.category
    ORDER BY cs.total_rev DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_sales_summary_by_category IS 'Get sales performance summary broken down by product category';


-- ============================================================================
-- 6. Get Product Details
-- Returns comprehensive information about a specific product
-- ============================================================================
CREATE OR REPLACE FUNCTION get_product_details(
    p_product_id INT DEFAULT NULL,
    p_product_name TEXT DEFAULT NULL
)
RETURNS TABLE(
    product_id INT,
    sku VARCHAR(50),
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    size VARCHAR(50),
    abv NUMERIC,
    description TEXT,
    cost_price NUMERIC,
    retail_price NUMERIC,
    current_stock INT,
    reorder_level INT,
    total_sold_30d BIGINT,
    total_revenue_30d NUMERIC,
    last_sale_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.sku,
        p.name,
        p.brand,
        c.name AS category,
        p.subcategory,
        p.size,
        p.abv,
        p.description,
        p.cost_price,
        p.retail_price,
        COALESCE(i.quantity_on_hand, 0) AS current_stock,
        COALESCE(i.reorder_level, 0) AS reorder_level,
        COALESCE(SUM(sli.quantity), 0) AS total_sold_30d,
        COALESCE(SUM(sli.line_total), 0) AS total_revenue_30d,
        MAX(st.transaction_date) AS last_sale_date
    FROM products p
    INNER JOIN categories c ON p.category_id = c.id
    LEFT JOIN inventory i ON p.id = i.product_id
    LEFT JOIN sales_line_items sli ON p.id = sli.product_id
    LEFT JOIN sales_transactions st ON sli.transaction_id = st.id
        AND st.transaction_date >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
    WHERE 
        p.status = 'active'
        AND (p_product_id IS NULL OR p.id = p_product_id)
        AND (p_product_name IS NULL OR p.name ILIKE '%' || p_product_name || '%')
    GROUP BY p.id, p.sku, p.name, p.brand, c.name, p.subcategory, p.size, p.abv, 
             p.description, p.cost_price, p.retail_price, i.quantity_on_hand, i.reorder_level
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_product_details IS 'Get comprehensive details for a specific product by ID or name';


-- ============================================================================
-- 7. Get Recent Transactions
-- Returns recent sales transactions with summary info
-- ============================================================================
CREATE OR REPLACE FUNCTION get_recent_transactions(
    p_limit INT DEFAULT 10
)
RETURNS TABLE(
    transaction_id INT,
    transaction_date TIMESTAMP,
    total_amount NUMERIC,
    payment_method VARCHAR(50),
    items_count BIGINT,
    products_list TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        st.id,
        st.transaction_date,
        st.total_amount,
        st.payment_method,
        COUNT(sli.id) AS items_count,
        STRING_AGG(p.name, ', ') AS products_list
    FROM sales_transactions st
    INNER JOIN sales_line_items sli ON st.id = sli.transaction_id
    INNER JOIN products p ON sli.product_id = p.id
    GROUP BY st.id, st.transaction_date, st.total_amount, st.payment_method
    ORDER BY st.transaction_date DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_recent_transactions IS 'Get recent sales transactions with item counts and product lists';