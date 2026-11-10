SELECT
    strftime('%Y-%m', scraped_at) AS month,
    product_id,
    ROUND(AVG(price), 2) AS avg_price,
    COUNT(*) AS records
FROM price_history
GROUP BY month, product_id
ORDER BY month DESC, product_id;