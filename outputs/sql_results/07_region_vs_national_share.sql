WITH counts AS (
 SELECT region_code,category_name,COUNT(*) AS count_in_region
 FROM poi WHERE region_code IS NOT NULL GROUP BY region_code,category_name),
national AS (SELECT category_name,SUM(count_in_region) AS count_all FROM counts GROUP BY category_name)
SELECT r.region_name,c.category_name,c.count_in_region,n.count_all,
ROUND(100.0*c.count_in_region/NULLIF(n.count_all,0),2) AS share_of_national_category_pct
FROM counts c JOIN national n USING(category_name) JOIN region r USING(region_code)
ORDER BY share_of_national_category_pct DESC;