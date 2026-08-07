"""
documentacion.py — Ventana de Documentación técnica de ThermoPhase.

Dos paneles: a la izquierda un árbol con las secciones y subsecciones; a la
derecha el desarrollo de cada una. El objetivo es doble: dejar constancia de
las ecuaciones y la configuración técnica implementada, y servir como guía de
aprendizaje explicando el sentido físico de cada concepto.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextBrowser,
    QSplitter,
)
from PyQt6.QtCore import Qt


_CSS = """
body   { font-family:'Arial Narrow','Arial'; font-size:14px; color:#000000; }
h2     { font-family:'Arial Narrow','Arial'; font-size:14px; font-weight:bold;
         color:#000000; margin:2px 0 9px 0; }
h3     { font-family:'Arial Narrow','Arial'; font-size:14px; font-weight:bold;
         color:#000000; margin:13px 0 4px 0; }
p      { font-size:14px; line-height:140%; margin:7px 0; color:#000000; }
li     { font-size:14px; line-height:138%; margin:2px 0; color:#000000; }
b      { font-weight:normal; color:#000000; }
i      { font-style:normal; }
.var   { color:#000000; font-style:normal; }
.eq    { margin:8px 0 8px 26px; color:#000000; }
.nota  { margin:7px 0; color:#000000; }
.fis   { margin:7px 0; color:#000000; }
"""


def _eq(txt):   return f'<div class="eq">{txt}</div>'
def _nota(txt): return f'<p class="nota">{txt}</p>'
def _fis(txt):  return f'<p class="fis">{txt}</p>'


# ── SECCIÓN 1 ────────────────────────────────────────────────────────
S1_1 = """
<h2>1.1 ¿Qué es una ecuación de estado?</h2>
<p>Una <b>ecuación de estado</b> (EOS, por <i>Equation of State</i>) es una
relación matemática que vincula las tres variables que describen el estado de
un fluido: la <b>presión</b> (P), el <b>volumen</b> molar V y la
<b>temperatura</b> (T). Conocidas dos de ellas, la EOS entrega la tercera.</p>
<p>El objetivo práctico en ingeniería de yacimientos y de gas es responder:
<i>a estas condiciones de P y T, ¿mi mezcla de hidrocarburos es líquido, gas o
coexisten ambas fases?, ¿qué densidad tiene?, ¿cuánta energía hay que quitarle
o agregarle?</i> Todo eso se deriva de una buena ecuación de estado.</p>
<p>El punto de partida es el <b>gas ideal</b>:</p>
""" + _eq("P &middot; V = R &middot; T") + """
<p>donde <span class="var">R</span> es la constante universal de los gases. El
motor de ThermoPhase trabaja en unidades de campo:
<span class="var">R</span> = 10.7316 psi&middot;ft&sup3;/(lb-mol&middot;&deg;R).</p>
""" + _fis("El gas ideal supone dos cosas que la realidad no cumple: (1) que "
"las moléculas no ocupan volumen (son puntos), y (2) que no se atraen ni se "
"repelen. A bajas presiones y altas temperaturas es razonable, pero en un "
"yacimiento —altas presiones, moléculas empaquetadas— falla por completo. "
"Corregir esas dos deficiencias es lo que hacen las EOS cúbicas.")

S1_2 = """
<h2>1.2 Del gas ideal a los fluidos reales</h2>
<p>Se introducen dos correcciones sobre el gas ideal, cada una atacando una de
las suposiciones falsas:</p>
<h3>Corrección por volumen propio (repulsión)</h3>
<p>Las moléculas <b>sí ocupan espacio</b>. El volumen disponible no es V, sino
V menos un volumen mínimo que ocupan las propias moléculas: el
<b>covolumen</b> <span class="var">b</span>. El término repulsivo pasa a:</p>
""" + _eq("P<sub>rep</sub> = R&middot;T / (V &minus; b)") + """
<p>Cuando V se acerca a b, la presión se dispara al infinito: es imposible
comprimir el fluido más allá del volumen de sus moléculas. Ese es el límite
físico de la fase líquida.</p>
<h3>Corrección por fuerzas atractivas</h3>
<p>Las moléculas <b>se atraen</b> (fuerzas de dispersión). Esa atracción
<b>reduce</b> la presión respecto de un gas ideal, por lo que se resta un
término:</p>
""" + _eq("P = R&middot;T / (V &minus; b) &minus; (término atractivo)") + """
""" + _fis("Una molécula a punto de golpear la pared es 'frenada' por la "
"atracción de las que quedan atrás; ese tirón hacia adentro baja la presión. "
"El término atractivo es la traducción matemática de ese tirón, y es lo que "
"hace posible que exista fase líquida: sin atracción, nada mantendría unidas "
"a las moléculas.")

S1_3 = """
<h2>1.3 El término de repulsión y el covolumen b</h2>
<p>El covolumen <span class="var">b</span> es el volumen molar mínimo al que se
puede comprimir la sustancia. Se calcula de las propiedades <b>críticas</b>,
donde la EOS debe cumplir una condición geométrica exacta (sección 2.1):</p>
""" + _eq("b = &Omega;<sub>b</sub> &middot; R&middot;T<sub>c</sub> / P<sub>c</sub>") + """
<p><span class="var">&Omega;<sub>b</sub></span> es una constante que depende de
la ecuación (PR o SRK).</p>
""" + _nota("b depende sólo de las propiedades críticas del componente, no de "
"la temperatura de operación: es una constante para cada sustancia.")

S1_4 = """
<h2>1.4 El término de atracción a y la función &alpha;(T)</h2>
<p>El término de atracción es el corazón de una EOS cúbica. Se escribe como el
producto de dos factores:</p>
""" + _eq("a(T) = a<sub>c</sub> &middot; &alpha;(T)") + """
<p><b>El factor a<sub>c</sub></b> fija la <i>magnitud</i> de la atracción y se
obtiene de las críticas:</p>
""" + _eq("a<sub>c</sub> = &Omega;<sub>a</sub> &middot; "
"R&sup2;&middot;T<sub>c</sub>&sup2; / P<sub>c</sub>") + """
<p><b>La función &alpha;(T)</b> introduce la <i>dependencia con la
temperatura</i>. Vale 1 en el punto crítico y crece al bajar T:</p>
""" + _eq("&alpha;(T) = [ 1 + m&middot;( 1 &minus; "
"&radic;(T/T<sub>c</sub>) ) ]&sup2;") + """
<p>El coeficiente <span class="var">m</span> es función del factor acéntrico
&omega; (sección 2.3) y difiere entre PR y SRK.</p>
""" + _fis("Al enfriar un fluido las moléculas se mueven más despacio y pasan "
"más tiempo 'sintiéndose' mutuamente: la atracción efectiva aumenta. "
"&alpha;(T) captura eso. En el punto crítico (&alpha; = 1) líquido y gas son "
"indistinguibles; por debajo, la atracción crece lo suficiente para permitir "
"la condensación. Sin la dependencia con T, la EOS no reproduciría las "
"presiones de vapor.")

S1_5 = """
<h2>1.5 La ecuación de Peng-Robinson (PR)</h2>
<p>Publicada por Peng y Robinson (1976), es hoy la EOS más usada en petróleo y
gas:</p>
""" + _eq("P = R&middot;T/(V &minus; b) &minus; "
"a&middot;&alpha;(T) / [ V(V+b) + b(V &minus; b) ]") + """
<p>El denominador <span class="var">V(V+b)+b(V&minus;b)</span> es lo que le da
su buena predicción de <b>densidades de líquido</b>. Sus constantes:</p>
""" + _eq("&Omega;<sub>a</sub> = 0.45724 &nbsp;&nbsp; "
"&Omega;<sub>b</sub> = 0.07780") + """
""" + _eq("m = 0.37464 + 1.54226&middot;&omega; &minus; 0.26992&middot;&omega;&sup2;") + """
""" + _nota("PR predice muy bien el equilibrio L-V de hidrocarburos y da "
"densidades de líquido más realistas que SRK; es la opción por defecto en "
"ThermoPhase.")

S1_6 = """
<h2>1.6 La ecuación de Soave-Redlich-Kwong (SRK)</h2>
<p>Propuesta por Soave (1972), fue la primera EOS cúbica en reproducir bien las
presiones de vapor de hidrocarburos:</p>
""" + _eq("P = R&middot;T/(V &minus; b) &minus; "
"a&middot;&alpha;(T) / [ V(V + b) ]") + """
<p>Difiere de PR en el denominador atractivo (aquí <span class="var">V(V+b)"
</span>) y en las constantes:</p>
""" + _eq("&Omega;<sub>a</sub> = 0.42748 &nbsp;&nbsp; "
"&Omega;<sub>b</sub> = 0.08664") + """
""" + _eq("m = 0.480 + 1.574&middot;&omega; &minus; 0.176&middot;&omega;&sup2;") + """
""" + _fis("SRK y PR comparten filosofía (repulsión + atracción dependiente de "
"T); difieren en la forma del denominador atractivo, que cambia cómo se "
"reparte el volumen. SRK tiende a sobrestimar el volumen de líquido; PR lo "
"corrige mejor. Ambas dan composiciones de equilibrio muy parecidas.")

S1_7 = """
<h2>1.7 Forma cúbica en el factor de compresibilidad Z</h2>
<p>Resolver para el volumen es incómodo; se prefiere el <b>factor de
compresibilidad</b>:</p>
""" + _eq("Z = P&middot;V / (R&middot;T)") + """
<p>que mide el alejamiento del gas ideal (Z = 1). Con dos grupos
adimensionales</p>
""" + _eq("A = a&middot;&alpha;&middot;P / (R&middot;T)&sup2; &nbsp;&nbsp; "
"B = b&middot;P / (R&middot;T)") + """
<p>la EOS se convierte en un <b>polinomio cúbico</b> en Z. Para PR:</p>
""" + _eq("Z&sup3; &minus; (1&minus;B)&middot;Z&sup2; + "
"(A &minus; 3B&sup2; &minus; 2B)&middot;Z &minus; "
"(A&middot;B &minus; B&sup2; &minus; B&sup3;) = 0") + """
<p>De ahí el nombre de ecuaciones <b>cúbicas</b>.</p>
""" + _fis("Un cúbico tiene una o tres raíces reales. Con tres, la <b>mayor</b> "
"es el vapor (mayor volumen, menor densidad) y la <b>menor</b> el líquido; la "
"intermedia es inestable y no tiene sentido físico. Que existan tres raíces "
"es la señal matemática de que el fluido puede separarse en dos fases.")

S1_8 = """
<h2>1.8 Selección de la raíz (líquido vs vapor)</h2>
<p>Con tres raíces reales, ThermoPhase elige según el rol de la fase:</p>
<ul>
<li>Para el <b>vapor</b>, la raíz <b>mayor</b> (Z<sub>V</sub>).</li>
<li>Para el <b>líquido</b>, la raíz <b>menor</b> (Z<sub>L</sub>).</li>
</ul>
<p>Con una sola raíz real, esa es la solución; la fase se clasifica por su
volumen o por el criterio de mínima energía de Gibbs.</p>
""" + _nota("Un error clásico —corregido en ThermoPhase— es usar la raíz "
"equivocada al trazar la envolvente: si en la rama de burbuja se toma la raíz "
"de vapor, la curva no cierra. La selección debe ser coherente con la EOS "
"activa (PR o SRK).")

S1_9 = """
<h2>1.9 Las cuatro variantes: PR/SRK &times; HYSYS/PVTsim</h2>
<p>ThermoPhase implementa <b>cuatro</b> EOS, combinando las dos ecuaciones con
dos <b>conjuntos de parámetros</b> según el simulador de referencia:</p>
<ul>
<li><b>Peng-Robinson (HYSYS)</b></li>
<li><b>SRK (HYSYS)</b></li>
<li><b>Peng-Robinson (PVTsim)</b></li>
<li><b>SRK (PVTsim)</b></li>
</ul>
<p>La <i>forma</i> de la ecuación es la misma dentro de cada familia; lo que
cambia entre HYSYS y PVTsim son las propiedades críticas tabuladas, los
factores acéntricos y sobre todo los k<sub>ij</sub> (sección 2.5).</p>
""" + _nota("HYSYS usa para SRK un conjunto de factores acéntricos propio "
"(OMHSRK) distinto del de PR; usar el &omega; de PR en el flash de SRK era un "
"error. Las Tc y Pc, en cambio, son idénticas entre PR y SRK.")


# ── SECCIÓN 2 ────────────────────────────────────────────────────────
S2_1 = """
<h2>2.1 Propiedades críticas (T<sub>c</sub>, P<sub>c</sub>)</h2>
<p>El <b>punto crítico</b> es el par (T<sub>c</sub>, P<sub>c</sub>) por encima
del cual desaparece la distinción entre líquido y gas: por más que se comprima,
no condensa. Es la piedra angular de toda EOS cúbica, porque a y b se calibran
para reproducirlo exactamente.</p>
<p>En el punto crítico la isoterma tiene un <b>punto de inflexión con tangente
horizontal</b>:</p>
""" + _eq("(&part;P/&part;V)<sub>T</sub> = 0 &nbsp;y&nbsp; "
"(&part;&sup2;P/&part;V&sup2;)<sub>T</sub> = 0 &nbsp; en el crítico") + """
<p>Imponer esas dos condiciones fija los valores de &Omega;<sub>a</sub> y
&Omega;<sub>b</sub> (secciones 1.5 y 1.6).</p>
""" + _fis("Esas derivadas nulas significan que la isoterma es localmente "
"plana en el crítico: comprimir no cambia la presión. Líquido y vapor se han "
"vuelto idénticos, y por eso la 'campana' de dos fases se cierra justo ahí "
"(es la isoterma del ícono de la barra de herramientas).")

S2_2 = """
<h2>2.2 El factor acéntrico &omega;</h2>
<p>Dos sustancias con parecidas Tc y Pc pueden comportarse distinto porque sus
moléculas tienen <b>formas</b> diferentes. El <b>factor acéntrico</b>
<span class="var">&omega;</span> (Pitzer) mide cuánto se aleja una molécula de
ser esférica (argón: &omega; &asymp; 0). Se define con la presión de vapor a
T/T<sub>c</sub> = 0.7:</p>
""" + _eq("&omega; = &minus;log<sub>10</sub>( P<sub>vap</sub>/P<sub>c</sub> ) "
"&minus; 1 &nbsp; en T/T<sub>c</sub> = 0.7") + """
<p>Cadenas más largas de hidrocarburos tienen mayor &omega;: metano &asymp; "
"0.011, nonano &gt; 0.44.</p>
""" + _fis("&omega; es el 'tercer parámetro' que corrige la forma molecular. "
"Entra en la EOS por el coeficiente m de &alpha;(T): moléculas más acéntricas "
"tienen una atracción que varía más con la temperatura. Sin &omega;, todas "
"las sustancias con iguales Tc y Pc se comportarían igual, lo cual es falso.")

S2_3 = """
<h2>2.3 El coeficiente m y la función &alpha;(T)</h2>
<p>La dependencia de la atracción con T se concentra en &alpha;(T), vía un
coeficiente m función del factor acéntrico. Cada EOS tiene su correlación:</p>
""" + _eq("PR:&nbsp; m = 0.37464 + 1.54226&middot;&omega; &minus; "
"0.26992&middot;&omega;&sup2;") + """
""" + _eq("SRK: m = 0.480 + 1.574&middot;&omega; &minus; "
"0.176&middot;&omega;&sup2;") + """
<p>Fueron ajustadas por sus autores para reproducir presiones de vapor de
hidrocarburos. Es el eslabón que conecta un dato macroscópico y medible
(&omega;) con el término de atracción.</p>
""" + _nota("El manual de Aspen especifica para SRK 0.480 + 1.574&middot;&omega; "
"&minus; 0.176&middot;&omega;&sup2;. Es un punto a vigilar: versiones antiguas "
"usaban 1.574 como constante fija.")

S2_4 = """
<h2>2.4 Reglas de mezclado (mixing rules)</h2>
<p>Lo anterior describe un componente <b>puro</b>. Un fluido de yacimiento es
una <b>mezcla</b> (13 componentes en ThermoPhase). ¿Qué a y b usar? Las
<b>reglas de mezclado</b>. Para el covolumen, lineal:</p>
""" + _eq("b<sub>m</sub> = &Sigma;<sub>i</sub> z<sub>i</sub> &middot; b<sub>i</sub>") + """
<p>Para la atracción, la <b>regla cuadrática</b> (interacciones por pares):</p>
""" + _eq("a<sub>m</sub> = &Sigma;<sub>i</sub> &Sigma;<sub>j</sub> "
"z<sub>i</sub> z<sub>j</sub> &radic;(a<sub>i</sub> a<sub>j</sub>) &middot; "
"(1 &minus; k<sub>ij</sub>)") + """
""" + _fis("La atracción entre dos moléculas <i>distintas</i> no es exactamente "
"la media geométrica de sus atracciones: (1 &minus; k<sub>ij</sub>) es la "
"corrección. Un k<sub>ij</sub> positivo reduce la atracción cruzada (las "
"moléculas 'se llevan peor' de lo esperado), típico entre parejas dispares "
"como CO&sub2; y un hidrocarburo.")

S2_5 = """
<h2>2.5 Coeficientes de interacción binaria k<sub>ij</sub></h2>
<p>Los <span class="var">k<sub>ij</sub></span> forman una <b>matriz
simétrica</b> (k<sub>ij</sub> = k<sub>ji</sub>, k<sub>ii</sub> = 0). Aunque
pequeños, tienen un efecto desproporcionado sobre la envolvente cerca del punto
crítico. Su magnitud sigue un patrón físico:</p>
<ul>
<li><b>HC&ndash;HC:</b> k<sub>ij</sub> &asymp; 0 (moléculas similares, mezcla
casi ideal; confirmado por Calsep/PVTsim).</li>
<li><b>CO&sub2;&ndash;HC:</b> &asymp; 0.08&ndash;0.12.</li>
<li><b>N&sub2;&ndash;HC:</b> intermedios, 0.03&ndash;0.08.</li>
</ul>
""" + _nota("Principio de ThermoPhase: <b>no se fabrican datos</b>. Si una tabla "
"autorizada no está disponible, se deja k<sub>ij</sub> = 0 con respaldo "
"documental en vez de inventar valores.")

S2_6 = """
<h2>2.6 Las tres fuentes de k<sub>ij</sub></h2>
<p>Se puede elegir el origen de la matriz entre tres opciones:</p>
<h3>1. HYSYS</h3>
<p>Valores que replican los de Aspen HYSYS (benchmark histórico).</p>
<h3>2. PVTsim &ndash; Knapp</h3>
<p>Basados en Knapp et al. y la convención de Calsep (HC&ndash;HC = 0).</p>
<h3>3. Chueh-Prausnitz (calculados)</h3>
<p>Se <b>calculan</b> de los volúmenes críticos de cada par:</p>
""" + _eq("1 &minus; k<sub>ij</sub> = "
"[ 2&middot;(V<sub>ci</sub><sup>1/3</sup>&middot;V<sub>cj</sub><sup>1/3</sup>)"
"<sup>1/2</sup> / (V<sub>ci</sub><sup>1/3</sup> + "
"V<sub>cj</sub><sup>1/3</sup>) ]<sup>n</sup>") + """
""" + _fis("Chueh-Prausnitz dice que la 'incompatibilidad' entre dos moléculas "
"depende sobre todo de la <b>diferencia de tamaños</b> (vía volúmenes "
"críticos), no de la polaridad. Por eso reproduce muy bien los pares "
"HC&ndash;HC (k<sub>ij</sub> casi idéntico a HYSYS) pero difiere en pares "
"como N&sub2;&ndash;C1, donde la química importa.")


# ── SECCIÓN 3 ────────────────────────────────────────────────────────
S3_1 = """
<h2>3.1 El problema del equilibrio de fases</h2>
<p>El <b>cálculo flash</b> responde: dada una mezcla de composición global
<span class="var">z</span> a P y T, ¿en cuánto vapor y líquido se separa y cuál
es la composición de cada fase? Definimos:</p>
<ul>
<li><span class="var">z<sub>i</sub></span>: fracción molar de i en la
alimentación.</li>
<li><span class="var">y<sub>i</sub></span>: fracción de i en el vapor.</li>
<li><span class="var">x<sub>i</sub></span>: fracción de i en el líquido.</li>
<li><span class="var">V</span>: fracción de mezcla que resulta vapor (0 a 1).</li>
</ul>
<p>La condición que gobierna todo es el <b>equilibrio termodinámico</b>: cada
componente tiene la misma <b>fugacidad</b> en ambas fases.</p>
""" + _eq("f<sub>i</sub><sup>V</sup> = f<sub>i</sub><sup>L</sup> "
"&nbsp; para todo i") + """
""" + _fis("Si un componente 'prefiere' el vapor, migrará hacia él hasta que ya "
"no haya ganancia en seguir migrando. Ese punto es la igualdad de fugacidades. "
"La fugacidad es la 'presión de escape efectiva' de un componente: mide sus "
"ganas de abandonar la fase en la que está.")

S3_2 = """
<h2>3.2 Fugacidad y coeficiente de fugacidad</h2>
<p>La <b>fugacidad</b> es una presión corregida que mide el potencial químico.
Se usa el <b>coeficiente de fugacidad</b> &phi;<sub>i</sub>, que la compara con
la de un gas ideal:</p>
""" + _eq("f<sub>i</sub> = &phi;<sub>i</sub> &middot; y<sub>i</sub> &middot; P") + """
<p>&phi;<sub>i</sub> es lo que aporta la <b>EOS</b>: tiene forma cerrada en
función de A, B, Z y de los k<sub>ij</sub>. La condición de equilibrio se
vuelve:</p>
""" + _eq("&phi;<sub>i</sub><sup>V</sup> y<sub>i</sub> P = "
"&phi;<sub>i</sub><sup>L</sup> x<sub>i</sub> P") + """
""" + _fis("La EOS traduce 'P, T y composición' en 'ganas de escapar' (&phi;) de "
"cada componente en cada fase. El trabajo pesado de un flash es calcular estos "
"coeficientes una y otra vez.")

S3_3 = """
<h2>3.3 La constante de equilibrio K</h2>
<p>De la igualdad de fugacidades surge la <b>constante de equilibrio</b>:</p>
""" + _eq("K<sub>i</sub> = y<sub>i</sub> / x<sub>i</sub> = "
"&phi;<sub>i</sub><sup>L</sup> / &phi;<sub>i</sub><sup>V</sup>") + """
<p>K<sub>i</sub> &gt; 1: el componente se concentra en el vapor (ligero, como
el metano). K<sub>i</sub> &lt; 1: se queda en el líquido (pesado, como el
nonano).</p>
""" + _nota("Como los &phi; dependen de x e y, y éstas de los K, el problema es "
"<b>implícito</b>: hay que iterar. Por eso el flash no es una fórmula directa.")

S3_4 = """
<h2>3.4 Estimación inicial: la correlación de Wilson</h2>
<p>Toda iteración necesita arranque. Para los K<sub>i</sub> se usa la
<b>correlación de Wilson</b>, con sólo críticas y factor acéntrico:</p>
""" + _eq("K<sub>i</sub> &asymp; (P<sub>ci</sub>/P) &middot; "
"exp[ 5.373&middot;(1 + &omega;<sub>i</sub>)&middot;"
"(1 &minus; T<sub>ci</sub>/T) ]") + """
<p>No es exacta, pero pone a cada componente del lado correcto y acelera la
convergencia del flash riguroso.</p>
""" + _fis("Wilson es una ley de Raoult corregida por acentricidad. Es la "
"'brújula' inicial: no da la respuesta final, pero apunta bien para que las "
"iteraciones con la EOS completa converjan rápido y sin oscilar.")

S3_5 = """
<h2>3.5 La ecuación de Rachford-Rice</h2>
<p>Con los K<sub>i</sub> estimados, hay que hallar V. Se parte del balance por
componente:</p>
""" + _eq("z<sub>i</sub> = V&middot;y<sub>i</sub> + "
"(1&minus;V)&middot;x<sub>i</sub>") + """
<p>Combinando con y<sub>i</sub> = K<sub>i</sub>x<sub>i</sub> y exigiendo que
cada fase sume 1, se llega a la <b>ecuación de Rachford-Rice</b>:</p>
""" + _eq("&Sigma;<sub>i</sub> z<sub>i</sub>&middot;(K<sub>i</sub> &minus; 1) / "
"[ 1 + V&middot;(K<sub>i</sub> &minus; 1) ] = 0") + """
<p>Una sola ecuación en V, resuelta por bisección o Newton. Es <b>monótona</b>
en el intervalo físico, así que converge de forma estable.</p>
""" + _fis("Rachford-Rice es contabilidad: todo lo que entra (z<sub>i</sub>) se "
"reparte entre vapor y líquido. Su forma garantiza una única solución física "
"entre burbuja y rocío; fuera de ese rango, V se sale de [0,1] y la mezcla es "
"monofásica.")

S3_6 = """
<h2>3.6 Análisis de estabilidad: &iquest;una o dos fases?</h2>
<p>Conviene saber si la mezcla realmente se separa. Es el <b>análisis de
estabilidad</b> (Michelsen), vía la distancia al <b>plano tangente de
Gibbs</b> (TPD):</p>
""" + _eq("TPD(w) = &Sigma;<sub>i</sub> w<sub>i</sub>&middot;"
"[ ln w<sub>i</sub> + ln &phi;<sub>i</sub>(w) &minus; "
"ln z<sub>i</sub> &minus; ln &phi;<sub>i</sub>(z) ] &ge; 0 &rArr; estable") + """
<p>Si alguna composición de prueba w hace TPD &lt; 0, la mezcla es inestable y
se separará en dos fases.</p>
""" + _fis("La energía de Gibbs es un paisaje de valles. Una fase es estable si "
"está en el fondo de su valle y no hay atajo a un valle más profundo "
"mezclándose de otra manera. El análisis busca ese atajo: si lo halla, "
"aparece una segunda fase. Es lo que evita reportar 'una fase' cuando hay dos.")

S3_7 = """
<h2>3.7 El algoritmo iterativo completo del flash</h2>
<p>El flash isotérmico-isobárico (T y P fijas) de ThermoPhase sigue estos
pasos:</p>
<ol>
<li><b>Estimación inicial</b> de K<sub>i</sub> con Wilson (3.4).</li>
<li><b>Resolver Rachford-Rice</b> (3.5) para V y las composiciones
x<sub>i</sub>, y<sub>i</sub>.</li>
<li><b>Calcular fugacidades</b> &phi;<sub>i</sub><sup>V</sup> y
&phi;<sub>i</sub><sup>L</sup> con la EOS, resolviendo el cúbico en Z y eligiendo
la raíz correcta de cada fase (1.7&ndash;1.8).</li>
<li><b>Actualizar K<sub>i</sub></b> = &phi;<sub>i</sub><sup>L</sup>/
&phi;<sub>i</sub><sup>V</sup> (3.3).</li>
<li><b>Convergencia</b>: si los K<sub>i</sub> ya no cambian (fugacidades
iguales en ambas fases), terminar; si no, volver al paso 2.</li>
<li><b>Clasificar</b>: V en (0,1) &rArr; dos fases; V &rarr; 0 o 1 &rArr;
monofásico (confirmado con estabilidad, 3.6).</li>
</ol>
""" + _nota("Este esquema de sustitución sucesiva es el que usa ThermoPhase. "
"Cerca del crítico o en mezclas casi azeotrópicas puede acelerarse o "
"estabilizarse con métodos adicionales, pero la lógica —igualar fugacidades "
"iterando— es siempre la misma.") + """
""" + _fis("Todo el flash es un lazo que ajusta el reparto de componentes hasta "
"que cada uno tiene las mismas 'ganas de escapar' en líquido y vapor. La EOS "
"aporta las fugacidades; Rachford-Rice, la contabilidad; Wilson, el arranque; "
"y la estabilidad, la certeza del número de fases.")


SECCIONES = [
    ("1. Fundamentos de las EOS cúbicas", [
        ("1.1 ¿Qué es una ecuación de estado?", S1_1),
        ("1.2 Del gas ideal a los fluidos reales", S1_2),
        ("1.3 El término de repulsión y el covolumen b", S1_3),
        ("1.4 El término de atracción a y α(T)", S1_4),
        ("1.5 Ecuación de Peng-Robinson (PR)", S1_5),
        ("1.6 Ecuación de Soave-Redlich-Kwong (SRK)", S1_6),
        ("1.7 Forma cúbica en Z", S1_7),
        ("1.8 Selección de la raíz (líquido/vapor)", S1_8),
        ("1.9 Las cuatro variantes PR/SRK × HYSYS/PVTsim", S1_9),
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
    # Carpeta ambar (seccion)
    p.setPen(QPen(QColor("#9A7A2A"), 1.3)); p.setBrush(QBrush(QColor("#E8C36A")))
    tab = QPainterPath()
    tab.moveTo(3, 7); tab.lineTo(3, 19); tab.lineTo(21, 19); tab.lineTo(21, 9)
    tab.lineTo(11, 9); tab.lineTo(9, 7); tab.closeSubpath()
    p.drawPath(tab)


def _dib_tema(p):
    # Pagina con esquina doblada (subseccion)
    p.setPen(QPen(QColor("#5A5A5A"), 1.3)); p.setBrush(QBrush(QColor("#FFFFFF")))
    pg = QPainterPath()
    pg.moveTo(6, 3); pg.lineTo(15, 3); pg.lineTo(19, 7); pg.lineTo(19, 21)
    pg.lineTo(6, 21); pg.closeSubpath()
    p.drawPath(pg)
    p.setPen(QPen(QColor("#5A5A5A"), 1.1)); p.setBrush(QBrush(_transparent()))
    p.drawLine(QPointF(15, 3), QPointF(15, 7)); p.drawLine(QPointF(15, 7), QPointF(19, 7))
    p.setPen(QPen(QColor("#8AA0C0"), 1.1))
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

        # ── Cuerpo: árbol (pestañas) | contenido ────────────────
        split = QSplitter(Qt.Orientation.Horizontal)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            'QTabWidget::pane { border:none; background:#F5F5F2; }'
            'QTabBar::tab { font-family:"Arial Narrow","Arial"; font-size:13px;'
            ' padding:4px 14px; background:#E4E4DE; border:1px solid #C8C8C2;'
            ' border-bottom:none; }'
            'QTabBar::tab:selected { background:#F5F5F2; }')

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QSize(18, 18))
        self.tree.setStyleSheet(
            'QTreeWidget { background:#F5F5F2; border:none;'
            ' font-family:"Arial Narrow","Arial"; font-size:14px; outline:0; }'
            'QTreeWidget::item { padding:3px 2px; }'
            'QTreeWidget::item:selected { background:#D6E3F0; color:#000000; }'
            'QTreeWidget::item:hover { background:#E8EEF5; }')

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
        self.tabs.addTab(self.tree, "Contenido")

        self.view = QTextBrowser()
        self.view.setOpenExternalLinks(False)
        self.view.document().setDefaultStyleSheet(_CSS)
        self.view.setStyleSheet(
            'QTextBrowser { background:#FFFFFF; border:none; padding:14px 20px; }')

        split.addWidget(self.tabs)
        split.addWidget(self.view)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setCollapsible(0, False)
        split.setSizes([270, 640])
        root.addWidget(split, 1)

        # Estado de navegacion
        self._idx = -1
        if self._orden:
            self._mostrar_indice(0)

    # ── Barra ───────────────────────────────────────────────────
    def _crear_barra(self):
        barra = QWidget()
        barra.setStyleSheet("background:#F0F0EE;")
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(6, 4, 6, 4); lay.setSpacing(4)

        def _btn(texto, icono, slot):
            b = QToolButton()
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            b.setText(texto); b.setIcon(icono); b.setIconSize(QSize(18, 18))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                'QToolButton { font-family:"Arial Narrow","Arial"; font-size:12px;'
                ' color:#000000; border:1px solid transparent; padding:3px 8px; }'
                'QToolButton:hover { background:#E0E6EE; border:1px solid #C0C8D2; }'
                'QToolButton:disabled { color:#A8A8A8; }')
            b.clicked.connect(slot)
            return b

        self.btn_ocultar = _btn("Ocultar", _mk_icon(_dib_ocultar), self._toggle_arbol)
        self.btn_atras = _btn("Atrás", _mk_icon(_dib_atras), lambda: self._navegar(-1))
        self.btn_adelante = _btn("Adelante", _mk_icon(_dib_adelante), lambda: self._navegar(1))
        lay.addWidget(self.btn_ocultar)
        sep = _QFrame(); sep.setFrameShape(_QFrame.Shape.VLine)
        sep.setStyleSheet("color:#CFCFCF;"); sep.setFixedWidth(1)
        lay.addWidget(sep)
        lay.addWidget(self.btn_atras)
        lay.addWidget(self.btn_adelante)
        lay.addStretch()
        return barra

    # ── Navegacion ──────────────────────────────────────────────
    def _toggle_arbol(self):
        self._arbol_visible = not getattr(self, '_arbol_visible', True)
        self.tabs.setVisible(self._arbol_visible)
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
