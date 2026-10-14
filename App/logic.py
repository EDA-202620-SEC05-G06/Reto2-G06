import csv
import os
import time
from DataStructures.List import array_list as lt
from DataStructures.List import single_linked_list as sll
from DataStructures.Map import map_separate_chaining as mp
from DataStructures.Map import map_linear_probing as lp
from DataStructures.Sort import sorting as sort

csv.field_size_limit(2147483647)

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data")


def new_logic():
    catalog = {"orders": lt.new_list(), "por_mes": mp.new_map(24, 4.0), "por_pais": mp.new_map(5, 4.0), "channel_count": lp.new_map(3, 0.5), "min_amount_order": None, "max_amount_order": None, "min_date": None, "max_date": None}
    return catalog


def load_data(catalog, filename):
    inicio = get_time()
    ruta = os.path.join(data_dir, filename)
    input_file = csv.DictReader(open(ruta, encoding="utf-8-sig"))
    for row in input_file:
        order = new_order(row)
        lt.add_last(catalog["orders"], order)
        add_por_mes(catalog, order)
        add_por_pais(catalog, order)
        contar_canal(catalog, order)
        revisar_resumen(catalog, order)
    fin = get_time()
    return delta_time(inicio, fin)


def new_order(row):
    order_id = row["Order_ID"]
    if not order_id:
        order_id = "Unknown"

    product = row["Product"]
    if not product:
        product = "Unknown"

    country = row["Country"]
    if not country:
        country = "Unknown"

    channel = row["Channel"]
    if not channel:
        channel = "Unknown"

    order_date = row["Order_Date"]
    if not order_date:
        order_date = "Unknown"

    order = {"Order_ID": order_id, "Product": product, "Country": country, "Channel": channel, "Order_Date": order_date, "Discount_Pct": float(row["Discount_Pct"]), "Price_per_Box": float(row["Price_per_Box"]), "Marketing_Spend": float(row["Marketing_Spend"]), "Boxes_Shipped": int(row["Boxes_Shipped"]), "Amount": float(row["Amount"])}
    return order


def add_por_mes(catalog, order):
    llavemes = order["Order_Date"][:7]
    mapadias = mp.get(catalog["por_mes"], llavemes)
    if mapadias is None:
        mapadias = lp.new_map(31, 0.5)
        mp.put(catalog["por_mes"], llavemes, mapadias)
    llavedia = order["Order_Date"]
    peddia = lp.get(mapadias, llavedia)
    if peddia is None:
        peddia = sll.new_list()
        lp.put(mapadias, llavedia, peddia)
    sll.add_last(peddia, order)


def add_por_pais(catalog, order):
    llavepais = order["Country"]
    mapaprods = mp.get(catalog["por_pais"], llavepais)
    if mapaprods is None:
        mapaprods = lp.new_map(12, 0.5)
        mp.put(catalog["por_pais"], llavepais, mapaprods)
    llaveprod = order["Product"]
    pedprod = lp.get(mapaprods, llaveprod)
    if pedprod is None:
        pedprod = sll.new_list()
        lp.put(mapaprods, llaveprod, pedprod)
    sll.add_last(pedprod, order)


def contar_canal(catalog, order):
    llave = order["Channel"]
    cuenta = lp.get(catalog["channel_count"], llave)
    if cuenta is None:
        cuenta = 0
    lp.put(catalog["channel_count"], llave, cuenta + 1)


def revisar_resumen(catalog, order):
    menor = catalog["min_amount_order"]
    if menor is None:
        catalog["min_amount_order"] = order
    elif order["Amount"] < menor["Amount"]:
        catalog["min_amount_order"] = order
    elif order["Amount"] == menor["Amount"] and order["Price_per_Box"] < menor["Price_per_Box"]:
        catalog["min_amount_order"] = order
    elif order["Amount"] == menor["Amount"] and order["Price_per_Box"] == menor["Price_per_Box"] and order["Order_ID"] < menor["Order_ID"]:
        catalog["min_amount_order"] = order

    mayor = catalog["max_amount_order"]
    if mayor is None:
        catalog["max_amount_order"] = order
    elif order["Amount"] > mayor["Amount"]:
        catalog["max_amount_order"] = order
    elif order["Amount"] == mayor["Amount"] and order["Price_per_Box"] < mayor["Price_per_Box"]:
        catalog["max_amount_order"] = order
    elif order["Amount"] == mayor["Amount"] and order["Price_per_Box"] == mayor["Price_per_Box"] and order["Order_ID"] < mayor["Order_ID"]:
        catalog["max_amount_order"] = order

    fecha = order["Order_Date"]
    if catalog["min_date"] is None or fecha < catalog["min_date"]:
        catalog["min_date"] = fecha
    if catalog["max_date"] is None or fecha > catalog["max_date"]:
        catalog["max_date"] = fecha


def get_load_report(catalog):
    orders = catalog["orders"]
    total = lt.size(orders)

    ordenados = lt.sub_list(orders, 0, total)
    sort.merge_sort(ordenados, cmp_amount_desc)

    cant = 5
    if total < 5:
        cant = total

    primeros = lt.new_list()
    for pos in range(cant):
        lt.add_last(primeros, lt.get_element(ordenados, pos))

    ultimos = lt.new_list()
    for pos in range(total - cant, total):
        lt.add_last(ultimos, lt.get_element(ordenados, pos))

    canales = lt.new_list()
    llaves = lp.key_set(catalog["channel_count"])
    for pos in range(lt.size(llaves)):
        canal = lt.get_element(llaves, pos)
        lt.add_last(canales, {"Channel": canal, "count": lp.get(catalog["channel_count"], canal)})
    sort.merge_sort(canales, cmp_canal)

    return {"total": total, "channels": canales, "min_date": catalog["min_date"], "max_date": catalog["max_date"], "min_amount_order": catalog["min_amount_order"], "max_amount_order": catalog["max_amount_order"], "first_five": primeros, "last_five": ultimos}


def cmp_canal(a, b):
    return a["Channel"] < b["Channel"]


def cmp_amount_desc(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req1(a, b):
    if a["Discount_Pct"] != b["Discount_Pct"]:
        return a["Discount_Pct"] > b["Discount_Pct"]
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req2(a, b):
    if a["Boxes_Shipped"] != b["Boxes_Shipped"]:
        return a["Boxes_Shipped"] < b["Boxes_Shipped"]
    if a["Order_Date"] != b["Order_Date"]:
        return a["Order_Date"] > b["Order_Date"]
    return a["Order_ID"] < b["Order_ID"]


def aporte(order):
    return order["Amount"] - order["Marketing_Spend"]


def cmp_req3(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    if aporte(a) != aporte(b):
        return aporte(a) > aporte(b)
    return a["Order_ID"] < b["Order_ID"]


def gana_req4(a, b):
    if a["Amount"] != b["Amount"]:
        return a["Amount"] > b["Amount"]
    if a["Marketing_Spend"] != b["Marketing_Spend"]:
        return a["Marketing_Spend"] < b["Marketing_Spend"]
    return a["Order_ID"] < b["Order_ID"]


def cmp_req5(a, b):
    if a["amount_total"] != b["amount_total"]:
        return a["amount_total"] > b["amount_total"]
    if a["boxes_total"] != b["boxes_total"]:
        return a["boxes_total"] > b["boxes_total"]
    return a["product"] < b["product"]


def cmp_req6(a, b):
    if a["efficiency"] != b["efficiency"]:
        return a["efficiency"] > b["efficiency"]
    if a["amount_total"] != b["amount_total"]:
        return a["amount_total"] > b["amount_total"]
    return a["country"] < b["country"]


def top_n(lista, n):
    cant = n
    if lt.size(lista) < n:
        cant = lt.size(lista)
    top = lt.new_list()
    for pos in range(cant):
        lt.add_last(top, lt.get_element(lista, pos))
    return top


def req_1(catalog, anio, mes, descmin, descmax):
    inicio = get_time()

    llave = str(anio) + "-"
    if mes < 10:
        llave = llave + "0"
    llave = llave + str(mes)

    mapadias = mp.get(catalog["por_mes"], llave)

    resultado = lt.new_list()
    sumamonto = 0
    sumap = 0
    sumab = 0

    if mapadias is not None:
        dias = lp.value_set(mapadias)
        for pos in range(lt.size(dias)):
            node = lt.get_element(dias, pos)["first"]
            while node is not None:
                order = node["info"]
                if descmin <= order["Discount_Pct"] <= descmax:
                    lt.add_last(resultado, order)
                    sumamonto += order["Amount"]
                    sumap += order["Price_per_Box"]
                    sumab += order["Boxes_Shipped"]
                node = node["next"]

    sort.merge_sort(resultado, cmp_req1)

    total = lt.size(resultado)
    promp = 0
    promb = 0
    if total > 0:
        promp = sumap / total
        promb = sumab / total

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "count": total, "total_amount": sumamonto, "avg_price": promp, "avg_boxes": promb, "orders": resultado}


def req_2(catalog, pais, cajasmin, cajasmax):
    inicio = get_time()

    mapaprods = mp.get(catalog["por_pais"], pais)

    resultado = lt.new_list()
    sumamerc = 0
    sumamonto = 0
    numprods = 0
    prodtop = None
    cuentatop = 0

    if mapaprods is not None:
        prods = lp.key_set(mapaprods)
        for pos in range(lt.size(prods)):
            prod = lt.get_element(prods, pos)
            cuenta = 0
            node = lp.get(mapaprods, prod)["first"]
            while node is not None:
                order = node["info"]
                if cajasmin <= order["Boxes_Shipped"] <= cajasmax:
                    lt.add_last(resultado, order)
                    sumamerc += order["Marketing_Spend"]
                    sumamonto += order["Amount"]
                    cuenta += 1
                node = node["next"]
            if cuenta > 0:
                numprods += 1
                if cuenta > cuentatop or (cuenta == cuentatop and prod < prodtop):
                    prodtop = prod
                    cuentatop = cuenta

    sort.merge_sort(resultado, cmp_req2)

    total = lt.size(resultado)
    prommerc = 0
    prommonto = 0
    if total > 0:
        prommerc = sumamerc / total
        prommonto = sumamonto / total

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "count": total, "num_products": numprods, "avg_marketing": prommerc, "avg_amount": prommonto, "top_product": prodtop, "top_product_count": cuentatop, "orders": resultado}


def req_3(catalog, fecha, montomin, montomax):
    inicio = get_time()

    peddia = None
    mapadias = mp.get(catalog["por_mes"], fecha[:7])
    if mapadias is not None:
        peddia = lp.get(mapadias, fecha)

    resultado = lt.new_list()
    sumamonto = 0
    sumamerc = 0
    sumaaporte = 0

    if peddia is not None:
        node = peddia["first"]
        while node is not None:
            order = node["info"]
            if montomin <= order["Amount"] <= montomax:
                lt.add_last(resultado, order)
                sumamonto += order["Amount"]
                sumamerc += order["Marketing_Spend"]
                sumaaporte += aporte(order)
            node = node["next"]

    sort.merge_sort(resultado, cmp_req3)

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "count": lt.size(resultado), "total_amount": sumamonto, "total_marketing": sumamerc, "total_aporte": sumaaporte, "orders": resultado}


def req_4(catalog, producto, pais):
    inicio = get_time()

    pedprod = None
    mapaprods = mp.get(catalog["por_pais"], pais)
    if mapaprods is not None:
        pedprod = lp.get(mapaprods, producto)

    total = 0
    sump = 0
    sumd = 0
    sum_m = 0
    sumb = 0
    top_1 = None
    top_2 = None

    if pedprod is not None:
        node = pedprod["first"]
        while node is not None:
            order = node["info"]
            total += 1
            sump += order["Price_per_Box"]
            sumd += order["Discount_Pct"]
            sum_m += order["Marketing_Spend"]
            sumb += order["Boxes_Shipped"]

            if top_1 is None or gana_req4(order, top_1):
                top_2 = top_1
                top_1 = order
            elif top_2 is None or gana_req4(order, top_2):
                top_2 = order

            node = node["next"]

    toppedidos = lt.new_list()
    if top_1 is not None:
        lt.add_last(toppedidos, top_1)
    if top_2 is not None:
        lt.add_last(toppedidos, top_2)

    promp = 0
    promd = 0
    promm = 0
    promb = 0
    if total > 0:
        promp = sump / total
        promd = sumd / total
        promm = sum_m / total
        promb = sumb / total

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "count": total, "avg_price": promp, "avg_discount": promd, "avg_marketing": promm, "avg_boxes": promb, "top_orders": toppedidos}


def req_5(catalog, n, pais, fechaini, fechafin):
    inicio = get_time()

    mapaprods = mp.get(catalog["por_pais"], pais)

    prods = lt.new_list()
    totalped = 0
    totalmonto = 0

    if mapaprods is not None:
        llaves = lp.key_set(mapaprods)
        for pos in range(lt.size(llaves)):
            prod = lt.get_element(llaves, pos)
            acum = {"product": prod, "count": 0, "boxes_total": 0, "amount_total": 0.0, "price_sum": 0.0, "disc_sum": 0.0, "marketing_total": 0.0}
            node = lp.get(mapaprods, prod)["first"]
            while node is not None:
                order = node["info"]
                if fechaini <= order["Order_Date"] <= fechafin:
                    acum["count"] += 1
                    acum["boxes_total"] += order["Boxes_Shipped"]
                    acum["amount_total"] += order["Amount"]
                    acum["price_sum"] += order["Price_per_Box"]
                    acum["disc_sum"] += order["Discount_Pct"]
                    acum["marketing_total"] += order["Marketing_Spend"]
                node = node["next"]
            if acum["count"] > 0:
                acum["avg_price"] = acum["price_sum"] / acum["count"]
                acum["avg_discount"] = acum["disc_sum"] / acum["count"]
                totalped += acum["count"]
                totalmonto += acum["amount_total"]
                lt.add_last(prods, acum)

    sort.merge_sort(prods, cmp_req5)

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "total_orders": totalped, "num_products": lt.size(prods), "total_amount": totalmonto, "top": top_n(prods, n)}


def req_6(catalog, n, producto, fechaini, fechafin):
    inicio = get_time()

    ranking = lt.new_list()
    totalped = 0
    totalmonto = 0
    totalmerc = 0
    numpaises = 0

    paises = mp.key_set(catalog["por_pais"])
    for pos in range(lt.size(paises)):
        pais = lt.get_element(paises, pos)
        pedprod = lp.get(mp.get(catalog["por_pais"], pais), producto)
        if pedprod is not None:
            acum = {"country": pais, "count": 0, "amount_total": 0.0, "marketing_total": 0.0, "boxes_total": 0, "price_sum": 0.0}
            node = pedprod["first"]
            while node is not None:
                order = node["info"]
                if fechaini <= order["Order_Date"] <= fechafin:
                    acum["count"] += 1
                    acum["amount_total"] += order["Amount"]
                    acum["marketing_total"] += order["Marketing_Spend"]
                    acum["boxes_total"] += order["Boxes_Shipped"]
                    acum["price_sum"] += order["Price_per_Box"]
                node = node["next"]
            if acum["count"] > 0:
                numpaises += 1
                totalped += acum["count"]
                totalmonto += acum["amount_total"]
                totalmerc += acum["marketing_total"]
                if acum["marketing_total"] > 0:
                    acum["avg_price"] = acum["price_sum"] / acum["count"]
                    acum["efficiency"] = acum["amount_total"] / acum["marketing_total"]
                    lt.add_last(ranking, acum)

    sort.merge_sort(ranking, cmp_req6)

    fin = get_time()
    return {"time_ms": delta_time(inicio, fin), "total_orders": totalped, "num_countries": numpaises, "total_amount": totalmonto, "total_marketing": totalmerc, "top": top_n(ranking, n)}


def get_time():
    return float(time.perf_counter()*1000)


def delta_time(start, end):
    elapsed = float(end - start)
    return elapsed
