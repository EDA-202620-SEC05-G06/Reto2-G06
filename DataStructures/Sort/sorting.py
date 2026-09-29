"""
ALGORITMOS DE ORDENAMIENTO GENERICOS - ISIS1225 Reto 2 (G06).

Todos operan sobre una array_list y reciben una funcion sort_criteria(a, b)
que retorna True si a debe ir ANTES que b (orden total estricto: retorna False
cuando a y b son equivalentes). Esto hace que merge_sort e insertion_sort sean
estables: ante empate se conserva el orden original.

No se usan sorted(), list.sort(), pandas ni librerias externas de ordenamiento.
"""

import DataStructures.List.array_list as al


def insertion_sort(my_list, sort_criteria):
    """Ordenamiento por insercion. O(n^2) peor caso, O(n) mejor caso. Estable."""
    n = al.size(my_list)
    i = 1
    while i < n:
        j = i
        while j > 0 and sort_criteria(al.get_element(my_list, j),
                                      al.get_element(my_list, j - 1)):
            al.exchange(my_list, j, j - 1)
            j -= 1
        i += 1
    return my_list


def selection_sort(my_list, sort_criteria):
    """Ordenamiento por seleccion. O(n^2) en todos los casos."""
    n = al.size(my_list)
    i = 0
    while i < n:
        pos_min = i
        j = i + 1
        while j < n:
            if sort_criteria(al.get_element(my_list, j),
                             al.get_element(my_list, pos_min)):
                pos_min = j
            j += 1
        al.exchange(my_list, i, pos_min)
        i += 1
    return my_list


def shell_sort(my_list, sort_criteria):
    """Ordenamiento Shell con incrementos 3x+1. O(n^3/2) peor caso."""
    n = al.size(my_list)
    h = 1
    while h < n // 3:
        h = 3 * h + 1
    while h >= 1:
        i = h
        while i < n:
            j = i
            while j >= h and sort_criteria(al.get_element(my_list, j),
                                           al.get_element(my_list, j - h)):
                al.exchange(my_list, j, j - h)
                j -= h
            i += 1
        h = h // 3
    return my_list


def merge_sort(my_list, sort_criteria):
    """
    Ordenamiento por mezcla (top-down). O(n log n) en todos los casos. Estable.
    Usa una lista auxiliar de tamano n (no es in-place).
    """
    n = al.size(my_list)
    if n > 1:
        aux = al.sub_list(my_list, 0, n)
        _merge_sort_rec(my_list, aux, sort_criteria, 0, n - 1)
    return my_list


def _merge_sort_rec(my_list, aux, sort_criteria, lo, hi):
    """Ordena recursivamente las dos mitades del rango [lo, hi] y las mezcla."""
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _merge_sort_rec(my_list, aux, sort_criteria, lo, mid)
    _merge_sort_rec(my_list, aux, sort_criteria, mid + 1, hi)
    _merge(my_list, aux, sort_criteria, lo, mid, hi)


def _merge(my_list, aux, sort_criteria, lo, mid, hi):
    """Mezcla las mitades ordenadas [lo, mid] y [mid+1, hi] usando aux."""
    k = lo
    while k <= hi:
        al.change_info(aux, k, al.get_element(my_list, k))
        k += 1
    i = lo
    j = mid + 1
    k = lo
    while k <= hi:
        if i > mid:
            al.change_info(my_list, k, al.get_element(aux, j))
            j += 1
        elif j > hi:
            al.change_info(my_list, k, al.get_element(aux, i))
            i += 1
        elif sort_criteria(al.get_element(aux, j), al.get_element(aux, i)):
            # aux[j] va antes que aux[i]; ante empate NO entra aqui (estable)
            al.change_info(my_list, k, al.get_element(aux, j))
            j += 1
        else:
            al.change_info(my_list, k, al.get_element(aux, i))
            i += 1
        k += 1


def quick_sort(my_list, sort_criteria):
    """Ordenamiento quick sort. O(n log n) promedio, O(n^2) peor caso."""
    _quick_sort_rec(my_list, sort_criteria, 0, al.size(my_list) - 1)
    return my_list


def _quick_sort_rec(my_list, sort_criteria, lo, hi):
    """Particiona y ordena recursivamente menores y mayores del pivote."""
    if lo >= hi:
        return
    pivot = _partition(my_list, sort_criteria, lo, hi)
    _quick_sort_rec(my_list, sort_criteria, lo, pivot - 1)
    _quick_sort_rec(my_list, sort_criteria, pivot + 1, hi)


def _partition(my_list, sort_criteria, lo, hi):
    """Deja el pivote (elemento en hi) en su posicion final y retorna su indice."""
    pivot = al.get_element(my_list, hi)
    i = lo
    j = lo
    while j < hi:
        if sort_criteria(al.get_element(my_list, j), pivot):
            al.exchange(my_list, i, j)
            i += 1
        j += 1
    al.exchange(my_list, i, hi)
    return i
