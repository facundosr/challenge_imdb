CREATE OR REPLACE VIEW vista_peliculas_actores AS
SELECT
  p.id AS pelicula_id,
  p.titulo,
  p.anio,
  p.calificacion,
  p.duracion,
  a.id AS actor_id,
  a.nombre AS actor_nombre
FROM peliculas p
JOIN actores a ON a.pelicula_id = p.id;

SELECT *
FROM vista_peliculas_actores
WHERE actor_nombre = 'Marlon Brando';