-- SQL script that ranks country origins of bands
-- Using the origin column
SELECT origin, SUM(nb_fans) AS nb_fans
FROM metal_bands
GROUP BY origin
ORDER BY nb_fans DESC;
