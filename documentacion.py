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


# ── Renderizado de ecuaciones (matplotlib -> imagen, diferido y cacheado) ──
_EQ_CACHE = {}


def _eq(latex):
    """Devuelve un marcador con la ecuación (se renderiza al mostrarla)."""
    return f'@@EQ:{_b64.b64encode(latex.encode()).decode()}@@'


def _render_eq_latex(latex, fontsize=15):
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
        fig.savefig(buf, format='png', dpi=140, bbox_inches='tight',
                    pad_inches=0.05, transparent=True)
        plt.close(fig)
        data = buf.getvalue()
        w_px = struct.unpack('>I', data[16:20])[0]
        h_px = struct.unpack('>I', data[20:24])[0]
        b = _b64.b64encode(data).decode()
        # A tamaño nativo (1:1) queda nítido; solo se escalan las muy anchas.
        MAXW = 540
        if w_px > MAXW:
            dh = int(h_px * MAXW / w_px)
            dim = f' width="{MAXW}" height="{dh}"'
        else:
            dim = ''
        html = (f'<p align="center" style="margin:12px 0">'
                f'<img src="data:image/png;base64,{b}"{dim}></p>')
    except Exception:
        html = '<p align="center">[ecuación]</p>'
    _EQ_CACHE[latex] = html
    return html


def _procesar_eqs(html):
    import re as _re
    return _re.sub(
        r'@@EQ:([A-Za-z0-9+/=]+)@@',
        lambda m: _render_eq_latex(_b64.b64decode(m.group(1)).decode()),
        html)


# ═════════════════════════════════════════════════════════════════════
#  SECCIÓN 1 — Fundamentos de las EOS cúbicas
# ═════════════════════════════════════════════════════════════════════
S1_1 = """
<h2>1.1 ¿Qué es una ecuación de estado?</h2>
<p>Una ecuación de estado (EOS, por <i>Equation of State</i>) es una relación
matemática que vincula las tres variables que describen el estado de un fluido:
la presión (P), el volumen molar (V) y la temperatura (T). Conocidas dos de
ellas, la EOS entrega la tercera, y a partir de ella todas las propiedades
termodinámicas derivadas.</p>
<p>El objetivo práctico es responder: a estas condiciones de presión y
temperatura, ¿mi mezcla de hidrocarburos es líquido, gas o coexisten ambas
fases? Todo eso se deriva de una buena ecuación de estado.</p>
<p>El punto de partida es el gas ideal, la ecuación de estado más simple:</p>
""" + _eq(r"P\,V = R\,T") + """
<p>donde R es la constante universal de los gases. El motor de ThermoPhase
trabaja internamente en unidades de campo, por lo que emplea el valor
R = 10.7316 psi·ft³/(lb-mol·°R).</p>
<p>El gas ideal supone dos cosas que la realidad no cumple:</p>
<ul>
<li>que las moléculas no ocupan volumen propio (se tratan como puntos), y</li>
<li>que no ejercen fuerzas entre sí (ni se atraen ni se repelen).</li>
</ul>
<p>A bajas presiones y altas temperaturas esa idealización es razonable, porque
las moléculas están muy separadas y su tamaño e interacciones son
despreciables. Pero en un yacimiento (altas presiones, moléculas muy
empaquetadas) ambas suposiciones fallan por completo. Corregir esas dos
deficiencias es exactamente lo que hacen las ecuaciones de estado cúbicas, y
por eso son la herramienta central de este programa.</p>
"""

S1_2 = """
<h2>1.2 Del gas ideal a los fluidos reales</h2>
<p>Para acercar el modelo a la realidad se introducen dos correcciones sobre la
ecuación del gas ideal, cada una atacando una de las suposiciones falsas.</p>
<h3>Corrección por volumen propio (corrección por repulsión)</h3>
<p>Las moléculas sí ocupan espacio. Por lo tanto, el volumen realmente
disponible para que se muevan no es V, sino V menos un volumen mínimo que
ocupan las propias moléculas. A ese volumen excluido se le llama covolumen (b),
y el término de presión se corrige reemplazando V por (V menos b):</p>
""" + _eq(r"P_{\mathrm{rep}} = \frac{R\,T}{V - b}") + """
<p>Cuando V se aproxima a b, el denominador tiende a cero y la presión se
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
""" + _eq(r"P = \frac{R\,T}{V - b}\; -\; \left(\text{término atractivo}\right)") + """
<p>Una forma intuitiva de verlo: una molécula que está a punto de golpear la
pared del recipiente es frenada por la atracción de las moléculas que quedan
detrás de ella. Ese tirón hacia adentro disminuye la fuerza del impacto y, por
lo tanto, la presión medida. El término atractivo es la traducción matemática
de ese tirón, y es lo que hace posible que exista una fase líquida: sin
atracción, nada mantendría a las moléculas unidas.</p>
"""

S1_3 = """
<h2>1.3 El término de repulsión y el covolumen b</h2>
<p>El covolumen b representa el volumen molar mínimo al que se puede comprimir
una sustancia; es, en esencia, el espacio que las propias moléculas ocupan y
del que ningún otro cuerpo puede disponer. Su papel en la ecuación es doble:
por un lado impone el límite físico de compresibilidad (la presión diverge
cuando V tiende a b), y por otro fija la escala de la rama líquida de la
isoterma, es decir, qué tan denso puede llegar a ser el fluido.</p>
<p>El valor de b no se ajusta empíricamente, sino que se deduce imponiendo que
la ecuación reproduzca de forma exacta el punto crítico de la sustancia (esta
condición geométrica se detalla en la sección de propiedades críticas). El
resultado es que b queda determinado por la temperatura y la presión críticas
del componente:</p>
""" + _eq(r"b = \Omega_b\;\frac{R\,T_c}{P_c}") + """
<p>donde el número adimensional Ω_b depende únicamente de la forma de la
ecuación elegida (toma un valor para Peng-Robinson y otro para SRK). Conviene
resaltar una consecuencia importante: b depende sólo de las propiedades
críticas del componente y no de la temperatura de operación. Es, por lo tanto,
una constante para cada sustancia, que ThermoPhase calcula una sola vez a
partir de la base de datos de propiedades.</p>
<p>Cuando se trabaja con una mezcla y no con un componente puro, el covolumen
de la mezcla se obtiene sumando linealmente los aportes de cada componente,
ponderados por su fracción molar. Ésta es la regla de mezclado que el programa
aplica en la función que evalúa b_m:</p>
""" + _eq(r"b_m = \sum_{i} z_i\, b_i") + """
<p>La linealidad tiene sentido físico directo: el volumen que ocupan las
moléculas de una mezcla es simplemente la suma de los volúmenes que ocupa cada
especie, sin efectos cruzados apreciables. Esto contrasta con el término de
atracción, que sí requiere una regla más elaborada porque involucra
interacciones entre pares de moléculas distintas.</p>
"""

S1_4 = """
<h2>1.4 El término de atracción a y la función α(T)</h2>
<p>El término de atracción es el corazón de una ecuación de estado cúbica y el
que más influye en la calidad de las predicciones de equilibrio. Se construye
como el producto de dos factores, uno que fija su magnitud y otro que introduce
la dependencia con la temperatura:</p>
""" + _eq(r"a(T) = a_c\;\alpha(T)") + """
<p>El primer factor, a_c, establece cuán intensa es la atracción de la
sustancia y, al igual que el covolumen, se obtiene de las condiciones críticas
imponiendo que la isoterma tenga en el punto crítico su inflexión característica:</p>
""" + _eq(r"a_c = \Omega_a\;\frac{R^{2}\,T_c^{\,2}}{P_c}") + """
<p>El segundo factor, α(T), es una función adimensional de la temperatura que
vale exactamente 1 en el punto crítico y crece a medida que la temperatura
disminuye. Su forma, propuesta por Soave y adoptada también por Peng-Robinson,
es:</p>
""" + _eq(r"\alpha(T) = \left[\,1 + m\left(1 - \sqrt{\tfrac{T}{T_c}}\,\right)\right]^{2}") + """
<p>El coeficiente m es una función del factor acéntrico ω (se detalla más
adelante) y toma expresiones distintas para Peng-Robinson y para SRK. Es el
parámetro que ajusta cuán rápido crece la atracción al enfriar el fluido.</p>
<p>El sentido físico de que la atracción dependa de la temperatura es el
siguiente: al enfriar un fluido, las moléculas se mueven más lentamente y pasan
más tiempo cerca unas de otras, de modo que la atracción efectiva entre ellas
aumenta. La función α(T) captura ese efecto. En el punto crítico (α igual a 1)
la agitación térmica es tan alta que la distinción entre líquido y gas
desaparece; por debajo de él, la atracción crece lo suficiente como para
permitir que el fluido condense. Sin esta dependencia con la temperatura, la
ecuación no podría reproducir correctamente las presiones de vapor de los
componentes, que son precisamente el dato que ancla todo el equilibrio de
fases.</p>
<p>En una mezcla, la magnitud de la atracción se obtiene con la regla de
mezclado cuadrática, que suma las interacciones entre todos los pares de
moléculas. ThermoPhase evalúa a_m con esta expresión cada vez que necesita las
propiedades de una fase:</p>
""" + _eq(r"a_m = \sum_{i}\sum_{j} z_i\,z_j\,\sqrt{a_i\,a_j}\,\left(1 - k_{ij}\right)") + """
<p>donde el factor (1 menos k_ij) corrige la atracción entre moléculas de
especies distintas. Esta regla y el significado de los coeficientes k_ij se
desarrollan en la sección de parámetros.</p>
"""

S1_5 = """
<h2>1.5 La ecuación de Peng-Robinson (PR)</h2>
<p>Publicada por Ding-Yu Peng y Donald Robinson en 1976, la ecuación de
Peng-Robinson es hoy la más utilizada en la industria del petróleo y el gas, y
es la opción por defecto de ThermoPhase. Su forma completa es:</p>
""" + _eq(r"P = \frac{R\,T}{V - b} \;-\; \frac{a\,\alpha(T)}{V(V+b) + b(V-b)}") + """
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
<h2>1.6 La ecuación de Soave-Redlich-Kwong (SRK)</h2>
<p>Propuesta por Giorgio Soave en 1972 como mejora de la ecuación de
Redlich-Kwong de 1949, la ecuación SRK fue la primera EOS cúbica capaz de
reproducir con buena precisión las presiones de vapor de los hidrocarburos, al
introducir la función α(T) dependiente del factor acéntrico. Su forma es:</p>
""" + _eq(r"P = \frac{R\,T}{V - b} \;-\; \frac{a\,\alpha(T)}{V(V+b)}") + """
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
<h2>1.7 Forma cúbica en el factor de compresibilidad Z</h2>
<p>Resolver la ecuación de estado directamente para el volumen es incómodo. Es
mucho más práctico trabajar con el factor de compresibilidad, que es una medida
adimensional de cuánto se aleja el fluido del comportamiento ideal:</p>
""" + _eq(r"Z = \frac{P\,V}{R\,T}") + """
<p>Un gas ideal tiene Z igual a 1; un líquido comprimido tiene Z pequeño, y un
gas real a alta presión puede tener Z mayor o menor que 1 según dominen la
repulsión o la atracción. Para reescribir la ecuación en términos de Z se
definen dos grupos adimensionales que concentran toda la información de la
sustancia y del estado:</p>
""" + _eq(r"A = \frac{a\,\alpha\,P}{(R\,T)^{2}} \qquad B = \frac{b\,P}{R\,T}") + """
<p>Sustituyendo, la ecuación de estado se transforma en un polinomio de tercer
grado en Z. Para Peng-Robinson toma la forma:</p>
""" + _eq(r"Z^{3} - (1-B)\,Z^{2} + \left(A - 3B^{2} - 2B\right)Z - \left(AB - B^{2} - B^{3}\right) = 0") + """
<p>De aquí proviene el nombre de ecuaciones cúbicas: siempre conducen a un
polinomio de tercer grado, que ThermoPhase resuelve de forma analítica (no
iterativa) mediante las funciones internas de solución del cúbico, una para
Peng-Robinson y otra para SRK.</p>
<p>Un polinomio cúbico puede tener una o tres raíces reales. Cuando hay tres,
la raíz mayor corresponde a la fase vapor (mayor volumen, menor densidad) y la
raíz menor a la fase líquida (menor volumen, mayor densidad); la raíz
intermedia carece de significado físico porque corresponde a una región
mecánicamente inestable. Que aparezcan tres raíces reales es precisamente la
señal matemática de que, a esas condiciones, el fluido puede separarse en dos
fases. Cómo se elige entre ellas se trata en la subsección siguiente.</p>
"""

S1_8 = """
<h2>1.8 Selección de la raíz por energía de Gibbs</h2>
<p>Cuando el polinomio cúbico entrega tres raíces reales, hay que decidir cuál
usar. El criterio físico correcto es siempre el mismo: de las raíces
candidatas, la fase real es la que tiene menor energía libre de Gibbs, porque
un sistema a temperatura y presión fijas evoluciona espontáneamente hacia el
estado de mínima energía de Gibbs.</p>
<p>Para una fase de composición dada, a la misma presión y temperatura, la
energía de Gibbs molar adimensional se puede expresar a través de los
coeficientes de fugacidad. Comparar dos raíces (por ejemplo la de vapor y la de
líquido de un mismo fluido) equivale a comparar la cantidad:</p>
""" + _eq(r"\frac{g}{R\,T} = \sum_{i} x_i \,\ln\!\left(\phi_i\, x_i\, P\right)") + """
<p>Como la composición, la presión y la temperatura son idénticas para ambas
raíces, la comparación se reduce a evaluar cuál raíz produce el menor valor de
la suma de x_i por el logaritmo de su coeficiente de fugacidad. La raíz que
minimiza esa suma es la estable, y es la que debe emplearse.</p>
<p>En la práctica, cuando ThermoPhase sabe de antemano el rol de la fase, aplica
directamente la consecuencia de este criterio: para las propiedades del vapor
utiliza la raíz mayor del cúbico (Z_V), y para el líquido la raíz menor (Z_L),
porque en cada caso ésa es la raíz que minimiza la energía de Gibbs de esa
fase. El criterio de mínima energía de Gibbs se vuelve indispensable en las
situaciones ambiguas: cuando existe una sola raíz real, o cuando se debe
clasificar un fluido monofásico como líquido o como vapor, el programa evalúa y
compara la energía de Gibbs de las raíces disponibles y se queda con la de
menor valor.</p>
<p>El sentido físico es transparente. La energía de Gibbs se puede imaginar
como un paisaje de valles a P y T fijas; el estado de equilibrio es el fondo
del valle más profundo. Cada raíz del cúbico es un estado candidato, y la
naturaleza siempre escoge el de menor energía. Elegir la raíz por este criterio
es, por lo tanto, dejar que sea la termodinámica y no una regla arbitraria la
que decida qué fase es la real.</p>
"""

S1_9 = """
<h2>1.9 Las cuatro variantes PR/SRK con parámetros HYSYS/PVTsim</h2>
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
<h2>2.1 Propiedades críticas (Tc, Pc)</h2>
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
<h2>2.2 El factor acéntrico ω</h2>
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
<h2>2.3 El coeficiente m y la función α(T)</h2>
<p>Como se anticipó, la dependencia de la atracción con la temperatura se
concentra en la función α(T), y ésta depende de un coeficiente m que a su vez es
función del factor acéntrico. Cada forma cúbica tiene su propia correlación,
ajustada por sus autores para reproducir las presiones de vapor de una serie de
hidrocarburos.</p>
<p>Para Peng-Robinson:</p>
""" + _eq(r"m = 0.37464 + 1.54226\,\omega - 0.26992\,\omega^{2}") + """
<p>Para SRK:</p>
""" + _eq(r"m = 0.480 + 1.574\,\omega - 0.176\,\omega^{2}") + """
<p>Este coeficiente es, por lo tanto, el eslabón que conecta un dato
macroscópico y fácil de tabular (el factor acéntrico) con el comportamiento
microscópico del término de atracción. Un m mayor implica una α(T) que crece más
rápido al enfriar, es decir, una atracción que se refuerza más al bajar la
temperatura, lo cual es propio de las moléculas más pesadas y alargadas.</p>
"""

S2_4 = """
<h2>2.4 Reglas de mezclado</h2>
<p>Todo lo anterior describe un componente puro. Pero un fluido de yacimiento es
una mezcla de muchos componentes (ThermoPhase trabaja con trece). Surge entonces
la pregunta de qué valores de a y de b usar para la mezcla, y la respuesta son
las reglas de mezclado.</p>
<p>Para el covolumen, la regla es lineal, porque el volumen ocupado por las
moléculas de la mezcla es simplemente la suma de los volúmenes de cada especie:</p>
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
<h2>2.5 Coeficientes de interacción binaria kij</h2>
<p>Los coeficientes de interacción binaria k_ij forman una matriz simétrica: el
coeficiente entre i y j es igual al que hay entre j e i, y el de un componente
consigo mismo es cero.</p>
""" + _eq(r"k_{ij} = k_{ji} \qquad k_{ii} = 0") + """
<p>Aunque suelen ser números pequeños, tienen un efecto
desproporcionado sobre la forma de la envolvente de fases, sobre todo en las
cercanías del punto crítico de la mezcla, donde pequeños cambios en la atracción
cruzada desplazan de manera notable las curvas de burbuja y de rocío.</p>
<p>Su magnitud sigue un patrón físico claro:</p>
<ul>
<li>Entre hidrocarburo e hidrocarburo, k_ij es prácticamente cero, porque son
moléculas químicamente similares que se mezclan casi de forma ideal.</li>
<li>Entre dióxido de carbono e hidrocarburo, k_ij ronda 0.08 a 0.12, reflejando
que el dióxido de carbono interactúa de manera apreciablemente distinta con las
cadenas de hidrocarburos.</li>
<li>Entre nitrógeno e hidrocarburo, los valores son intermedios, del orden de
0.03 a 0.08 según la pareja.</li>
</ul>
<p>Un principio de diseño de ThermoPhase es que no se fabrican datos. Cuando una
tabla autorizada no está disponible en las fuentes accesibles, no se inventan
valores: se deja el coeficiente en cero con respaldo documental, en lugar de
rellenarlo con un número arbitrario que degradaría la confiabilidad del
modelo.</p>
"""

S2_6 = """
<h2>2.6 Las tres fuentes de kij</h2>
<p>ThermoPhase permite elegir el origen de la matriz de coeficientes binarios
entre tres opciones, lo que hace posible comparar y validar contra distintos
simuladores.</p>
<h3>Parámetros de HYSYS</h3>
<p>Valores tabulados que replican los del simulador Aspen HYSYS, que ha sido el
punto de comparación histórico del proyecto.</p>
<h3>Parámetros de PVTsim (Knapp)</h3>
<p>Basados en la recopilación de Knapp y colaboradores y en la convención de
Calsep, empleada por PVTsim, que fija en cero los pares hidrocarburo con
hidrocarburo.</p>
<h3>Correlación de Chueh-Prausnitz (calculados)</h3>
<p>En lugar de tabularse, estos coeficientes se calculan a partir de los
volúmenes críticos de cada par de componentes mediante la correlación de
Chueh-Prausnitz:</p>
""" + _eq(r"1 - k_{ij} = \left[\frac{2\,\sqrt{\,V_{c,i}^{1/3}\;V_{c,j}^{1/3}}}{V_{c,i}^{1/3} + V_{c,j}^{1/3}}\right]^{\,n}") + """
<p>La idea física de esta correlación es que la incompatibilidad entre dos
moléculas depende sobre todo de la diferencia de tamaños, representada por sus
volúmenes críticos, y no tanto de su naturaleza química. Por eso reproduce muy
bien los pares de hidrocarburos de tamaños graduales, en los que el coeficiente
resulta casi idéntico al de HYSYS, pero difiere más en pares como
nitrógeno con metano, donde la química (y no sólo el tamaño) juega un papel
importante.</p>
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
""" + _eq(r"f_i^{\,V} = f_i^{\,L} \qquad \text{para todo componente } i") + """
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
componente con la que tendría en un gas ideal a la misma presión y composición:</p>
""" + _eq(r"f_i = \phi_i\; y_i\; P") + """
<p>El coeficiente de fugacidad es precisamente lo que la ecuación de estado
permite calcular. Para las ecuaciones cúbicas tiene una forma cerrada que
depende de los grupos adimensionales A y B, de la raíz Z de la fase, de la
composición y de los coeficientes de interacción binaria. Para Peng-Robinson,
la expresión que ThermoPhase evalúa (de forma vectorizada para los trece
componentes a la vez) es:</p>
""" + _eq(r"\ln\phi_i = \frac{b_i}{b_m}\,(Z-1) - \ln(Z-B) - \frac{A}{2\sqrt{2}\,B}\left(\frac{2\sum_j z_j a_{ij}}{a_m} - \frac{b_i}{b_m}\right)\ln\!\left[\frac{Z+(1+\sqrt{2})B}{Z+(1-\sqrt{2})B}\right]") + """
<p>Cada término tiene un significado: el primero recoge el efecto del tamaño
relativo de la molécula (a través de la relación entre su covolumen y el de la
mezcla), el segundo proviene de la corrección por volumen excluido (la
repulsión), y el tercero, el más elaborado, condensa toda la contribución de la
atracción y de las interacciones cruzadas. La condición de equilibrio de
fugacidades se escribe entonces en términos de los coeficientes de fugacidad de
cada fase:</p>
""" + _eq(r"\phi_i^{\,V}\, y_i\, P = \phi_i^{\,L}\, x_i\, P") + """
<p>Aquí se ve por qué la ecuación de estado es imprescindible: es la que
traduce presión, temperatura y composición en las ganas de escapar de cada
componente en cada fase. El grueso del trabajo de cómputo de un flash consiste
en evaluar estos coeficientes de fugacidad una y otra vez.</p>
"""

S3_3 = """
<h2>3.3 La constante de equilibrio K</h2>
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
<h2>3.4 Estimación inicial: la correlación de Wilson</h2>
<p>Todo procedimiento iterativo necesita un punto de partida. Para los
coeficientes de reparto K_i, ThermoPhase emplea la correlación de Wilson, que
entrega una primera aproximación razonable usando únicamente las propiedades
críticas y el factor acéntrico de cada componente:</p>
""" + _eq(r"K_i = \frac{P_{c,i}}{P}\,\exp\!\left[\,5.373\,(1 + \omega_i)\left(1 - \frac{T_{c,i}}{T}\right)\right]") + """
<p>La correlación de Wilson no es exacta, pero coloca a cada componente del lado
correcto (los ligeros con K mayor que 1 y los pesados con K menor que 1) y
proporciona un arranque estable. En ThermoPhase, estos valores de Wilson no se
usan directamente para el flash, sino que sirven como semilla del análisis de
estabilidad, que es el paso que decide si hay una o dos fases y que refina los
coeficientes de reparto. Recién los coeficientes que salen del análisis de
estabilidad se emplean para iniciar el flash propiamente dicho, como se detalla
en las subsecciones siguientes.</p>
"""

S3_5 = """
<h2>3.5 La ecuación de Rachford-Rice</h2>
<p>Una vez que se dispone de un conjunto de coeficientes de reparto K_i, hace
falta determinar cuánta mezcla se vaporiza, es decir, el valor de V. Se parte
del balance de materia por componente, que reparte lo que entra entre las dos
fases:</p>
""" + _eq(r"z_i = V\,y_i + (1 - V)\,x_i") + """
<p>Combinando este balance con la definición de los coeficientes de reparto
(y_i igual a K_i por x_i) y exigiendo que las fracciones molares de cada fase
sumen 1, se llega a la ecuación de Rachford-Rice, que es una única ecuación en
la incógnita V:</p>
""" + _eq(r"\sum_{i} \frac{z_i\,(K_i - 1)}{1 + V\,(K_i - 1)} = 0") + """
<p>Esta ecuación tiene la ventaja de ser monótona en el intervalo físico de V,
lo que garantiza una solución única y una convergencia estable. ThermoPhase la
resuelve numéricamente por el método de Newton acotado al intervalo válido.
Cuando la solución de V cae dentro del intervalo entre 0 y 1, el sistema es
bifásico; cuando V se sale de ese intervalo, la mezcla es monofásica. El sentido
físico de Rachford-Rice es simple contabilidad: todo lo que entra en la
alimentación debe repartirse exactamente entre el vapor y el líquido.</p>
"""

S3_6 = """
<h2>3.6 Análisis de estabilidad</h2>
<p>Antes de resolver el flash es necesario saber si la mezcla realmente se
separa en dos fases o si permanece como una sola. De esto se encarga el análisis
de estabilidad, que en ThermoPhase reproduce fielmente el procedimiento
implementado y validado en la referencia del proyecto. La idea de fondo,
formalizada por Michelsen, es la del plano tangente a la energía de Gibbs: una
fase es estable si ninguna fase incipiente de otra composición tiene menor
energía de Gibbs; si se encuentra una composición de prueba que baja por debajo
del plano tangente, la mezcla es inestable y se separará.</p>
<p>El procedimiento concreto que sigue el programa es el siguiente. Se parte de
dos juegos de coeficientes de reparto, ambos inicializados con la correlación de
Wilson: uno para ensayar una fase vapor incipiente (K^V) y otro para una fase
líquida incipiente (K^L). Con ellos se construyen las composiciones normalizadas
de esas fases de prueba:</p>
""" + _eq(r"Y_i^{V} = \frac{z_i\,K_i^{V}}{\sum_j z_j\,K_j^{V}} \qquad Y_i^{L} = \frac{z_i / K_i^{L}}{\sum_j z_j / K_j^{L}}") + """
<p>Para cada fase de prueba y para la alimentación se evalúan las fugacidades
con la ecuación de estado, seleccionando la raíz de vapor o de líquido según
corresponda. A partir de la comparación de esas fugacidades se actualizan los
coeficientes de reparto, con un esquema normalizado por las sumas de cada fase
incipiente:</p>
""" + _eq(r"S_V = \sum_i z_i\,K_i^{V} \qquad S_L = \sum_i \frac{z_i}{K_i^{L}}") + """
<p>La normalización por S_V y S_L es lo que evita que la búsqueda diverja: en un
sistema monofásico hace que los coeficientes converjan de manera controlada
hacia la solución trivial, en la que todos los K tienden a 1, en lugar de
dispararse hacia los límites numéricos. Al terminar la iteración, el programa
decide la estabilidad con dos criterios. Por un lado, si alguna de las sumas
S_V o S_L supera la unidad, existe una fase incipiente con menor energía de
Gibbs y la mezcla es inestable, es decir, bifásica. Por otro, para distinguir la
solución trivial de una genuina, se evalúa la suma de los logaritmos de los
coeficientes al cuadrado, considerando sólo los componentes presentes:</p>
""" + _eq(r"\sum_{i:\,z_i > 0} \left(\ln K_i\right)^{2} < \varepsilon \;\Rightarrow\; \text{solución trivial (fase estable)}") + """
<p>El punto clave, y lo que caracteriza al procedimiento de ThermoPhase, es qué
coeficientes de reparto quedan para el flash. Cuando el análisis concluye que la
mezcla es inestable, los coeficientes que se pasan al flash no son los de
Wilson, sino el producto de los dos juegos refinados durante la propia búsqueda
de estabilidad:</p>
""" + _eq(r"K_i^{\text{flash}} = K_i^{V}\cdot K_i^{L}") + """
<p>De este modo el flash arranca desde una estimación mucho más cercana a la
solución que la de Wilson, lo que acelera y estabiliza su convergencia. Si en
cambio el análisis concluye que la mezcla es estable, no hace falta flash: se
reporta directamente una sola fase, clasificada como tendiente a vapor o a
líquido según cuál de las dos búsquedas haya dado la solución trivial.</p>
"""

S3_7 = """
<h2>3.7 El algoritmo completo del flash</h2>
<p>Reuniendo todas las piezas, el cálculo de equilibrio a presión y temperatura
fijas que ejecuta ThermoPhase sigue este orden, que refleja exactamente la
implementación del programa:</p>
<ol>
<li>Se estiman los coeficientes de reparto iniciales con la correlación de
Wilson, a partir de las propiedades críticas y el factor acéntrico.</li>
<li>Con esos valores como semilla se ejecuta el análisis de estabilidad, que
itera sus propios coeficientes de fase vapor y de fase líquida y determina si la
mezcla es de una o de dos fases.</li>
<li>Si el análisis concluye que la mezcla es estable, se reporta una sola fase y
el cálculo termina. Si concluye que es inestable, se construyen los coeficientes
de reparto para el flash como el producto de los dos juegos refinados en la
estabilidad.</li>
<li>Con esos coeficientes se entra al flash. El programa primero aplica dos
verificaciones rápidas de fase única, que son la forma que toma el balance en
los extremos:</li>
</ol>
""" + _eq(r"\sum_i K_i\,z_i \le 1 \;\Rightarrow\; \text{líquido} \qquad \sum_i \frac{z_i}{K_i} \le 1 \;\Rightarrow\; \text{vapor}") + """
<ol start="5">
<li>Si ninguna de esas condiciones se cumple, la mezcla es bifásica y se resuelve
la ecuación de Rachford-Rice para hallar la fracción vaporizada V y, con ella,
las composiciones x_i e y_i de cada fase.</li>
<li>Con esas composiciones se recalculan los coeficientes de fugacidad de ambas
fases mediante la ecuación de estado, resolviendo el polinomio cúbico en Z y
tomando la raíz correcta para cada fase, y se actualizan los coeficientes de
reparto con la relación entre los coeficientes de fugacidad del líquido y del
vapor.</li>
<li>Se repiten los pasos anteriores hasta que los coeficientes de reparto ya no
cambian, es decir, hasta que las fugacidades de cada componente coinciden en
ambas fases dentro de la tolerancia. En ese momento se tiene la solución del
equilibrio.</li>
</ol>
<p>Todo el cálculo es, en el fondo, un lazo que ajusta el reparto de los
componentes hasta que cada uno tiene las mismas ganas de escapar en el líquido
y en el vapor. La ecuación de estado aporta las fugacidades; Rachford-Rice
aporta la contabilidad del reparto; la correlación de Wilson aporta el arranque;
y el análisis de estabilidad aporta tanto la certeza sobre el número de fases
como una estimación afinada de los coeficientes con la que el flash converge de
manera rápida y robusta.</p>
"""


SECCIONES = [
    ("1. Fundamentos de las EOS cúbicas", [
        ("1.1 ¿Qué es una ecuación de estado?", S1_1),
        ("1.2 Del gas ideal a los fluidos reales", S1_2),
        ("1.3 El término de repulsión y el covolumen b", S1_3),
        ("1.4 El término de atracción a y α(T)", S1_4),
        ("1.5 Ecuación de Peng-Robinson (PR)", S1_5),
        ("1.6 Ecuación de Soave-Redlich-Kwong (SRK)", S1_6),
        ("1.7 Forma cúbica en Z", S1_7),
        ("1.8 Selección de la raíz por energía de Gibbs", S1_8),
        ("1.9 Las cuatro variantes PR/SRK", S1_9),
    ]),
    ("2. Parámetros de la ecuación de estado", [
        ("2.1 Propiedades críticas (Tc, Pc)", S2_1),
        ("2.2 El factor acéntrico ω", S2_2),
        ("2.3 El coeficiente m y α(T)", S2_3),
        ("2.4 Reglas de mezclado", S2_4),
        ("2.5 Coeficientes de interacción binaria kij", S2_5),
        ("2.6 Las tres fuentes de kij", S2_6),
    ]),
    ("3. El cálculo flash (equilibrio L-V)", [
        ("3.1 El problema del equilibrio de fases", S3_1),
        ("3.2 Fugacidad y coeficiente de fugacidad", S3_2),
        ("3.3 La constante de equilibrio K", S3_3),
        ("3.4 Estimación inicial (Wilson)", S3_4),
        ("3.5 La ecuación de Rachford-Rice", S3_5),
        ("3.6 Análisis de estabilidad", S3_6),
        ("3.7 Algoritmo completo del flash", S3_7),
    ]),
]
import re
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
        izq_lay.setContentsMargins(4, 3, 4, 4); izq_lay.setSpacing(2)

        # Etiqueta de sección "Contenido" + línea (fuera del recuadro)
        lbl = QLabel("Contenido")
        lbl.setStyleSheet(
            'background:transparent; color:#404040;'
            ' font-family:"Arial Narrow","Arial"; font-size:10pt;')
        izq_lay.addWidget(lbl)
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

        ic_sec = _mk_icon(_dib_seccion)
        ic_tema = _mk_icon(_dib_tema)
        self._contenido = {}
        self._orden = []          # lista lineal de subsecciones (para prev/next)
        for sec_titulo, subs in SECCIONES:
            top = QTreeWidgetItem([_sin_num(sec_titulo)])
            top.setIcon(0, ic_sec)
            self.tree.addTopLevelItem(top)
            for sub_titulo, html in subs:
                child = QTreeWidgetItem([_sin_num(sub_titulo)])
                child.setIcon(0, ic_tema)
                top.addChild(child)
                self._contenido[id(child)] = html
                self._orden.append(child)
            top.setExpanded(True)
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

        self.view = QTextBrowser()
        self.view.setOpenExternalLinks(False)
        self.view.document().setDefaultStyleSheet(_CSS)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet(
            'QTextBrowser { background:#FFFFFF; border:none; padding:14px 22px; }')

        split.addWidget(izq)
        split.addWidget(self.view)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setCollapsible(0, False)
        split.setSizes([250, 660])
        split.setHandleWidth(6)
        root.addWidget(split, 1)

        # Estado de navegacion
        self._idx = -1
        if self._orden:
            self._mostrar_indice(0)

    # ── Barra ───────────────────────────────────────────────────
    def _crear_barra(self):
        barra = QWidget()
        barra.setStyleSheet("background:#D4D4D4;")
        barra.setFixedHeight(24)
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(4, 0, 4, 0); lay.setSpacing(2)

        def _btn(texto, slot):
            b = QToolButton()
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            b.setText(texto)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                'QToolButton { font-family:"Arial Narrow","Arial"; font-size:11pt;'
                ' color:#000000; border:none; padding:2px 10px; }'
                'QToolButton:hover { background:#C4C4C4; }'
                'QToolButton:disabled { color:#9A9A9A; }')
            b.clicked.connect(slot)
            return b

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
        self.btn_ocultar.setText("Ocultar" if self._arbol_visible else "Mostrar")

    def _navegar(self, delta):
        if not self._orden:
            return
        nuevo = self._idx + delta
        if 0 <= nuevo < len(self._orden):
            self._mostrar_indice(nuevo)

    def _mostrar_indice(self, idx):
        self._idx = idx
        item = self._orden[idx]
        self.tree.setCurrentItem(item)
        html = self._contenido.get(id(item), "")
        # el titulo (h2) va sin numero
        html = re.sub(r'(<h2>)\s*[\d]+(\.[\d]+)*\.?\s+', r'\1', html)
        # renderizar las ecuaciones a imagen
        html = _procesar_eqs(html)
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
