"""
ARRAY LIST (lista basada en arreglo) - ISIS1225 Reto 2 (Grupo 06).

Implementacion de la lista basada en arreglo vista en el curso. Se maneja el
contrato de diccionario del curso: la estructura es un dict con las llaves
"elements" (el arreglo) y "size" (numero de elementos).

Todas las posiciones (pos) manejadas por get_element / change_info son
0-indexadas, consistente con el pseudocodigo de ordenamiento del curso
(rangos [lo, hi] con lo = 0 y hi = size - 1).
"""


def new_list():
    """Crea una lista basada en arreglo vacia."""
    return {"elements": [], "size": 0, "type": "ARRAY_LIST"}


def size(my_list):
    """Retorna el numero de elementos de la lista."""
    return my_list["size"]


def is_empty(my_list):
    """Retorna True si la lista esta vacia."""
    return my_list["size"] == 0


def add_last(my_list, element):
    """Agrega un elemento al final de la lista."""
    my_list["elements"].append(element)
    my_list["size"] += 1
    return my_list


def add_first(my_list, element):
    """Agrega un elemento al inicio de la lista."""
    my_list["elements"].insert(0, element)
    my_list["size"] += 1
    return my_list


def get_element(my_list, pos):
    """Retorna el elemento en la posicion pos (0-indexada)."""
    return my_list["elements"][pos]


def change_info(my_list, pos, new_info):
    """Cambia el elemento en la posicion pos (0-indexada)."""
    my_list["elements"][pos] = new_info
    return my_list


def first_element(my_list):
    """Retorna el primer elemento de la lista."""
    return my_list["elements"][0]


def last_element(my_list):
    """Retorna el ultimo elemento de la lista."""
    return my_list["elements"][my_list["size"] - 1]


def exchange(my_list, pos_i, pos_j):
    """Intercambia los elementos de las posiciones pos_i y pos_j."""
    tmp = my_list["elements"][pos_i]
    my_list["elements"][pos_i] = my_list["elements"][pos_j]
    my_list["elements"][pos_j] = tmp
    return my_list


def sub_list(my_list, start, num_elements):
    """
    Retorna una nueva array_list con num_elements copiados a partir de la
    posicion start (0-indexada). Se usa como lista auxiliar en merge sort.
    """
    sub = new_list()
    end = start + num_elements
    i = start
    while i < end:
        add_last(sub, my_list["elements"][i])
        i += 1
    return sub
