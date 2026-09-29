# Análisis de complejidad — Requerimientos 1 y 5 (Reto 2, Grupo 06)

Este documento cubre la carga de datos y los requerimientos 1 y 5. Está pensado
para integrarse al informe grupal en PDF de la carpeta `Docs` junto con el
análisis de los demás requerimientos.

## Convenciones

Sea `n` el número total de pedidos cargados. Para un requerimiento, `m` es el
número de pedidos del bucket consultado (los de un mes, o los de un país) y `k`
el número de registros que finalmente hay que ordenar. Salvo que se diga lo
contrario, las complejidades de las tablas de hash son de caso promedio, que es
el caso de operación real con una función de hash de distribución uniforme y un
factor de carga controlado.

## Tablas de hash construidas en la carga

Durante la carga (una sola lectura del archivo) se construyen tres tablas de
hash, todas por **Separate Chaining**:

`orders_by_month`: la llave es la cadena `"YYYY-MM"` y el valor es un `array_list`
con los pedidos de ese mes. Su propósito es que el Requerimiento 1 llegue
directamente a los pedidos de un mes sin recorrer la lista principal.

`orders_by_country`: la llave es el `Country` y el valor es un `array_list` con
los pedidos de ese país. Sirve al Requerimiento 5 para llegar directamente a los
pedidos de un país.

`channel_count`: la llave es el `Channel` y el valor es el número de pedidos de
ese canal. Alimenta el reporte de la carga.

En los tres casos el valor almacenado es una colección o un acumulador, no un
registro suelto, y el número de llaves distintas es pequeño y acotado (unos 24
meses para dos años, un puñado de países, tres canales). Ese es exactamente el
escenario donde **Separate Chaining es preferible a Linear Probing**: el valor
natural de cada posición es una lista que crece, el encadenamiento la aloja sin
problema y el factor de carga se mantiene sano con alpha cercano a 5 sin
desperdiciar memoria. Linear Probing, en cambio, guarda una sola pareja por
posición, obliga a mantener alpha cercano a 0.5 y a rehashear con más frecuencia,
y no aporta ninguna ventaja de localidad aquí porque nunca se recorre la tabla
por rangos de llaves.

### Complejidad de la carga

La lectura y construcción es `O(n)`: cada pedido se inserta una vez en la lista
principal y una vez en cada tabla de hash, y cada `put`/`get` es `O(1)`
promedio. El reporte de la carga incluye los primeros y últimos cinco pedidos
ordenados de manera descendente por `Amount`, lo que exige ordenar una copia de
la lista principal con **merge sort**: eso aporta un término `O(n log n)`, que
domina el costo total del reporte de carga. Los mínimos y máximos de `Amount` y
de fecha se calculan durante la misma pasada en `O(n)`, sin ordenar.

## Requerimiento 1 — pedidos por mes y rango de descuento

**Estrategia.** Se calcula la llave `"YYYY-MM"` a partir del año y el mes y se
obtiene el bucket del mes con `get` sobre `orders_by_month` en `O(1)` promedio.
Solo se recorren los `m` pedidos de ese mes filtrando por el rango de descuento
(inclusivo). Los `k` pedidos que pasan el filtro se ordenan con **merge sort** de
manera descendente por `Discount_Pct`, con desempate por `Amount` descendente y
luego por `Order_ID` ascendente.

**Complejidad.** El acceso al bucket es `O(1)`. El filtro recorre el mes en
`O(m)`. El ordenamiento es `O(k log k)`. La operación dominante es el
ordenamiento de los resultados, de modo que el requerimiento es
**`O(m + k log k)`**, con `k <= m <= n`. Como `m` es solo el subconjunto de un
mes, esto es mucho menor que recorrer los `n` pedidos, y en la práctica `m` es
del orden de `n/24`.

**Tipo de tabla de hash.** Separate Chaining, por la razón explicada arriba: la
consulta necesita todos los pedidos de un mes, y guardarlos como una lista
encadenada en la posición de la llave es lo natural y evita recorrer la lista
principal (lo que invalidaría el requerimiento).

**Ordenamiento.** Merge sort, `O(k log k)` en todos los casos y estable, lo que
respeta el orden relativo cuando el criterio de tres niveles deja elementos
equivalentes.

## Requerimiento 5 — N productos con mayor recaudo por país y rango de fechas

**Estrategia.** Se obtiene el bucket del país con `get` sobre `orders_by_country`
en `O(1)` promedio. Se recorren los `m` pedidos del país filtrando por el rango
de fechas (inclusivo, comparando las cadenas `YYYY-MM-DD`, que son comparables
cronológicamente). Cada pedido que pasa el filtro se agrega en una segunda tabla
de hash por producto (`Product` como llave, acumulador como valor: número de
pedidos, total de cajas, recaudo, suma de precio, suma de descuento, total de
mercadeo). Terminada la agregación hay `p` productos distintos; se llevan a un
`array_list`, se ordenan con **merge sort** de manera descendente por recaudo,
con desempate por total de `Boxes_Shipped` descendente y luego por nombre de
producto ascendente, y se toman los primeros `N`.

**Complejidad.** El acceso al bucket del país es `O(1)`. El recorrido con filtro
y agregación es `O(m)`, porque cada pedido hace un `put`/`get` de `O(1)`
promedio sobre la tabla de productos. El ordenamiento de los productos es
`O(p log p)` y la selección del top N es `O(N)`. Como `p` es pequeño y acotado
(la cantidad de productos del catálogo), el término dominante es el recorrido del
país: el requerimiento es **`O(m + p log p)`**, con `p <= m <= n`.

**Tipo de tabla de hash.** Separate Chaining en las dos tablas. En
`orders_by_country` el valor es la lista de pedidos del país, igual que en el
Requerimiento 1. En la tabla de agregación por producto el número de llaves es
pequeño y el valor es un acumulador que se actualiza en sitio; Separate Chaining
lo maneja con `put`/`get` en `O(1)` promedio sin necesidad de mantener alpha
bajo. Linear Probing no ofrece ventaja porque no se hacen consultas por rango de
llaves ni se aprovecha la localidad contigua.

**Ordenamiento.** Merge sort sobre los `p` productos, `O(p log p)` y estable.

## Integración de estructuras lineales

Las estructuras lineales del curso intervienen de forma funcional en ambos
requerimientos: los buckets de los meses y de los países son `array_list`, los
resultados filtrados y las listas de productos a ordenar son `array_list`, y los
buckets internos de cada tabla por Separate Chaining son `single_linked_list`.
Ninguna estructura lineal se crea sin usarse en la solución.
