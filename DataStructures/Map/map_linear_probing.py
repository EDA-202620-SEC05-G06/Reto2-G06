"""
MAPA POR LINEAR PROBING (sondeo lineal) - ISIS1225 Reto 2 (G06).

Tabla de hash con manejo de colisiones por direccionamiento abierto (sondeo
lineal), vista en el curso. Cada posicion del arreglo esta vacia o guarda una
unica pareja <key, value>. Ante colision se busca la siguiente posicion libre
hacia adelante con wrap-around.

Factor de carga: alpha = n / N. Para Linear Probing se mantiene alpha ~ 0.5;
la tabla duplica su capacidad cuando n / N supera max_load_factor.

Mismo API del TAD Mapa del curso que map_separate_chaining.
"""

import DataStructures.List.array_list as al

_EMPTY = None


def _next_prime(n):
    """Retorna el menor numero primo >= n."""
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


def new_map(num_elements=17, max_load_factor=0.5):
    """Crea un mapa vacio por Linear Probing."""
    capacity = _next_prime(int(num_elements / max_load_factor) + 1)
    return {
        "keys": [_EMPTY] * capacity,
        "values": [_EMPTY] * capacity,
        "capacity": capacity,
        "size": 0,
        "max_load_factor": max_load_factor,
        "type": "LINEAR_PROBING",
    }


def _hash(my_map, key):
    """Funcion de hash al rango [0, capacity - 1]."""
    return abs(hash(key)) % my_map["capacity"]


def size(my_map):
    """Retorna el numero de parejas almacenadas."""
    return my_map["size"]


def is_empty(my_map):
    """Retorna True si el mapa esta vacio."""
    return my_map["size"] == 0


def _find_slot(my_map, key):
    """
    Retorna (found, pos). Si la llave existe, found=True y pos es su posicion.
    Si no existe, found=False y pos es la primera posicion libre para insertarla.
    """
    idx = _hash(my_map, key)
    capacity = my_map["capacity"]
    while my_map["keys"][idx] is not _EMPTY:
        if my_map["keys"][idx] == key:
            return True, idx
        idx = (idx + 1) % capacity
    return False, idx


def contains(my_map, key):
    """Retorna True si la llave se encuentra en el mapa."""
    found, _ = _find_slot(my_map, key)
    return found


def put(my_map, key, value):
    """Agrega la pareja <key, value>. Reemplaza el valor si la llave existe."""
    if (my_map["size"] + 1) / my_map["capacity"] > my_map["max_load_factor"]:
        _rehash(my_map)
    found, pos = _find_slot(my_map, key)
    if found:
        my_map["values"][pos] = value
        return my_map
    my_map["keys"][pos] = key
    my_map["values"][pos] = value
    my_map["size"] += 1
    return my_map


def get(my_map, key):
    """Retorna el valor asociado a la llave, o None si no existe."""
    found, pos = _find_slot(my_map, key)
    if not found:
        return None
    return my_map["values"][pos]


def remove(my_map, key):
    """Elimina la pareja con la llave dada y reubica el cluster afectado."""
    found, pos = _find_slot(my_map, key)
    if not found:
        return my_map
    my_map["keys"][pos] = _EMPTY
    my_map["values"][pos] = _EMPTY
    my_map["size"] -= 1
    idx = (pos + 1) % my_map["capacity"]
    while my_map["keys"][idx] is not _EMPTY:
        rk = my_map["keys"][idx]
        rv = my_map["values"][idx]
        my_map["keys"][idx] = _EMPTY
        my_map["values"][idx] = _EMPTY
        my_map["size"] -= 1
        put(my_map, rk, rv)
        idx = (idx + 1) % my_map["capacity"]
    return my_map


def key_set(my_map):
    """Retorna un array_list con todas las llaves del mapa."""
    keys = al.new_list()
    i = 0
    while i < my_map["capacity"]:
        if my_map["keys"][i] is not _EMPTY:
            al.add_last(keys, my_map["keys"][i])
        i += 1
    return keys


def value_set(my_map):
    """Retorna un array_list con todos los valores del mapa."""
    values = al.new_list()
    i = 0
    while i < my_map["capacity"]:
        if my_map["keys"][i] is not _EMPTY:
            al.add_last(values, my_map["values"][i])
        i += 1
    return values


def _rehash(my_map):
    """Duplica la capacidad (siguiente primo) y reubica todas las parejas."""
    old_keys = my_map["keys"]
    old_values = my_map["values"]
    new_capacity = _next_prime(my_map["capacity"] * 2)
    my_map["keys"] = [_EMPTY] * new_capacity
    my_map["values"] = [_EMPTY] * new_capacity
    my_map["capacity"] = new_capacity
    my_map["size"] = 0
    i = 0
    while i < len(old_keys):
        if old_keys[i] is not _EMPTY:
            put(my_map, old_keys[i], old_values[i])
        i += 1
    return my_map
