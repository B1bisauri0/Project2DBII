from neo4j import GraphDatabase
from fastapi import FastAPI, HTTPException

app = FastAPI()

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

@app.get("/")
async def root():
    return {"message": "Welcome to the Neo4j API"}

# Calculate the route for a given order
@app.get("/routeOrder/{order_id}")
def calculateRoute(order_id: float):
    with driver.session() as session:
        try:
            # Project the graph in memory
            session.run("""
                CALL gds.graph.project(
                    'rutas-grafo',
                    'NodoCalle',
                    {
                        CONECTADO_A: {
                            properties: 'distancia'
                        }
                    }
                )
            """)

            # Execute the Dijkstra algorithm to find the shortest path
            result = session.run("""
                MATCH (o:Order {id: $order_id})
                MATCH (start:NodoCalle)<-[:INICIA_EN]-(o)-[:ENTREGA_EN]->(end:NodoCalle)

                CALL gds.shortestPath.dijkstra.stream('rutas-grafo', {
                    sourceNode: id(start),
                    targetNode: id(end),
                    relationshipWeightProperty: 'distancia'
                })
                YIELD index, sourceNode, targetNode, totalCost, nodeIds

                RETURN 
                    [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS ruta_ids,
                    totalCost AS distancia_total
            """, order_id=float(order_id))

            row = result.single()
            if row is None:
                raise HTTPException(status_code=404, detail="No se encontró una ruta para ese pedido")

            ruta = row["ruta_ids"]
            distancia = row["distancia_total"]

            return {
                "pedido": order_id,
                "ruta": ruta,
                "distancia_total": distancia
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculando ruta: {str(e)}")

        finally:
            # Clean up the graph projection in memory
            session.run("CALL gds.graph.drop('rutas-grafo', false)")

@app.get("/top5Copurchases")
def top5Copurchases():
    with driver.session() as session:
        result = session.run("""
            MATCH (p1:Product)<-[:HAVE]-(o:Order)-[:HAVE]->(p2:Product)
            WHERE p1.id < p2.id
            WITH p1.nombre AS prod1, p2.nombre AS prod2, COUNT(*) AS veces_juntos
            RETURN prod1, prod2, veces_juntos
            ORDER BY veces_juntos DESC
            LIMIT 5
        """)
        return [{"producto1": r["prod1"], "producto2": r["prod2"], "veces_juntos": r["veces_juntos"]} for r in result]

@app.get("/influencialUser")
def influencialUser():
    with driver.session() as session:
        result = session.run("""
            MATCH (u1:User)-[:RECOMMENDED]->(u2:User)
            RETURN u1.username AS recomendador, COUNT(u2) AS cantidad_recomendados
            ORDER BY cantidad_recomendados DESC
        """)
        return [{"usuario": r["recomendador"], "recomendaciones": r["cantidad_recomendados"]} for r in result]
