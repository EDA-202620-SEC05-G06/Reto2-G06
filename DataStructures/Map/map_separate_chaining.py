"""
MAPA POR SEPARATE CHAINING (encadenamiento separado) - ISIS1225 Reto 2 (G06).

Tabla de hash con manejo de colisiones por encadenamiento separado, vista en el
curso. La tabla es un arreglo (array_list) de buckets; cada bucket es una lista
sencillamente encadenada de parejas {"key", "value"}.

API del TAD Mapa del curso:
    new_map, put, get, contains, remove, size, is_empty, key_set, value_set.

Factor de carga: alpha = n / N. Para Separate Chaining se sugiere alpha ~ 5;
la tabla duplica su capacidad cuando n / N supera max_load_factor.
"""

import DataStructures.List.array_list as al
import DataStructures.List.single_linked_list as sll


def _next_prime(n):
    """Retorna el menor numero primo >= n (para tamanos de tabla)."""
    def is_prime(x):
        if x < 2:
            return False
        if x % 2 == 0:
            return x == 2
        d = 3
        while d * d <= x:
            if x % d == 0:
                return False
            d += 2
        return True
    candidate = n if n % 2 == 1 else n + 1
    while not is_prime(candidate):
        candidate += 2
    return candidate


def new_map(num_elements=17, max_load_factor=5.0):
    """
    Crea un mapa vacio por Separate Chaining con capacidad para almacenar
    aproximadamente num_elements manteniendo el factor de carga objetivo.
    """
    capacity = _next_prime(int(num_elements / max_load_factor) + 1)
    buckets = al.new_list()
    i = 0
    while i < capacity:
        al.add_last(buckets, sll.new_list())
        i += 1
    return {
        "buckets": buckets,
        "capacity": capacity,
        "size": 0,
        "max_load_factor": max_load_factor,
        "type": "SEPARATE_CHAINING",
    }


def _hash(my_map, key):
    """Funcion de hash: lleva la llave al rango [0, capacity - 1] (metodo division)."""
    return abs(hash(key)) % my_map["capacity"]


def _find_node(bucket, key):
    """Busca en un bucket el nodo cuya pareja tiene la llave dada. None si no existe."""
    node = bucket["first"]
    while node is not None:
        if node["info"]["key"] == key:
            return node
        node = node["next"]
    return None


def size(my_map):
    """Retorna el numero de parejas almacenadas."""
    return my_map["size"]


def is_empty(my_map):
    """Retorna True si el mapa esta vacio."""
    return my_map["size"] == 0


def contains(my_map, key):
    """Retorna True si la llave se encuentra en el mapa."""
    idx = _hash(my_map, key)
    bucket = al.get_element(my_map["buckets"], idx)
    return _find_node(bucket, key) is not None


def put(my_map, key, value):
    """
    Agrega la pareja <key, value>. Si la llave ya existe, reemplaza el valor.
    Duplica la capacidad si se supera el factor de carga.
    """
    idx = _hash(my_map, key)
    bucket = al.get_element(my_map["buckets"], idx)
    node = _find_node(bucket, key)
    if node is not None:
        node["info"]["value"] = value
        return my_map
    sll.add_first(bucket, {"key": key, "value": value})
    my_map["size"] += 1
    if my_map["size"] / my_map["capacity"] > my_map["max_load_factor"]:
        _rehash(my_map)
    return my_map


def get(my_map, key):
    """Retorna el valor asociado a la llave, o None si no existe."""
    idx = _hash(my_map, key)
    bucket = al.get_element(my_map["buckets"], idx)
    node = _find_node(bucket, key)
    if node is None:
        return None
    return node["info"]["value"]


def remove(my_map, key):
    """Elimina la pareja con la llave dada (si existe)."""
    idx = _hash(my_map, key)
    bucket = al.get_element(my_map["buckets"], idx)
    prev = None
    node = bucket["first"]
    while node is not None:
        if node["info"]["key"] == key:
            if prev is None:
                bucket["first"] = node["next"]
            else:
                prev["next"] = node["next"]
            if node is bucket["last"]:
                bucket["last"] = prev
            bucket["size"] -= 1
            my_map["size"] -= 1
            return my_map
        prev = node
        node = node["next"]
    return my_map


def key_set(my_map):
    """Retorna un array_list con todas las llaves del mapa."""
    keys = al.new_list()
    for bucket in my_map["buckets"]["elements"]:
        for pair in sll.iterator(bucket):
            al.add_last(keys, pair["key"])
    return keys


def value_set(my_map):
    """Retorna un array_list con todos los valores del mapa."""
    values = al.new_list()
    for bucket in my_map["buckets"]["elements"]:
        for pair in sll.iterator(bucket):
            al.add_last(values, pair["value"])
    return values


def _rehash(my_map):
    """Duplica la capacidad (siguiente primo) y reubica todas las parejas."""
    old_buckets = my_map["buckets"]
    new_capacity = _next_prime(my_map["capacity"] * 2)
    new_buckets = al.new_list()
    i = 0
    while i < new_capacity:
        al.add_last(new_buckets, sll.new_list())
        i += 1
    my_map["buckets"] = new_buckets
    my_map["capacity"] = new_capacity
    for bucket in old_buckets["elements"]:
        for pair in sll.iterator(bucket):
            idx = _hash(my_map, pair["key"])
            sll.add_first(al.get_element(new_buckets, idx), pair)
    return my_map
