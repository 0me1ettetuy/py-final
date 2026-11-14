SELECT r.region_name, COUNT(p.osm_key) AS poi_count
FROM region r LEFT JOIN poi p ON p.region_code=r.region_code
GROUP BY r.region_code ORDER BY poi_count DESC;