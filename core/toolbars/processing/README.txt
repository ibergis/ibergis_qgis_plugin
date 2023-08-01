Done:
- Performance para 600.000 TIN BCN 	(cellsize-10) 
	- Colapsar geometries: 15-20 seg
	- Triangular 30 segundos
	- Insertar en geopackage 4 minutos
	- Genera 2dmesh 10 segundos

Todo:
- Proceso de check (internamente limpia i después hace check y te dice donde)
- Proceso de triangulación (limpieza, check y si va todo bien triangula i si no dice donde)

Codigo: 
- Se hará un proveedor de processing, y usaremos esta estrategia, que passar por hacer una classe
- Resolver pip install de todas las dependencias
- el mallador tiene diferentes opciones de mallado (gmesher). Hemos probado bydefault. Se podria investigar parametros:
   https://deltares.github.io/pandamesh/api/gmsh.html
- El cellsize tien la opción de trabakar con un raster, per si interessa (problema memoria per BCN)
- Estudiar la materialización de los resultados de la malla:
	- Insertar por codigo directamente en geopackage (BCN- 4minttos)
	- Insertar al geopackage mitjançant qgis ???
	- Generar capa temporal de QGIS i mover al geopackage ???
	- Generar una malla en formato malla  (Generar es instanani carregar a qgis son 15 min o més)
	- Seria deseable que IBER tome estandar de lectura 2Dmesh estandar, si es que hay