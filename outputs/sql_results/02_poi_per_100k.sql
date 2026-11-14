SELECT r.region_name, r.population,
COUNT(p.osm_key) AS poi_count,
ROUND(100000.0*COUNT(p.osm_key)/r.population, 2) AS poi_per_100k
FROM region r LEFT JOIN poi p ON r.region_code=p.region_code
GROUP BY r.region_code ORDER BY poi_per_100k DESC;