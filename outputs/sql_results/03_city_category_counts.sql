SELECT r.region_name, c.category_name, COUNT(p.osm_key) AS poi_count
FROM poi p JOIN region r ON p.region_code=r.region_code
JOIN category c ON p.category_name=c.category_name
WHERE r.region_code IN ('astana','almaty_city','shymkent')
GROUP BY r.region_code, c.category_name ORDER BY r.region_name,poi_count DESC;