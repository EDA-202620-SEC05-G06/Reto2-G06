# Análisis de complejidad — Requerimiento 6 (Reto 2, Grupo 06)

Requerimiento grupal. Usa las mismas convenciones de los demás análisis: `n` es
el total de pedidos cargados, `m` el número de pedidos del producto consultado y
`c` el número de países distintos entre los pedidos filtrados.

## Tabla de hash agregada a la carga

`orders_by_product`: **Separate Chaining**. La llave es el `Product` y el valor
es un `array_list` con los pedidos de ese producto. Su propósito es que el
Requerimiento 6 llegue directamente a los pedidos de un producto sin recorrer la
lista principal. Agrega un `get` y, la primera vez que aparece cada producto, un
`put` por pedido durante la carga, ambos `O(1)` promedio, así que la carga sigue
siendo `O(n)` en la lectura.

## Requerimiento 6 — N países con mayor eficiencia de mercadeo

**Estrategia.** Se obtiene el bucket del producto con `get` sobre
`orders_by_product` en `O(1)` promedio. Se recorren los `m` pedidos de ese
producto filtrando por el rango de fechas (inclusivo, comparando las cadenas
`YYYY-MM-DD`, que son comparables cronológicamente). Cada pedido que pasa el
filtro suma al `Amount` total y al `Marketing_Spend` total de la consulta y se
agrega en una segunda tabla de hash por país (`Country` como llave, acumulador
como valor: número de pedidos, `Amount` total, `Marketing_Spend` total, total de
cajas y suma de precio). Terminada la agregación se recorren los `c` países: a
los que tienen `Marketing_Spend` total mayor que cero se les calcula el precio
promedio y la eficiencia `suma(Amount) / suma(Marketing_Spend)` y pasan a un
`array_list`; los demás no entran al ranking. Ese `array_list` se ordena con
**merge sort** de manera descendente por eficiencia, con desempate por `Amount`
total descendente y luego por `Country` ascendente, y se toman los primeros `N`.

**Complejidad.** El acceso al bucket del producto es `O(1)`. El recorrido con
filtro y agregación es `O(m)`, porque cada pedido hace un `get` de `O(1)`
promedio sobre la tabla de países. Calcular las eficiencias es `O(c)`, el
ordenamiento es `O(c log c)` y la selección del top N es `O(N)` con `N <= c`.
El requerimiento es **`O(m + c log c)`**, con `c <= m <= n`. Como `c` es pequeño
y acotado (los países del conjunto de datos), la operación dominante es el
recorrido de los pedidos del producto, que es en promedio una fracción `n/p` de
los pedidos, con `p` el número de productos.

**Tipo de tabla de hash.** Dos tablas, cada una del tipo que conviene a lo que
almacena:

`orders_by_product` es **Separate Chaining**: pocas llaves y el valor de cada
una es una lista de pedidos que crece durante la carga, por lo que un factor de
carga alto no penaliza y no se desperdicia memoria.

La tabla de agregación por país es **Linear Probing**: se consulta una vez por
cada pedido filtrado (hasta `m` operaciones `get`), el número de llaves es
pequeño y conocido de antemano y nunca se eliminan llaves. Con alpha de 0.5 la
tabla no hace rehash y cada consulta se resuelve en uno o dos sondeos sobre un
arreglo contiguo, sin crear ni recorrer nodos encadenados.

**Ordenamiento.** Merge sort sobre los `c` países, `O(c log c)` en todos los
casos y estable.

**Estructuras lineales.** El bucket del producto, la lista de países a ordenar
y la lista del top N son `array_list`.
