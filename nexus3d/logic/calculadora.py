PRECIO_KWH = 1.05
CONSUMO_WATTS = 350
COSTO_MAQUINA_HORA = 1.12
OVERHEAD = 1.3
STOCK_MINIMO_ALERTA = 10

ESTADOS_COTIZACION = ["Borrador", "Guardada", "Completada", "Cancelada"]


def calc_filament_cost(color_entries, db):
    fallback_price = (
        db.cursor.execute(
            "SELECT precio_unitario FROM materiales WHERE categoria LIKE '%filamento%' LIMIT 1"
        ).fetchone() or (850,)
    )[0]
    total = 0.0
    for entry in color_entries:
        grams = float(entry['gramos'].get() or 0)
        if grams <= 0:
            continue
        mat_str = entry['combo'].get()
        if mat_str:
            m_id = int(mat_str.split(" | ")[0])
            row = db.cursor.execute(
                "SELECT precio_unitario FROM materiales WHERE id=?", (m_id,)
            ).fetchone()
            price = row[0] if row else fallback_price
        else:
            price = fallback_price
        total += (price / 1000) * grams
    return total


def calc_piece_cost(hours, filament_cost, extra_mats_cost, ganancia):
    c_luz = (CONSUMO_WATTS / 1000) * hours * PRECIO_KWH
    c_maq = hours * COSTO_MAQUINA_HORA
    return ((filament_cost + c_luz + c_maq) * OVERHEAD * ganancia) + extra_mats_cost


def calc_stock_product_cost(hours, filament_cost, extra_mats_cost, ganancia):
    c_ops = ((CONSUMO_WATTS / 1000) * hours * PRECIO_KWH + hours * COSTO_MAQUINA_HORA) * OVERHEAD
    return (filament_cost + c_ops) * ganancia + extra_mats_cost
