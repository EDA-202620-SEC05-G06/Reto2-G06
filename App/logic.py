"""
LOGICA (controlador) - ISIS1225 Reto 2 (Grupo 06).

Carga de datos y requerimientos.

Requerimientos implementados: 1, 2, 5 y 6.
La carga de datos (load_data) es infraestructura compartida del grupo: se deja
implementada aqui porque construye las tablas de hash que consultan TODOS los
requerimientos. El equipo debe conciliar esta seccion con el resto del reto.

Estructuras del curso usadas (carpeta DataStructures):
  - array_list             -> listas basadas en arreglo
  - single_linked_list     -> buckets del mapa por Separate Chaining
  - map_separate_chaining  -> tablas de hash por encadenamiento separado
  - map_linear_probing     -> tablas de hash por sondeo lineal (conteo por
                              producto del Req. 2, agregacion por pais del Req. 6)
  - sorting.merge_sort     -> ordenamiento generico O(n log n) y estable
"""

import time
import csv

import DataStructures.List.array_list as al
import DataStructures.Map.map_separate_chaining as mp
import DataStructures.Map.map_linear_probing as lp
import DataStructures.Sort.sorting as sort

# Se aumenta el limite de campos de lectura del CSV segun la nota del reto.
csv.field_size_limit(2147483647)


# =============================================================================
# Creacion del catalogo
# =============================================================================

def new_logic():
    """
    Crea el catalogo con las estructuras de datos del reto.

    Tablas de hash construidas durante la carga:
      - orders_by_month:   Separate Chaining. Llave "YYYY-MM" -> array_list de
                           pedidos de ese mes. Soporta el Requerimiento 1.
      - orders_by_country: Separate Chaining. Llave Country -> array_list de
                           pedidos de ese pais. Soporta los Requerimientos 2 y 5.
      - orders_by_product: Separate Chaining. Llave Product -> array_list de
                           pedidos de ese producto. Soporta el Requerimiento 6.
      - channel_count:     Separate Chaining. Llave Channel -> numero de pedidos
                           del canal. Soporta el reporte de la carga.
    """
    catalog = {
        "orders": al.new_list(),
        "orders_by_month": mp.new_map(31, 4.0),
        "orders_by_country": mp.new_map(31, 4.0),
        "orders_by_product": mp.new_map(31, 4.0),
        "channel_count": mp.new_map(11, 4.0),
        # Datos de resumen calculados durante la carga:
        "min_amount_order": None,
        "max_amount_order": None,
        "min_date": None,
        "max_date": None,
    }
    return catalog


# =============================================================================
# Utilidades de parseo
# =============================================================================

def _to_float(value):
    """Convierte a float de forma segura; vacio o invalido -> 0.0."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _to_int(value):
    """Convierte a int de forma segura; vacio o invalido -> 0."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def _clean_text(value):
    """Retorna el texto sin espacios sobrantes; vacio -> 'Unknown'."""
    if value is None:
        return "Unknown"
    value = value.strip()
    return value if value != "" else "Unknown"


def _new_order(row):
    """Construye el registro (dict) de un pedido a partir de una fila del CSV."""
    return {
        "Order_ID": _clean_text(row.get("Order_ID")),
        "Product": _clean_text(row.get("Product")),
        "Country": _clean_text(row.get("Country")),
        "Channel": _clean_text(row.get("Channel")),
        "Order_Date": _clean_text(row.get("Order_Date")),
        "Discount_Pct": _to_float(row.get("Discount_Pct")),
        "Price_per_Box": _to_float(row.get("Price_per_Box")),
        "Marketing_Spend": _to_float(row.get("Marketing_Spend")),
        "Boxes_Shipped": _to_int(row.get("Boxes_Shipped")),
        "Amount": _to_float(row.get("Amount")),
    }


# =============================================================================
# Carga de datos
# =============================================================================

def load_data(catalog, filename):
    """
    Carga los datos del reto leyendo el archivo UNA sola vez. Durante la lectura
    construye la lista principal y las tablas de hash. Retorna el tiempo de carga
    en milisegundos (el reporte se arma con get_load_report).
    """
    start = get_time()
    with open(filename, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            order = _new_order(row)
            al.add_last(catalog["orders"], order)
            _index_by_month(catalog, order)
            _index_by_country(catalog, order)
            _index_by_product(catalog, order)
            _count_channel(catalog, order)
            _track_summary(catalog, order)
    stop = get_time()
    return delta_time(start, stop)


def _index_by_month(catalog, order):
    """Agrega el pedido al bucket 'YYYY-MM' del mapa orders_by_month."""
    key = order["Order_Date"][:7]  # "YYYY-MM"
    bucket = mp.get(catalog["orders_by_month"], key)
    if bucket is None:
        bucket = al.new_list()
        mp.put(catalog["orders_by_month"], key, bucket)
    al.add_last(bucket, order)


def _index_by_country(catalog, order):
    """Agrega el pedido al bucket del pais en el mapa orders_by_country."""
    key = order["Country"]
    bucket = mp.get(catalog["orders_by_country"], key)
    if bucket is None:
        bucket = al.new_list()
        mp.put(catalog["orders_by_country"], key, bucket)
    al.add_last(bucket, order)


def _index_by_product(catalog, order):
    """Agrega el pedido al bucket del producto en el mapa orders_by_product."""
    llave = order["Product"]
    pedidosprod = mp.get(catalog["orders_by_product"], llave)
    if pedidosprod is None:
        pedidosprod = al.new_list()
        mp.put(catalog["orders_by_product"], llave, pedidosprod)
    al.add_last(pedidosprod, order)


def _count_channel(catalog, order):
    """Incrementa el contador de pedidos del canal."""
    key = order["Channel"]
    current = mp.get(catalog["channel_count"], key)
    if current is None:
        current = 0
    mp.put(catalog["channel_count"], key, current + 1)


def _track_summary(catalog, order):
    """Actualiza min/max de Amount y de fecha durante la carga."""
    if catalog["min_amount_order"] is None or _is_lower_amount(order, catalog["min_amount_order"]):
        catalog["min_amount_order"] = order
    if catalog["max_amount_order"] is None or _is_higher_amount(order, catalog["max_amount_order"]):
        catalog["max_amount_order"] = order
    date = order["Order_Date"]
    if catalog["min_date"] is None or date < catalog["min_date"]:
        catalog["min_date"] = date
    if catalog["max_date"] is None or date > catalog["max_date"]:
        catalog["max_date"] = date


def _is_lower_amount(order, ref):
    """True si order tiene menor Amount (desempate: menor Price_per_Box, luego Order_ID)."""
    if order["Amount"] != ref["Amount"]:
        return order["Amount"] < ref["Amount"]
    if order["Price_per_Box"] != ref["Price_per_Box"]:
        return order["Price_per_Box"] < ref["Price_per_Box"]
    return order["Order_ID"] < ref["Order_ID"]


def _is_higher_amount(order, ref):
    """True si order tiene mayor Amount (desempate: menor Price_per_Box, luego Order_ID)."""
    if order["Amount"] != ref["Amount"]:
        return order["Amount"] > ref["Amount"]
    if order["Price_per_Box"] != ref["Price_per_Box"]:
        return order["Price_per_Box"] < ref["Price_per_Box"]
    return order["Order_ID"] < ref["Order_ID"]


def get_load_report(catalog):
    """
    Arma el reporte de la carga (Parte 2) usando las estructuras ya construidas.
    Para los primeros/ultimos 5 ordena una copia de la lista principal de manera
    descendente por Amount (desempate Order_ID ascendente) con merge sort.
    """
    orders = catalog["orders"]
    total = al.size(orders)

    ordered = al.sub_list(orders, 0, total)
    sort.merge_sort(ordered, _cmp_amount_desc_id_asc)

    first_five = al.new_list()
    last_five = al.new_list()
    i = 0
    while i < 5 and i < total:
        al.add_last(first_five, al.get_element(ordered, i))
        i += 1
    i = total - 5 if total >= 5 else 0
    while i < total:
        al.add_last(last_five, al.get_element(ordered, i))
        i += 1

    channels = al.new_list()
    for key in mp.key_set(catalog["channel_count"])["elements"]:
        al.add_last(channels, {"Channel": key,
                               "count": mp.get(catalog["channel_count"], key)})
    sort.merge_sort(channels, lambda a, b: a["Channel"] < b["Channel"])

    return {
        "total": total,
        "channels": channels,
        "min_date": catalog["min_date"],
        "max_date": catalog["max_date"],
        "min_amount_order": catalog["min_amount_order"],
        "max_amount_order": catalog["max_amount_order"],
        "first_five": first_five,
        "last_five": last_five,
    }


# =============================================================================
# Criterios de ordenamiento (sort_criteria)
# =============================================================================

def _cmp_amount_desc_id_asc(a, b):
    """Descendente por Amount; desempate Order_ID ascendente."""
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def _cmp_req1(a, b):
    """Req1: descendente por Discount_Pct; desempate Amount desc, luego Order_ID asc."""
    if a["Discount_Pct"] != b["Discount_Pct"]:
        return a["Discount_Pct"] > b["Discount_Pct"]
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def _cmp_req2(a, b):
    """Req2: ascendente por Boxes_Shipped; desempate Order_Date desc, luego Order_ID asc."""
    if a["Boxes_Shipped"] != b["Boxes_Shipped"]:
        return a["Boxes_Shipped"] < b["Boxes_Shipped"]
    if a["Order_Date"] != b["Order_Date"]:
        return a["Order_Date"] > b["Order_Date"]
    return a["Order_ID"] < b["Order_ID"]


def _cmp_req5(a, b):
    """Req5: descendente por recaudo; desempate Boxes_Shipped total desc, luego nombre asc."""
    if a["amount_total"] != b["amount_total"]:
        return a["amount_total"] > b["amount_total"]
    if a["boxes_total"] != b["boxes_total"]:
        return a["boxes_total"] > b["boxes_total"]
    return a["product"] < b["product"]


def _cmp_req6(a, b):
    """Req6: descendente por eficiencia; desempate Amount total desc, luego Country asc."""
    if a["efficiency"] != b["efficiency"]:
        return a["efficiency"] > b["efficiency"]
    if a["amount_total"] != b["amount_total"]:
        return a["amount_total"] > b["amount_total"]
    return a["country"] < b["country"]


# =============================================================================
# Requerimiento 1 (Individual): pedidos por mes y rango de descuento
# =============================================================================

def req_1(catalog, year, month, disc_min, disc_max):
    """
    Consulta los pedidos de un mes (year, month) cuyo Discount_Pct esta en
    [disc_min, disc_max]. Accede directamente al bucket del mes en la tabla de
    hash orders_by_month (NO recorre la lista principal de pedidos).

    Retorna un dict con el tiempo, el conteo, el monto total recaudado, los
    promedios de Price_per_Box y Boxes_Shipped, y la lista de pedidos ordenada
    de manera descendente por Discount_Pct.
    """
    start = get_time()

    key = "%04d-%02d" % (int(year), int(month))
    month_bucket = mp.get(catalog["orders_by_month"], key)

    result = al.new_list()
    total_amount = 0.0
    sum_price = 0.0
    sum_boxes = 0

    if month_bucket is not None:
        for order in month_bucket["elements"]:
            if disc_min <= order["Discount_Pct"] <= disc_max:
                al.add_last(result, order)
                total_amount += order["Amount"]
                sum_price += order["Price_per_Box"]
                sum_boxes += order["Boxes_Shipped"]

    sort.merge_sort(result, _cmp_req1)

    count = al.size(result)
    avg_price = (sum_price / count) if count > 0 else 0.0
    avg_boxes = (sum_boxes / count) if count > 0 else 0.0

    stop = get_time()
    return {
        "time_ms": delta_time(start, stop),
        "count": count,
        "total_amount": total_amount,
        "avg_price": avg_price,
        "avg_boxes": avg_boxes,
        "orders": result,
    }


# =============================================================================
# Requerimiento 2 (Individual): pedidos por pais y rango de cajas enviadas
# =============================================================================

def req_2(catalog, pais, cajasmin, cajasmax):
    """
    Consulta los pedidos de un pais cuyo Boxes_Shipped esta en [cajasmin,
    cajasmax]. Accede directamente al bucket del pais en la tabla de hash
    orders_by_country (NO recorre la lista principal de pedidos) y cuenta los
    pedidos por producto en una tabla de hash por Linear Probing.

    Retorna un dict con el tiempo, el conteo, el numero de productos diferentes,
    los promedios de Marketing_Spend y Amount, el producto mas frecuente con su
    numero de pedidos, y la lista de pedidos ordenada de manera ascendente por
    Boxes_Shipped.
    """
    inicio = get_time()

    pedidospais = mp.get(catalog["orders_by_country"], pais)

    resultado = al.new_list()
    cuentaprod = lp.new_map(17, 0.5)
    sumamercadeo = 0.0
    sumamonto = 0.0

    if pedidospais is not None:
        for pedido in pedidospais["elements"]:
            if cajasmin <= pedido["Boxes_Shipped"] <= cajasmax:
                al.add_last(resultado, pedido)
                sumamercadeo += pedido["Marketing_Spend"]
                sumamonto += pedido["Amount"]
                actual = lp.get(cuentaprod, pedido["Product"])
                if actual is None:
                    actual = 0
                lp.put(cuentaprod, pedido["Product"], actual + 1)

    # Producto mas frecuente; ante empate, el de nombre alfabeticamente menor.
    prodtop = None
    cuentatop = 0
    for producto in lp.key_set(cuentaprod)["elements"]:
        frecuencia = lp.get(cuentaprod, producto)
        if frecuencia > cuentatop or (frecuencia == cuentatop and producto < prodtop):
            prodtop = producto
            cuentatop = frecuencia

    sort.merge_sort(resultado, _cmp_req2)

    total = al.size(resultado)
    prommercadeo = (sumamercadeo / total) if total > 0 else 0.0
    prommonto = (sumamonto / total) if total > 0 else 0.0

    fin = get_time()
    return {
        "time_ms": delta_time(inicio, fin),
        "count": total,
        "num_products": lp.size(cuentaprod),
        "avg_marketing": prommercadeo,
        "avg_amount": prommonto,
        "top_product": prodtop,
        "top_product_count": cuentatop,
        "orders": resultado,
    }


# =============================================================================
# Requerimiento 5 (Grupal): N productos con mayor recaudo por pais y fechas
# =============================================================================

def req_5(catalog, n, country, date_ini, date_fin):
    """
    Obtiene los N productos con mayor recaudo en un pais durante [date_ini,
    date_fin]. Accede al bucket del pais en la tabla de hash orders_by_country y
    agrega por producto en una segunda tabla de hash (NO recorre la lista
    principal de pedidos).

    Retorna un dict con el tiempo, el numero de pedidos filtrados, el numero de
    productos diferentes, el recaudo total y el top N de productos.
    """
    start = get_time()

    country_bucket = mp.get(catalog["orders_by_country"], country)

    by_product = mp.new_map(31, 4.0)
    total_orders = 0
    total_amount = 0.0

    if country_bucket is not None:
        for order in country_bucket["elements"]:
            if date_ini <= order["Order_Date"] <= date_fin:
                total_orders += 1
                total_amount += order["Amount"]
                _accumulate_product(by_product, order)

    # Construir array_list de resumenes por producto a partir del mapa.
    products = al.new_list()
    for acc in mp.value_set(by_product)["elements"]:
        acc["avg_price"] = (acc["price_sum"] / acc["count"]) if acc["count"] > 0 else 0.0
        acc["avg_discount"] = (acc["disc_sum"] / acc["count"]) if acc["count"] > 0 else 0.0
        al.add_last(products, acc)

    num_products = al.size(products)

    sort.merge_sort(products, _cmp_req5)

    top = al.new_list()
    limit = n if n < num_products else num_products
    i = 0
    while i < limit:
        al.add_last(top, al.get_element(products, i))
        i += 1

    stop = get_time()
    return {
        "time_ms": delta_time(start, stop),
        "total_orders": total_orders,
        "num_products": num_products,
        "total_amount": total_amount,
        "top": top,
    }


def _accumulate_product(by_product, order):
    """Acumula las metricas del pedido en el resumen del producto (tabla de hash)."""
    key = order["Product"]
    acc = mp.get(by_product, key)
    if acc is None:
        acc = {
            "product": key,
            "count": 0,
            "boxes_total": 0,
            "amount_total": 0.0,
            "price_sum": 0.0,
            "disc_sum": 0.0,
            "marketing_total": 0.0,
        }
        mp.put(by_product, key, acc)
    acc["count"] += 1
    acc["boxes_total"] += order["Boxes_Shipped"]
    acc["amount_total"] += order["Amount"]
    acc["price_sum"] += order["Price_per_Box"]
    acc["disc_sum"] += order["Discount_Pct"]
    acc["marketing_total"] += order["Marketing_Spend"]


# =============================================================================
# Requerimiento 6 (Grupal): N paises con mayor eficiencia de mercadeo
# =============================================================================

def req_6(catalog, n, producto, fechaini, fechafin):
    """
    Obtiene los N paises con mayor eficiencia de mercadeo para un producto
    durante [fechaini, fechafin]. Accede al bucket del producto en la tabla de
    hash orders_by_product (NO recorre la lista principal de pedidos) y agrega
    por pais en una tabla de hash por Linear Probing.

    La eficiencia de un pais es suma(Amount) / suma(Marketing_Spend). Los paises
    con suma de Marketing_Spend igual a cero no entran al ranking.

    Retorna un dict con el tiempo, el numero de pedidos filtrados, el numero de
    paises diferentes, el Amount total, el Marketing_Spend total y el top N.
    """
    inicio = get_time()

    pedidosprod = mp.get(catalog["orders_by_product"], producto)

    porpais = lp.new_map(11, 0.5)
    totalpedidos = 0
    totalmonto = 0.0
    totalmercadeo = 0.0

    if pedidosprod is not None:
        for pedido in pedidosprod["elements"]:
            if fechaini <= pedido["Order_Date"] <= fechafin:
                totalpedidos += 1
                totalmonto += pedido["Amount"]
                totalmercadeo += pedido["Marketing_Spend"]
                acumulado = lp.get(porpais, pedido["Country"])
                if acumulado is None:
                    acumulado = {
                        "country": pedido["Country"],
                        "count": 0,
                        "amount_total": 0.0,
                        "marketing_total": 0.0,
                        "boxes_total": 0,
                        "price_sum": 0.0,
                    }
                    lp.put(porpais, pedido["Country"], acumulado)
                acumulado["count"] += 1
                acumulado["amount_total"] += pedido["Amount"]
                acumulado["marketing_total"] += pedido["Marketing_Spend"]
                acumulado["boxes_total"] += pedido["Boxes_Shipped"]
                acumulado["price_sum"] += pedido["Price_per_Box"]

    # Solo entran al ranking los paises con eficiencia calculable.
    paises = lp.value_set(porpais)
    ranking = al.new_list()
    for acumulado in paises["elements"]:
        if acumulado["marketing_total"] > 0:
            acumulado["avg_price"] = acumulado["price_sum"] / acumulado["count"]
            acumulado["efficiency"] = (acumulado["amount_total"]
                                       / acumulado["marketing_total"])
            al.add_last(ranking, acumulado)

    sort.merge_sort(ranking, _cmp_req6)

    top = al.new_list()
    limite = n if n < al.size(ranking) else al.size(ranking)
    i = 0
    while i < limite:
        al.add_last(top, al.get_element(ranking, i))
        i += 1

    fin = get_time()
    return {
        "time_ms": delta_time(inicio, fin),
        "total_orders": totalpedidos,
        "num_countries": al.size(paises),
        "total_amount": totalmonto,
        "total_marketing": totalmercadeo,
        "top": top,
    }


# =============================================================================
# Requerimientos del equipo (pendientes por otros integrantes)
# =============================================================================

def req_3(catalog):
    """Requerimiento 3 (individual) - responsable: otro integrante del grupo."""
    # TODO: implementar por el integrante asignado
    pass


def req_4(catalog):
    """Requerimiento 4 (grupal) - pendiente."""
    # TODO: implementar (grupal)
    pass


# =============================================================================
# Funciones para medir tiempos de ejecucion
# =============================================================================

def get_time():
    """Devuelve el instante de tiempo de procesamiento en milisegundos."""
    return float(time.perf_counter() * 1000)


def delta_time(start, end):
    """Devuelve la diferencia entre dos instantes de tiempo (milisegundos)."""
    return float(end - start)
