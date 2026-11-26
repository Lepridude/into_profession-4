-- GetUserHistory: input variable user_id (Integer); output fields below.
SELECT p.product_name AS product_name,
       p.aisle AS aisle,
       p.department AS department,
       p.department_rus AS department_rus,
       COUNT(*) AS order_count
FROM orders_prior AS op
JOIN orders AS o ON o.order_id = op.order_id
JOIN products AS p ON p.product_id = op.product_id
WHERE o.user_id = :user_id
GROUP BY p.product_id, p.product_name, p.aisle, p.department, p.department_rus
ORDER BY order_count DESC, p.product_name ASC
LIMIT 10;

-- CheckUserId: input variable user_id (Integer); output one row user_exists=1/0.
SELECT CASE WHEN EXISTS (SELECT 1 FROM orders WHERE user_id = :user_id)
            THEN 1 ELSE 0 END AS user_exists;
