import sys
from tabulate import tabulate
import App.logic as logic
from DataStructures.List import array_list as lt

default_limit = 1000
sys.setrecursionlimit(default_limit*10)

archivos = ["chocolate_sale_100_elementos.csv", "chocolate_sale_20_ptc.csv", "chocolate_sale_40_ptc.csv", "chocolate_sale_60_ptc.csv", "chocolate_sale_80_ptc.csv", "chocolate_sale_100_ptc.csv"]


def new_logic():
    control = logic.new_logic()
    return control


def print_menu():
    print("Bienvenido")
    print("0- Cargar información")
    print("1- Ejecutar Requerimiento 1")
    print("2- Ejecutar Requerimiento 2")
    print("3- Ejecutar Requerimiento 3")
    print("4- Ejecutar Requerimiento 4")
    print("5- Ejecutar Requerimiento 5")
    print("6- Ejecutar Requerimiento 6")
    print("7- Salir")


def filas_muestra(lista, formato):
    filas = []
    total = lt.size(lista)
    if total > 20:
        for pos in range(10):
            filas.append(formato(lt.get_element(lista, pos)))
        for pos in range(total - 10, total):
            filas.append(formato(lt.get_element(lista, pos)))
    else:
        for pos in range(total):
            filas.append(formato(lt.get_element(lista, pos)))
    return filas


def filas_todas(lista, formato):
    filas = []
    for pos in range(lt.size(lista)):
        filas.append(formato(lt.get_element(lista, pos)))
    return filas


def no_cargado(control):
    if lt.size(control["orders"]) == 0:
        print("\nPrimero debe cargar la información (opción 0).")
        return True
    return False


carga_headers = ["Order_ID", "Product", "Country", "Channel", "Order_Date", "Boxes_Shipped", "Price_per_Box", "Amount"]


def format_carga(order):
    return [order["Order_ID"], order["Product"], order["Country"], order["Channel"], order["Order_Date"], order["Boxes_Shipped"], order["Price_per_Box"], order["Amount"]]


def format_canal(canal):
    return [canal["Channel"], canal["count"]]


def load_data(control):
    print("\nArchivos disponibles:")
    for pos in range(len(archivos)):
        print(f"{pos + 1}- {archivos[pos]}")
    opcion = int(input("Seleccione el archivo a cargar (1-6): \n"))
    if opcion < 1 or opcion > 6:
        opcion = 1
    archivo = archivos[opcion - 1]

    print(f"\nCargando {archivo} ...")
    tiempocarga = logic.load_data(control, archivo)
    reporte = logic.get_load_report(control)

    print(f"\nTiempo de carga: {tiempocarga:.3f} [ms]")
    print(f"Total de pedidos cargados: {reporte['total']}")

    print("\nTotal de pedidos por canal de venta:")
    print(tabulate(filas_todas(reporte["channels"], format_canal), headers=["Channel", "Pedidos"], tablefmt="grid"))

    print(f"\nFecha más antigua: {reporte['min_date']}")
    print(f"Fecha más reciente: {reporte['max_date']}")

    print("\nPedido de menor Amount:")
    print(tabulate([format_carga(reporte["min_amount_order"])], headers=carga_headers, tablefmt="grid"))

    print("\nPedido de mayor Amount:")
    print(tabulate([format_carga(reporte["max_amount_order"])], headers=carga_headers, tablefmt="grid"))

    print("\nPrimeros 5 pedidos (descendente por Amount):")
    print(tabulate(filas_todas(reporte["first_five"], format_carga), headers=carga_headers, tablefmt="grid"))

    print("\nÚltimos 5 pedidos (descendente por Amount):")
    print(tabulate(filas_todas(reporte["last_five"], format_carga), headers=carga_headers, tablefmt="grid"))


def format_req1(order):
    return [order["Order_ID"], order["Product"], order["Country"], order["Channel"], order["Order_Date"], order["Discount_Pct"], order["Price_per_Box"], order["Boxes_Shipped"], order["Amount"]]


def print_req_1(control):
    if no_cargado(control):
        return

    anio = int(input("Ingrese el año del pedido (YYYY): \n"))
    mes = int(input("Ingrese el mes del pedido (1-12): \n"))
    descmin = float(input("Ingrese el descuento mínimo (%): \n"))
    descmax = float(input("Ingrese el descuento máximo (%): \n"))

    resultado = logic.req_1(control, anio, mes, descmin, descmax)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos que cumplieron el filtro: {resultado['count']}")
    print(f"Monto total recaudado: {resultado['total_amount']:.2f}")
    print(f"Promedio Price_per_Box: {resultado['avg_price']:.2f}")
    print(f"Promedio Boxes_Shipped: {resultado['avg_boxes']:.2f}")

    if resultado["count"] == 0:
        print("\nNo se encontraron pedidos para ese mes y rango de descuento.")
        return

    encabezados = ["Order_ID", "Product", "Country", "Channel", "Order_Date", "Discount_Pct", "Price_per_Box", "Boxes_Shipped", "Amount"]
    print("\nPedidos (descendente por Discount_Pct):")
    print(tabulate(filas_muestra(resultado["orders"], format_req1), headers=encabezados, tablefmt="grid"))


def format_req2(order):
    return [order["Order_ID"], order["Product"], order["Channel"], order["Order_Date"], order["Boxes_Shipped"], order["Price_per_Box"], order["Marketing_Spend"], order["Amount"]]


def print_req_2(control):
    if no_cargado(control):
        return

    pais = input("Ingrese el país: \n")
    cajasmin = int(input("Ingrese el número mínimo de cajas enviadas: \n"))
    cajasmax = int(input("Ingrese el número máximo de cajas enviadas: \n"))

    resultado = logic.req_2(control, pais, cajasmin, cajasmax)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos que cumplieron el filtro: {resultado['count']}")
    print(f"Productos diferentes en el resultado: {resultado['num_products']}")
    print(f"Promedio Marketing_Spend: {resultado['avg_marketing']:.2f}")
    print(f"Promedio Amount: {resultado['avg_amount']:.2f}")

    if resultado["count"] == 0:
        print("\nNo se encontraron pedidos para ese país y rango de cajas.")
        return

    print(f"Producto más frecuente: {resultado['top_product']} ({resultado['top_product_count']} pedidos)")

    encabezados = ["Order_ID", "Product", "Channel", "Order_Date", "Boxes_Shipped", "Price_per_Box", "Marketing_Spend", "Amount"]
    print("\nPedidos (ascendente por Boxes_Shipped):")
    print(tabulate(filas_muestra(resultado["orders"], format_req2), headers=encabezados, tablefmt="grid"))


def format_req3(order):
    return [order["Order_ID"], order["Product"], order["Country"], order["Order_Date"], order["Marketing_Spend"], order["Boxes_Shipped"], order["Amount"], round(logic.aporte(order), 2)]


def print_req_3(control):
    if no_cargado(control):
        return

    fecha = input("Ingrese la fecha del pedido (YYYY-MM-DD): \n")
    montomin = float(input("Ingrese el valor mínimo de costo total: \n"))
    montomax = float(input("Ingrese el valor máximo de costo total: \n"))

    resultado = logic.req_3(control, fecha, montomin, montomax)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos que cumplieron el filtro: {resultado['count']}")
    print(f"Monto total recaudado: {resultado['total_amount']:.2f}")
    print(f"Inversión total en mercadeo: {resultado['total_marketing']:.2f}")
    print(f"Aporte comercial total: {resultado['total_aporte']:.2f}")

    if resultado["count"] == 0:
        print("\nNo se encontraron pedidos para esa fecha y rango de costo total.")
        return

    encabezados = ["Order_ID", "Product", "Country", "Order_Date", "Marketing_Spend", "Boxes_Shipped", "Amount", "Aporte comercial"]
    print("\nPedidos (descendente por Amount):")
    print(tabulate(filas_muestra(resultado["orders"], format_req3), headers=encabezados, tablefmt="grid"))


def format_req4(order):
    return [order["Order_ID"], order["Channel"], order["Order_Date"], order["Boxes_Shipped"], order["Amount"]]


def print_req_4(control):
    if no_cargado(control):
        return

    producto = input("Ingrese el nombre del producto: \n")
    pais = input("Ingrese el país: \n")

    resultado = logic.req_4(control, producto, pais)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos de '{producto}' en '{pais}': {resultado['count']}")

    if resultado["count"] == 0:
        print(f"\nNo se encontraron pedidos para '{producto}' en '{pais}'.")
        return

    tablaprom = [["Price_per_Box", f"{resultado['avg_price']:.2f}"], ["Discount_Pct", f"{resultado['avg_discount']:.2f}"], ["Marketing_Spend", f"{resultado['avg_marketing']:.2f}"], ["Boxes_Shipped", f"{resultado['avg_boxes']:.2f}"]]
    print("\nPromedios de los pedidos:")
    print(tabulate(tablaprom, headers=["Característica", "Promedio"], tablefmt="grid"))

    print("\nLos 2 pedidos de mayor Amount:")
    print(tabulate(filas_todas(resultado["top_orders"], format_req4), headers=["Order_ID", "Channel", "Order_Date", "Boxes_Shipped", "Amount"], tablefmt="grid"))


def format_req5(prod):
    return [prod["product"], prod["count"], prod["boxes_total"], round(prod["amount_total"], 2), round(prod["avg_price"], 2), round(prod["avg_discount"], 2), round(prod["marketing_total"], 2)]


def print_req_5(control):
    if no_cargado(control):
        return

    n = int(input("Ingrese el número N de productos: \n"))
    pais = input("Ingrese el país: \n")
    fechaini = input("Ingrese la fecha inicial (YYYY-MM-DD): \n")
    fechafin = input("Ingrese la fecha final (YYYY-MM-DD): \n")

    resultado = logic.req_5(control, n, pais, fechaini, fechafin)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos que cumplieron el filtro: {resultado['total_orders']}")
    print(f"Productos diferentes encontrados: {resultado['num_products']}")
    print(f"Recaudo total: {resultado['total_amount']:.2f}")

    if resultado["num_products"] == 0:
        print("\nNo se encontraron pedidos para ese país y rango de fechas.")
        return

    encabezados = ["Product", "Pedidos", "Boxes_Total", "Recaudo", "Precio_Prom", "Desc_Prom", "Marketing_Total"]
    print(f"\nTop {n} productos por recaudo:")
    print(tabulate(filas_todas(resultado["top"], format_req5), headers=encabezados, tablefmt="grid"))


def format_req6(pais):
    return [pais["country"], pais["count"], round(pais["amount_total"], 2), round(pais["marketing_total"], 2), pais["boxes_total"], round(pais["avg_price"], 2), round(pais["efficiency"], 4)]


def print_req_6(control):
    if no_cargado(control):
        return

    n = int(input("Ingrese el número N de países: \n"))
    producto = input("Ingrese el producto: \n")
    fechaini = input("Ingrese la fecha inicial (YYYY-MM-DD): \n")
    fechafin = input("Ingrese la fecha final (YYYY-MM-DD): \n")

    resultado = logic.req_6(control, n, producto, fechaini, fechafin)

    print(f"\nTiempo de ejecución: {resultado['time_ms']:.3f} [ms]")
    print(f"Pedidos que cumplieron el filtro: {resultado['total_orders']}")
    print(f"Países diferentes encontrados: {resultado['num_countries']}")
    print(f"Amount total: {resultado['total_amount']:.2f}")
    print(f"Marketing_Spend total: {resultado['total_marketing']:.2f}")

    if resultado["total_orders"] == 0:
        print("\nNo se encontraron pedidos para ese producto y rango de fechas.")
        return

    encabezados = ["Country", "Pedidos", "Amount_Total", "Marketing_Total", "Boxes_Total", "Precio_Prom", "Eficiencia"]
    print(f"\nTop {n} países por eficiencia de mercadeo:")
    print(tabulate(filas_todas(resultado["top"], format_req6), headers=encabezados, tablefmt="grid"))


control = new_logic()


def main():
    working = True
    while working:
        print_menu()
        inputs = input("Seleccione una opción para continuar\n")
        if int(inputs) == 0:
            print("Cargando información de los archivos ....\n")
            load_data(control)
        elif int(inputs) == 1:
            print_req_1(control)
        elif int(inputs) == 2:
            print_req_2(control)
        elif int(inputs) == 3:
            print_req_3(control)
        elif int(inputs) == 4:
            print_req_4(control)
        elif int(inputs) == 5:
            print_req_5(control)
        elif int(inputs) == 6:
            print_req_6(control)
        elif int(inputs) == 7:
            working = False
            print("\nGracias por utilizar el programa")
        else:
            print("Opción errónea, vuelva a elegir.\n")
    sys.exit(0)
