# Análisis de complejidad — Requerimiento 2 (Reto 2, Grupo 06)

Responsable: Nicolás Fajardo. Usa las mismas convenciones del análisis de los
requerimientos 1 y 5: `n` es el total de pedidos cargados, `m` el número de
pedidos del país consultado, `k` el número de pedidos que pasan el filtro y `p`
el número de productos distintos entre ellos.

## Requerimiento 2 — pedidos por país y rango de cajas enviadas

**Estrategia.** Se obtiene el bucket del país con `get` sobre
`orders_by_country` (tabla construida en la carga) en `O(1)` promedio. Solo se
recorren los `m` pedidos de ese país filtrando por `Boxes_Shipped` dentro del
rango (inclusivo). Cada pedido que pasa el filtro se agrega a un `array_list` de
resultados, acumula `Marketing_Spend` y `Amount` para los promedios e incrementa
el contador de su producto en una segunda tabla de hash (`Product` como llave,
número de pedidos como valor). Al terminar, se recorren las `p` llaves de esa
tabla para hallar el producto más frecuente (ante empate, el de nombre
alfabéticamente menor) y su tamaño da el número de productos diferentes. Los `k`
pedidos se ordenan con **merge sort** de manera ascendente por `Boxes_Shipped`,
con desempate por `Order_Date` descendente y luego por `Order_ID` ascendente.

**Complejidad.** El acceso al bucket es `O(1)`. El filtro con conteo por
producto es `O(m)`, porque cada pedido hace un `get` y un `put` de `O(1)`
promedio. Hallar el producto más frecuente es `O(p)`. El ordenamiento es
`O(k log k)`. El requerimiento es **`O(m + k log k)`**, con `p <= k <= m <= n`;
la operación dominante es el ordenamiento cuando el rango de cajas es amplio y
el recorrido del país cuando es estrecho. En el peor caso (un solo país y un
rango que lo incluye todo) es `O(n log n)`.

**Tipo de tabla de hash.** Se usan dos tablas, cada una del tipo que conviene a
lo que almacena:

`orders_by_country` es **Separate Chaining**: hay pocas llaves y el valor de
cada una es una lista de pedidos que crece durante la carga, de modo que un
factor de carga alto no penaliza y no se desperdicia memoria.

La tabla de conteo por producto es **Linear Probing**: el valor es un entero que
se actualiza una vez por cada pedido filtrado (hasta `m` pares `get`/`put`), el
número de llaves es pequeño y conocido de antemano (los productos del catálogo)
y nunca se eliminan llaves. Con alpha de 0.5 la tabla no hace rehash, cada
operación resuelve en uno o dos sondeos sobre un arreglo contiguo y se evita
crear y recorrer nodos encadenados, que es justo el costo que Separate Chaining
añadiría en la operación más repetida del requerimiento.

**Ordenamiento.** Merge sort, `O(k log k)` en todos los casos y estable. Se
prefiere sobre quick sort porque `Boxes_Shipped` tiene muchos valores repetidos
y los pedidos de un país pueden venir parcialmente ordenados, casos en los que
quick sort se acerca a su peor caso `O(k^2)`.

**Estructuras lineales.** El bucket del país y la lista de resultados que se
ordena son `array_list`; las llaves de la tabla de conteo se recorren como
`array_list`.
