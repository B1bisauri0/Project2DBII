# Instrucciones para ejecutar el proyecto

1. **Desempaquetar el .zip del proyecto**:

2. **Generar los csv de los nodos**:

   Para realizar este paso, se requiere ir a la siguiente ruta y pegarla en la terminal:

   ```bash
   .\init-map\generator.py
   ```

   Una vez ejecutado ese programa de Python, se crearan las carpetas de csv en las que se encuentra todo un mapa de coordenadas de la provincia de Cartago.

3. **Ejecutar el docker compose up**:
   Se debe de ejecutar todo el docker-compose primero con el:

   ```
   docker compose up --build
   ```

   Con esto se empezaran a cargar todos los contenedores al sistema de docker.

4. **Crear los nodos y sus relaciones del mapa de Cartago en Neo4J**:

   Para este paso, se debe de verificar que ya esta corriendo de manera correcta el servidor de Neo4J. Para realizar la verificacion se puede ir a `http://localhost:7474/browser/`. Una vez verificado, se puede ejecutar el siguiente programa para cargar los csv a Neo4J.

   ```bash
   .\init-map\load_nodes.py
   ```

5. **Cargar los datos de Postgres a Neo4J**:

   Para poder realizar este paso, se debe de verificar que este Postgres corriendo de manera correcta en docker y verificar que se haya inicializado la base de datos de manera correcta. Esto se puede verificar en `http://localhost:5050/browser/`. Una vez verificado, se puede ejecutar el programa que carga los datos de Postgres a Neo4J y crea sus respectivas relaciones.

   ```bash
   .\export-neo4j\export-postgres-neo.py
   ```

   Una vez ejecutado ese programa, se procedera a correr otro programa para cargar las relaciones de donde se va a iniciar el pedido de alguna orden y donde va a terminar. Para eso se ejecutara el siguiente programa:

   ```bash
   .\export-neo4j\match-nodes-users.py
   ```

6. **Arrancar el API para realizar las consultas a Neo4J**:

   Para poder empezar a correr el API y realizar las consultas se debe de ir a la ruta de `.\src\` y ejecutar el siguiente comando:

   ```
   uvicorn main:app --reload
   ```

   Abre tu navegador y ve a `http://localhost:3000/docs`. Una vez dentro de el servicio se podran ver todos los request que se le pueden hacer a la base de datos de Neo4J. Para la consulta del reporte, en el swagger da la opcion de descargarlo una vez hecha la consulta.
