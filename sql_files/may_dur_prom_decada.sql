WITH duracion_por_decada AS (
  SELECT
    (anio / 10) * 10 AS decada,
    titulo,
    anio,
    duracion,
    ROW_NUMBER() OVER (PARTITION BY (anio / 10) * 10 ORDER BY duracion DESC) AS rn
  FROM peliculas
  WHERE duracion IS NOT NULL AND anio IS NOT NULL
)
SELECT decada, titulo, anio, duracion
FROM duracion_por_decada
WHERE rn <= 5
ORDER BY decada, duracion DESC;
