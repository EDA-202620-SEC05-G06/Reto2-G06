"""
SINGLE LINKED LIST (lista sencillamente encadenada) - ISIS1225 Reto 2 (G06).

Lista encadenada vista en el curso. Cada nodo es un dict con las llaves
"info" (el elemento) y "next" (referencia al siguiente nodo). La lista es un
dict con "first", "last" y "size".

Se usa como estructura de cada bucket en el mapa por Separate Chaining.
"""


def new_list():
    """Crea una lista encadenada vacia."""
    return {"first": None, "last": None, "size": 0, "type": "SINGLE_LINKED"}


def size(my_list):
    """Retorna el numero de elementos de la lista."""
    return my_list["size"]


def is_empty(my_list):
    """Retorna True si la lista esta vacia."""
    return my_list["size"] == 0


def _new_node(element):
    """Crea un nodo con la informacion dada."""
    return {"info": element, "next": None}


def add_first(my_list, element):
    """Agrega un elemento al inicio de la lista (O(1))."""
    node = _new_node(element)
    node["next"] = my_list["first"]
    my_list["first"] = node
    if my_list["size"] == 0:
        my_list["last"] = node
    my_list["size"] += 1
    return my_list


def add_last(my_list, element):
    """Agrega un elemento al final de la lista (O(1))."""
    node = _new_node(element)
    if my_list["size"] == 0:
        my_list["first"] = node
    else:
        my_list["last"]["next"] = node
    my_list["last"] = node
    my_list["size"] += 1
    return my_list


def first_element(my_list):
    """Retorna el primer elemento (info del primer nodo)."""
    if my_list["first"] is None:
        return None
    return my_list["first"]["info"]


def iterator(my_list):
    """
    Generador que recorre los elementos (info) de la lista.
    Permite recorrer un bucket sin exponer los nodos.
    """
    node = my_list["first"]
    while node is not None:
        yield node["info"]
        node = node["next"]
