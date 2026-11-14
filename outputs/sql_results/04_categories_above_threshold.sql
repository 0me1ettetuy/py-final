SELECT category_name, COUNT(*) AS poi_count
FROM poi GROUP BY category_name HAVING COUNT(*) >= 100
ORDER BY poi_count DESC;