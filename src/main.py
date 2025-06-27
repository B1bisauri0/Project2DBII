from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from functions import driver, show_graph_mem, clear_graph_mem, top5_copurchases, influencial_user, obtein_dealer_orders, close_driver, calculate_route
import atexit
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

app = FastAPI()

@atexit.register
def shutdown():
    close_driver()

@app.get("/")
async def root():
    return {"message": "Welcome to the Neo4j API"}

# Endpoint to calculate the route for a given order
@app.get("/routeOrder/{order_id}")
def calculate_route_endpoint(order_id: float):
    with driver.session() as session:
        try:
            show_graph_mem(session)
            ruta_data = calculate_route(session, order_id)
            if not ruta_data:
                raise HTTPException(status_code=404, detail="No se encontró una ruta para ese pedido")

            return {
                "pedido": order_id,
                "ruta": ruta_data["ruta_ids"],
                "distancia_total": ruta_data["distancia_total"]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculando ruta: {str(e)}")

        finally:
            clear_graph_mem(session)

# Endpoint to get the top 5 copurchased products
@app.get("/top5Copurchases")
def get_top5_copurchases_endpoint():
    with driver.session() as session:
        return top5_copurchases(session)

# Endpoint to get the influential users based on recommendations
@app.get("/influencialUser")
def get_influencial_user_endpoint():
    with driver.session() as session:
        return influencial_user(session)

# Endpoint to get dealer orders and their routes
@app.get("/dealer/{dealer_id}")
def get_dealer_orders_and_routes_endpoint(dealer_id: int):
    with driver.session() as session:
        try:
            show_graph_mem(session)
            pedidos = obtein_dealer_orders(session, dealer_id)
            if not pedidos:
                raise HTTPException(status_code=404, detail=f"No se encontraron pedidos para el repartidor {dealer_id}")
            return {"dealer_id": dealer_id, "pedidos": pedidos}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando datos: {str(e)}")
        finally:
            clear_graph_mem(session)

# Endpoint to export a general report as a PDF
@app.get("/report/export")
def export_reporte_general_endpoint():
    with driver.session() as session:
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        y = 800
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, y, "Reporte General de Neo4j")
        y -= 40
        
        # Tp 5 productos más comprados juntos
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "Top 5 Productos Más Comprados Juntos")
        y -= 20
        p.setFont("Helvetica", 12)
        copurchases = top5_copurchases(session)
        for i, item in enumerate(copurchases, start=1):
            text = f"{i}. {item['producto1']} & {item['producto2']} - Veces juntos: {item['veces_juntos']}"
            p.drawString(120, y, text)
            y -= 18
        
        y -= 30
        # Influential users
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "Usuarios Más Influyentes en Recomendaciones")
        y -= 20
        p.setFont("Helvetica", 12)
        influentials = influencial_user(session)
        for i, item in enumerate(influentials, start=1):
            text = f"{i}. Usuario: {item['usuario']} - Recomendaciones: {item['recomendaciones']}"
            p.drawString(120, y, text)
            y -= 18

        y -= 30
        # All dealers and their orders
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "Pedidos y Rutas de Todos los Repartidores")
        y -= 20

        # Obtain all dealers list
        repartidores = session.run("MATCH (d:Dealer) RETURN d.id AS id, d.name AS name, d.lastName AS lastName ORDER BY d.id")
        
        show_graph_mem(session)

        for r in repartidores:
            if y < 120:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 12)

            repartidor_id = r["id"]
            repartidor_nombre = f"{r['name']} {r['lastName']}"
            p.setFont("Helvetica-Bold", 13)
            p.drawString(100, y, f"Repartidor: {repartidor_nombre} (ID: {repartidor_id})")
            y -= 20
            p.setFont("Helvetica", 12)

            pedidos = obtein_dealer_orders(session, repartidor_id)
            if pedidos:
                MAX_WIDTH = 350
                LINE_HEIGHT = 14
                MIN_Y = 50
                
                for pedido in pedidos:
                    if y < 100:
                        p.showPage()
                        y = 800
                        p.setFont("Helvetica", 12)

                    texto_pedido = f"Pedido ID: {pedido['order_id']} - Total: {pedido['total_price']}"
                    p.drawString(110, y, texto_pedido)
                    y -= 15

                    ruta = pedido.get("ruta", [])
                    distancia = pedido.get("distancia_total", "N/A")
                    ruta_texto = ', '.join(map(str, ruta)) if ruta else "Sin ruta"
                    lineas_ruta = simpleSplit(ruta_texto, "Helvetica", 10, MAX_WIDTH)

                    for linea in lineas_ruta:
                        if y < MIN_Y:
                            p.showPage()
                            y = 800
                            p.setFont("Helvetica", 12)
                        p.drawString(130, y, linea)
                        y -= LINE_HEIGHT

                    if y < MIN_Y:
                        p.showPage()
                        y = 800
                        p.setFont("Helvetica", 12)
                    p.drawString(130, y, f"Distancia total: {distancia}")
                    y -= 20
            else:
                p.drawString(110, y, "No se encontraron pedidos para este repartidor.")
                y -= 20

        clear_graph_mem(session)
        p.showPage()
        p.save()
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reporte_general_neo4j.pdf"}
        )