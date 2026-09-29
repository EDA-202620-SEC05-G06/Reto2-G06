"""
VISTA (interfaz de consola) - ISIS1225 Reto 2 (Grupo 06).

Menu principal y presentacion de resultados de la carga, el Requerimiento 1 y el
Requerimiento 5. Los demas requerimientos quedan a cargo de otros integrantes.
"""

import sys
import os

import App.logic as logic

# Se aumenta el limite de recursion segun la nota del reto (merge/quick sort).
default_limit = 1000
sys.setrecursionlimit(default_limit * 10)

# Impresion de tablas: se usa tabulate si esta disponible; si no, formato plano.
try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False

# Archivos de datos disponibles en la carpeta Data.
DATA_FILES = {
    "1": "chocolate_sale_100_elementos.csv",
    "2": "chocolate_sale_20_ptc.csv",
    "3": "chocolate_sale_40_ptc.csv",
    "4": "chocolate_sale_60_ptc.csv",
    "5": "chocolate_sale_80_ptc.csv",
    "6": "chocolate_sale_100_ptc.csv",
}


def new_logic():
    """Crea la instancia del controlador (catalogo)."""
    return logic.new_logic()


def print_menu():
    print("\n===================================================")
    print("           Reto 2 - Ventas de Chocolate (G06)")
    print("===================================================")
    print("0- Cargar informacion")
    print("1- Ejecutar Requerimiento 1 (mes + rango de descuento)")
    print("2- Ejecutar Requerimiento 2")
    print("3- Ejecutar Requerimiento 3")
    print("4- Ejecutar Requerimiento 4")
    print("5- Ejecutar Requerimiento 5 (top N productos por recaudo)")
    print("6- Ejecutar Requerimiento 6")
    print("7- Salir")


# =============================================================================
# Utilidades de impresion
# =============================================================================

def _print_table(headers, rows):
    """Imprime una tabla con tabulate si esta disponible, o en formato plano."""
    if len(rows) == 0:
        print("(sin registros)")
        return
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".2f"))
    else:
        print(" | ".join(str(h) for h in headers))
        print("-" * 80)
        for row in rows:
            print(" | ".join(str(c) for c in row))


def _order_row(order):
    """Fila para un pedido en el Requerimiento 1."""
    return [
        order["Order_ID"], order["Product"], order["Country"], order["Channel"],
        order["Order_Date"], round(order["Discount_Pct"], 2),
        round(order["Price_per_Box"], 2), order["Boxes_Shipped"],
        round(order["Amount"], 2),
    ]


def _sample_rows(a_list, row_fn):
    """
    Aplica la regla de presentacion: si hay mas de 20 registros muestra los
    primeros 10 y los ultimos 10; de lo contrario los muestra todos.
    Retorna la lista de filas ya formateadas.
    """
    n = a_list["size"]
    rows = []
    if n > 20:
        i = 0
        while i < 10:
            rows.append(row_fn(a_list["elements"][i]))
            i += 1
        rows.append(["...", "...", "...", "...", "...", "...", "...", "...", "..."])
        i = n - 10
        while i < n:
            rows.append(row_fn(a_list["elements"][i]))
            i += 1
    else:
        for elem in a_list["elements"]:
            rows.append(row_fn(elem))
    return rows


# =============================================================================
# Carga de datos
# =============================================================================

def load_data(control):
    """Solicita el archivo a cargar, ejecuta la carga y presenta el reporte."""
    print("\nArchivos disponibles:")
    for key in sorted(DATA_FILES):
        print("  %s- %s" % (key, DATA_FILES[key]))
    choice = input("Seleccione el archivo a cargar (1-6): ").strip()
    filename = DATA_FILES.get(choice, DATA_FILES["1"])

    data_dir = os.path.join(os.path.dirname(__file__), "..", "Data")
    filepath = os.path.join(data_dir, filename)

    print("\nCargando %s ...\n" % filename)
    load_time = logic.load_data(control, filepath)
    report = logic.get_load_report(control)

    print("Tiempo de carga: %.2f ms" % load_time)
    print("Total de pedidos cargados: %d" % report["total"])

    print("\nTotal de pedidos por canal de venta:")
    ch_rows = [[c["Channel"], c["count"]] for c in report["channels"]["elements"]]
    _print_table(["Channel", "Pedidos"], ch_rows)

    print("\nRango de fechas de los pedidos:")
    print("  Fecha mas antigua: %s" % report["min_date"])
    print("  Fecha mas reciente: %s" % report["max_date"])

    print("\nPedido con MENOR Amount:")
    _print_table(_carga_headers(), [_carga_row(report["min_amount_order"])])
    print("\nPedido con MAYOR Amount:")
    _print_table(_carga_headers(), [_carga_row(report["max_amount_order"])])

    print("\nPrimeros 5 pedidos (ordenados descendente por Amount):")
    _print_table(_carga_headers(),
                 [_carga_row(o) for o in report["first_five"]["elements"]])
    print("\nUltimos 5 pedidos (ordenados descendente por Amount):")
    _print_table(_carga_headers(),
                 [_carga_row(o) for o in report["last_five"]["elements"]])


def _carga_headers():
    return ["Order_ID", "Product", "Country", "Channel", "Order_Date",
            "Boxes_Shipped", "Price_per_Box", "Amount"]


def _carga_row(order):
    if order is None:
        return ["-"] * 8
    return [
        order["Order_ID"], order["Product"], order["Country"], order["Channel"],
        order["Order_Date"], order["Boxes_Shipped"],
        round(order["Price_per_Box"], 2), round(order["Amount"], 2),
    ]


# =============================================================================
# Requerimiento 1
# =============================================================================

def print_req_1(control):
    """Solicita parametros, ejecuta el Requerimiento 1 y presenta el resultado."""
    try:
        year = int(input("Año del pedido (YYYY): ").strip())
        month = int(input("Mes del pedido (1-12): ").strip())
        disc_min = float(input("Descuento minimo (%): ").strip())
        disc_max = float(input("Descuento maximo (%): ").strip())
    except ValueError:
        print("Entrada invalida. Intente de nuevo.")
        return

    result = logic.req_1(control, year, month, disc_min, disc_max)

    print("\n--- Requerimiento 1 ---")
    print("Tiempo de ejecucion: %.2f ms" % result["time_ms"])
    print("Pedidos que cumplieron el filtro: %d" % result["count"])
    print("Monto total recaudado (suma Amount): %.2f" % result["total_amount"])
    print("Promedio Price_per_Box: %.2f" % result["avg_price"])
    print("Promedio Boxes_Shipped: %.2f" % result["avg_boxes"])

    if result["count"] == 0:
        print("\nNo se encontraron pedidos para el mes y rango indicados.")
        return

    print("\nPedidos (descendente por Discount_Pct):")
    headers = ["Order_ID", "Product", "Country", "Channel", "Order_Date",
               "Discount_Pct", "Price_per_Box", "Boxes_Shipped", "Amount"]
    _print_table(headers, _sample_rows(result["orders"], _order_row))


# =============================================================================
# Requerimiento 5
# =============================================================================
# Requerimiento 5
# =============================================================================

def print_req_5(control):
    """Se implementa en el siguiente commit."""
    print("Requerimiento 5 pendiente (se agrega en el siguiente commit).")


# =============================================================================
# Requerimientos a cargo de otros integrantes
# =============================================================================

def print_req_2(control):
    print("Requerimiento 2 pendiente (a cargo de otro integrante).")


def print_req_3(control):
    print("Requerimiento 3 pendiente (a cargo de otro integrante).")


def print_req_4(control):
    print("Requerimiento 4 pendiente (grupal).")


def print_req_6(control):
    print("Requerimiento 6 pendiente (grupal).")


# =============================================================================
# Menu principal
# =============================================================================

control = new_logic()


def main():
    """Menu principal."""
    working = True
    while working:
        print_menu()
        inputs = input("Seleccione una opcion para continuar\n").strip()
        if inputs == "0":
            load_data(control)
        elif inputs == "1":
            print_req_1(control)
        elif inputs == "2":
            print_req_2(control)
        elif inputs == "3":
            print_req_3(control)
        elif inputs == "4":
            print_req_4(control)
        elif inputs == "5":
            print_req_5(control)
        elif inputs == "6":
            print_req_6(control)
        elif inputs == "7":
            working = False
            print("\nGracias por utilizar el programa")
        else:
            print("Opcion erronea, vuelva a elegir.\n")
    sys.exit(0)
