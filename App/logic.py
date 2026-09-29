"""
LOGICA (controlador) - ISIS1225 Reto 2 (Grupo 06).

Carga de datos y requerimientos.

Responsable de este archivo (parcial): Requerimiento 1 y Requerimiento 5.
La carga de datos (load_data) es infraestructura compartida del grupo: se deja
implementada aqui porque construye las tablas de hash que consultan TODOS los
requerimientos. El equipo debe conciliar esta seccion con el resto del reto.

Estructuras del curso usadas (carpeta DataStructures):
  - array_list             -> listas basadas en arreglo
  - single_linked_list     -> buckets del mapa por Separate Chaining
  - map_separate_chaining  -> tablas de hash por encadenamiento separado
  - map_linear_probing     -> tablas de hash por sondeo lineal (disponible)
  - sorting.merge_sort     -> ordenamiento generico O(n log n) y estable
"""

import time
import csv

import DataStructures.List.array_list as al
import DataStructures.Map.map_separate_chaining as mp
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
                           pedidos de ese pais. Soporta el Requerimiento 5.
      - channel_count:     Separate Chaining. Llave Channel -> numero de pedidos
                           del canal. Soporta el reporte de la carga.
    """
    catalog = {
        "orders": al.new_list(),
        "orders_by_month": mp.new_map(31, 4.0),
        "orders_by_country": mp.new_map(31, 4.0),
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
# Requerimiento 5 (Grupal): pendiente (se implementa en el siguiente commit)
# =============================================================================

def req_5(catalog, n, country, date_ini, date_fin):
    """Requerimiento 5 (grupal) - se implementa en el siguiente commit."""
    # TODO: implementar Requerimiento 5
    pass


# =============================================================================
# Requerimientos del equipo (pendientes por otros integrantes)
# =============================================================================

def req_2(catalog):
    """Requerimiento 2 (individual) - responsable: otro integrante del grupo."""
    # TODO: implementar por el integrante asignado
    pass


def req_3(catalog):
    """Requerimiento 3 (individual) - responsable: otro integrante del grupo."""
    # TODO: implementar por el integrante asignado
    pass


def req_4(catalog):
    """Requerimiento 4 (grupal) - pendiente."""
    # TODO: implementar (grupal)
    pass


def req_6(catalog):
    """Requerimiento 6 (grupal) - pendiente."""
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
