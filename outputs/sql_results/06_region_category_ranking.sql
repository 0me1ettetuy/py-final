WITH counts AS (
 SELECT region_code, category_name, COUNT(*) AS poi_count
 FROM poi WHERE region_code IS NOT NULL GROUP BY region_code,category_name)
SELECT r.region_name, c.category_name, c.poi_count,
DENSE_RANK() OVER (PARTITION BY c.region_code ORDER BY c.poi_count DESC) AS category_rank
FROM counts c JOIN region r ON c.region_code=r.region_code
ORDER BY r.region_name, category_rank;