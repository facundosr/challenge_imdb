SELECT
  anio,
  STDDEV_POP(calificacion) AS desviacion_estandar_calificacion
FROM peliculas
WHERE calificacion IS NOT NULL AND anio IS NOT NULL
GROUP BY anio
ORDER BY anio;
