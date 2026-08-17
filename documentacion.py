"""
documentacion.py — Ventana de Documentación técnica de ThermoPhase.

Dos paneles: a la izquierda un árbol (pestaña Contenido) con las secciones y
subsecciones; a la derecha el desarrollo de cada una. Explica las ecuaciones
implementadas y su sentido físico, siguiendo la forma en que ThermoPhase
realiza los cálculos. Las ecuaciones se renderizan como imágenes matemáticas
(fracciones apiladas y tipografía de ecuación).
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextBrowser, QSplitter,
)
from PyQt6.QtCore import Qt
import base64 as _b64


_CSS = """
body   { font-family:'Arial Narrow','Arial'; font-size:14px; color:#000000; }
h2     { font-family:'Arial Narrow','Arial'; font-size:14px; font-weight:bold;
         color:#000000; margin:2px 0 9px 0; }
h3     { font-family:'Arial Narrow','Arial'; font-size:14px; font-weight:bold;
         color:#000000; margin:14px 0 4px 0; }
p      { font-size:14px; line-height:142%; margin:7px 0; color:#000000;
         text-align:justify; }
li     { font-size:14px; line-height:140%; margin:3px 0; color:#000000; }
b      { font-weight:normal; color:#000000; }
i      { font-style:normal; }
"""


# ── Renderizado de ecuaciones (matplotlib, alta resolución) ──────────
_EQ_CACHE = {}


def _eq(latex):
    """Devuelve un marcador con la ecuación (se renderiza al mostrarla)."""
    return f'@@EQ:{_b64.b64encode(latex.encode()).decode()}@@'


def _render_eq_png(latex, fontsize=12, dpi=200):
    """Renderiza la ecuación a PNG de alta resolución. Devuelve (bytes, w, h)."""
    if latex in _EQ_CACHE:
        return _EQ_CACHE[latex]
    try:
        import matplotlib
        matplotlib.use('Agg')
        matplotlib.rcParams['mathtext.fontset'] = 'cm'   # una sola tipografía
        import matplotlib.pyplot as plt
        import io, struct
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f'${latex}$', fontsize=fontsize, color='#000000')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                    pad_inches=0.04, transparent=True)
        plt.close(fig)
        data = buf.getvalue()
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        res = (data, w, h)
    except Exception:
        res = (None, 0, 0)
    _EQ_CACHE[latex] = res
    return res


# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 1 — Fundamentos de las EOS cúbicas
# ═════════════════════════════════════════════════════════════════════
S1_1 = """
<h2>1.1 Ecuación de estado</h2>
<p>Una ecuación de estado (EOS, por <i>Equation of State</i>) es una relación
matemática que vincula las tres variables que describen el estado de un fluido:
la presión (P), el volumen molar (V) y la temperatura (T). Conocidas dos de
ellas, la EOS entrega la tercera, y a partir de ella todas las propiedades
termodinámicas derivadas.</p>
<p>El objetivo práctico es responder: a estas condiciones de presión y
temperatura, ¿mi mezcla de hidrocarburos es líquido, gas o coexisten ambas
fases? Todo eso se deriva de una buena ecuación de estado.</p>
<p>El punto de partida es la ecuación del gas ideal, la ecuación de estado más
simple:</p>
""" + _eq(r"P\,V = n\,R\,T") + """
<p>donde n es el número de moles y R es la constante universal de los gases. El
motor de ThermoPhase trabaja internamente en unidades de campo, por lo que
emplea el valor R = 10.7316 psi·ft³/(lb-mol·°R).</p>
<p>El gas ideal supone dos cosas que la realidad no cumple:</p>
<ul>
<li>Las moléculas no ocupan volumen propio (se tratan como puntos).</li>
<li>Las moléculas no ejercen fuerzas entre sí (ni se atraen ni se repelen).</li>
</ul>
<p>A bajas presiones y altas temperaturas esa idealización es razonable, porque
las moléculas están muy separadas y su tamaño e interacciones son
despreciables. Pero en un yacimiento o una planta de procesamiento (altas
presiones, moléculas muy empaquetadas) ambas suposiciones fallan por completo.
Corregir esas dos deficiencias es exactamente lo que hacen las ecuaciones de
estado cúbicas, y por eso son la herramienta central de este programa.</p>
"""

S1_2 = """
<h2>1.2 Del gas ideal a los fluidos reales</h2>
<p>Para acercar el modelo a la realidad se introducen dos correcciones sobre la
ecuación del gas ideal, cada una atacando una de las suposiciones falsas.</p>
<h3>Corrección por volumen propio (corrección por repulsión)</h3>
<p>Las moléculas sí ocupan espacio. Por lo tanto, el volumen realmente
disponible para que se muevan no es V, sino V menos un volumen mínimo que
ocupan las propias moléculas. A ese volumen excluido se le llama covolumen (b),
que es el volumen ocupado por un mol de moléculas. El término de presión se
corrige reemplazando V por (V menos n·b), donde n es el número de moles:</p>
""" + _eq(r"P = \frac{n\,R\,T}{V - n\,b}") + """
<p>Cuando V se aproxima a n·b, el denominador tiende a cero y la presión se
dispara hacia el infinito. Físicamente esto expresa que es imposible comprimir
el fluido más allá del volumen que ocupan sus propias moléculas: ese es el
límite duro de la fase líquida. Se le llama repulsión porque, a distancias muy
cortas, las nubes electrónicas de las moléculas se repelen con fuerza y actúan
como esferas casi rígidas.</p>
<h3>Corrección por fuerzas atractivas (corrección por atracción)</h3>
<p>Las moléculas también se atraen entre sí mediante fuerzas de atracción
intermolecular. Esa atracción tiende a juntarlas y, en consecuencia, reduce la
presión que ejercen sobre las paredes del recipiente respecto de la que
ejercería un gas ideal. Por eso al término repulsivo se le resta un término
atractivo:</p>
""" + _eq(r"P = \frac{n\,R\,T}{V - n\,b}\; -\; \left(\text{termino atractivo}\right)") + """
<p>Una forma intuitiva de verlo: una molécula que está a punto de golpear la
pared del recipiente es frenada por la atracción de las moléculas que quedan
detrás de ella. Ese tirón hacia adentro disminuye la fuerza del impacto y, por
lo tanto, la presión medida. El término atractivo es la traducción matemática
de ese tirón, y es lo que hace posible que exista una fase líquida: sin
atracción, nada mantendría a las moléculas unidas.</p>
"""

S1_3 = """
<h2>1.3 Término de repulsión</h2>
<p>Dentro del término de repulsión de la EOS se encuentra el covolumen b, que
representa el volumen molar mínimo al que se puede comprimir una sustancia; es,
en esencia, el espacio que las propias moléculas ocupan y del que ningún otro
cuerpo puede disponer. Su papel en la ecuación es doble.</p>
<p>El primer papel es fijar el límite físico de compresibilidad: no se puede
comprimir el fluido más allá del tamaño de sus propias moléculas. En la
ecuación esto se ve porque, cuando el volumen se acerca a n·b, el denominador
(V menos n·b) tiende a cero y la presión tiende a infinito.</p>
<p>El segundo papel es fijar la escala de la rama líquida de la isoterma.
Conviene explicarlo con calma. Si se dibuja la presión frente al volumen a
temperatura constante (una isoterma), la parte de la curva que corresponde al
líquido es casi vertical: el líquido es muy poco compresible, de modo que
grandes cambios de presión producen cambios mínimos de volumen. ¿Dónde se
ubica esa pared casi vertical sobre el eje del volumen? Justamente cerca de
n·b, porque el líquido no puede tener un volumen menor que el que ocupan sus
moléculas. Por eso se dice que b fija la escala de la rama líquida: es el valor
alrededor del cual se acomodan los volúmenes del líquido y, por lo tanto,
determina la densidad máxima que el modelo le asigna a la fase líquida. En
términos físicos, un covolumen mayor (moléculas más grandes) desplaza esa pared
hacia volúmenes mayores y predice un líquido menos denso; un covolumen menor la
desplaza hacia volúmenes pequeños y predice un líquido más denso.</p>
<p>El valor de b no se ajusta a ojo ni se mide directamente: se deduce
obligando a que la ecuación reproduzca de forma exacta el punto crítico de la
sustancia. El punto crítico es un estado muy particular (se detalla en la
sección de propiedades críticas) en el que líquido y gas se vuelven idénticos;
matemáticamente, la isoterma que pasa por él tiene una forma geométrica
precisa. Al imponerle a la EOS que respete esa forma en el punto crítico se
obtienen ecuaciones que despejan b (y también el parámetro de atracción) en
función de datos que sí se conocen y tabulan: la temperatura y la presión
críticas. El resultado es:</p>
""" + _eq(r"b = \Omega_b\;\frac{R\,T_c}{P_c}") + """
<p>donde el número adimensional <b>&Omega;<sub>b</sub></b> depende únicamente de
la forma de la ecuación elegida (toma un valor para Peng-Robinson y otro para
SRK). Conviene resaltar una consecuencia importante: b depende sólo de las
propiedades críticas del componente y no de la temperatura de operación. Es,
por lo tanto, una constante para cada sustancia, que ThermoPhase calcula una
sola vez a partir de la base de datos de propiedades.</p>
<p>Cuando se trabaja con una mezcla y no con un componente puro, el covolumen de
la mezcla se obtiene sumando linealmente los aportes de cada componente,
ponderados por su fracción molar. Ésta es la regla de mezclado que el programa
aplica en la función que evalúa <b>b<sub>m</sub></b>:</p>
""" + _eq(r"b_m = \sum_{i} z_i\, b_i") + """
<p>La linealidad tiene sentido físico directo: el volumen que ocupan las
moléculas de una mezcla es simplemente la suma de los volúmenes que ocupa cada
especie, sin efectos cruzados apreciables. Esto contrasta con el término de
atracción, que sí requiere una regla más elaborada porque involucra
interacciones entre pares de moléculas distintas.</p>
"""

S1_4 = """
<h2>1.4 Término de atracción</h2>
<p>El término de atracción es el corazón de una ecuación de estado cúbica y el
que más influye en la calidad de las predicciones de equilibrio. Se construye
como el producto de dos factores: uno que fija la magnitud de la atracción
molecular y otro que introduce la dependencia con la temperatura.</p>
""" + _eq(r"a(T) = a_c\;\alpha(T)") + """
<p>El primer factor, <b>a<sub>c</sub></b>, establece cuán intensa es la
atracción de la sustancia. Al igual que el covolumen, se obtiene obligando a la
ecuación a reproducir el punto crítico. La idea física es la misma que con b:
en el punto crítico la isoterma tiene una forma geométrica única (una inflexión
con tangente horizontal, es decir, una zona momentáneamente plana), y al exigir
que la EOS respete esa forma se despeja a_c en función de datos conocidos, la
temperatura y la presión críticas. Así, a_c queda anclado a propiedades
medibles y no a un ajuste arbitrario:</p>
""" + _eq(r"a_c = \Omega_a\;\frac{R^{2}\,T_c^{\,2}}{P_c}") + """
<p>El segundo factor, α(T), es una función adimensional de la temperatura que
vale exactamente 1 en el punto crítico y crece a medida que la temperatura
disminuye. Su sentido físico es capturar cómo cambia la fuerza atractiva
efectiva con la temperatura: al enfriar el fluido, las moléculas se mueven más
despacio, permanecen más tiempo cerca unas de otras y su atracción efectiva
aumenta, de modo que α crece; al calentarlo, la agitación térmica vence a la
atracción y α disminuye hasta valer 1 en el punto crítico. Su forma, propuesta
por Soave y adoptada también por Peng-Robinson, es:</p>
""" + _eq(r"\alpha(T) = \left[\,1 + m\left(1 - \sqrt{\frac{T}{T_c}}\,\right)\right]^{2}") + """
<p>El coeficiente m es una función del factor acéntrico ω (se detalla más
adelante) y toma expresiones distintas para Peng-Robinson y para SRK. Es el
parámetro que ajusta cuán rápido crece la atracción al enfriar el fluido.</p>
<p>La consecuencia de esta dependencia con la temperatura es fundamental: en el
punto crítico (α igual a 1) la distinción entre líquido y gas desaparece; por
debajo de él, la atracción crece lo suficiente como para permitir que el fluido
condense. Sin esta dependencia, la ecuación no podría reproducir correctamente
las presiones de vapor de los componentes, que son precisamente el dato que
ancla todo el equilibrio de fases.</p>
<p>En una mezcla, la magnitud de la atracción se obtiene con la regla de
mezclado cuadrática, que suma las interacciones entre todos los pares de
moléculas. ThermoPhase evalúa <b>a<sub>m</sub></b> con esta expresión cada vez
que necesita las propiedades de una fase:</p>
""" + _eq(r"a_m = \sum_{i}\sum_{j} z_i\,z_j\,\sqrt{a_i\,a_j}\,\left(1 - k_{ij}\right)") + """
<p>donde el factor (1 menos k_ij) corrige la atracción entre moléculas de
especies distintas. Esta regla y el significado de los coeficientes k_ij se
desarrollan en la sección de parámetros.</p>
"""

S1_5 = """
<h2>1.5 Ecuación de Peng-Robinson (PR)</h2>
<p>Publicada por Ding-Yu Peng y Donald Robinson en 1976, la ecuación de
Peng-Robinson es hoy la más utilizada en la industria del petróleo y el gas, y
es la opción por defecto de ThermoPhase. Su forma completa es:</p>
""" + _eq(r"P = \frac{n\,R\,T}{V - n\,b} \;-\; \frac{a\,\alpha(T)}{V(V+b) + b(V-b)}") + """
<p>Lo que distingue a Peng-Robinson de ecuaciones anteriores es el denominador
del término atractivo. Su estructura fue elegida deliberadamente para mejorar
la predicción de las densidades de la fase líquida, que en modelos previos
resultaban poco realistas. Las constantes que la definen son:</p>
""" + _eq(r"\Omega_a = 0.45724 \qquad \Omega_b = 0.07780") + """
<p>y el coeficiente m de la función α(T) se calcula a partir del factor
acéntrico mediante el polinomio ajustado por sus autores:</p>
""" + _eq(r"m = 0.37464 + 1.54226\,\omega - 0.26992\,\omega^{2}") + """
<p>La combinación de un buen ajuste del equilibrio líquido-vapor de
hidrocarburos con densidades de líquido más realistas es la razón por la cual
Peng-Robinson se ha vuelto el estándar de la industria.</p>
"""

S1_6 = """
<h2>1.6 Ecuación de Soave-Redlich-Kwong (SRK)</h2>
<p>Propuesta por Giorgio Soave en 1972 como mejora de la ecuación de
Redlich-Kwong de 1949, la ecuación SRK fue la primera EOS cúbica capaz de
reproducir con buena precisión las presiones de vapor de los hidrocarburos, al
introducir la función α(T) dependiente del factor acéntrico. Su forma es:</p>
""" + _eq(r"P = \frac{n\,R\,T}{V - n\,b} \;-\; \frac{a\,\alpha(T)}{V(V + b)}") + """
<p>La diferencia respecto de Peng-Robinson está en el denominador del término
atractivo, que aquí es simplemente V(V+b), y en el valor de las constantes:</p>
""" + _eq(r"\Omega_a = 0.42748 \qquad \Omega_b = 0.08664") + """
<p>El coeficiente m de SRK tiene su propia correlación con el factor
acéntrico:</p>
""" + _eq(r"m = 0.480 + 1.574\,\omega - 0.176\,\omega^{2}") + """
<p>SRK y Peng-Robinson comparten la misma filosofía (repulsión más atracción
dependiente de la temperatura) y difieren sólo en la forma del denominador
atractivo, que cambia la manera en que se reparte el volumen entre las fases.
En la práctica, SRK tiende a sobrestimar el volumen de la fase líquida,
mientras que Peng-Robinson lo corrige mejor. Sin embargo, ambas producen
composiciones de equilibrio muy similares, por lo que la elección entre una y
otra suele depender de con qué software de referencia se desee comparar.</p>
"""

S1_7 = """
<h2>1.7 Forma cúbica de la ecuación de estado</h2>
<p>Resolver la ecuación de estado directamente para el volumen es incómodo. Es
mucho más práctico trabajar con el factor de compresibilidad Z, que es una
medida adimensional de cuánto se aleja el fluido del comportamiento ideal. Se
define como:</p>
""" + _eq(r"Z = \frac{P\,V}{n\,R\,T}") + """
<p>Una forma equivalente y muy intuitiva de entender Z es como el cociente
entre el volumen real que ocupa el fluido y el volumen que ocuparía si fuera un
gas ideal a la misma presión y temperatura:</p>
""" + _eq(r"Z = \frac{V_{\mathrm{real}}}{V_{\mathrm{ideal}}} \qquad V_{\mathrm{ideal}} = \frac{n\,R\,T}{P}") + """
<p>De aquí se ve la relación de Z con la repulsión y la atracción. Cuando
domina la repulsión (a alta presión, con las moléculas muy juntas y
resistiéndose a la compresión), el fluido ocupa más volumen del que ocuparía un
gas ideal, de modo que Z es mayor que 1. Cuando domina la atracción (las
moléculas se juntan más de lo que lo haría un gas ideal), el fluido ocupa menos
volumen y Z es menor que 1. Un gas ideal, sin fuerzas, tiene Z igual a 1, y un
líquido comprimido, con las moléculas casi en contacto, tiene un Z pequeño.</p>
<p>Para reescribir la ecuación en términos de Z se definen dos grupos
adimensionales que concentran toda la información de la sustancia y del
estado:</p>
""" + _eq(r"A = \frac{a\,\alpha\,P}{(R\,T)^{2}} \qquad B = \frac{b\,P}{R\,T}") + """
<p>Sustituyendo, la ecuación de estado se transforma en un polinomio de tercer
grado en Z. La forma del polinomio depende de la ecuación. Para Peng-Robinson
es:</p>
""" + _eq(r"Z^{3} - (1-B)\,Z^{2} + \left(A - 3B^{2} - 2B\right)Z - \left(AB - B^{2} - B^{3}\right) = 0") + """
<p>Los grupos adimensionales A y B se definen igual para SRK, pero como su
término atractivo tiene otra forma, el polinomio cúbico de SRK es distinto:</p>
""" + _eq(r"Z^{3} - Z^{2} + \left(A - B - B^{2}\right)Z - A\,B = 0") + """
<p>De aquí proviene el nombre de ecuaciones cúbicas: siempre conducen a un
polinomio de tercer grado, que ThermoPhase resuelve de forma analítica (no
iterativa) mediante las funciones internas de solución del cúbico, una para
Peng-Robinson y otra para SRK.</p>
<p>Un polinomio cúbico puede tener una o tres raíces reales. Cuando hay tres, la
raíz mayor normalmente corresponde a la fase vapor (mayor volumen, menor
densidad) y la raíz menor a la fase líquida (menor volumen, mayor densidad); la
raíz intermedia carece de significado físico porque corresponde a una región
mecánicamente inestable. Que aparezcan tres raíces reales es precisamente la
señal matemática de que, a esas condiciones, el fluido puede separarse en dos
fases. Cómo se elige entre ellas se trata en la subsección siguiente.</p>
"""

S1_8 = """
<h2>1.8 Selección de la raíz por energía de Gibbs</h2>
<p>Cuando el polinomio cúbico entrega tres raíces reales, hay que decidir cuál
usar. Para entender el criterio conviene recordar qué es la energía libre de
Gibbs: es una medida de la energía disponible de un sistema a presión y
temperatura fijas, y la termodinámica establece que, en esas condiciones, todo
sistema evoluciona espontáneamente hacia el estado de menor energía de Gibbs,
igual que una pelota rueda hacia el punto más bajo de un terreno.</p>
<p>Cada raíz del cúbico representa un estado posible del fluido (un volumen, una
densidad). El criterio, entonces, es directo: de las raíces candidatas, la fase
que realmente existe es la que tiene la menor energía de Gibbs, porque es hacia
ese estado hacia el que la naturaleza lleva al sistema.</p>
<p>Para una fase de composición dada, a la misma presión y temperatura, la
energía de Gibbs molar (dividida por R·T para dejarla adimensional) se puede
escribir a través de los coeficientes de fugacidad, que son la cantidad que la
propia ecuación de estado entrega para cada raíz. Comparar dos raíces equivale
entonces a comparar:</p>
""" + _eq(r"\frac{G}{n\,R\,T} = \sum_{i} x_i \,\ln\!\left(\phi_i\, x_i\, P\right)") + """
<p>Como la composición, la presión y la temperatura son idénticas para ambas
raíces, la comparación se reduce a evaluar cuál raíz produce el menor valor de
la suma de x_i por el logaritmo de su coeficiente de fugacidad. La raíz que
minimiza esa suma es la estable, y es la que debe emplearse.</p>
<p>En la práctica, cuando ThermoPhase sabe de antemano el rol de la fase, aplica
directamente la consecuencia de este criterio: para las propiedades del vapor
utiliza la raíz mayor del cúbico (la de mayor volumen, Z_V), y para el líquido
la raíz menor (la de menor volumen, Z_L), porque en cada caso ésa es la raíz
que minimiza la energía de Gibbs de esa fase. El criterio de mínima energía de
Gibbs se vuelve indispensable en las situaciones ambiguas: cuando existe una
sola raíz real, o cuando hay que decidir si un fluido monofásico debe tratarse
como líquido o como vapor. En esos casos el programa evalúa la energía de Gibbs
de las raíces disponibles y se queda con la de menor valor, dejando que sea la
termodinámica, y no una regla fija, la que decida qué fase es la real.</p>
"""

S1_9 = """
<h2>1.9 Las cuatro variantes PR/SRK</h2>
<p>ThermoPhase implementa cuatro ecuaciones de estado seleccionables, que
surgen de combinar las dos formas cúbicas con dos conjuntos de parámetros,
según el simulador comercial que se tome como referencia para la validación:</p>
<ul>
<li>Peng-Robinson con parámetros HYSYS</li>
<li>SRK con parámetros HYSYS</li>
<li>Peng-Robinson con parámetros PVTsim</li>
<li>SRK con parámetros PVTsim</li>
</ul>
<p>Dentro de cada familia (Peng-Robinson o SRK) la forma de la ecuación es la
misma; lo que cambia entre HYSYS y PVTsim son los valores tabulados de las
propiedades críticas, los factores acéntricos y, sobre todo, los coeficientes
de interacción binaria. Estas pequeñas diferencias en los datos de entrada se
traducen en diferencias apreciables en la envolvente de fases, en especial
cerca del punto crítico de la mezcla, y por eso poder alternar entre conjuntos
de parámetros es útil para reproducir fielmente cada simulador de referencia.</p>
<p>Un detalle que ThermoPhase respeta cuidadosamente es que HYSYS emplea para
SRK un conjunto de factores acéntricos propio, distinto del que usa para
Peng-Robinson, mientras que las temperaturas y presiones críticas son idénticas
entre ambas. El programa enruta cada conjunto de factores acéntricos a la
ecuación que corresponde, de modo que el flash de SRK usa los factores
acéntricos de SRK y no los de Peng-Robinson.</p>
"""


# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 2 — Parámetros de la EOS
# ═════════════════════════════════════════════════════════════════════
S2_1 = """
<h2>2.1 Propiedades críticas</h2>
<p>El punto crítico de una sustancia es el par de temperatura y presión
(Tc, Pc) por encima del cual desaparece la distinción entre líquido y gas: por
más que se comprima el fluido, ya no condensa. Es la piedra angular de toda
ecuación de estado cúbica, porque los parámetros a y b se calibran justamente
para que la ecuación reproduzca ese punto de manera exacta.</p>
<p>Matemáticamente, en el punto crítico la isoterma presenta un punto de
inflexión con tangente horizontal en el diagrama presión-volumen. Es decir, la
primera y la segunda derivada de la presión respecto del volumen se anulan
simultáneamente:</p>
""" + _eq(r"\left(\frac{\partial P}{\partial V}\right)_{T} = 0 \qquad \left(\frac{\partial^{2} P}{\partial V^{2}}\right)_{T} = 0") + """
<p>Imponer estas dos condiciones a la ecuación de estado es lo que fija los
valores numéricos de Ω_a y Ω_b vistos en las secciones anteriores, y lo que
liga a_c y b directamente a Tc y Pc. En otras palabras, las propiedades
críticas no son un dato accesorio: son las que determinan por completo los
parámetros de la ecuación para cada sustancia.</p>
<p>El sentido físico de que ambas derivadas se anulen es que, en el punto
crítico, la isoterma se vuelve localmente plana: comprimir el fluido no cambia
su presión. Líquido y vapor han igualado su densidad y todas sus propiedades, y
se han vuelto indistinguibles. Por eso la campana de dos fases se cierra
exactamente en ese punto, que es también el vértice de la isoterma que aparece
en el ícono de la barra de herramientas del programa.</p>
"""

S2_2 = """
<h2>2.2 El factor acéntrico</h2>
<p>Dos sustancias pueden tener temperaturas y presiones críticas parecidas y,
sin embargo, comportarse de manera distinta, porque sus moléculas tienen formas
diferentes. El factor acéntrico ω, introducido por Pitzer, cuantifica cuánto se
aleja una molécula de ser una esfera perfecta. Una molécula esférica y simple
como el argón tiene un factor acéntrico cercano a cero, mientras que las
cadenas largas de hidrocarburos tienen valores crecientes.</p>
<p>Se define a partir de la presión de vapor de la sustancia evaluada a una
temperatura reducida de 0.7, comparada con su presión crítica:</p>
""" + _eq(r"\omega = -\log_{10}\!\left(\frac{P_{\mathrm{vap}}}{P_c}\right)_{T/T_c = 0.7} - 1") + """
<p>El valor 0.7 no es casual: a esa temperatura reducida, las sustancias
esféricas simples tienen una presión de vapor reducida de aproximadamente 0.1,
lo que hace que su factor acéntrico sea cero por construcción. Cualquier
desviación de ese comportamiento (moléculas más alargadas o complejas) produce
un factor acéntrico positivo. A modo de referencia, el metano tiene ω cercano a
0.011 y el nonano supera 0.44.</p>
<p>El factor acéntrico es el tercer parámetro que corrige el efecto de la forma
molecular, y entra en la ecuación de estado a través del coeficiente m de la
función α(T): las moléculas más acéntricas tienen una atracción que varía más
fuertemente con la temperatura. Sin este parámetro, todas las sustancias con
iguales Tc y Pc se comportarían de manera idéntica, lo cual contradice la
experiencia.</p>
"""

S2_3 = """
<h2>2.3 El coeficiente m y la función alfa de temperatura</h2>
<p>Como se anticipó, la dependencia de la atracción con la temperatura se
concentra en la función alfa de temperatura, α(T), y ésta depende de un
coeficiente de correlación m que a su vez es función del factor acéntrico. Cada
forma cúbica tiene su propia correlación, ajustada por sus autores para
reproducir las presiones de vapor de una serie de hidrocarburos.</p>
<p>Para Peng-Robinson:</p>
""" + _eq(r"m = 0.37464 + 1.54226\,\omega - 0.26992\,\omega^{2}") + """
<p>Para SRK:</p>
""" + _eq(r"m = 0.480 + 1.574\,\omega - 0.176\,\omega^{2}") + """
<p>Este coeficiente es, por lo tanto, el eslabón que conecta un dato
macroscópico y fácil de tabular (el factor acéntrico) con el comportamiento
microscópico del término de atracción. Un coeficiente m mayor implica una
función alfa que crece más rápido al enfriar, es decir, una atracción que se
refuerza más al bajar la temperatura, lo cual es propio de las moléculas más
pesadas y alargadas.</p>
"""

S2_4 = """
<h2>2.4 Reglas de mezclado</h2>
<p>Todo lo anterior describe un componente puro. Pero un fluido de yacimiento es
una mezcla de muchos componentes. Surge entonces la pregunta de qué valores de a
y de b usar para la mezcla, y la respuesta son las reglas de mezclado.</p>
<p>Para el covolumen, la regla es lineal, porque el volumen ocupado por las
moléculas de la mezcla es simplemente la suma de los volúmenes de cada
especie:</p>
""" + _eq(r"b_m = \sum_{i} z_i\, b_i") + """
<p>Para el término de atracción se emplea una regla cuadrática, que considera
las interacciones entre todos los pares de moléculas i y j, incluidos los pares
mixtos:</p>
""" + _eq(r"a_m = \sum_{i}\sum_{j} z_i\,z_j\,\sqrt{a_i\,a_j}\,\left(1 - k_{ij}\right)") + """
<p>La raíz del producto de a_i por a_j es la media geométrica, que estima la
atracción entre dos moléculas distintas a partir de las atracciones de cada una.
El sentido físico del factor (1 menos k_ij) es que esa media geométrica no es
exacta: la atracción real entre moléculas de especies diferentes puede ser algo
menor o mayor que el promedio, y el coeficiente k_ij corrige esa desviación. Un
k_ij positivo reduce la atracción cruzada, es decir, indica que las dos especies
se llevan peor de lo que sugeriría la media geométrica, situación típica entre
parejas químicamente dispares como el dióxido de carbono y un hidrocarburo.</p>
"""

S2_5 = """
<h2>2.5 Coeficientes de interacción binaria</h2>
<p>Los coeficientes de interacción binaria k_ij forman una matriz simétrica: el
coeficiente entre i y j es igual al que hay entre j e i, y el de un componente
consigo mismo es cero.</p>
""" + _eq(r"k_{ij} = k_{ji} \qquad k_{ii} = 0") + """
<p>Aunque suelen ser números pequeños, tienen un efecto desproporcionado sobre
la forma de la envolvente de fases, sobre todo en las cercanías del punto
crítico de la mezcla, donde pequeños cambios en la atracción cruzada desplazan
de manera notable las curvas de burbuja y de rocío. Su magnitud sigue un patrón
físico claro:</p>
<ul>
<li>Entre hidrocarburo e hidrocarburo, k_ij es prácticamente cero, porque son
moléculas químicamente similares que se mezclan casi de forma ideal.</li>
<li>Entre dióxido de carbono e hidrocarburo, k_ij ronda 0.08 a 0.12, reflejando
que el dióxido de carbono interactúa de manera apreciablemente distinta con las
cadenas de hidrocarburos.</li>
<li>Entre nitrógeno e hidrocarburo, los valores son intermedios, del orden de
0.03 a 0.08 según la pareja.</li>
</ul>
"""

S2_6 = """
<h2>2.6 Base de datos de los coeficientes de interacción binaria</h2>
<p>Cada una de las cuatro ecuaciones de estado del programa tiene su propia
matriz de coeficientes de interacción binaria. En otras palabras, los k_ij no
sólo dependen del simulador de referencia, sino también de la forma de la
ecuación, de modo que ThermoPhase maneja cuatro fuentes tabuladas, una por
variante:</p>
<ul>
<li>Peng-Robinson con parámetros HYSYS.</li>
<li>SRK con parámetros HYSYS.</li>
<li>Peng-Robinson con parámetros PVTsim.</li>
<li>SRK con parámetros PVTsim.</li>
</ul>
<p>Al seleccionar una ecuación de estado, el programa carga automáticamente la
matriz de coeficientes que le corresponde. Las matrices de HYSYS replican las
del simulador Aspen HYSYS, que ha sido el punto de comparación histórico del
proyecto; las de PVTsim se basan en la recopilación de Knapp y colaboradores y
en la convención de Calsep, empleada por PVTsim, que fija en cero los pares
hidrocarburo con hidrocarburo. Como principio, ThermoPhase no fabrica datos:
cuando una tabla autorizada no está disponible, el coeficiente se deja en cero
con respaldo documental en lugar de inventarlo.</p>
<h3>Correlación de Chueh-Prausnitz (calculada)</h3>
<p>Además de las cuatro matrices tabuladas, el programa ofrece una opción en la
que los coeficientes no se toman de una tabla sino que se calculan a partir de
los volúmenes críticos de cada par de componentes, mediante la correlación de
Chueh-Prausnitz. Esta correlación no depende de la ecuación de estado (la misma
matriz sirve para PR y para SRK):</p>
""" + _eq(r"1 - k_{ij} = \left[\frac{2\,\sqrt{\,V_{c,i}^{1/3}\;V_{c,j}^{1/3}}}{V_{c,i}^{1/3} + V_{c,j}^{1/3}}\right]^{\,n}") + """
<p>La idea física de esta correlación es que la incompatibilidad entre dos
moléculas depende sobre todo de la diferencia de tamaños, representada por sus
volúmenes críticos, y no tanto de su naturaleza química. Por eso reproduce muy
bien los pares de hidrocarburos de tamaños graduales, en los que el coeficiente
resulta casi idéntico al de HYSYS, pero difiere más en pares como nitrógeno con
metano, donde la química (y no sólo el tamaño) juega un papel importante.</p>
"""


# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 3 — El cálculo flash
# ═════════════════════════════════════════════════════════════════════
S3_1 = """
<h2>3.1 El problema del equilibrio de fases</h2>
<p>El cálculo flash responde la pregunta central de la termodinámica de fases:
dada una mezcla de composición global z a una presión y temperatura fijas, ¿en
cuánto vapor y cuánto líquido se separa, y cuál es la composición de cada
fase? Para plantearlo se definen las siguientes cantidades:</p>
<ul>
<li>z_i, la fracción molar del componente i en la alimentación (lo que entra).</li>
<li>y_i, la fracción molar de i en la fase vapor.</li>
<li>x_i, la fracción molar de i en la fase líquida.</li>
<li>V, la fracción de la mezcla total que resulta vapor, entre 0 y 1.</li>
</ul>
<p>La condición que gobierna todo el problema es el equilibrio termodinámico: en
el equilibrio, cada componente tiene la misma fugacidad en ambas fases.</p>
""" + _eq(r"f_i^{\,V} = f_i^{\,L}") + """
<p>La fugacidad se puede entender como la presión de escape efectiva de un
componente, es decir, una medida de sus ganas de abandonar la fase en la que se
encuentra. Si un componente tiene mayor fugacidad en el líquido que en el vapor,
migrará del líquido al vapor; el proceso continúa hasta que las fugacidades se
igualan y ya no hay ganancia en seguir migrando. Ese estado de equilibrio, en el
que las ganas de escapar se han igualado en ambas fases para cada componente, es
lo que el cálculo flash busca encontrar.</p>
"""

S3_2 = """
<h2>3.2 Fugacidad y coeficiente de fugacidad</h2>
<p>Trabajar con la fugacidad en términos absolutos es incómodo, por lo que se
usa el coeficiente de fugacidad φ_i, que compara la fugacidad real de un
componente con la que tendría en un gas ideal a la misma presión y
composición:</p>
""" + _eq(r"f_i = \phi_i\; y_i\; P") + """
<p>El coeficiente de fugacidad es precisamente lo que la ecuación de estado
permite calcular. Para las ecuaciones cúbicas tiene una forma cerrada que
depende de los grupos adimensionales A y B, de la raíz Z de la fase, de la
composición y de los coeficientes de interacción binaria. Para Peng-Robinson,
la expresión que ThermoPhase evalúa (de forma vectorizada para todos los componentes a la vez) es:</p>
""" + _eq(r"\ln\phi_i = \frac{b_i}{b_m}(Z-1) - \ln(Z-B) - \frac{A}{2\sqrt{2}\,B}\left(\frac{2\sum_j z_j a_{ij}}{a_m} - \frac{b_i}{b_m}\right)\ln\!\left[\frac{Z+(1+\sqrt{2})B}{Z+(1-\sqrt{2})B}\right]") + """
<p>Para SRK, como el término atractivo tiene otra forma, el coeficiente de
fugacidad cambia en su último término, que pasa a depender de ln[(Z+B)/Z] en
lugar del factor con raíz de dos:</p>
""" + _eq(r"\ln\phi_i = \frac{b_i}{b_m}(Z-1) - \ln(Z-B) - \frac{A}{B}\left(\frac{2\sum_j z_j a_{ij}}{a_m} - \frac{b_i}{b_m}\right)\ln\!\left(\frac{Z+B}{Z}\right)") + """
<p>En ambas expresiones, el primer término recoge el efecto del tamaño relativo
de la molécula (a través de la relación entre su covolumen y el de la mezcla),
el segundo proviene de la corrección por volumen excluido (la repulsión), y el
tercero condensa toda la contribución de la atracción y de las interacciones
cruzadas. La condición de equilibrio de fugacidades se escribe entonces en
términos de los coeficientes de fugacidad de cada fase:</p>
""" + _eq(r"\phi_i^{\,V}\, y_i\, P = \phi_i^{\,L}\, x_i\, P") + """
<p>Aquí se ve por qué la ecuación de estado es imprescindible: es la que traduce
presión, temperatura y composición en las ganas de escapar de cada componente en
cada fase. El grueso del trabajo de cómputo de un flash consiste en evaluar
estos coeficientes de fugacidad una y otra vez.</p>
"""

S3_3 = """
<h2>3.3 Constante de equilibrio</h2>
<p>De la igualdad de fugacidades surge de forma natural la constante de
equilibrio, o relación de reparto, que indica cuánto prefiere un componente la
fase vapor frente a la líquida:</p>
""" + _eq(r"K_i = \frac{y_i}{x_i} = \frac{\phi_i^{\,L}}{\phi_i^{\,V}}") + """
<p>Un valor de K_i mayor que 1 significa que el componente se concentra
preferentemente en el vapor: es un componente ligero y volátil, como el metano.
Un valor menor que 1 indica que el componente tiende a quedarse en el líquido:
es un componente pesado, como el nonano.</p>
<p>Conviene notar que los coeficientes de fugacidad dependen de las
composiciones x e y, que a su vez dependen de los K. El problema es, por lo
tanto, implícito: los K definen las composiciones y las composiciones redefinen
los K. Ésta es la razón por la cual el cálculo del equilibrio no es una fórmula
directa, sino un proceso iterativo.</p>
"""

S3_4 = """
<h2>3.4 Estimación inicial de las constantes de equilibrio</h2>
<p>Todo procedimiento iterativo necesita un punto de partida. Para los
coeficientes de reparto K_i, ThermoPhase emplea la correlación de Wilson, que
entrega una primera aproximación razonable usando únicamente las propiedades
críticas y el factor acéntrico de cada componente:</p>
""" + _eq(r"K_i = \frac{P_{c,i}}{P}\,\exp\!\left[\,5.373\,(1 + \omega_i)\left(1 - \frac{T_{c,i}}{T}\right)\right]") + """
<p>La correlación de Wilson no es exacta, pero coloca a cada componente del lado
correcto (los ligeros con K mayor que 1 y los pesados con K menor que 1) y
proporciona un arranque estable. En ThermoPhase, estos valores de Wilson sirven
como semilla del análisis de estabilidad, que es el paso que decide si hay una o
dos fases y que refina los coeficientes de reparto. Como se detalla en las
subsecciones siguientes, los coeficientes con los que finalmente arranca el
flash provienen de ese análisis.</p>
"""

S3_5 = """
<h2>3.5 La ecuación de Rachford-Rice</h2>
<p>Una vez que se sabe que la mezcla es bifásica, hace falta determinar cuánta
mezcla se vaporiza, es decir, el valor de V. Se parte del balance de materia
por componente, que reparte lo que entra entre las dos fases:</p>
""" + _eq(r"z_i = V\,y_i + (1 - V)\,x_i") + """
<p>Combinando este balance con la definición de los coeficientes de reparto
(y_i igual a K_i por x_i) y exigiendo que las fracciones molares de cada fase
sumen 1, se llega a la ecuación de Rachford-Rice, que es una única ecuación en
la incógnita V:</p>
""" + _eq(r"\sum_{i} \frac{z_i\,(K_i - 1)}{1 + V\,(K_i - 1)} = 0") + """
<p>Esta ecuación no es un método de flash por sí sola; es una herramienta
matemática que permite resolver V de forma eficiente dado un conjunto de K_i.
Tiene la ventaja de ser estrictamente monótona en el intervalo físico de V
(entre cero y uno), lo que garantiza una solución única y una convergencia
estable. ThermoPhase la resuelve numéricamente por el método de Newton acotado
al intervalo válido. Su sentido físico es simple contabilidad: todo lo que entra
en la alimentación debe repartirse exactamente entre el vapor y el líquido. El
algoritmo que la invoca, y que constituye el verdadero cálculo del equilibrio, se
describe en la subsección siguiente.</p>
"""

S3_6 = """
<h2>3.6 Análisis de estabilidad</h2>
<p>Antes de resolver el flash conviene saber si la mezcla realmente se separa en
dos fases o si permanece como una sola. De esto se encarga el análisis de
estabilidad, que en ThermoPhase reproduce el procedimiento de Michelsen
implementado y validado en la referencia del proyecto. La idea de fondo es la
del plano tangente a la energía de Gibbs: una fase es estable si ninguna fase
incipiente de otra composición tiene menor energía de Gibbs; si se encuentra una
composición de prueba que baja por debajo del plano tangente, la mezcla es
inestable y se separará.</p>
<p>El procedimiento concreto que sigue el programa parte de dos juegos de
coeficientes de reparto, ambos inicializados con la correlación de Wilson: uno
para ensayar una fase vapor incipiente (K^V) y otro para una fase líquida
incipiente (K^L). Con ellos se construyen las composiciones normalizadas de esas
fases de prueba:</p>
""" + _eq(r"Y_i^{V} = \frac{z_i\,K_i^{V}}{\sum_j z_j\,K_j^{V}} \qquad Y_i^{L} = \frac{z_i / K_i^{L}}{\sum_j z_j / K_j^{L}}") + """
<p>Para cada fase de prueba y para la alimentación se evalúan las fugacidades con
la ecuación de estado, seleccionando la raíz de vapor o de líquido según
corresponda. A partir de la comparación de esas fugacidades se actualizan los
coeficientes de reparto, con un esquema normalizado por las sumas de cada fase
incipiente:</p>
""" + _eq(r"S_V = \sum_i z_i\,K_i^{V} \qquad S_L = \sum_i \frac{z_i}{K_i^{L}}") + """
<p>La normalización por S_V y S_L evita que la búsqueda diverja: en un sistema
monofásico hace que los coeficientes converjan de manera controlada hacia la
solución trivial, en la que todos los K tienden a 1, en lugar de dispararse
hacia los límites numéricos. Al terminar la iteración, el programa decide la
estabilidad con dos criterios. Por un lado, si alguna de las sumas S_V o S_L
supera la unidad, existe una fase incipiente con menor energía de Gibbs y la
mezcla es inestable, es decir, bifásica. Por otro, para distinguir la solución
trivial de una genuina, se evalúa la suma de los logaritmos de los coeficientes
al cuadrado, considerando sólo los componentes presentes:</p>
""" + _eq(r"\sum_{i:\,z_i > 0} \left(\ln K_i\right)^{2} < \varepsilon \;\Rightarrow\; \text{solucion trivial}") + """
<p>El punto clave es qué coeficientes de reparto quedan para el flash. Cuando el
análisis concluye que la mezcla es inestable, los coeficientes que se pasan al
flash no son los de Wilson, sino el producto de los dos juegos refinados durante
la propia búsqueda de estabilidad:</p>
""" + _eq(r"K_i^{\text{flash}} = K_i^{V}\cdot K_i^{L}") + """
<p>De este modo el flash arranca desde una estimación mucho más cercana a la
solución. Si en cambio el análisis concluye que la mezcla es estable, el flash
arranca con los coeficientes de Wilson. En ambos casos, como se explica en la
subsección siguiente, el flash siempre se ejecuta a continuación.</p>
"""

S3_7 = """
<h2>3.7 El algoritmo completo del flash</h2>
<p>El método que ThermoPhase implementa para el cálculo del equilibrio
líquido-vapor es el de Muskat-McDowell, un esquema iterativo de sustitución
sucesiva que actualiza los coeficientes de reparto hasta que las fugacidades se
igualan en ambas fases. A diferencia de Rachford-Rice, que es únicamente una
ecuación para resolver V dados los K_i, el método de Muskat-McDowell es el
algoritmo completo que envuelve ese paso como una herramienta interna.</p>
<h3>Preparación de los coeficientes de reparto iniciales</h3>
<p>Antes de entrar al flash, se ejecuta el análisis de estabilidad descrito en la
subsección anterior. Si la mezcla resulta inestable, el flash arrancará con el
producto de los dos juegos de coeficientes refinados en la estabilidad (K^V por
K^L), que es una estimación mucho más cercana a la solución que la de Wilson.
Si la mezcla resulta estable, el flash arrancará con los coeficientes de Wilson.
En ambos casos el flash siempre se ejecuta; la clasificación final en una o dos
fases la produce el propio algoritmo.</p>
<h3>El bucle de Muskat-McDowell</h3>
<p>Con los coeficientes de reparto del paso anterior, el algoritmo entra en un
lazo iterativo. En cada iteración se evalúan primero dos sumatorios que actúan
como criterio de fase:</p>
""" + _eq(r"\sum_i K_i\,z_i \leq 1 \;\Rightarrow\; \text{liquido} \qquad \sum_i \frac{z_i}{K_i} \leq 1 \;\Rightarrow\; \text{vapor}") + """
<p>Si el primer sumatorio no supera la unidad, toda la mezcla es líquida y se
asigna x_i = z_i; si el segundo no supera la unidad, toda la mezcla es vapor y
se asigna y_i = z_i. Cuando ninguno de los dos criterios se cumple, la mezcla es
bifásica: en ese caso se invoca la ecuación de Rachford-Rice para resolver la
fracción vaporizada V, y con ella se calculan las composiciones de cada fase:</p>
""" + _eq(r"x_i = \frac{z_i}{1 + V\,(K_i - 1)} \qquad y_i = K_i\,x_i") + """
<p>Con las composiciones de cada fase se evalúan los coeficientes de fugacidad
mediante la ecuación de estado, resolviendo el cúbico en Z y tomando la raíz que
corresponde a cada fase. Cuando una de las fases es evanescente (composición
prácticamente cero), su coeficiente de fugacidad se fija en 1 para todos los
componentes: esto evita que los coeficientes de reparto colapsen a la solución
trivial y deja que la clasificación de fase dependa únicamente de los sumatorios
anteriores, tal como lo hace la referencia del proyecto.</p>
<p>A partir de las fugacidades de cada fase se actualizan los coeficientes de
reparto como el cociente entre el coeficiente de fugacidad del líquido y el del
vapor:</p>
""" + _eq(r"K_i = \frac{\phi_i^{\,L}}{\phi_i^{\,V}}") + """
<p>El lazo se repite hasta que las fugacidades de cada componente coinciden en
ambas fases dentro de la tolerancia. Cuando converge, se tiene la solución del
equilibrio: la fracción vaporizada V, las composiciones x e y de cada fase y el
número de fases presentes. En el fondo, el método de Muskat-McDowell es un
proceso que ajusta iterativamente el reparto de los componentes hasta que cada
uno tiene las mismas ganas de escapar en el líquido y en el vapor, usando la
ecuación de estado para calcular fugacidades y la ecuación de Rachford-Rice
como herramienta interna para resolver el balance de materia en los casos
bifásicos.</p>
"""



# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 4 — Envolvente de fases
# ═════════════════════════════════════════════════════════════════════
S4_1 = """
<h2>4.1 Envolvente de fases</h2>
<p>La envolvente de fases es la curva que delimita, en el plano presión-temperatura,
la región donde una mezcla de composición fija coexiste como líquido y como vapor
simultáneamente. Dentro de esa curva el sistema es bifásico; fuera de ella, a la
izquierda o debajo, es monofásico líquido o vapor según el caso.</p>
<p>La curva tiene dos ramas que parten del mismo punto a baja presión y se cierran
en el punto crítico de la mezcla:</p>
<ul>
<li>La <b>curva de burbuja</b> representa las condiciones en las que el líquido
está a punto de comenzar a vaporizarse: la fracción de vapor es prácticamente
cero y una burbuja incipiente acaba de aparecer.</li>
<li>La <b>curva de rocío</b> representa las condiciones en las que el vapor está
a punto de comenzar a condensar: la fracción de líquido es prácticamente cero y
una gota incipiente acaba de aparecer.</li>
</ul>
<p>En ambos casos la condición matemática es la misma que la del flash monofásico
fronterizo:</p>
""" + _eq(r"\text{burbuja:}\quad \sum_i K_i\,z_i = 1 \qquad \text{rocio:}\quad \sum_i \frac{z_i}{K_i} = 1") + """
<p>La envolvente es uno de los resultados más valiosos de la termodinámica de
mezclas porque permite conocer, de un solo vistazo, si una mezcla producida en
un yacimiento estará en una o dos fases en cualquier punto del sistema de
producción, desde la presión del yacimiento hasta las condiciones de la
superficie, o en cualquier equipo de proceso.</p>
"""

S4_2 = """
<h2>4.2 El método de Ziervogel (GoalSeek con continuación de curva)</h2>
<p>El método que ThermoPhase emplea como base para trazar la envolvente sigue el
esquema de Ziervogel. La idea central es que cada punto de la curva de burbuja
o de rocío se obtiene resolviendo un GoalSeek de una sola variable, alternando
entre temperatura y presión como variable de búsqueda, mientras la otra se
impone desde el punto anterior.</p>
<h3>La condición de saturación y la composición fija</h3>
<p>En un punto de burbuja, el líquido tiene la composición global de la mezcla
(x_i = z_i) y el vapor incipiente tiene una composición que hay que calcular.
La condición de saturación exige que las fracciones molares del vapor sumen la
unidad, lo que equivale a la ecuación:</p>
""" + _eq(r"F_{\text{burbuja}} = \sum_i K_i\,z_i - 1 = 0") + """
<p>En un punto de rocío el rol se invierte: el vapor tiene la composición global
(y_i = z_i) y el líquido incipiente es el que se calcula:</p>
""" + _eq(r"F_{\text{rocio}} = \sum_i \frac{z_i}{K_i} - 1 = 0") + """
<p>El detalle clave de la implementación es que la composición de la fase
incipiente se mantiene <b>fija</b> durante cada GoalSeek: solo la variable de
búsqueda (temperatura o presión) se mueve, mientras la composición de la fase
incipiente permanece constante. Solo después de que el GoalSeek
converge se actualiza la composición de la fase incipiente con los K_i
recién calculados, y el proceso se repite hasta que esa composición ya no
cambia entre una iteración y la siguiente.</p>
<h3>Inicio de la curva con la correlación de Wilson</h3>
<p>Para arrancar el trazado, el programa necesita un primer punto de saturación.
Fija la presión en un valor bajo (10 psia) y busca la temperatura de burbuja
inicial resolviendo por Newton-Raphson la ecuación de Wilson, que es una
aproximación analítica de los K_i válida lejos del punto crítico:</p>
""" + _eq(r"\sum_i z_i\,K_i^{\text{Wilson}}(T,P) = 1 \qquad K_i^{\text{Wilson}} = \frac{P_{c,i}}{P}\,\exp\!\left[5.373\,(1+\omega_i)\left(1-\frac{T_{c,i}}{T}\right)\right]") + """
<p>Con esa temperatura inicial se evalúan los K_i de Wilson, se construye la
composición de la fase incipiente (vapor para burbuja, líquido para rocío) y
se ejecuta el primer GoalSeek, que refina la temperatura usando ya los
coeficientes de fugacidad de la ecuación de estado en lugar de la aproximación
de Wilson.</p>
<h3>Continuación de la curva punto a punto</h3>
<p>Con el primer punto convergido, el algoritmo avanza a lo largo de la curva
usando un esquema de predictor simple: da un pequeño paso en temperatura o en
presión (el que resulte más adecuado según la pendiente local de la curva) y
usa el resultado anterior como punto de partida para el GoalSeek del siguiente.
La elección de qué variable mover en cada tramo se basa en el parámetro β, que
mide la inclinación local de la curva en escala logarítmica:</p>
""" + _eq(r"\beta = \left|\frac{\Delta\ln P}{\Delta\ln T}\right|") + """
<p>Cuando β es grande (la curva es casi vertical, la presión cambia mucho con
poca variación de temperatura), se avanza fijando temperatura y buscando
presión; cuando β es pequeño (la curva es casi horizontal), se avanza fijando
presión y buscando temperatura. Este ajuste automático permite seguir la curva
de manera estable en todas las zonas, incluidas las regiones de alta pendiente
cerca del cricondenterm (temperatura máxima) y la cricondenbar (presión máxima).</p>
<h3>Cercanía al punto crítico y cambio de solucionador</h3>
<p>A medida que la curva se aproxima al punto crítico de la mezcla, los K_i
tienden a 1 y las fases se vuelven casi indistinguibles. En esa zona el
GoalSeek con el método secante (que usa derivadas) puede diverger porque la
función se vuelve muy plana. Para detectar esta situación el programa evalúa en
cada punto el criterio de Gallardo:</p>
""" + _eq(r"\varpi = |Z_L - Z_V|") + """
<p>Cuando ϖ cae por debajo de 0.2, las fases son casi idénticas y el programa
cambia automáticamente el solucionador del GoalSeek: abandona el método de la
secante y pasa a <b>bisección</b>, que no usa derivadas y nunca diverge,
aunque converge más lentamente. Cuando ϖ vuelve a crecer, se retoma la secante.
El trazado se detiene cuando todos los K_i se acercan suficientemente a 1,
señal de que se ha alcanzado el punto crítico.</p>
"""

S4_3 = """
<h2>4.3 El método de Michelsen (continuación por pseudo-longitud de arco)</h2>
<p>El método de Michelsen (1980) es un algoritmo de continuación mucho más
sofisticado que el GoalSeek punto a punto. En lugar de resolver una ecuación
escalar en una variable, plantea un sistema de ecuaciones no lineales que incluye
todas las condiciones de equilibrio simultáneamente, junto con una ecuación
adicional de restricción de arco que fija cuánto avanza el trazado en cada paso.
ThermoPhase lo usa como complemento cuando el método de Ziervogel no logra cerrar
la envolvente en la zona del punto crítico.</p>
<h3>Variables y sistema de ecuaciones</h3>
<p>El método trabaja en el espacio logarítmico de las variables de estado. Para
una mezcla con m componentes presentes (z_i mayor que cero), el vector de
incógnitas en cada punto de la curva es:</p>
""" + _eq(r"X = \left(\ln K_1,\;\ldots,\;\ln K_m,\;\ln T,\;\ln P\right)") + """
<p>El sistema de ecuaciones que debe satisfacerse en cada punto de la envolvente
consta de m ecuaciones de igualdad de fugacidades (una por componente presente),
una ecuación de saturación y una restricción de pseudo-longitud de arco:</p>
""" + _eq(r"g_i = \ln K_i + \ln\phi_i^V - \ln\phi_i^L = 0 \quad (i = 1\ldots m)") + """
""" + _eq(r"g_{m+1} = \sum_i K_i\,z_i - 1 = 0") + """
""" + _eq(r"g_{m+2} = t\cdot(X - X_{\text{ref}}) - \Delta s = 0") + """
<p>La última ecuación es la restricción de arco: el vector tangente t (calculado
en el punto anterior) proyectado sobre el desplazamiento desde el punto de
referencia debe ser igual al tamaño de paso Δs. Esto garantiza que el trazado
avance una distancia controlada a lo largo de la curva, sin que el algoritmo
pueda retroceder ni saltar a una solución distante.</p>
<h3>Newton-Raphson con Jacobiano analítico</h3>
<p>El sistema anterior se resuelve con Newton-Raphson multivariable. La clave de
la eficiencia y la robustez del método está en que el Jacobiano (la matriz de
derivadas parciales del sistema respecto a las incógnitas) se calcula de forma
analítica a partir de las derivadas de los coeficientes de fugacidad respecto a
temperatura, presión y composición. Eso hace que cada iteración de Newton
converja cuadráticamente cuando está cerca de la solución.</p>
<h3>El vector tangente y la predicción del siguiente punto</h3>
<p>El vector tangente al arco en cada punto convergido se obtiene como el vector
nulo del Jacobiano del sistema (sin la restricción de arco), calculado por
descomposición en valores singulares (SVD). Ese vector tangente actúa como
predictor del siguiente punto: la solución del paso anterior, desplazada en la
dirección del tangente una distancia Δs, sirve como punto de partida para el
Newton-Raphson del paso siguiente. La magnitud de Δs se ajusta automáticamente:
se agranda cuando Newton converge en pocas iteraciones (zona suave de la curva)
y se reduce cuando le cuesta más (zona compleja, cerca del crítico).</p>
<h3>Estrategia bidireccional para la cola de rocío</h3>
<p>Un problema frecuente en gases livianos es que la rama de rocío a bajas
presiones forma una cola larga y con pendiente pronunciada que el trazado
unidireccional puede perder. ThermoPhase lo resuelve con una estrategia
bidireccional: traza la envolvente desde un punto de burbuja de baja presión
en sentido ascendente, rodea el punto crítico y desciende por la rama de rocío
superior; luego arranca un segundo trazado desde un punto de rocío de baja
presión en sentido ascendente hasta conectarse con el primero. Los dos tramos
se combinan para formar la envolvente completa, incluida la cola inferior de
rocío que el trazado simple habría omitido.</p>
<h3>Subespaciado activo</h3>
<p>Para mejorar la eficiencia, el sistema de ecuaciones se construye únicamente
con los componentes que tienen fracción molar positiva (z_i mayor que cero).
Esto reduce el Jacobiano de (NC+2) filas y columnas a (m+2), donde m es el
número de componentes presentes, lo que es especialmente ventajoso en mezclas de
producción donde varios componentes de la base de datos tienen fracción nula.</p>
"""

S4_4 = """
<h2>4.4 Flujo de cálculo: Ziervogel con fallback a Michelsen</h2>
<p>Cuando se solicita el trazado de la envolvente completa, ThermoPhase sigue
un flujo de decisión automático que combina los dos métodos para obtener siempre
la mejor envolvente posible con el menor tiempo de cómputo:</p>
<ol>
<li>Se trazan las curvas de burbuja y de rocío por el método de Ziervogel,
que es rápido y robusto para la gran mayoría de mezclas.</li>
<li>Se mide el hueco que queda entre las últimas puntas de las dos curvas
(la distancia geométrica en el plano P-T entre el último punto de burbuja y el
último punto de rocío). Si ese hueco es menor que la tolerancia de cierre
(15 unidades en el plano adimensional), Ziervogel ha cerrado bien y la
envolvente se devuelve directamente.</li>
<li>Si el hueco es mayor, Michelsen entra como complemento: traza el arco del
ápice que Ziervogel no pudo cerrar, extrae de él el tramo comprendido entre
las dos puntas de Ziervogel, lo divide por la cricondenbar (el punto de máxima
presión del arco) en lado-burbuja y lado-rocío, y empalma ese tramo con los
extremos de Ziervogel para completar la envolvente.</li>
</ol>
<p>Esta estrategia combina lo mejor de ambos métodos: la fidelidad al modelo de
referencia de Ziervogel y la robustez en la zona crítica de Michelsen. En la
gran mayoría de las mezclas típicas de producción, Ziervogel cierra por sí solo
y Michelsen no llega a ejecutarse.</p>
<h3>Caso especial: mezclas casi azeotrópicas</h3>
<p>Cuando todos los componentes presentes tienen temperaturas críticas muy
similares (razón Tc_max/Tc_min menor que 1.10, como ocurre en mezclas de CO2
con etano o de isopentano con pentano normal), la envolvente es muy estrecha y
los coeficientes de interacción binaria cruzados dificultan la convergencia de
Ziervogel. En ese caso el programa anula internamente los coeficientes k_ij del
par casi ideal, ejecuta el trazado con k_ij = 0 (que converge con facilidad),
y restaura los k_ij originales en el resultado. Los puntos (P, T) trazados con
k_ij = 0 son prácticamente idénticos a los que se obtendrían con los k_ij
originales, porque para pares casi ideales esos coeficientes son ya muy
cercanos a cero.</p>
"""

S4_5 = """
<h2>4.5 Punto crítico y líneas de calidad</h2>
<p>Además de las curvas de burbuja y de rocío, ThermoPhase calcula y muestra
sobre la envolvente información adicional que enriquece su interpretación.</p>
<h3>Punto crítico de la mezcla</h3>
<p>El punto crítico es el vértice donde las dos ramas se unen. En él las fases
líquida y vapor se vuelven idénticas: sus densidades, composiciones y todas sus
propiedades coinciden. Matemáticamente corresponde al límite en el que todos los
coeficientes de reparto K_i tienden simultáneamente a 1. El programa lo
identifica como el punto de la envolvente donde se cumple el criterio:</p>
""" + _eq(r"\sum_i (K_i - 1)^2 < \varepsilon_{\text{crit}}") + """
<h3>Cricondenterm y cricondenbar</h3>
<p>Dos puntos especiales de la envolvente tienen nombre propio. La
<b>cricondenterm</b> es la temperatura máxima de la envolvente: por encima de
ella, la mezcla no puede condensar a ninguna presión. La <b>cricondenbar</b> es
la presión máxima de la envolvente: por encima de ella no puede existir una
mezcla bifásica a ninguna temperatura. Ambos puntos se identifican
automáticamente como los extremos de la curva en cada coordenada.</p>
<h3>Líneas de calidad</h3>
<p>Las líneas de calidad son curvas interiores de la envolvente que unen los
puntos con la misma fracción de vapor (la calidad del vapor, Q). La línea Q = 0
es la curva de burbuja y la línea Q = 1 es la de rocío; las intermedias (Q =
0.1, 0.2, ..., 0.9) muestran cómo cambia la proporción de vapor dentro de la
región bifásica. Para calcular cada punto interior de una línea de calidad, el
programa ejecuta un flash isotérmico a la fracción de vapor deseada,
determinando las condiciones de presión y composición de cada fase a esa calidad
fija sobre la isoterma correspondiente.</p>
"""



# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 5 — Identificación de fase monofásica
# ═════════════════════════════════════════════════════════════════════
S5_1 = """
<h2>5.1 El problema de la identificación de fase</h2>
<p>Cuando el cálculo flash converge a una sola fase, la ecuación de estado
produce un único factor de compresibilidad Z. A partir de ese resultado es
necesario determinar si el fluido monofásico tiene carácter líquido o
carácter vapor, porque los modelos de densidad, viscosidad y conductividad
térmica aplican correlaciones distintas según la fase.</p>
<p>Esta determinación es directa cuando el fluido está claramente fuera de
la envolvente de fases: un gas a baja presión tiene Z cercano a 1 y baja
densidad; un líquido comprimido tiene Z pequeño y alta densidad. La
dificultad aparece en la región densa, donde la presión supera la
cricondenbar de la mezcla y el fluido no puede existir como dos fases a
ninguna temperatura. En esa región el fluido es termodinámicamente único,
pero puede tener comportamiento más cercano al líquido o al vapor, y el
programa necesita decidir qué conjunto de modelos de propiedades lo
representa mejor.</p>
<p>ThermoPhase aplica un algoritmo de tres criterios en cascada para las
variantes PR y SRK (y sus homólogas con parámetros PVTsim). Los criterios
se evalúan en orden de prioridad: el primero se basa en los parámetros de
la ecuación de estado, el segundo en la compresibilidad isotérmica, y el
tercero en la composición de la mezcla.</p>
"""

S5_2 = """
<h2>5.2 Compresibilidad isotérmica</h2>
<p>La compresibilidad isotérmica mide la variación relativa del volumen
molar con la presión a temperatura constante:</p>
""" + _eq(r"\kappa = -\frac{1}{V}\left(\frac{\partial V}{\partial P}\right)_T") + """
<p>Para el gas ideal κ = 1/P. Para trabajar con una magnitud adimensional
independiente de las unidades de presión se define el factor de
compresibilidad isotérmica β:</p>
""" + _eq(r"\beta = P\,\kappa = -\frac{P}{V}\left(\frac{\partial V}{\partial P}\right)_T") + """
<p>Para el gas ideal β = 1; para un líquido β es mucho menor que 1. El
umbral β = 0.75 separa estados con comportamiento predominantemente gaseoso
de estados con comportamiento líquido.</p>
<h3>Cálculo analítico</h3>
<p>ThermoPhase calcula β mediante la derivada analítica de la ecuación de
estado. Para Peng-Robinson:</p>
""" + _eq(r"\left(\frac{\partial P}{\partial V}\right)_T^{PR} = -\frac{RT}{(V-b)^2} + \frac{2\,a_m(V+b)}{(V^2+2bV-b^2)^2}") + """
<p>Para Soave-Redlich-Kwong:</p>
""" + _eq(r"\left(\frac{\partial P}{\partial V}\right)_T^{SRK} = -\frac{RT}{(V-b)^2} + \frac{a_m(2V+b)}{V^2(V+b)^2}") + """
<p>La compresibilidad adimensional resulta:</p>
""" + _eq(r"\beta = -\frac{P}{V\,(\partial P/\partial V)_T}") + """
<p>Esta expresión es algebraicamente equivalente a la forma cerrada en
función de A = aₘP/(RT)² y B = bₘP/(RT):</p>
""" + _eq(r"\beta = \frac{1}{P}\left(1 - \frac{2AB + zB + 2B^2z - Az}{z\,(3z^2-2z+A-B-B^2)}\right)") + """
<p>donde z es el factor de compresibilidad de la mezcla. La diferencia
numérica entre ambas formas es del orden de 10⁻¹⁶, confirmando que son
la misma expresión.</p>
"""

S5_3 = """
<h2>5.3 Criterio de la relación A/B</h2>
<p>A presiones superiores a la cricondenbar de la mezcla, el factor Z
permanece por encima de 0.75 en todo el rango de temperatura y los criterios
de compresibilidad y composición no producen ninguna frontera. Sin embargo,
el fluido puede ser un líquido comprimido si su temperatura está por debajo
de un valor característico que no depende de la presión: en el plano P-T
esta frontera es una línea vertical.</p>
<p>La cantidad que determina esa línea es la razón de parámetros
adimensionales de la EOS:</p>
""" + _eq(r"\frac{A}{B} = \frac{a_m P/(RT)^2}{b_m P/(RT)} = \frac{a_m}{b_m R T}") + """
<p>El factor P se cancela en la razón, lo que explica directamente que la
frontera sea independiente de la presión. La transición ocurre cuando A/B
iguala la razón de las constantes universales de la ecuación de estado,
Ω_a/Ω_b:</p>
""" + _eq(r"\frac{A}{B} = \frac{\Omega_a}{\Omega_b} \quad\Longrightarrow\quad T_{\text{frontera}} = \frac{a_m(T)}{b_m\,R\,(\Omega_a/\Omega_b)}") + """
<p>Cuando A/B supera el umbral Ω_a/Ω_b, el término atractivo de la mezcla
domina sobre la energía cinética y el fluido tiene carácter líquido; por
debajo del umbral el término repulsivo prevalece y el fluido puede ser
vapor. Los valores para cada EOS son:</p>
""" + _eq(r"\left.\frac{\Omega_a}{\Omega_b}\right|_{PR} = \frac{0.45724}{0.07780} \approx 5.877") + """
""" + _eq(r"\left.\frac{\Omega_a}{\Omega_b}\right|_{SRK} = \frac{0.42748}{0.08664} \approx 4.934") + """
<p>Estos valores son consecuencia directa de las constantes de Peng y
Robinson (1976) y de Soave (1972); no son parámetros ajustados a datos
experimentales.</p>
"""

S5_4 = """
<h2>5.4 Algoritmo completo</h2>
<p>Los tres criterios se evalúan en cascada. En cuanto uno produce una
clasificación definitiva, los restantes no se evalúan.</p>
<ol>
<li><b>Criterio A/B.</b> Si A/B = aₘ/(bₘRT) supera Ω_a/Ω_b de la EOS
activa, el fluido se clasifica como <b>líquido</b> comprimido. Esta
condición cubre la región de alta presión sin necesidad del punto
crítico de la mezcla.</li>
<li><b>Compresibilidad isotérmica.</b> Si Z &gt; 0.3 y β &gt; 0.75
simultáneamente, el fluido se clasifica como <b>vapor</b>. La condición
Z &gt; 0.3 descarta líquidos muy comprimidos donde β puede ser elevado.</li>
<li><b>Composición de ligeros.</b> Si Z &gt; 0.75 y la suma de fracciones
molares de los compuestos con punto normal de ebullición menor a 230 K
supera la de los pesados, el fluido se clasifica como <b>vapor</b>; en
caso contrario como <b>líquido</b>.</li>
</ol>
<p>El criterio β tiene prioridad sobre el criterio A/B porque β &gt; 0.75
es condición suficiente de comportamiento gaseoso incluso a alta presión
(por ejemplo, cerca del punto crítico de la mezcla). El criterio A/B
tiene prioridad sobre la regla de composición porque sin esa compuerta,
en la región densa donde Z permanece por encima de 0.75, la regla de
composición devolvería vapor en todo el rango de temperatura.</p>
<p>Los compuestos con NBP &lt; 230 K en el sistema de ThermoPhase son
N₂ (77 K), metano (111 K), etano (185 K) y CO₂ (195 K). El propano
(NBP ≈ 231 K) y los restantes quedan clasificados como pesados.</p>
"""

S5_5 = """
<h2>5.5 Variante con parámetros PVTsim</h2>
<p>Las variantes PR_PVT y SRK_PVT aplican el mismo algoritmo de
identificación. Las constantes Ω_a/Ω_b son idénticas porque la forma
cúbica de las EOS no varía entre bases de datos.</p>
<p>Los valores de aₘ y bₘ sí dependen de los parámetros de componente.
PVTsim sigue las tablas de Pedersen y Christensen (2007), que para los
componentes puros ligeros difieren ligeramente de las propiedades de la
base de datos de HYSYS, principalmente en Tc y ω del metano y el etano.
Esas diferencias desplazan la temperatura de frontera en la misma magnitud
que el error en los parámetros de componente.</p>
<h3>Referencias</h3>
<p>Peng, D.Y. y Robinson, D.B. (1976). A Two-Constant Equation of State.
<em>Industrial and Engineering Chemistry Fundamentals</em>, 15(1), 59-64.</p>
<p>Soave, G. (1972). Equilibrium constants from a modified Redlich-Kwong
equation of state. <em>Chemical Engineering Science</em>, 27(6), 1197-1203.</p>
<p>Pedersen, K.S. y Christensen, P.L. (2007). <em>Phase Behavior of
Petroleum Reservoir Fluids</em>. CRC Press.</p>
"""



S6_1 = """
<h2>6.1 Densidad de líquido y vapor</h2>
<p>La densidad es una de las propiedades derivadas más utilizadas en el
diseño de procesos: interviene en el dimensionamiento de tuberías y
recipientes, en el cálculo de la caída de presión y en la medición de
inventarios. Una vez resuelto el equilibrio y conocido el factor de
compresibilidad de cada fase, la densidad puede obtenerse directamente de
la ecuación de estado; sin embargo, las ecuaciones cúbicas predicen el
volumen del líquido con un error apreciable, típicamente entre 5 y 15 por
ciento, mientras que reproducen el volumen del vapor con buena exactitud.</p>
<p>Por esta razón el programa ofrece dos rutas de cálculo de densidad. La
fase vapor se evalúa siempre con la ecuación de estado. Para la fase líquida
el usuario puede elegir entre la densidad de la propia ecuación de estado o
el método de estados correspondientes COSTALD, que fue desarrollado
específicamente para densidades de líquido y alcanza errores inferiores al
uno por ciento en el rango de hidrocarburos. Adicionalmente, cuando se usa
la densidad de la ecuación de estado puede aplicarse la corrección de
volumen de Peneloux, que mejora la densidad de líquido mediante un traslado
del volumen molar.</p>
<p>El programa aplica la ruta seleccionada de forma consistente en todos
los puntos donde reporta densidad: el resultado del flash, la pestaña de
propiedades, la pestaña de saturación y el mapa de densidad comparten la
misma función de cálculo, de modo que un mismo estado siempre produce el
mismo valor de densidad y de factor de compresibilidad.</p>
"""

S6_2 = """
<h2>6.2 Densidad por la ecuación de estado</h2>
<p>La ruta más directa obtiene el volumen molar del factor de
compresibilidad de la fase. Resuelto el equilibrio, la ecuación cúbica
entrega el factor Z de cada fase; el volumen molar se despeja de la
definición del factor de compresibilidad:</p>
""" + _eq(r"V = \frac{Z\,R\,T}{P}") + """
<p>y la densidad másica se obtiene dividiendo el peso molecular de la fase
entre el volumen molar:</p>
""" + _eq(r"\rho = \frac{M}{V} = \frac{M\,P}{Z\,R\,T}") + """
<p>donde M es el peso molecular de la mezcla en la fase considerada,
calculado como la suma de las fracciones molares por los pesos moleculares
de cada componente. Esta ruta es la que el programa usa siempre para la
fase vapor y la que emplea para la fase líquida cuando el usuario
selecciona el método de la ecuación de estado.</p>
<p>El motor interno opera en unidades de campo, con la presión en psia, la
temperatura en grados Rankine y la constante universal de los gases igual a
10.7316 psi·ft³/(lbmol·°R). El volumen molar resulta en ft³/lbmol y la
densidad en lb/ft³; la conversión al sistema de unidades activo se aplica en
la capa de presentación.</p>
"""

S6_3 = """
<h2>6.3 El método COSTALD</h2>
<p>El método de estados correspondientes para densidad de líquido
(Corresponding States Liquid Density) predice el volumen del líquido a
partir de la temperatura reducida y de un parámetro característico de cada
componente. Fue formulado por Hankinson y Thomson y adoptado como norma por
el American Petroleum Institute. El programa lo utiliza para la densidad de
la fase líquida cuando el usuario elige este método.</p>
<p>Cada componente aporta dos parámetros propios: el volumen característico
V*, que tiene unidades de volumen molar, y un factor acéntrico específico
del método. El cálculo se organiza en cuatro etapas: primero se combinan los
parámetros de los componentes en parámetros de mezcla; después se evalúa el
volumen del líquido saturado; luego se estima la presión de saturación de la
mezcla; y finalmente se corrige el volumen por el efecto de la presión para
obtener el líquido comprimido.</p>
<h3>Parámetros de mezcla</h3>
<p>El volumen característico de la mezcla combina los volúmenes de los
componentes mediante una regla de tercios que pondera la contribución lineal
y las contribuciones de las potencias dos tercios y un tercio:</p>
""" + _eq(r"V^*_m = \frac{1}{4}\left[\sum_i x_i V^*_i + 3\left(\sum_i x_i {V^*_i}^{2/3}\right)\left(\sum_i x_i {V^*_i}^{1/3}\right)\right]") + """
<p>La temperatura pseudocrítica de la mezcla se obtiene de una doble suma
sobre todos los pares de componentes, ponderada por el producto de los
volúmenes característicos y las temperaturas críticas:</p>
""" + _eq(r"T_{cm} = \frac{1}{V^*_m}\sum_i\sum_j x_i x_j \sqrt{V^*_i T_{ci} V^*_j T_{cj}}") + """
<p>El factor acéntrico de la mezcla es el promedio molar de los factores
acéntricos de los componentes:</p>
""" + _eq(r"\omega_m = \sum_i x_i\,\omega_i") + """
<p>La presión pseudocrítica de la mezcla se deriva de un factor de
compresibilidad crítico que depende del factor acéntrico:</p>
""" + _eq(r"Z_{cm} = 0.291 - 0.080\,\omega_m \qquad P_{cm} = \frac{Z_{cm}\,R\,T_{cm}}{V^*_m}") + """
"""

S6_4 = """
<h2>6.4 Volumen del líquido saturado</h2>
<p>El volumen del líquido saturado se expresa como el producto del volumen
característico de la mezcla por una función de volumen reducido, corregida
por una función de desviación que escala con el factor acéntrico:</p>
""" + _eq(r"V_s = V^*_m\,V^{(0)}_R\left(1 - \omega_m\,V^{(\delta)}_R\right)") + """
<p>La función de volumen reducido de referencia depende únicamente de la
temperatura reducida a través de la variable auxiliar τ = 1 − T<sub>r</sub>,
y es válida en el intervalo 0.25 &lt; T<sub>r</sub> &lt; 0.95:</p>
""" + _eq(r"V^{(0)}_R = 1 - 1.52816\,\tau^{1/3} + 1.43907\,\tau^{2/3} - 0.81446\,\tau + 0.190454\,\tau^{4/3}") + """
<p>La función de desviación introduce la dependencia con el factor
acéntrico y se expresa como un cociente de polinomios en la temperatura
reducida:</p>
""" + _eq(r"V^{(\delta)}_R = \frac{-0.296123 + 0.386914\,T_r - 0.0427258\,T_r^2 - 0.0480645\,T_r^3}{T_r - 1.00001}") + """
<p>El término constante 1.00001 en el denominador desplaza ligeramente la
singularidad fuera del punto crítico para evitar la división por cero en
T<sub>r</sub> = 1. La densidad del líquido saturado es el peso molecular
dividido entre el volumen saturado.</p>
"""

S6_5 = """
<h2>6.5 Presión de saturación de la mezcla</h2>
<p>La corrección por presión requiere conocer la presión de saturación de
la mezcla a la temperatura de trabajo. Se emplea la ecuación de vapor de
Riedel en la formulación de Hankinson, Estes y Coker, que expresa la presión
de saturación reducida como suma de un término de referencia y un término
proporcional al factor acéntrico:</p>
""" + _eq(r"\log_{10} P_{Rs} = P^{(0)}_R + \omega_m\,P^{(1)}_R") + """
<p>Los dos términos se construyen a partir de dos funciones auxiliares de la
temperatura reducida:</p>
""" + _eq(r"F = 35.0 - \frac{36.0}{T_r} - 96.736\,\log_{10}T_r + T_r^{6}") + """
""" + _eq(r"G = \log_{10}T_r + 0.03721754\,F") + """
""" + _eq(r"P^{(0)}_R = 5.8031817\,\log_{10}T_r + 0.07608141\,F \qquad P^{(1)}_R = 4.86601\,G") + """
<p>La presión de saturación dimensional resulta del producto de la presión
reducida por la presión pseudocrítica de la mezcla:</p>
""" + _eq(r"P_s = P_{Rs}\,P_{cm}") + """
"""

S6_6 = """
<h2>6.6 Corrección por presión del líquido comprimido</h2>
<p>El volumen saturado corresponde al líquido en equilibrio con su vapor. A
presiones mayores que la de saturación el líquido se comprime, y su volumen
disminuye según una ecuación de tipo Tait generalizada que relaciona el
volumen comprimido con el saturado a través de un término logarítmico en la
presión:</p>
""" + _eq(r"V = V_s\left[1 - C\,\ln\!\left(\frac{B + P}{B + P_s}\right)\right]") + """
<p>El parámetro B tiene unidades de presión y establece la escala
característica de la compresión. Se obtiene multiplicando la presión
pseudocrítica por un polinomio en τ = 1 − T<sub>r</sub>:</p>
""" + _eq(r"B = P_{cm}\left(-1 - 9.070217\,\tau^{1/3} + 62.45326\,\tau^{2/3} - 135.1102\,\tau + e_1\,\tau^{4/3}\right)") + """
<p>El coeficiente e₁ y el coeficiente C dependen del factor acéntrico de la
mezcla:</p>
""" + _eq(r"e_1 = \exp\!\left(4.79594 + 0.250047\,\omega_m + 1.14188\,\omega_m^2\right)") + """
""" + _eq(r"C = 0.0861488 + 0.0344483\,\omega_m") + """
<p>La densidad del líquido comprimido es el peso molecular de la fase
dividido entre este volumen corregido. La corrección solo se aplica cuando
la presión de trabajo supera la de saturación; en caso contrario se conserva
el volumen saturado.</p>
"""

S6_7 = """
<h2>6.7 Transición al régimen supercrítico</h2>
<p>La correlación del volumen saturado pierde validez cuando la temperatura
reducida se acerca a la unidad, porque las funciones de volumen reducido
divergen en las proximidades del punto crítico. Para evitar una
discontinuidad en la densidad al pasar del líquido al fluido supercrítico,
el programa distingue tres regímenes según la temperatura pseudo-reducida de
la mezcla.</p>
<p>Por debajo de T<sub>r</sub> = 0.95 se aplica el método COSTALD completo
con la corrección por presión. Por encima de T<sub>r</sub> = 1.0 el método
deja de tener sentido físico y la densidad del líquido se toma directamente
de la ecuación de estado. En la banda intermedia, entre T<sub>r</sub> = 0.95
y T<sub>r</sub> = 1.0, la densidad se interpola con un perfil cuadrático
entre la densidad de líquido en T<sub>r</sub> = 0.95 obtenida por COSTALD y
la densidad de la ecuación de estado en T<sub>r</sub> = 1.0:</p>
""" + _eq(r"\rho = \rho_{0.95} + \left(\rho_{1.0}^{EOS} - \rho_{0.95}\right)\left(\frac{T_r - 0.95}{1.0 - 0.95}\right)^2") + """
<p>El perfil cuadrático reproduce la curvatura de la densidad hacia el punto
crítico y garantiza una transición suave hacia el régimen supercrítico. Esta
banda de suavizado corresponde al comportamiento estándar del cálculo de
densidad de líquido con estados correspondientes.</p>
<h3>Alcance del método</h3>
<p>El método COSTALD alcanza su máxima exactitud para hidrocarburos con
factor acéntrico moderado. Para mezclas muy ligeras dominadas por metano, con
peso molecular por debajo de 30, la correlación conserva un residuo pequeño
inherente al modelo de estados correspondientes, documentado por sus autores.
En el rango habitual de gas natural y condensados el método reproduce las
densidades de referencia con error inferior al uno por ciento.</p>
<h3>Referencias</h3>
<p>Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for saturated
densities of liquids and their mixtures. <em>AIChE Journal</em>, 25(4),
653-663.</p>
<p>Thomson, G.H., Brobst, K.R. y Hankinson, R.W. (1982). An improved
correlation for densities of compressed liquids and liquid mixtures.
<em>AIChE Journal</em>, 28(4), 671-676.</p>
"""

S6_8 = """
<h2>6.8 Corrección de volumen de Peneloux</h2>
<p>La corrección de volumen de Peneloux (traslado de volumen o volume shift)
es un método empírico que mejora la densidad de líquido predicha por la
ecuación de estado sin alterar el equilibrio de fases. Se aplica cuando el
usuario selecciona la densidad de la ecuación de estado y activa la
corrección desde el selector correspondiente.</p>
<p>La idea es sencilla: las ecuaciones cúbicas predicen un volumen molar de
líquido sistemáticamente desviado del real. Peneloux propuso trasladar el
volumen calculado una cantidad constante para cada componente, de modo que
el volumen corregido reproduzca mejor la densidad. El volumen trasladado de
la mezcla es el de la ecuación de estado menos el parámetro de traslado:</p>
""" + _eq(r"V = V_{EOS} - c \qquad c = \sum_i x_i\,c_i") + """
<p>El parámetro de traslado de cada componente se estima a partir de sus
propiedades críticas y del factor de compresibilidad de Rackett, con
constantes distintas para cada ecuación de estado:</p>
""" + _eq(r"Z_{RA,i} = 0.29056 - 0.08775\,\omega_i") + """
""" + _eq(r"\text{SRK:}\quad c_i = 0.40768\,\frac{R\,T_{ci}}{P_{ci}}\left(0.29441 - Z_{RA,i}\right)") + """
""" + _eq(r"\text{PR:}\quad c_i = 0.50033\,\frac{R\,T_{ci}}{P_{ci}}\left(0.25969 - Z_{RA,i}\right)") + """
<h3>Neutralidad frente al equilibrio</h3>
<p>El traslado de volumen es algebraicamente neutro en el cálculo del
equilibrio de fases. Al aplicarse el mismo desplazamiento al volumen de
ambas fases, la contribución del traslado se cancela en la relación de
fugacidades que gobierna el reparto de componentes, de modo que las
fracciones molares de vapor y líquido, las constantes de equilibrio y la
propia frontera de la envolvente no se modifican. Lo que cambia es el
volumen molar reportado de cada fase y, en consecuencia, su densidad y su
factor de compresibilidad.</p>
<h3>Efecto sobre el factor de compresibilidad</h3>
<p>Como el factor de compresibilidad es proporcional al volumen molar, el
traslado se refleja directamente en el Z de cada fase. Sustituyendo el
volumen corregido en la definición del factor de compresibilidad se obtiene
una expresión que resta al Z de la ecuación de estado un término
proporcional al parámetro de traslado:</p>
""" + _eq(r"Z = \frac{P\,(V_{EOS} - c)}{R\,T} = Z_{EOS} - \frac{P\,c}{R\,T}") + """
<p>La corrección se aplica tanto a la fase líquida como a la fase vapor, de
manera que el factor de compresibilidad y la densidad de ambas fases son
coherentes con el volumen trasladado. En la fase vapor el efecto es pequeño
porque el volumen molar es grande frente al parámetro de traslado, pero no
es nulo; en la fase líquida el efecto es mayor y es donde el método aporta la
mejora buscada.</p>
<h3>Referencias</h3>
<p>Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent correction for
Redlich-Kwong-Soave volumes. <em>Fluid Phase Equilibria</em>, 8(1), 7-23.</p>
<p>Pedersen, K.S. y Christensen, P.L. (2007). <em>Phase Behavior of
Petroleum Reservoir Fluids</em>. CRC Press.</p>
"""

# ============================================================
# SECCIÓN 7 — ENTALPÍA Y ENTROPÍA
# ============================================================

S7_1 = """
<h2>7.1 Entalpía y entropía de la mezcla</h2>
<p>La entalpía y la entropía son las propiedades termodinámicas que
gobiernan los balances de energía de un proceso: la entalpía interviene en
el cálculo de cargas térmicas de intercambiadores y en el trabajo de
compresión, y la entropía permite evaluar procesos ideales de referencia
como la compresión isentrópica. El programa calcula ambas propiedades para
cada fase a partir de la composición, la temperatura y la presión.</p>
<p>El cálculo sigue el esquema de estado de referencia más desviación. Cada
propiedad se descompone en una contribución de gas ideal, que depende solo
de la temperatura y la composición, y una contribución de desviación que
recoge el efecto de las fuerzas intermoleculares a la presión de trabajo. La
contribución de gas ideal se evalúa componente por componente a partir de la
capacidad calorífica; la desviación se obtiene de la ecuación de estado de
Peng-Robinson.</p>
""" + _eq(r"H(T,P) = H^{ID}(T) + \left[H(T,P) - H^{ID}(T)\right]") + """
""" + _eq(r"S(T,P) = S^{ID}(T,P) + \left[S(T,P) - S^{ID}(T,P)\right]") + """
<p>El término entre corchetes es la desviación respecto al gas ideal. Este
esquema permite usar una base de capacidad calorífica de alta exactitud para
la parte ideal y reservar la ecuación de estado para el efecto de la
presión, que es donde las ecuaciones cúbicas son más fiables.</p>
"""

S7_2 = """
<h2>7.2 Contribución de gas ideal</h2>
<p>La entalpía de gas ideal de cada componente se obtiene de un polinomio de
temperatura de quinto grado que representa la entalpía específica referida a
la base interna del banco de propiedades, ajustada por un desplazamiento que
sitúa el origen en la entalpía de formación a 25 grados Celsius:</p>
""" + _eq(r"H^{ID}_i(T) = H_{\text{off},i} + \frac{M_i}{2.326}\left(a_i + b_i T + c_i T^2 + d_i T^3 + e_i T^4 + f_i T^5\right)") + """
<p>El polinomio se evalúa con la temperatura en kelvin y entrega la entalpía
específica en kJ/kg; el factor que contiene el peso molecular la convierte a
unidades molares de campo. El desplazamiento de entalpía de cada componente
es el valor tabulado en la base de propiedades y garantiza que las entalpías
de distintos componentes compartan un origen común consistente con las
entalpías de formación.</p>
<p>La capacidad calorífica de gas ideal es la derivada del polinomio de
entalpía respecto a la temperatura, multiplicada por el peso molecular para
convertirla a base molar:</p>
""" + _eq(r"C_p^{ID}(T) = \frac{dH^{ID}}{dT}") + """
<p>La entropía de gas ideal de cada componente parte de un desplazamiento
tabulado y añade la integral de la capacidad calorífica sobre la
temperatura, más el término de presión que refiere la entropía a la presión
de una atmósfera:</p>
""" + _eq(r"S^{ID}_i(T,P) = S_{\text{off},i} + \int_{298.15}^{T}\frac{C_p^{ID}(T')}{T'}\,dT' - R\,\ln\!\frac{P}{P_0}") + """
<p>La integral se resuelve numéricamente por la regla de Simpson compuesta.
Para la mezcla, las contribuciones ideales se suman ponderadas por las
fracciones molares y la entropía incorpora además el término de mezclado
ideal, que refleja el aumento de entropía al combinar componentes puros:</p>
""" + _eq(r"S^{ID}_{\text{mez}} = \sum_i x_i S^{ID}_i - R\sum_i x_i\ln x_i") + """
"""

S7_3 = """
<h2>7.3 Desviación por la ecuación de estado</h2>
<p>La desviación respecto al gas ideal recoge el efecto de las fuerzas
intermoleculares y se deriva analíticamente de la ecuación de Peng-Robinson.
La desviación de entalpía combina el término del factor de compresibilidad
con un término que depende del parámetro atractivo y de su derivada respecto
a la temperatura:</p>
""" + _eq(r"H - H^{ID} = RT(Z-1) + \frac{T\,\dfrac{da_m}{dT} - a_m}{2\sqrt{2}\,b_m}\,\ln\!\left(\frac{Z + (1+\sqrt{2})B}{Z + (1-\sqrt{2})B}\right)") + """
<p>La desviación de entropía tiene una estructura análoga, con el término
del factor de compresibilidad y el término logarítmico ponderado por la
derivada del parámetro atractivo:</p>
""" + _eq(r"S - S^{ID} = R\,\ln(Z - B) + \frac{1}{2\sqrt{2}\,b_m}\,\frac{da_m}{dT}\,\ln\!\left(\frac{Z + (1+\sqrt{2})B}{Z + (1-\sqrt{2})B}\right)") + """
<p>donde B es el parámetro adimensional de covolumen de la mezcla,
B = b<sub>m</sub>·P/(R·T), y Z es el factor de compresibilidad de la fase. La
derivada del parámetro atractivo respecto a la temperatura se obtiene de la
regla de mezclado aplicada a las derivadas de cada componente:</p>
""" + _eq(r"\frac{da_m}{dT} = \sum_i\sum_j x_i x_j\,\frac{da_{ij}}{dT} \qquad \frac{da_{ij}}{dT} = \frac{1}{2}\,a_{ij}\left(\frac{1}{a_i\alpha_i}\frac{d(a_i\alpha_i)}{dT} + \frac{1}{a_j\alpha_j}\frac{d(a_j\alpha_j)}{dT}\right)") + """
<p>El término de presión de la entropía se contabiliza dentro de la
contribución ideal, por lo que la desviación de entropía conserva únicamente
el residual asociado a la no idealidad. Las desviaciones se evalúan con el
factor de compresibilidad de la fase correspondiente: la raíz de líquido para
la fase líquida y la raíz de vapor para la fase vapor.</p>
"""

S7_4 = """
<h2>7.4 Ensamblaje por fase</h2>
<p>La entalpía de una fase reúne la contribución ideal de cada componente y
la desviación de la mezcla evaluada con el factor de compresibilidad de esa
fase:</p>
""" + _eq(r"H_{\text{fase}} = \sum_i x_i H^{ID}_i(T) + \left[H - H^{ID}\right]_{\text{mez}}") + """
<p>La entropía de una fase reúne las contribuciones ideales por componente,
el término de mezclado ideal y la desviación de la mezcla:</p>
""" + _eq(r"S_{\text{fase}} = \sum_i x_i S^{ID}_i(T,P) - R\sum_i x_i\ln x_i + \left[S - S^{ID}\right]_{\text{mez}}") + """
<p>Cuando el sistema se encuentra en equilibrio de dos fases, la entalpía y
la entropía globales se obtienen combinando las propiedades de cada fase
ponderadas por la fracción de vapor. La base de entalpía y de entropía es la
misma que emplea el simulador de referencia, de modo que los valores
absolutos son directamente comparables además de las diferencias.</p>
<p>Las propiedades ideales se calculan siempre con los parámetros de
Peng-Robinson, porque los desplazamientos de entalpía y de entropía están
referidos a esa ecuación de estado; la contribución de desviación es la
única que cambiaría con otra ecuación, y su efecto sobre el valor absoluto es
pequeño frente a la contribución ideal.</p>
<h3>Referencias</h3>
<p>Peng, D.Y. y Robinson, D.B. (1976). A Two-Constant Equation of State.
<em>Industrial and Engineering Chemistry Fundamentals</em>, 15(1), 59-64.</p>
<p>Smith, J.M., Van Ness, H.C. y Abbott, M.M. (2005). <em>Introduction to
Chemical Engineering Thermodynamics</em>, 7ª ed. McGraw-Hill.</p>
"""



SECCIONES = [
    ("1. Fundamentos de las EOS cúbicas", [
        ("1.1 Ecuación de estado", S1_1),
        ("1.2 Del gas ideal a los fluidos reales", S1_2),
        ("1.3 Término de repulsión", S1_3),
        ("1.4 Término de atracción", S1_4),
        ("1.5 Ecuación de Peng-Robinson (PR)", S1_5),
        ("1.6 Ecuación de Soave-Redlich-Kwong (SRK)", S1_6),
        ("1.7 Forma cúbica de la ecuación de estado", S1_7),
        ("1.8 Selección de la raíz por energía de Gibbs", S1_8),
        ("1.9 Las cuatro variantes PR/SRK", S1_9),
    ]),
    ("2. Parámetros de la ecuación de estado", [
        ("2.1 Propiedades críticas", S2_1),
        ("2.2 El factor acéntrico", S2_2),
        ("2.3 El coeficiente m y la función alfa", S2_3),
        ("2.4 Reglas de mezclado", S2_4),
        ("2.5 Coeficientes de interacción binaria", S2_5),
        ("2.6 Base de datos de los coeficientes", S2_6),
    ]),
    ("3. El cálculo flash (equilibrio L-V)", [
        ("3.1 El problema del equilibrio de fases", S3_1),
        ("3.2 Fugacidad y coeficiente de fugacidad", S3_2),
        ("3.3 Constante de equilibrio", S3_3),
        ("3.4 Estimación inicial de las K", S3_4),
        ("3.5 La ecuación de Rachford-Rice", S3_5),
        ("3.6 Análisis de estabilidad", S3_6),
        ("3.7 Algoritmo completo del flash", S3_7),
    ]),
    ("4. Envolvente de fases", [
        ("4.1 Envolvente de fases", S4_1),
        ("4.2 Método de Ziervogel", S4_2),
        ("4.3 Método de Michelsen", S4_3),
        ("4.4 Flujo de cálculo combinado", S4_4),
        ("4.5 Punto crítico y líneas de calidad", S4_5),
    ]),
    ("5. Identificación de fase monofásica", [
        ("5.1 El problema monofásico", S5_1),
        ("5.2 Compresibilidad isotérmica", S5_2),
        ("5.3 Criterio de alta presión (A/B)", S5_3),
        ("5.4 Algoritmo completo", S5_4),
        ("5.5 Variante PVTsim", S5_5),
    ]),
    ("6. Densidad de líquido y vapor", [
        ("6.1 Densidad de líquido y vapor", S6_1),
        ("6.2 Densidad por la ecuación de estado", S6_2),
        ("6.3 El método COSTALD", S6_3),
        ("6.4 Volumen del líquido saturado", S6_4),
        ("6.5 Presión de saturación de la mezcla", S6_5),
        ("6.6 Corrección por presión", S6_6),
        ("6.7 Transición al régimen supercrítico", S6_7),
        ("6.8 Corrección de volumen de Peneloux", S6_8),
    ]),
    ("7. Entalpía y entropía", [
        ("7.1 Entalpía y entropía de la mezcla", S7_1),
        ("7.2 Contribución de gas ideal", S7_2),
        ("7.3 Desviación por la ecuación de estado", S7_3),
        ("7.4 Ensamblaje por fase", S7_4),
    ]),
]
import re
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QUrl


class _Visor(QTextBrowser):
    """QTextBrowser que resuelve las ecuaciones 'eq://N' como imágenes de alta
    resolución (devicePixelRatio) para que se vean nítidas."""

    def __init__(self):
        super().__init__()
        self._imgs = {}

    def loadResource(self, tipo, url):
        clave = url.toString()
        if clave in self._imgs:
            return self._imgs[clave]
        return super().loadResource(tipo, url)
from PyQt6.QtWidgets import (
    QVBoxLayout, QTabWidget, QToolButton, QFrame as _QFrame,
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath,
)
from PyQt6.QtCore import QSize, QRectF, QPointF


def _sin_num(s):
    """Quita el prefijo numerico ('1.4 ', '2. ') de un titulo."""
    return re.sub(r'^\s*[\d]+(\.[\d]+)*\.?\s+', '', s)


# ── Iconos (dibujados a mano, en el estilo del programa) ─────────────
def _mk_icon(draw_fn, size=18):
    px = QPixmap(size, size); px.fill(_transparent())
    p = QPainter(px); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(size / 24.0, size / 24.0); draw_fn(p); p.end()
    return QIcon(px)


def _transparent():
    from PyQt6.QtCore import Qt as _Qt
    return _Qt.GlobalColor.transparent


def _dib_seccion(p):
    # Carpeta ambar (seccion) — paleta del programa
    p.setPen(QPen(QColor("#9A7A2A"), 1.3)); p.setBrush(QBrush(QColor("#E8C36A")))
    tab = QPainterPath()
    tab.moveTo(3, 7); tab.lineTo(3, 19); tab.lineTo(21, 19); tab.lineTo(21, 9)
    tab.lineTo(11, 9); tab.lineTo(9, 7); tab.closeSubpath()
    p.drawPath(tab)
    p.setPen(QPen(QColor("#B8942F"), 1.0)); p.setBrush(QBrush(_transparent()))
    p.drawLine(QPointF(3, 12), QPointF(21, 12))


def _dib_tema(p):
    # Pagina con esquina doblada y renglones azules (subseccion)
    p.setPen(QPen(QColor("#4A4A4A"), 1.3)); p.setBrush(QBrush(QColor("#FFFFFF")))
    pg = QPainterPath()
    pg.moveTo(6, 3); pg.lineTo(15, 3); pg.lineTo(19, 7); pg.lineTo(19, 21)
    pg.lineTo(6, 21); pg.closeSubpath()
    p.drawPath(pg)
    p.setPen(QPen(QColor("#4A4A4A"), 1.1)); p.setBrush(QBrush(_transparent()))
    p.drawLine(QPointF(15, 3), QPointF(15, 7)); p.drawLine(QPointF(15, 7), QPointF(19, 7))
    p.setPen(QPen(QColor("#1F5FA8"), 1.1))
    p.drawLine(QPointF(8.5, 11), QPointF(16.5, 11))
    p.drawLine(QPointF(8.5, 14), QPointF(16.5, 14))
    p.drawLine(QPointF(8.5, 17), QPointF(13.5, 17))


def _dib_ocultar(p):
    p.setPen(QPen(QColor("#4A4A4A"), 1.4)); p.setBrush(QBrush(QColor("#FFFFFF")))
    p.drawRect(QRectF(3, 5, 18, 14))
    p.setBrush(QBrush(QColor("#C9D6E4")))
    p.drawRect(QRectF(3, 5, 6, 14))


def _dib_atras(p):
    p.setPen(QPen(QColor("#2E6E3A"), 2.2)); p.setBrush(QBrush(_transparent()))
    p.drawLine(QPointF(15, 5), QPointF(8, 12)); p.drawLine(QPointF(8, 12), QPointF(15, 19))


def _dib_adelante(p):
    p.setPen(QPen(QColor("#2E6E3A"), 2.2)); p.setBrush(QBrush(_transparent()))
    p.drawLine(QPointF(9, 5), QPointF(16, 12)); p.drawLine(QPointF(16, 12), QPointF(9, 19))


class DocTecnica(QWidget):
    """Ventana de Documentación técnica: barra + árbol (pestaña Contenido) +
    contenido, al estilo de un visor de ayuda."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#FFFFFF;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ── Barra de herramientas superior ──────────────────────
        barra = self._crear_barra()
        root.addWidget(barra)
        sep = _QFrame(); sep.setFrameShape(_QFrame.Shape.HLine)
        sep.setStyleSheet("color:#C4C4C4; background:#C4C4C4;"); sep.setFixedHeight(1)
        root.addWidget(sep)

        # ── Cuerpo: árbol | contenido ───────────────────────────
        split = QSplitter(Qt.Orientation.Horizontal)

        from PyQt6.QtWidgets import QScrollArea, QLabel
        # Panel izquierdo: fondo gris; el label "Contenido" va FUERA del
        # recuadro (como "Cálculos"/"Datos"), y el árbol es un recuadro blanco
        # que crece o disminuye con la cantidad de opciones.
        izq = QWidget()
        izq.setStyleSheet("background:#D4D4D4;")
        self.izq = izq
        izq_lay = QVBoxLayout(izq)
        izq_lay.setContentsMargins(6, 3, 4, 4); izq_lay.setSpacing(2)

        # Etiqueta de sección "Contenido" + línea (fuera del recuadro)
        self.lbl_contenido = QLabel("Contenido")
        self.lbl_contenido.setStyleSheet(
            'background:transparent; color:#000000;'
            ' font-family:"Arial Narrow","Arial"; font-size:10pt;')
        izq_lay.addWidget(self.lbl_contenido)
        linea = _QFrame(); linea.setFixedHeight(1)
        linea.setStyleSheet('background:#C4C4C4; border:none;')
        izq_lay.addWidget(linea)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(14)
        self.tree.setIconSize(QSize(16, 16))
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setStyleSheet(
            'QTreeWidget { background:#FFFFFF; border:1px solid #7F7F7F;'
            ' font-family:"Arial Narrow","Arial"; font-size:10pt; outline:0; }'
            'QTreeWidget::item { height:22px; padding-left:2px; }'
            'QTreeWidget::item:selected { background:#DCDCDC; color:#000000; }'
            'QTreeWidget::item:hover { background:#EDEDED; }')

        self._contenido = {}
        self._orden = []          # lista lineal de subsecciones (para prev/next)
        self._tops = []           # items de seccion (para retraducir)
        for sec_titulo, subs in SECCIONES:
            top = QTreeWidgetItem([_sin_num(sec_titulo)])
            self.tree.addTopLevelItem(top)
            self._tops.append(top)
            for sub_titulo, html in subs:
                child = QTreeWidgetItem([_sin_num(sub_titulo)])
                top.addChild(child)
                self._contenido[id(child)] = html
                self._orden.append(child)
            top.setExpanded(False)
        self.tree.itemClicked.connect(self._on_item)
        self.tree.itemExpanded.connect(lambda *_: self._ajustar_alto_arbol())
        self.tree.itemCollapsed.connect(lambda *_: self._ajustar_alto_arbol())
        self._ajustar_alto_arbol()

        # Contenedor gris que aloja el árbol arriba (el resto queda gris)
        izq_cont = QWidget(); izq_cont.setStyleSheet("background:#D4D4D4;")
        cont_lay = QVBoxLayout(izq_cont)
        cont_lay.setContentsMargins(0, 0, 0, 0); cont_lay.setSpacing(0)
        cont_lay.addWidget(self.tree)
        cont_lay.addStretch(1)

        # Scroll (sin barra visible; se navega con la rueda del mouse)
        izq_scroll = QScrollArea()
        izq_scroll.setWidget(izq_cont)
        izq_scroll.setWidgetResizable(True)
        izq_scroll.setFrameShape(_QFrame.Shape.NoFrame)
        izq_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        izq_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        izq_scroll.setStyleSheet("QScrollArea { background:#D4D4D4; border:none; }")
        izq_lay.addWidget(izq_scroll, 1)

        self.view = _Visor()
        self.view.setOpenExternalLinks(False)
        self.view.document().setDefaultStyleSheet(_CSS)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet(
            'QTextBrowser { background:#FFFFFF; border:none; padding:14px 24px; }')

        split.addWidget(izq)
        split.addWidget(self.view)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setCollapsible(0, False)
        split.setSizes([250, 660])
        # Margen (asa gris) que separa el arbol del area de redaccion
        split.setHandleWidth(1)
        split.setStyleSheet("QSplitter::handle { background:#7F7F7F; }")
        root.addWidget(split, 1)

        # Estado de navegacion — sin seleccion inicial (vista en blanco)
        self._idx = -1
        self.view.setHtml("")

    # ── Barra ───────────────────────────────────────────────────
    def _crear_barra(self):
        import idioma as _i18n
        barra = QWidget()
        barra.setStyleSheet("background:#D4D4D4;")
        barra.setFixedHeight(22)
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(4, 0, 4, 0); lay.setSpacing(2)

        def _btn(texto, slot):
            b = QToolButton()
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            b.setText(texto)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                'QToolButton { font-family:"Arial Narrow","Arial"; font-size:10pt;'
                ' color:#000000; border:none; padding:1px 9px; }'
                'QToolButton:hover { background:#C4C4C4; }'
                'QToolButton:disabled { color:#9A9A9A; }')
            b.clicked.connect(slot)
            return b

        self.btn_ocultar = _btn(_i18n.t("Ocultar"), self._toggle_arbol)
        self.btn_atras = _btn(_i18n.t("Atrás"), lambda: self._navegar(-1))
        self.btn_adelante = _btn(_i18n.t("Adelante"), lambda: self._navegar(1))

        self.btn_ocultar = _btn("Ocultar", self._toggle_arbol)
        self.btn_atras = _btn("Atrás", lambda: self._navegar(-1))
        self.btn_adelante = _btn("Adelante", lambda: self._navegar(1))
        lay.addWidget(self.btn_ocultar)
        sep = _QFrame(); sep.setFrameShape(_QFrame.Shape.VLine)
        sep.setStyleSheet("color:#CFCFCF;"); sep.setFixedWidth(1)
        lay.addWidget(sep)
        lay.addWidget(self.btn_atras)
        lay.addWidget(self.btn_adelante)
        lay.addStretch()
        return barra

    # ── Navegacion ──────────────────────────────────────────────
    def _ajustar_alto_arbol(self):
        """El recuadro del árbol crece o disminuye según las opciones visibles."""
        n = 0
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            n += 1
            if top.isExpanded():
                n += top.childCount()
        self.tree.setFixedHeight(8 + 22 * n)

    def _toggle_arbol(self):
        self._arbol_visible = not getattr(self, '_arbol_visible', True)
        self.izq.setVisible(self._arbol_visible)
        import idioma as _i18n
        self.btn_ocultar.setText(
            _i18n.t("Ocultar") if self._arbol_visible else _i18n.t("Mostrar"))

    def retraducir(self):
        """Traduce los textos de la ventana (barra, etiquetas, títulos)."""
        import idioma as _i18n
        vis = getattr(self, '_arbol_visible', True)
        self.lbl_contenido.setText(_i18n.t("Contenido"))
        self.btn_ocultar.setText(_i18n.t("Ocultar") if vis else _i18n.t("Mostrar"))
        self.btn_atras.setText(_i18n.t("Atrás"))
        self.btn_adelante.setText(_i18n.t("Adelante"))
        for si, (sec_titulo, subs) in enumerate(SECCIONES):
            top = self._tops[si]
            top.setText(0, _i18n.t(_sin_num(sec_titulo)))
            for ci, (sub_titulo, _h) in enumerate(subs):
                top.child(ci).setText(0, _i18n.t(_sin_num(sub_titulo)))
        if 0 <= self._idx < len(self._orden):
            self._mostrar_indice(self._idx)

    def _navegar(self, delta):
        if not self._orden:
            return
        nuevo = self._idx + delta
        if 0 <= nuevo < len(self._orden):
            self._mostrar_indice(nuevo)

    def _procesar_eqs(self, html):
        """Reemplaza los marcadores de ecuación por imágenes nítidas.
        Se renderiza al devicePixelRatio real de la pantalla (1:1 físico), de
        modo que la ecuación se ve nítida a cualquier DPI, sin artefactos de
        reescalado; todas comparten el mismo tamaño de letra."""
        from PyQt6.QtGui import QTextDocument
        try:
            dpr = float(self.view.devicePixelRatioF())
        except Exception:
            dpr = 1.0
        if dpr < 1.0:
            dpr = 1.0
        REF_DPI = 118            # dpi de referencia (tamaño de letra pequeño)
        dpi = int(round(REF_DPI * dpr))
        if not hasattr(self, '_eq_imgs'):
            self._eq_imgs = {}; self._eq_count = 0
        doc = self.view.document()
        def repl(m):
            latex = _b64.b64decode(m.group(1)).decode()
            clave = (latex, dpr)
            rec = self._eq_imgs.get(clave)
            if rec is None:
                data, w, h = _render_eq_png(latex, fontsize=11, dpi=dpi)
                if data is None:
                    return '<p align="center">[ecuación]</p>'
                img = QImage()
                img.loadFromData(data)
                img.setDevicePixelRatio(dpr)   # 1:1 físico => nítido
                self._eq_count += 1
                rec = (f"eq://{self._eq_count}", img)
                self._eq_imgs[clave] = rec
            url, img = rec
            doc.addResource(QTextDocument.ResourceType.ImageResource,
                            QUrl(url), img)
            return (f'<p align="center" style="margin:10px 0">'
                    f'<img src="{url}"></p>')
        return re.sub(r'@@EQ:([A-Za-z0-9+/=]+)@@', repl, html)

    def _mostrar_indice(self, idx):
        self._idx = idx
        item = self._orden[idx]
        self.tree.setCurrentItem(item)
        html = self._contenido.get(id(item), "")
        # el titulo (h2) va sin numero
        html = re.sub(r'(<h2>)\s*[\d]+(\.[\d]+)*\.?\s+', r'\1', html)
        # renderizar las ecuaciones a imagen nítida
        html = self._procesar_eqs(html)
        self.view.setHtml(html)
        self.view.verticalScrollBar().setValue(0)
        self.btn_atras.setEnabled(idx > 0)
        self.btn_adelante.setEnabled(idx < len(self._orden) - 1)

    def _on_item(self, item, _col=0):
        if id(item) in self._contenido:
            self._mostrar_indice(self._orden.index(item))
        else:
            # Es una seccion: expandir/colapsar y mostrar su primera subseccion
            item.setExpanded(not item.isExpanded())
            if item.childCount():
                self._mostrar_indice(self._orden.index(item.child(0)))
