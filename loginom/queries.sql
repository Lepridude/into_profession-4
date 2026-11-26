-- GetUserHistory: input user_id (Integer), output TOP-10 products.
SELECT p.product_name AS product_name,
       p.department_rus AS department_rus,
       p.aisle AS aisle,
       COUNT(*) AS order_count
FROM orders_prior AS op
INNER JOIN orders AS o ON o.order_id = op.order_id
INNER JOIN products AS p ON p.product_id = op.product_id
WHERE o.user_id = :user_id
GROUP BY p.product_id, p.product_name, p.department_rus, p.aisle
ORDER BY order_count DESC, p.product_name ASC
LIMIT 10;

-- CheckUserId: input user_id (Integer), output exactly one row.
SELECT CASE
    WHEN EXISTS (SELECT 1 FROM orders WHERE user_id = :user_id) THEN 1
    ELSE 0
END AS user_exists;
