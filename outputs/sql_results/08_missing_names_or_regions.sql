SELECT category_name,COUNT(*) AS total,
SUM(CASE WHEN name IS NULL OR TRIM(name)='' THEN 1 ELSE 0 END) AS missing_name,
SUM(CASE WHEN region_code IS NULL THEN 1 ELSE 0 END) AS missing_region
FROM poi GROUP BY category_name ORDER BY total DESC;