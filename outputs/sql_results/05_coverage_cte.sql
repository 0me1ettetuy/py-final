WITH category_counts AS (
 SELECT region_code, COUNT(DISTINCT category_name) AS categories_observed, COUNT(*) AS poi_count
 FROM poi WHERE region_code IS NOT NULL GROUP BY region_code)
SELECT r.region_name, COALESCE(c.categories_observed,0) AS categories_observed,
COALESCE(c.poi_count,0) AS poi_count
FROM region r LEFT JOIN category_counts c USING(region_code)
ORDER BY categories_observed DESC, poi_count DESC;