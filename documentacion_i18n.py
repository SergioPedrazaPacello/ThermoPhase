# -*- coding: utf-8 -*-
"""
Traducción del contenido HTML de la Documentación técnica.

El contenido de cada apartado está escrito en español en `documentacion.py`.
Este módulo traduce ese HTML al inglés cuando el idioma activo es EN,
sustituyendo cada bloque de texto (párrafo, encabezado o elemento de lista)
por su equivalente traducido. Las ecuaciones (marcadores @@EQ:...@@) son
universales y no se tocan.

El emparejamiento se hace por el TEXTO NORMALIZADO del bloque (colapsando
espacios), de modo que las etiquetas internas <sub>, <sup>, <em> se conservan
tal cual en la traducción. Un bloque sin entrada en el diccionario se deja en
español (degradación elegante), lo que permite ir traduciendo de forma
incremental sin romper nada.
"""
import re

# Diccionario ES -> EN a nivel de bloque de párrafo. La clave es el texto
# interior del bloque con los espacios colapsados a uno solo (sin las etiquetas
# <p>/<h2>/<h3>/<li> externas, pero conservando las etiquetas internas).
TRAD_DOC = {}


def _norm(s):
    """Normaliza el texto de un bloque: colapsa espacios en blanco."""
    return re.sub(r'\s+', ' ', s).strip()


_BLOQUE_RE = re.compile(r'<(h2|h3|p|li)>(.*?)</\1>', re.S)


def traducir_html(html, idioma):
    """Devuelve el HTML traducido al idioma dado ('ES' o 'EN').

    En ES devuelve el original. En EN sustituye el interior de cada bloque
    <h2>/<h3>/<p>/<li> por su traducción si existe en TRAD_DOC.
    """
    if idioma != 'EN':
        return html

    def repl(m):
        tag, inner = m.group(1), m.group(2)
        clave = _norm(inner)
        trad = TRAD_DOC.get(clave)
        if trad is None:
            return m.group(0)          # sin traducción: dejar en español
        return f'<{tag}>{trad}</{tag}>'

    return _BLOQUE_RE.sub(repl, html)


def registrar(pares):
    """Añade traducciones al diccionario. `pares` es una lista de (es, en)
    donde `es` es el texto del bloque en español (se normaliza) y `en` su
    traducción."""
    for es, en in pares:
        TRAD_DOC[_norm(es)] = en


# ══════════════════════════════════════════════════════════════════════
# Sección 9 — Poder calorífico y GPM
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("9.1 Poder calorífico y riqueza del gas",
     "9.1 Heating value and gas richness"),
    ("""El poder calorífico o valor calorífico de un gas cuantifica la energía
liberada por la combustión completa de una unidad de gas. Es una de las
propiedades comerciales más importantes en la industria del gas natural,
ya que fija el precio del gas vendido y determina si una corriente cumple
las especificaciones de un contrato de venta o de un gasoducto. El
programa calcula el poder calorífico para la fase vapor, la fase líquida
y la mezcla global en cada punto calculado.""",
     "The heating value or calorific value of a gas quantifies the energy "
     "released by the complete combustion of a unit of gas. It is one of the "
     "most important commercial properties in the natural gas industry, since "
     "it sets the price of the gas sold and determines whether a stream meets "
     "the specifications of a sales contract or a pipeline. The program "
     "computes the heating value for the vapour phase, the liquid phase and "
     "the overall mixture at each calculated point."),
    ("""Se reportan dos definiciones del poder calorífico. El poder calorífico
superior o bruto (HHV, por <em>higher heating value</em>) supone que el
agua producida en la combustión condensa a líquido, de modo que se
recupera su calor latente de vaporización. El poder calorífico inferior o
neto (LHV, por <em>lower heating value</em>) supone que el agua
permanece como vapor y no se recupera ese calor. La diferencia entre
ambos es precisamente el calor latente del agua formada.""",
     "Two definitions of heating value are reported. The higher or gross "
     "heating value (HHV) assumes that the water produced in combustion "
     "condenses to liquid, so that its latent heat of vaporization is "
     "recovered. The lower or net heating value (LHV) assumes that the water "
     "remains as vapour and that heat is not recovered. The difference "
     "between the two is precisely the latent heat of the water formed."),
    ("""Cada definición se expresa en dos bases. La base volumétrica se reporta
en BTU por pie cúbico de gas ideal a las condiciones estándar de 60 °F y
14.696 psia, que es la convención de las tablas GPSA y del software de
referencia. La base másica se reporta en BTU por libra. Adicionalmente se
reporta la riqueza en licuables mediante el GPM, que se describe en la
sección 9.4.""",
     "Each definition is expressed on two bases. The volumetric basis is "
     "reported in BTU per cubic foot of ideal gas at the standard conditions "
     "of 60 °F and 14.696 psia, which is the convention of the GPSA tables and "
     "of the reference software. The mass basis is reported in BTU per pound. "
     "In addition, the richness in liquefiables is reported through the GPM, "
     "described in section 9.4."),

    ("9.2 Cálculo del poder calorífico volumétrico",
     "9.2 Calculation of the volumetric heating value"),
    ("""El poder calorífico volumétrico de una fase se obtiene como el promedio
molar de los valores caloríficos de sus componentes puros, tal como
establece la referencia GPSA:""",
     "The volumetric heating value of a phase is obtained as the molar "
     "average of the calorific values of its pure components, as established "
     "by the GPSA reference:"),
    ("""donde z<sub>i</sub> es la fracción molar del componente i en la fase
considerada (vapor, líquido o mezcla) y VC<sub>i</sub> es el valor
calorífico volumétrico del componente puro en base gas ideal, tabulado a
60 °F y 14.696 psia. La ponderación por fracción molar es exacta en base
gas ideal porque el volumen molar es el mismo para todos los componentes
a esas condiciones.""",
     "where z<sub>i</sub> is the mole fraction of component i in the phase "
     "considered (vapour, liquid or mixture) and VC<sub>i</sub> is the "
     "volumetric calorific value of the pure component on an ideal-gas basis, "
     "tabulated at 60 °F and 14.696 psia. The mole-fraction weighting is exact "
     "on an ideal-gas basis because the molar volume is the same for all "
     "components at those conditions."),
    ("""Los valores por componente se toman de la tabla GPSA-87. Los
combustibles principales tienen, en BTU por pie cúbico, los valores netos
y brutos siguientes: metano 909.4 / 1010.0, etano 1618.7 / 1769.6,
propano 2314.9 / 2516.1, isobutano 3000.4 / 3251.9 y n-butano
3010.8 / 3262.3, creciendo de forma aproximadamente lineal con el número
de carbonos. El nitrógeno y el dióxido de carbono no son combustibles y
tienen valor calorífico nulo: actúan como diluyentes que reducen el poder
calorífico de la mezcla en proporción a su fracción molar.""",
     "The per-component values are taken from the GPSA-87 table. The main "
     "fuels have, in BTU per cubic foot, the following net and gross values: "
     "methane 909.4 / 1010.0, ethane 1618.7 / 1769.6, propane 2314.9 / 2516.1, "
     "isobutane 3000.4 / 3251.9 and n-butane 3010.8 / 3262.3, growing "
     "approximately linearly with carbon number. Nitrogen and carbon dioxide "
     "are not combustible and have zero calorific value: they act as diluents "
     "that reduce the heating value of the mixture in proportion to their mole "
     "fraction."),

    ("9.3 Conversión a base másica",
     "9.3 Conversion to a mass basis"),
    ("""Para obtener el poder calorífico en base másica se pasa primero de la
base volumétrica a la base molar multiplicando por el volumen molar del
gas ideal a condiciones estándar:""",
     "To obtain the heating value on a mass basis, one first converts from "
     "the volumetric basis to the molar basis by multiplying by the molar "
     "volume of the ideal gas at standard conditions:"),
    ("""El valor calorífico molar es entonces el volumétrico multiplicado por
ese volumen molar, y el valor másico se obtiene dividiendo por el peso
molecular de la fase:""",
     "The molar calorific value is then the volumetric one multiplied by that "
     "molar volume, and the mass value is obtained by dividing by the "
     "molecular weight of the phase:"),
    ("""donde M<sub>fase</sub> es el peso molecular de la fase, calculado como
el promedio molar de los pesos moleculares de sus componentes. El poder
calorífico volumétrico se expresa siempre en base gas ideal, de manera
que el valor de la fase líquida corresponde al que tendría su composición
si se evaporase a gas ideal, coherente con la convención de las tablas
GPSA y del software de referencia.""",
     "where M<sub>phase</sub> is the molecular weight of the phase, computed "
     "as the molar average of the molecular weights of its components. The "
     "volumetric heating value is always expressed on an ideal-gas basis, so "
     "that the value of the liquid phase corresponds to what its composition "
     "would have if it were vaporized to ideal gas, consistent with the "
     "convention of the GPSA tables and of the reference software."),

    ("9.4 Contenido de licuables (GPM)",
     "9.4 Liquefiable content (GPM)"),
    ("""El GPM, del inglés <em>gallons per thousand cubic feet</em>, mide el
contenido de hidrocarburos licuables recuperables de una corriente de
gas. Expresa cuántos galones de líquido se obtendrían a partir de mil
pies cúbicos de gas si se recuperasen los componentes de propano y más
pesados. Es un indicador directo de la riqueza del gas y del atractivo
económico de instalar una planta de extracción de licuables.""",
     "The GPM, from <em>gallons per thousand cubic feet</em>, measures the "
     "content of recoverable liquefiable hydrocarbons in a gas stream. It "
     "expresses how many gallons of liquid would be obtained from one thousand "
     "cubic feet of gas if the propane-and-heavier components were recovered. "
     "It is a direct indicator of the richness of the gas and of the economic "
     "attractiveness of installing a liquefiables extraction plant."),
    ("""El GPM se calcula sumando la contribución de cada componente C3+
ponderada por su fracción molar en el gas y por su factor de galones por
libra-mol, y refiriendo el resultado a mil pies cúbicos de gas ideal:""",
     "The GPM is computed by summing the contribution of each C3+ component "
     "weighted by its mole fraction in the gas and by its gallons-per-pound-"
     "mole factor, referring the result to one thousand cubic feet of ideal "
     "gas:"),
    ("""donde G<sub>i</sub> es el volumen líquido en galones por libra-mol del
componente i y V<sub>m</sub> es el volumen molar del gas ideal a
condiciones estándar. Los factores G<sub>i</sub> crecen con el tamaño
molecular: propano 10.433, isobutano 12.386, n-butano 11.937, isopentano
13.853 y n-pentano 13.712 galones por libra-mol, y así sucesivamente para
los más pesados.""",
     "where G<sub>i</sub> is the liquid volume in gallons per pound-mole of "
     "component i and V<sub>m</sub> is the molar volume of the ideal gas at "
     "standard conditions. The G<sub>i</sub> factors grow with molecular size: "
     "propane 10.433, isobutane 12.386, n-butane 11.937, isopentane 13.853 and "
     "n-pentane 13.712 gallons per pound-mole, and so on for the heavier ones."),
    ("""Solo los componentes de propano en adelante se contabilizan en el GPM,
puesto que el metano y el etano no se recuperan habitualmente como
líquido en las plantas de procesamiento convencionales. El nitrógeno y el
dióxido de carbono tampoco contribuyen. Por convención el GPM se reporta
para la fase gas, que es la corriente de la que se extraen los
licuables.""",
     "Only propane-and-heavier components are counted in the GPM, since "
     "methane and ethane are not usually recovered as liquid in conventional "
     "processing plants. Nitrogen and carbon dioxide do not contribute either. "
     "By convention the GPM is reported for the gas phase, which is the stream "
     "from which the liquefiables are extracted."),
    ("Referencias", "References"),
    ("""Gas Processors Suppliers Association (1987). <em>GPSA Engineering
Data Book</em>, 10.ª edición. Tulsa, Oklahoma.""",
     "Gas Processors Suppliers Association (1987). <em>GPSA Engineering "
     "Data Book</em>, 10th edition. Tulsa, Oklahoma."),
    ("""Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>,
volumen 1. Campbell Petroleum Series.""",
     "Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>, "
     "volume 1. Campbell Petroleum Series."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 10 — Formación de hidratos
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("10.1 Formación de hidratos de gas",
     "10.1 Gas hydrate formation"),
    ("""Los hidratos de gas son compuestos cristalinos de inclusión en los que
moléculas de agua forman una red de jaulas mediante enlaces de hidrógeno,
y moléculas de gas ligero quedan atrapadas dentro de esas cavidades. Se
forman cuando hidrocarburos ligeros u otros gases como el nitrógeno o el
dióxido de carbono están en contacto con agua a temperaturas bajas,
típicamente por debajo de unos 35 °C, y a presión elevada. A diferencia
del hielo, los hidratos pueden existir muy por encima del punto de
congelación del agua, de modo que constituyen un riesgo operativo aun a
temperaturas templadas.""",
     "Gas hydrates are crystalline inclusion compounds in which water "
     "molecules form a network of cages through hydrogen bonds, and light gas "
     "molecules become trapped inside those cavities. They form when light "
     "hydrocarbons or other gases such as nitrogen or carbon dioxide are in "
     "contact with water at low temperatures, typically below about 35 °C, and "
     "at high pressure. Unlike ice, hydrates can exist well above the freezing "
     "point of water, so they represent an operational risk even at mild "
     "temperatures."),
    ("""En la industria del gas los hidratos son un problema recurrente porque
pueden taponar tuberías, válvulas, estranguladores y equipos de
separación, con paradas de producción y riesgos de seguridad. Predecir
las condiciones de presión y temperatura a las que se forman permite
diseñar la deshidratación del gas o la inyección de inhibidores. El
programa calcula, para la composición del fluido, la temperatura de
formación de hidrato a una presión dada o la presión de formación a una
temperatura dada, siguiendo el modelo del software de referencia
PVTsim.""",
     "In the gas industry, hydrates are a recurring problem because they can "
     "plug pipelines, valves, chokes and separation equipment, causing "
     "production shutdowns and safety hazards. Predicting the pressure and "
     "temperature conditions at which they form makes it possible to design "
     "gas dehydration or inhibitor injection. For the fluid composition, the "
     "program computes the hydrate formation temperature at a given pressure, "
     "or the formation pressure at a given temperature, following the model of "
     "the reference software PVTsim."),
    ("""El programa considera las estructuras de hidrato I y II, que se
diferencian en el número y el tamaño de sus cavidades. La estructura I
tiene 46 moléculas de agua por celda unitaria, con 2 cavidades pequeñas y
6 grandes; la estructura II tiene 136 moléculas de agua, con 16 cavidades
pequeñas y 8 grandes. Para una composición dada, el programa determina
cuál de las dos estructuras es la estable en cada condición como aquella
de menor potencial químico del agua.""",
     "The program considers hydrate structures I and II, which differ in the "
     "number and size of their cavities. Structure I has 46 water molecules "
     "per unit cell, with 2 small cavities and 6 large ones; structure II has "
     "136 water molecules, with 16 small cavities and 8 large ones. For a "
     "given composition, the program determines which of the two structures is "
     "stable at each condition as the one with the lower chemical potential of "
     "water."),

    ("10.2 El modelo de van der Waals y Platteeuw",
     "10.2 The van der Waals and Platteeuw model"),
    ("""El cálculo de hidratos se basa en el modelo estadístico de adsorción de
van der Waals y Platteeuw (1959), en la forma práctica propuesta por
Munck y colaboradores (1988). La formación de hidrato se plantea como el
paso del agua desde su estado puro (líquido o hielo, estado α) hasta el
hidrato lleno (estado H), pasando por un estado intermedio hipotético de
red vacía (estado β). La diferencia de potencial químico del agua entre
el hidrato y el agua pura se descompone así en dos contribuciones:""",
     "The hydrate calculation is based on the statistical adsorption model of "
     "van der Waals and Platteeuw (1959), in the practical form proposed by "
     "Munck and coworkers (1988). Hydrate formation is posed as the passage of "
     "water from its pure state (liquid or ice, state α) to the filled hydrate "
     "(state H), through a hypothetical intermediate state of empty lattice "
     "(state β). The difference in chemical potential of water between the "
     "hydrate and pure water is thus decomposed into two contributions:"),
    ("""El primer término representa la estabilización de la red causada por la
adsorción de las moléculas de gas en las cavidades, y siempre reduce el
potencial químico. El segundo término es la diferencia entre la red vacía
hipotética y el agua pura, y se obtiene por termodinámica clásica. La
curva de formación de hidrato es el lugar de puntos de presión y
temperatura donde ambas contribuciones se cancelan:""",
     "The first term represents the stabilization of the lattice caused by "
     "the adsorption of gas molecules in the cavities, and it always lowers "
     "the chemical potential. The second term is the difference between the "
     "hypothetical empty lattice and pure water, and it is obtained from "
     "classical thermodynamics. The hydrate formation curve is the locus of "
     "pressure and temperature points where both contributions cancel:"),
    ("""A la izquierda de la curva la diferencia es negativa y el hidrato es
estable; a la derecha es positiva y el agua permanece como líquido o
hielo sin formar hidrato.""",
     "To the left of the curve the difference is negative and the hydrate is "
     "stable; to the right it is positive and the water remains as liquid or "
     "ice without forming hydrate."),

    ("10.3 Término de adsorción de Langmuir",
     "10.3 Langmuir adsorption term"),
    ("""La estabilización de la red por el gas atrapado se calcula con la
teoría de adsorción de Langmuir. La diferencia de potencial químico entre
la red vacía y la red llena se expresa como:""",
     "The stabilization of the lattice by the trapped gas is computed with "
     "Langmuir adsorption theory. The difference in chemical potential between "
     "the empty lattice and the filled lattice is expressed as:"),
    ("""donde ν<sub>i</sub> es el número de cavidades de tipo i por molécula de
agua e Y<sub>Ki</sub> es la probabilidad de que una cavidad de tipo i esté
ocupada por una molécula de gas de tipo K. Esta probabilidad de ocupación
sigue la isoterma de Langmuir:""",
     "where ν<sub>i</sub> is the number of cavities of type i per water "
     "molecule and Y<sub>Ki</sub> is the probability that a cavity of type i is "
     "occupied by a gas molecule of type K. This occupancy probability follows "
     "the Langmuir isotherm:"),
    ("""donde f<sub>K</sub> es la fugacidad del componente K en la fase de
hidrocarburos y C<sub>Ki</sub> es la constante de adsorción de Langmuir,
específica de cada componente, cada tipo de cavidad y cada estructura. La
constante de adsorción depende de la temperatura según la expresión de
dos parámetros de Munck:""",
     "where f<sub>K</sub> is the fugacity of component K in the hydrocarbon "
     "phase and C<sub>Ki</sub> is the Langmuir adsorption constant, specific to "
     "each component, each cavity type and each structure. The adsorption "
     "constant depends on temperature according to the two-parameter "
     "expression of Munck:"),
    ("""Los parámetros A<sub>Ki</sub> y B<sub>Ki</sub> se determinan por ajuste
a datos experimentales de formación de hidratos y son específicos de la
ecuación de estado seleccionada. El programa emplea los parámetros de la
base de datos de PVTsim, con un juego para las ecuaciones de la familia
Peng-Robinson y otro para las de la familia Soave-Redlich-Kwong, ya que
las fugacidades calculadas por cada ecuación son ligeramente distintas.""",
     "The parameters A<sub>Ki</sub> and B<sub>Ki</sub> are determined by "
     "fitting to experimental hydrate formation data and are specific to the "
     "selected equation of state. The program uses the parameters from the "
     "PVTsim database, with one set for the Peng-Robinson family of equations "
     "and another for the Soave-Redlich-Kwong family, since the fugacities "
     "computed by each equation are slightly different."),

    ("10.4 Término de referencia del agua",
     "10.4 Water reference term"),
    ("""La diferencia de potencial químico entre la red vacía y el agua pura se
obtiene por integración de la relación termodinámica fundamental entre
los estados β y α, con la presión de referencia tomada como cero:""",
     "The difference in chemical potential between the empty lattice and pure "
     "water is obtained by integrating the fundamental thermodynamic relation "
     "between states β and α, with the reference pressure taken as zero:"),
    ("""donde T<sub>0</sub> es la temperatura de referencia de 273.15 K, Δμ<sub>0</sub>
es la diferencia de potencial químico a esa temperatura, ΔH<sub>0</sub> es
la diferencia de entalpía, ΔC<sub>p</sub> la diferencia de capacidad
calorífica, ΔV la diferencia de volumen molar y T̄ = (T + T<sub>0</sub>)/2
la temperatura media que aproxima la dependencia del término de presión.
Los valores de ΔH y ΔV distinguen si el agua de referencia está como
líquido o como hielo, con el cambio a 273.15 K.""",
     "where T<sub>0</sub> is the reference temperature of 273.15 K, "
     "Δμ<sub>0</sub> is the chemical potential difference at that temperature, "
     "ΔH<sub>0</sub> is the enthalpy difference, ΔC<sub>p</sub> the heat "
     "capacity difference, ΔV the molar volume difference and "
     "T̄ = (T + T<sub>0</sub>)/2 the mean temperature that approximates the "
     "dependence of the pressure term. The values of ΔH and ΔV distinguish "
     "whether the reference water is liquid or ice, switching at 273.15 K."),
    ("""Las constantes de referencia son específicas de cada estructura y de la
ecuación de estado. Para la estructura I se emplean los valores de
Erickson: Δμ<sub>0</sub> = 1264 J/mol, ΔH<sub>0</sub> = −4858 J/mol en
agua líquida y ΔV = 4.6 cm³/mol. Para la estructura II el programa usa
constantes ligeramente ajustadas por ecuación de estado, próximas a
Δμ<sub>0</sub> = 883 J/mol, que reproducen las curvas de referencia de
PVTsim con una precisión del orden de la centésima de grado Rankine.""",
     "The reference constants are specific to each structure and to the "
     "equation of state. For structure I the Erickson values are used: "
     "Δμ<sub>0</sub> = 1264 J/mol, ΔH<sub>0</sub> = −4858 J/mol in liquid "
     "water and ΔV = 4.6 cm³/mol. For structure II the program uses constants "
     "slightly tuned per equation of state, close to Δμ<sub>0</sub> = 883 "
     "J/mol, which reproduce the PVTsim reference curves to a precision on the "
     "order of a hundredth of a degree Rankine."),

    ("10.5 Fugacidad de mezcla y flujo de cálculo",
     "10.5 Mixture fugacity and calculation flow"),
    ("""La adsorción de Langmuir usa la fugacidad de cada componente formador
en la fase de hidrocarburos. Un aspecto decisivo del cálculo es que a lo
largo de la curva de hidratos la mezcla de hidrocarburos no está
necesariamente en una sola fase: con frecuencia coexisten una fase gas y
una fase líquida de hidrocarburos, o el fluido es un líquido denso. Por
ello el programa realiza un cálculo flash bien convergido en cada punto y
emplea la fugacidad de mezcla, es decir, el promedio molar de la fugacidad
de cada componente sobre las fases de hidrocarburos presentes. En
equilibrio la fugacidad de un componente es igual en todas las fases, de
modo que este promedio es consistente. Evaluar la fugacidad tratando la
composición global como una sola fase produciría errores apreciables en
la zona donde la mezcla es bifásica.""",
     "Langmuir adsorption uses the fugacity of each former component in the "
     "hydrocarbon phase. A decisive aspect of the calculation is that along "
     "the hydrate curve the hydrocarbon mixture is not necessarily in a single "
     "phase: a gas phase and a hydrocarbon liquid phase frequently coexist, or "
     "the fluid is a dense liquid. The program therefore performs a "
     "well-converged flash calculation at each point and uses the mixture "
     "fugacity, that is, the molar average of the fugacity of each component "
     "over the hydrocarbon phases present. At equilibrium the fugacity of a "
     "component is equal in all phases, so this average is consistent. "
     "Evaluating the fugacity by treating the overall composition as a single "
     "phase would produce appreciable errors in the region where the mixture "
     "is two-phase."),
    ("""Para trazar un punto de la curva se fija una de las dos variables,
presión o temperatura, y se resuelve la otra buscando la condición en que
el potencial químico del hidrato iguala al del agua pura. La curva de
hidratos puede ser monótona, como ocurre en gases ricos en metano, o
tener forma cerrada con dos ramas, como sucede en mezclas sin metano; el
programa localiza las raíces del criterio mediante un barrido que detecta
los cambios de signo y toma la frontera de formación correspondiente. Se
evalúan las estructuras I y II y se reporta la de menor potencial químico
como la estable.""",
     "To trace a point of the curve, one of the two variables, pressure or "
     "temperature, is fixed and the other is solved by seeking the condition "
     "at which the chemical potential of the hydrate equals that of pure "
     "water. The hydrate curve can be monotonic, as happens in methane-rich "
     "gases, or have a closed shape with two branches, as occurs in mixtures "
     "without methane; the program locates the roots of the criterion through "
     "a scan that detects sign changes and takes the corresponding formation "
     "boundary. Structures I and II are evaluated and the one with the lower "
     "chemical potential is reported as the stable one."),
    ("""El resultado del cálculo incluye la temperatura o presión de formación
de hidrato y, en esas condiciones, el flash de la mezcla de hidrocarburos
con la composición de cada fase y sus propiedades. El efecto del contenido
de agua de la mezcla sobre la curva es despreciable, por lo que el cálculo
se realiza sin necesidad de resolver la fase acuosa.""",
     "The calculation result includes the hydrate formation temperature or "
     "pressure and, at those conditions, the flash of the hydrocarbon mixture "
     "with the composition of each phase and its properties. The effect of the "
     "water content of the mixture on the curve is negligible, so the "
     "calculation is performed without needing to solve the aqueous phase."),
    ("""van der Waals, J.H. y Platteeuw, J.C. (1959). Clathrate Solutions.
<em>Advances in Chemical Physics</em>, 2, pp. 1-57.""",
     "van der Waals, J.H. and Platteeuw, J.C. (1959). Clathrate Solutions. "
     "<em>Advances in Chemical Physics</em>, 2, pp. 1-57."),
    ("""Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). Computations of
the Formation of Gas Hydrates. <em>Chemical Engineering Science</em>, 43,
pp. 2661-2672.""",
     "Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). Computations "
     "of the Formation of Gas Hydrates. <em>Chemical Engineering Science</em>, "
     "43, pp. 2661-2672."),
    ("""Michelsen, M.L. (1991). Calculation of Hydrate Fugacities.
<em>Chemical Engineering Science</em>, 46, pp. 1192-1193.""",
     "Michelsen, M.L. (1991). Calculation of Hydrate Fugacities. "
     "<em>Chemical Engineering Science</em>, 46, pp. 1192-1193."),
    ("""Erickson, D.D. (1983). Development of a Natural Gas Hydrate Prediction
Computer Program. Tesis de maestría, Colorado School of Mines.""",
     "Erickson, D.D. (1983). Development of a Natural Gas Hydrate Prediction "
     "Computer Program. Master's thesis, Colorado School of Mines."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 1 — Fundamentos de las EOS cúbicas
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("1.1 Ecuación de estado", "1.1 Equation of state"),
    ("""Una ecuación de estado (EOS, por <i>Equation of State</i>) es una relación matemática que vincula las tres variables que describen el estado de un fluido: la presión (P), el volumen molar (V) y la temperatura (T). Conocidas dos de ellas, la EOS entrega la tercera, y a partir de ella todas las propiedades termodinámicas derivadas.""",
     "An equation of state (EOS) is a mathematical relation that links the three variables describing the state of a fluid: pressure (P), molar volume (V) and temperature (T). Given two of them, the EOS delivers the third, and from it all the derived thermodynamic properties."),
    ("""El objetivo práctico es responder: a estas condiciones de presión y temperatura, ¿mi mezcla de hidrocarburos es líquido, gas o coexisten ambas fases? Todo eso se deriva de una buena ecuación de estado.""",
     "The practical goal is to answer: at these pressure and temperature conditions, is my hydrocarbon mixture a liquid, a gas, or do both phases coexist? All of that is derived from a good equation of state."),
    ("""El punto de partida es la ecuación del gas ideal, la ecuación de estado más simple:""",
     "The starting point is the ideal-gas equation, the simplest equation of state:"),
    ("""donde n es el número de moles y R es la constante universal de los gases. El motor de ThermoPhase trabaja internamente en unidades de campo, por lo que emplea el valor R = 10.7316 psi·ft³/(lb-mol·°R).""",
     "where n is the number of moles and R is the universal gas constant. The ThermoPhase engine works internally in field units, so it uses the value R = 10.7316 psi·ft³/(lb-mol·°R)."),
    ("""El gas ideal supone dos cosas que la realidad no cumple:""",
     "The ideal gas assumes two things that reality does not satisfy:"),
    ("""Las moléculas no ocupan volumen propio (se tratan como puntos).""",
     "Molecules occupy no volume of their own (they are treated as points)."),
    ("""Las moléculas no ejercen fuerzas entre sí (ni se atraen ni se repelen).""",
     "Molecules exert no forces on each other (they neither attract nor repel)."),
    ("""A bajas presiones y altas temperaturas esa idealización es razonable, porque las moléculas están muy separadas y su tamaño e interacciones son despreciables. Pero en un yacimiento o una planta de procesamiento (altas presiones, moléculas muy empaquetadas) ambas suposiciones fallan por completo. Corregir esas dos deficiencias es exactamente lo que hacen las ecuaciones de estado cúbicas, y por eso son la herramienta central de este programa.""",
     "At low pressures and high temperatures that idealization is reasonable, because the molecules are far apart and their size and interactions are negligible. But in a reservoir or a processing plant (high pressures, tightly packed molecules) both assumptions fail completely. Correcting those two deficiencies is exactly what cubic equations of state do, and that is why they are the central tool of this program."),

    ("1.2 Del gas ideal a los fluidos reales", "1.2 From ideal gas to real fluids"),
    ("""Para acercar el modelo a la realidad se introducen dos correcciones sobre la ecuación del gas ideal, cada una atacando una de las suposiciones falsas.""",
     "To bring the model closer to reality, two corrections are introduced on the ideal-gas equation, each attacking one of the false assumptions."),
    ("Corrección por volumen propio (corrección por repulsión)",
     "Own-volume correction (repulsion correction)"),
    ("""Las moléculas sí ocupan espacio. Por lo tanto, el volumen realmente disponible para que se muevan no es V, sino V menos un volumen mínimo que ocupan las propias moléculas. A ese volumen excluido se le llama covolumen (b), que es el volumen ocupado por un mol de moléculas. El término de presión se corrige reemplazando V por (V menos n·b), donde n es el número de moles:""",
     "Molecules do occupy space. Therefore the volume actually available for them to move in is not V, but V minus a minimum volume occupied by the molecules themselves. That excluded volume is called the co-volume (b), the volume occupied by one mole of molecules. The pressure term is corrected by replacing V with (V minus n·b), where n is the number of moles:"),
    ("""Cuando V se aproxima a n·b, el denominador tiende a cero y la presión se dispara hacia el infinito. Físicamente esto expresa que es imposible comprimir el fluido más allá del volumen que ocupan sus propias moléculas: ese es el límite duro de la fase líquida. Se le llama repulsión porque, a distancias muy cortas, las nubes electrónicas de las moléculas se repelen con fuerza y actúan como esferas casi rígidas.""",
     "When V approaches n·b, the denominator tends to zero and the pressure shoots to infinity. Physically this expresses that it is impossible to compress the fluid beyond the volume occupied by its own molecules: that is the hard limit of the liquid phase. It is called repulsion because, at very short distances, the electron clouds of the molecules repel strongly and act as nearly rigid spheres."),
    ("Corrección por fuerzas atractivas (corrección por atracción)",
     "Attractive-force correction (attraction correction)"),
    ("""Las moléculas también se atraen entre sí mediante fuerzas de atracción intermolecular. Esa atracción tiende a juntarlas y, en consecuencia, reduce la presión que ejercen sobre las paredes del recipiente respecto de la que ejercería un gas ideal. Por eso al término repulsivo se le resta un término atractivo:""",
     "Molecules also attract one another through intermolecular attractive forces. That attraction tends to draw them together and, consequently, reduces the pressure they exert on the walls of the vessel relative to what an ideal gas would exert. An attractive term is therefore subtracted from the repulsive term:"),
    ("""Una forma intuitiva de verlo: una molécula que está a punto de golpear la pared del recipiente es frenada por la atracción de las moléculas que quedan detrás de ella. Ese tirón hacia adentro disminuye la fuerza del impacto y, por lo tanto, la presión medida. El término atractivo es la traducción matemática de ese tirón, y es lo que hace posible que exista una fase líquida: sin atracción, nada mantendría a las moléculas unidas.""",
     "An intuitive way to see it: a molecule about to hit the wall of the vessel is slowed by the attraction of the molecules behind it. That inward pull decreases the force of the impact and therefore the measured pressure. The attractive term is the mathematical translation of that pull, and it is what makes a liquid phase possible: without attraction, nothing would hold the molecules together."),

    ("1.3 Término de repulsión", "1.3 Repulsion term"),
    ("""Dentro del término de repulsión de la EOS se encuentra el covolumen b, que representa el volumen molar mínimo al que se puede comprimir una sustancia; es, en esencia, el espacio que las propias moléculas ocupan y del que ningún otro cuerpo puede disponer. Su papel en la ecuación es doble.""",
     "Within the repulsion term of the EOS is the co-volume b, which represents the minimum molar volume to which a substance can be compressed; it is, in essence, the space that the molecules themselves occupy and that no other body can use. Its role in the equation is twofold."),
    ("""El primer papel es fijar el límite físico de compresibilidad: no se puede comprimir el fluido más allá del tamaño de sus propias moléculas. En la ecuación esto se ve porque, cuando el volumen se acerca a n·b, el denominador (V menos n·b) tiende a cero y la presión tiende a infinito.""",
     "The first role is to set the physical limit of compressibility: the fluid cannot be compressed beyond the size of its own molecules. In the equation this is seen because, when the volume approaches n·b, the denominator (V minus n·b) tends to zero and the pressure tends to infinity."),
    ("""El segundo papel es fijar la escala de la rama líquida de la isoterma. Conviene explicarlo con calma. Si se dibuja la presión frente al volumen a temperatura constante (una isoterma), la parte de la curva que corresponde al líquido es casi vertical: el líquido es muy poco compresible, de modo que grandes cambios de presión producen cambios mínimos de volumen. ¿Dónde se ubica esa pared casi vertical sobre el eje del volumen? Justamente cerca de n·b, porque el líquido no puede tener un volumen menor que el que ocupan sus moléculas. Por eso se dice que b fija la escala de la rama líquida: es el valor alrededor del cual se acomodan los volúmenes del líquido y, por lo tanto, determina la densidad máxima que el modelo le asigna a la fase líquida. En términos físicos, un covolumen mayor (moléculas más grandes) desplaza esa pared hacia volúmenes mayores y predice un líquido menos denso; un covolumen menor la desplaza hacia volúmenes pequeños y predice un líquido más denso.""",
     "The second role is to set the scale of the liquid branch of the isotherm. It is worth explaining calmly. If one plots pressure against volume at constant temperature (an isotherm), the part of the curve corresponding to the liquid is nearly vertical: the liquid is very slightly compressible, so large pressure changes produce minimal volume changes. Where is that nearly vertical wall located on the volume axis? Precisely near n·b, because the liquid cannot have a volume smaller than the one its molecules occupy. That is why b is said to set the scale of the liquid branch: it is the value around which the liquid volumes settle and therefore determines the maximum density the model assigns to the liquid phase. In physical terms, a larger co-volume (larger molecules) shifts that wall toward larger volumes and predicts a less dense liquid; a smaller co-volume shifts it toward small volumes and predicts a denser liquid."),
    ("""El valor de b no se ajusta a ojo ni se mide directamente: se deduce obligando a que la ecuación reproduzca de forma exacta el punto crítico de la sustancia. El punto crítico es un estado muy particular (se detalla en la sección de propiedades críticas) en el que líquido y gas se vuelven idénticos; matemáticamente, la isoterma que pasa por él tiene una forma geométrica precisa. Al imponerle a la EOS que respete esa forma en el punto crítico se obtienen ecuaciones que despejan b (y también el parámetro de atracción) en función de datos que sí se conocen y tabulan: la temperatura y la presión críticas. El resultado es:""",
     "The value of b is not adjusted by eye nor measured directly: it is deduced by forcing the equation to reproduce exactly the critical point of the substance. The critical point is a very particular state (detailed in the critical properties section) at which liquid and gas become identical; mathematically, the isotherm passing through it has a precise geometric shape. By requiring the EOS to respect that shape at the critical point, one obtains equations that solve for b (and also the attraction parameter) as functions of data that are indeed known and tabulated: the critical temperature and pressure. The result is:"),
    ("""donde el número adimensional <b>&Omega;<sub>b</sub></b> depende únicamente de la forma de la ecuación elegida (toma un valor para Peng-Robinson y otro para SRK). Conviene resaltar una consecuencia importante: b depende sólo de las propiedades críticas del componente y no de la temperatura de operación. Es, por lo tanto, una constante para cada sustancia, que ThermoPhase calcula una sola vez a partir de la base de datos de propiedades.""",
     "where the dimensionless number <b>&Omega;<sub>b</sub></b> depends only on the form of the chosen equation (it takes one value for Peng-Robinson and another for SRK). It is worth highlighting an important consequence: b depends only on the critical properties of the component and not on the operating temperature. It is, therefore, a constant for each substance, which ThermoPhase computes only once from the properties database."),
    ("""Cuando se trabaja con una mezcla y no con un componente puro, el covolumen de la mezcla se obtiene sumando linealmente los aportes de cada componente, ponderados por su fracción molar. Ésta es la regla de mezclado que el programa aplica en la función que evalúa <b>b<sub>m</sub></b>:""",
     "When working with a mixture rather than a pure component, the co-volume of the mixture is obtained by linearly summing the contributions of each component, weighted by its mole fraction. This is the mixing rule the program applies in the function that evaluates <b>b<sub>m</sub></b>:"),
    ("""La linealidad tiene sentido físico directo: el volumen que ocupan las moléculas de una mezcla es simplemente la suma de los volúmenes que ocupa cada especie, sin efectos cruzados apreciables. Esto contrasta con el término de atracción, que sí requiere una regla más elaborada porque involucra interacciones entre pares de moléculas distintas.""",
     "The linearity has direct physical meaning: the volume occupied by the molecules of a mixture is simply the sum of the volumes occupied by each species, without appreciable cross effects. This contrasts with the attraction term, which does require a more elaborate rule because it involves interactions between pairs of different molecules."),

    ("1.4 Término de atracción", "1.4 Attraction term"),
    ("""El término de atracción es el corazón de una ecuación de estado cúbica y el que más influye en la calidad de las predicciones de equilibrio. Se construye como el producto de dos factores: uno que fija la magnitud de la atracción molecular y otro que introduce la dependencia con la temperatura.""",
     "The attraction term is the heart of a cubic equation of state and the one that most influences the quality of the equilibrium predictions. It is built as the product of two factors: one that sets the magnitude of the molecular attraction and another that introduces the temperature dependence."),
    ("""El primer factor, <b>a<sub>c</sub></b>, establece cuán intensa es la atracción de la sustancia. Al igual que el covolumen, se obtiene obligando a la ecuación a reproducir el punto crítico. La idea física es la misma que con b: en el punto crítico la isoterma tiene una forma geométrica única (una inflexión con tangente horizontal, es decir, una zona momentáneamente plana), y al exigir que la EOS respete esa forma se despeja a_c en función de datos conocidos, la temperatura y la presión críticas. Así, a_c queda anclado a propiedades medibles y no a un ajuste arbitrario:""",
     "The first factor, <b>a<sub>c</sub></b>, sets how intense the attraction of the substance is. Like the co-volume, it is obtained by forcing the equation to reproduce the critical point. The physical idea is the same as with b: at the critical point the isotherm has a unique geometric shape (an inflection with horizontal tangent, that is, a momentarily flat region), and by requiring the EOS to respect that shape one solves for a_c as a function of known data, the critical temperature and pressure. Thus a_c is anchored to measurable properties and not to an arbitrary adjustment:"),
    ("""El segundo factor, α(T), es una función adimensional de la temperatura que vale exactamente 1 en el punto crítico y crece a medida que la temperatura disminuye. Su sentido físico es capturar cómo cambia la fuerza atractiva efectiva con la temperatura: al enfriar el fluido, las moléculas se mueven más despacio, permanecen más tiempo cerca unas de otras y su atracción efectiva aumenta, de modo que α crece; al calentarlo, la agitación térmica vence a la atracción y α disminuye hasta valer 1 en el punto crítico. Su forma, propuesta por Soave y adoptada también por Peng-Robinson, es:""",
     "The second factor, α(T), is a dimensionless function of temperature that equals exactly 1 at the critical point and grows as the temperature decreases. Its physical meaning is to capture how the effective attractive force changes with temperature: on cooling the fluid, the molecules move more slowly, stay near one another longer and their effective attraction increases, so α grows; on heating it, thermal agitation overcomes attraction and α decreases until it equals 1 at the critical point. Its form, proposed by Soave and also adopted by Peng-Robinson, is:"),
    ("""El coeficiente m es una función del factor acéntrico ω (se detalla más adelante) y toma expresiones distintas para Peng-Robinson y para SRK. Es el parámetro que ajusta cuán rápido crece la atracción al enfriar el fluido.""",
     "The coefficient m is a function of the acentric factor ω (detailed later) and takes different expressions for Peng-Robinson and for SRK. It is the parameter that adjusts how fast the attraction grows on cooling the fluid."),
    ("""La consecuencia de esta dependencia con la temperatura es fundamental: en el punto crítico (α igual a 1) la distinción entre líquido y gas desaparece; por debajo de él, la atracción crece lo suficiente como para permitir que el fluido condense. Sin esta dependencia, la ecuación no podría reproducir correctamente las presiones de vapor de los componentes, que son precisamente el dato que ancla todo el equilibrio de fases.""",
     "The consequence of this temperature dependence is fundamental: at the critical point (α equal to 1) the distinction between liquid and gas disappears; below it, the attraction grows enough to allow the fluid to condense. Without this dependence, the equation could not correctly reproduce the vapour pressures of the components, which are precisely the data that anchor the entire phase equilibrium."),
    ("""En una mezcla, la magnitud de la atracción se obtiene con la regla de mezclado cuadrática, que suma las interacciones entre todos los pares de moléculas. ThermoPhase evalúa <b>a<sub>m</sub></b> con esta expresión cada vez que necesita las propiedades de una fase:""",
     "In a mixture, the magnitude of the attraction is obtained with the quadratic mixing rule, which sums the interactions between all pairs of molecules. ThermoPhase evaluates <b>a<sub>m</sub></b> with this expression each time it needs the properties of a phase:"),
    ("""donde el factor (1 menos k_ij) corrige la atracción entre moléculas de especies distintas. Esta regla y el significado de los coeficientes k_ij se desarrollan en la sección de parámetros.""",
     "where the factor (1 minus k_ij) corrects the attraction between molecules of different species. This rule and the meaning of the k_ij coefficients are developed in the parameters section."),

    ("1.5 Ecuación de Peng-Robinson (PR)", "1.5 Peng-Robinson equation (PR)"),
    ("""Publicada por Ding-Yu Peng y Donald Robinson en 1976, la ecuación de Peng-Robinson es hoy la más utilizada en la industria del petróleo y el gas, y es la opción por defecto de ThermoPhase. Su forma completa es:""",
     "Published by Ding-Yu Peng and Donald Robinson in 1976, the Peng-Robinson equation is today the most widely used in the oil and gas industry, and is the default option in ThermoPhase. Its full form is:"),
    ("""Lo que distingue a Peng-Robinson de ecuaciones anteriores es el denominador del término atractivo. Su estructura fue elegida deliberadamente para mejorar la predicción de las densidades de la fase líquida, que en modelos previos resultaban poco realistas. Las constantes que la definen son:""",
     "What distinguishes Peng-Robinson from earlier equations is the denominator of the attractive term. Its structure was deliberately chosen to improve the prediction of liquid-phase densities, which in previous models were unrealistic. The constants that define it are:"),
    ("""y el coeficiente m de la función α(T) se calcula a partir del factor acéntrico mediante el polinomio ajustado por sus autores:""",
     "and the coefficient m of the α(T) function is computed from the acentric factor through the polynomial fitted by its authors:"),
    ("""La combinación de un buen ajuste del equilibrio líquido-vapor de hidrocarburos con densidades de líquido más realistas es la razón por la cual Peng-Robinson se ha vuelto el estándar de la industria.""",
     "The combination of a good fit of the vapour-liquid equilibrium of hydrocarbons with more realistic liquid densities is the reason Peng-Robinson has become the industry standard."),

    ("1.6 Ecuación de Soave-Redlich-Kwong (SRK)", "1.6 Soave-Redlich-Kwong equation (SRK)"),
    ("""Propuesta por Giorgio Soave en 1972 como mejora de la ecuación de Redlich-Kwong de 1949, la ecuación SRK fue la primera EOS cúbica capaz de reproducir con buena precisión las presiones de vapor de los hidrocarburos, al introducir la función α(T) dependiente del factor acéntrico. Su forma es:""",
     "Proposed by Giorgio Soave in 1972 as an improvement of the 1949 Redlich-Kwong equation, the SRK equation was the first cubic EOS able to reproduce the vapour pressures of hydrocarbons with good accuracy, by introducing the α(T) function dependent on the acentric factor. Its form is:"),
    ("""La diferencia respecto de Peng-Robinson está en el denominador del término atractivo, que aquí es simplemente V(V+b), y en el valor de las constantes:""",
     "The difference from Peng-Robinson is in the denominator of the attractive term, which here is simply V(V+b), and in the value of the constants:"),
    ("""El coeficiente m de SRK tiene su propia correlación con el factor acéntrico:""",
     "The coefficient m of SRK has its own correlation with the acentric factor:"),
    ("""SRK y Peng-Robinson comparten la misma filosofía (repulsión más atracción dependiente de la temperatura) y difieren sólo en la forma del denominador atractivo, que cambia la manera en que se reparte el volumen entre las fases. En la práctica, SRK tiende a sobrestimar el volumen de la fase líquida, mientras que Peng-Robinson lo corrige mejor. Sin embargo, ambas producen composiciones de equilibrio muy similares, por lo que la elección entre una y otra suele depender de con qué software de referencia se desee comparar.""",
     "SRK and Peng-Robinson share the same philosophy (repulsion plus temperature-dependent attraction) and differ only in the form of the attractive denominator, which changes how the volume is distributed between the phases. In practice, SRK tends to overestimate the volume of the liquid phase, while Peng-Robinson corrects it better. However, both produce very similar equilibrium compositions, so the choice between them usually depends on which reference software one wishes to compare with."),

    ("1.7 Forma cúbica de la ecuación de estado", "1.7 Cubic form of the equation of state"),
    ("""Resolver la ecuación de estado directamente para el volumen es incómodo. Es mucho más práctico trabajar con el factor de compresibilidad Z, que es una medida adimensional de cuánto se aleja el fluido del comportamiento ideal. Se define como:""",
     "Solving the equation of state directly for the volume is awkward. It is much more practical to work with the compressibility factor Z, a dimensionless measure of how far the fluid departs from ideal behaviour. It is defined as:"),
    ("""Una forma equivalente y muy intuitiva de entender Z es como el cociente entre el volumen real que ocupa el fluido y el volumen que ocuparía si fuera un gas ideal a la misma presión y temperatura:""",
     "An equivalent and very intuitive way to understand Z is as the ratio between the real volume the fluid occupies and the volume it would occupy if it were an ideal gas at the same pressure and temperature:"),
    ("""De aquí se ve la relación de Z con la repulsión y la atracción. Cuando domina la repulsión (a alta presión, con las moléculas muy juntas y resistiéndose a la compresión), el fluido ocupa más volumen del que ocuparía un gas ideal, de modo que Z es mayor que 1. Cuando domina la atracción (las moléculas se juntan más de lo que lo haría un gas ideal), el fluido ocupa menos volumen y Z es menor que 1. Un gas ideal, sin fuerzas, tiene Z igual a 1, y un líquido comprimido, con las moléculas casi en contacto, tiene un Z pequeño.""",
     "From here one sees the relation of Z to repulsion and attraction. When repulsion dominates (at high pressure, with the molecules very close together and resisting compression), the fluid occupies more volume than an ideal gas would, so Z is greater than 1. When attraction dominates (the molecules come together more than an ideal gas would), the fluid occupies less volume and Z is less than 1. An ideal gas, with no forces, has Z equal to 1, and a compressed liquid, with the molecules almost in contact, has a small Z."),
    ("""Para reescribir la ecuación en términos de Z se definen dos grupos adimensionales que concentran toda la información de la sustancia y del estado:""",
     "To rewrite the equation in terms of Z, two dimensionless groups are defined that concentrate all the information about the substance and the state:"),
    ("""Sustituyendo, la ecuación de estado se transforma en un polinomio de tercer grado en Z. La forma del polinomio depende de la ecuación. Para Peng-Robinson es:""",
     "Substituting, the equation of state transforms into a third-degree polynomial in Z. The form of the polynomial depends on the equation. For Peng-Robinson it is:"),
    ("""Los grupos adimensionales A y B se definen igual para SRK, pero como su término atractivo tiene otra forma, el polinomio cúbico de SRK es distinto:""",
     "The dimensionless groups A and B are defined the same way for SRK, but since its attractive term has another form, the SRK cubic polynomial is different:"),
    ("""De aquí proviene el nombre de ecuaciones cúbicas: siempre conducen a un polinomio de tercer grado, que ThermoPhase resuelve de forma analítica (no iterativa) mediante las funciones internas de solución del cúbico, una para Peng-Robinson y otra para SRK.""",
     "This is where the name cubic equations comes from: they always lead to a third-degree polynomial, which ThermoPhase solves analytically (non-iteratively) through the internal cubic-solving functions, one for Peng-Robinson and another for SRK."),
    ("""Un polinomio cúbico puede tener una o tres raíces reales. Cuando hay tres, la raíz mayor normalmente corresponde a la fase vapor (mayor volumen, menor densidad) y la raíz menor a la fase líquida (menor volumen, mayor densidad); la raíz intermedia carece de significado físico porque corresponde a una región mecánicamente inestable. Que aparezcan tres raíces reales es precisamente la señal matemática de que, a esas condiciones, el fluido puede separarse en dos fases. Cómo se elige entre ellas se trata en la subsección siguiente.""",
     "A cubic polynomial can have one or three real roots. When there are three, the largest root normally corresponds to the vapour phase (larger volume, lower density) and the smallest to the liquid phase (smaller volume, higher density); the intermediate root has no physical meaning because it corresponds to a mechanically unstable region. The appearance of three real roots is precisely the mathematical signal that, at those conditions, the fluid can split into two phases. How to choose between them is treated in the next subsection."),

    ("1.8 Selección de la raíz por energía de Gibbs", "1.8 Root selection by Gibbs energy"),
    ("""Cuando el polinomio cúbico entrega tres raíces reales, hay que decidir cuál usar. Para entender el criterio conviene recordar qué es la energía libre de Gibbs: es una medida de la energía disponible de un sistema a presión y temperatura fijas, y la termodinámica establece que, en esas condiciones, todo sistema evoluciona espontáneamente hacia el estado de menor energía de Gibbs, igual que una pelota rueda hacia el punto más bajo de un terreno.""",
     "When the cubic polynomial delivers three real roots, one must decide which to use. To understand the criterion it helps to recall what Gibbs free energy is: it is a measure of the available energy of a system at fixed pressure and temperature, and thermodynamics establishes that, under those conditions, every system evolves spontaneously toward the state of lowest Gibbs energy, just as a ball rolls toward the lowest point of a terrain."),
    ("""Cada raíz del cúbico representa un estado posible del fluido (un volumen, una densidad). El criterio, entonces, es directo: de las raíces candidatas, la fase que realmente existe es la que tiene la menor energía de Gibbs, porque es hacia ese estado hacia el que la naturaleza lleva al sistema.""",
     "Each root of the cubic represents a possible state of the fluid (a volume, a density). The criterion is therefore direct: of the candidate roots, the phase that actually exists is the one with the lowest Gibbs energy, because that is the state toward which nature drives the system."),
    ("""Para una fase de composición dada, a la misma presión y temperatura, la energía de Gibbs molar (dividida por R·T para dejarla adimensional) se puede escribir a través de los coeficientes de fugacidad, que son la cantidad que la propia ecuación de estado entrega para cada raíz. Comparar dos raíces equivale entonces a comparar:""",
     "For a phase of given composition, at the same pressure and temperature, the molar Gibbs energy (divided by R·T to make it dimensionless) can be written through the fugacity coefficients, which are the quantity the equation of state itself delivers for each root. Comparing two roots is then equivalent to comparing:"),
    ("""Como la composición, la presión y la temperatura son idénticas para ambas raíces, la comparación se reduce a evaluar cuál raíz produce el menor valor de la suma de x_i por el logaritmo de su coeficiente de fugacidad. La raíz que minimiza esa suma es la estable, y es la que debe emplearse.""",
     "Since the composition, pressure and temperature are identical for both roots, the comparison reduces to evaluating which root produces the smaller value of the sum of x_i times the logarithm of its fugacity coefficient. The root that minimizes that sum is the stable one, and is the one to be used."),
    ("""En la práctica, cuando ThermoPhase sabe de antemano el rol de la fase, aplica directamente la consecuencia de este criterio: para las propiedades del vapor utiliza la raíz mayor del cúbico (la de mayor volumen, Z_V), y para el líquido la raíz menor (la de menor volumen, Z_L), porque en cada caso ésa es la raíz que minimiza la energía de Gibbs de esa fase. El criterio de mínima energía de Gibbs se vuelve indispensable en las situaciones ambiguas: cuando existe una sola raíz real, o cuando hay que decidir si un fluido monofásico debe tratarse como líquido o como vapor. En esos casos el programa evalúa la energía de Gibbs de las raíces disponibles y se queda con la de menor valor, dejando que sea la termodinámica, y no una regla fija, la que decida qué fase es la real.""",
     "In practice, when ThermoPhase knows in advance the role of the phase, it applies the consequence of this criterion directly: for the vapour properties it uses the largest root of the cubic (the one with the largest volume, Z_V), and for the liquid the smallest root (the smallest volume, Z_L), because in each case that is the root that minimizes the Gibbs energy of that phase. The minimum Gibbs energy criterion becomes indispensable in ambiguous situations: when there is a single real root, or when one must decide whether a single-phase fluid should be treated as liquid or as vapour. In those cases the program evaluates the Gibbs energy of the available roots and keeps the one with the lowest value, letting thermodynamics, and not a fixed rule, decide which phase is the real one."),

    ("1.9 Las cuatro variantes PR/SRK", "1.9 The four PR/SRK variants"),
    ("""ThermoPhase implementa cuatro ecuaciones de estado seleccionables, que surgen de combinar las dos formas cúbicas con dos conjuntos de parámetros, según el simulador comercial que se tome como referencia para la validación:""",
     "ThermoPhase implements four selectable equations of state, which arise from combining the two cubic forms with two sets of parameters, depending on the commercial simulator taken as a reference for validation:"),
    ("Peng-Robinson con parámetros HYSYS", "Peng-Robinson with HYSYS parameters"),
    ("SRK con parámetros HYSYS", "SRK with HYSYS parameters"),
    ("Peng-Robinson con parámetros PVTsim", "Peng-Robinson with PVTsim parameters"),
    ("SRK con parámetros PVTsim", "SRK with PVTsim parameters"),
    ("""Dentro de cada familia (Peng-Robinson o SRK) la forma de la ecuación es la misma; lo que cambia entre HYSYS y PVTsim son los valores tabulados de las propiedades críticas, los factores acéntricos y, sobre todo, los coeficientes de interacción binaria. Estas pequeñas diferencias en los datos de entrada se traducen en diferencias apreciables en la envolvente de fases, en especial cerca del punto crítico de la mezcla, y por eso poder alternar entre conjuntos de parámetros es útil para reproducir fielmente cada simulador de referencia.""",
     "Within each family (Peng-Robinson or SRK) the form of the equation is the same; what changes between HYSYS and PVTsim are the tabulated values of the critical properties, the acentric factors and, above all, the binary interaction coefficients. These small differences in the input data translate into appreciable differences in the phase envelope, especially near the critical point of the mixture, and that is why being able to switch between parameter sets is useful for faithfully reproducing each reference simulator."),
    ("""Un detalle que ThermoPhase respeta cuidadosamente es que HYSYS emplea para SRK un conjunto de factores acéntricos propio, distinto del que usa para Peng-Robinson, mientras que las temperaturas y presiones críticas son idénticas entre ambas. El programa enruta cada conjunto de factores acéntricos a la ecuación que corresponde, de modo que el flash de SRK usa los factores acéntricos de SRK y no los de Peng-Robinson.""",
     "A detail that ThermoPhase carefully respects is that HYSYS uses for SRK its own set of acentric factors, different from the one it uses for Peng-Robinson, while the critical temperatures and pressures are identical between the two. The program routes each set of acentric factors to the corresponding equation, so that the SRK flash uses the SRK acentric factors and not the Peng-Robinson ones."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 2 — Parámetros de la ecuación de estado
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("2.1 Propiedades críticas", "2.1 Critical properties"),
    ("""El punto crítico de una sustancia es el par de temperatura y presión (Tc, Pc) por encima del cual desaparece la distinción entre líquido y gas: por más que se comprima el fluido, ya no condensa. Es la piedra angular de toda ecuación de estado cúbica, porque los parámetros a y b se calibran justamente para que la ecuación reproduzca ese punto de manera exacta.""",
     "The critical point of a substance is the pair of temperature and pressure (Tc, Pc) above which the distinction between liquid and gas disappears: no matter how much the fluid is compressed, it no longer condenses. It is the cornerstone of every cubic equation of state, because the parameters a and b are calibrated precisely so that the equation reproduces that point exactly."),
    ("""Matemáticamente, en el punto crítico la isoterma presenta un punto de inflexión con tangente horizontal en el diagrama presión-volumen. Es decir, la primera y la segunda derivada de la presión respecto del volumen se anulan simultáneamente:""",
     "Mathematically, at the critical point the isotherm presents an inflection point with horizontal tangent in the pressure-volume diagram. That is, the first and second derivatives of pressure with respect to volume vanish simultaneously:"),
    ("""Imponer estas dos condiciones a la ecuación de estado es lo que fija los valores numéricos de Ω_a y Ω_b vistos en las secciones anteriores, y lo que liga a_c y b directamente a Tc y Pc. En otras palabras, las propiedades críticas no son un dato accesorio: son las que determinan por completo los parámetros de la ecuación para cada sustancia.""",
     "Imposing these two conditions on the equation of state is what fixes the numerical values of Ω_a and Ω_b seen in the previous sections, and what links a_c and b directly to Tc and Pc. In other words, the critical properties are not an accessory datum: they are what completely determine the parameters of the equation for each substance."),
    ("""El sentido físico de que ambas derivadas se anulen es que, en el punto crítico, la isoterma se vuelve localmente plana: comprimir el fluido no cambia su presión. Líquido y vapor han igualado su densidad y todas sus propiedades, y se han vuelto indistinguibles. Por eso la campana de dos fases se cierra exactamente en ese punto, que es también el vértice de la isoterma que aparece en el ícono de la barra de herramientas del programa.""",
     "The physical meaning of both derivatives vanishing is that, at the critical point, the isotherm becomes locally flat: compressing the fluid does not change its pressure. Liquid and vapour have equalized their density and all their properties, and have become indistinguishable. That is why the two-phase dome closes exactly at that point, which is also the vertex of the isotherm that appears in the program's toolbar icon."),

    ("2.2 El factor acéntrico", "2.2 The acentric factor"),
    ("""Dos sustancias pueden tener temperaturas y presiones críticas parecidas y, sin embargo, comportarse de manera distinta, porque sus moléculas tienen formas diferentes. El factor acéntrico ω, introducido por Pitzer, cuantifica cuánto se aleja una molécula de ser una esfera perfecta. Una molécula esférica y simple como el argón tiene un factor acéntrico cercano a cero, mientras que las cadenas largas de hidrocarburos tienen valores crecientes.""",
     "Two substances can have similar critical temperatures and pressures and yet behave differently, because their molecules have different shapes. The acentric factor ω, introduced by Pitzer, quantifies how far a molecule departs from being a perfect sphere. A simple spherical molecule such as argon has an acentric factor close to zero, while long hydrocarbon chains have increasing values."),
    ("""Se define a partir de la presión de vapor de la sustancia evaluada a una temperatura reducida de 0.7, comparada con su presión crítica:""",
     "It is defined from the vapour pressure of the substance evaluated at a reduced temperature of 0.7, compared with its critical pressure:"),
    ("""El valor 0.7 no es casual: a esa temperatura reducida, las sustancias esféricas simples tienen una presión de vapor reducida de aproximadamente 0.1, lo que hace que su factor acéntrico sea cero por construcción. Cualquier desviación de ese comportamiento (moléculas más alargadas o complejas) produce un factor acéntrico positivo. A modo de referencia, el metano tiene ω cercano a 0.011 y el nonano supera 0.44.""",
     "The value 0.7 is not accidental: at that reduced temperature, simple spherical substances have a reduced vapour pressure of about 0.1, which makes their acentric factor zero by construction. Any deviation from that behaviour (more elongated or complex molecules) produces a positive acentric factor. For reference, methane has ω close to 0.011 and nonane exceeds 0.44."),
    ("""El factor acéntrico es el tercer parámetro que corrige el efecto de la forma molecular, y entra en la ecuación de estado a través del coeficiente m de la función α(T): las moléculas más acéntricas tienen una atracción que varía más fuertemente con la temperatura. Sin este parámetro, todas las sustancias con iguales Tc y Pc se comportarían de manera idéntica, lo cual contradice la experiencia.""",
     "The acentric factor is the third parameter that corrects for the effect of molecular shape, and it enters the equation of state through the coefficient m of the α(T) function: more acentric molecules have an attraction that varies more strongly with temperature. Without this parameter, all substances with equal Tc and Pc would behave identically, which contradicts experience."),

    ("2.3 El coeficiente m y la función alfa de temperatura", "2.3 The coefficient m and the alpha temperature function"),
    ("""Como se anticipó, la dependencia de la atracción con la temperatura se concentra en la función alfa de temperatura, α(T), y ésta depende de un coeficiente de correlación m que a su vez es función del factor acéntrico. Cada forma cúbica tiene su propia correlación, ajustada por sus autores para reproducir las presiones de vapor de una serie de hidrocarburos.""",
     "As anticipated, the temperature dependence of the attraction is concentrated in the alpha temperature function, α(T), which depends on a correlation coefficient m that is in turn a function of the acentric factor. Each cubic form has its own correlation, fitted by its authors to reproduce the vapour pressures of a series of hydrocarbons."),
    ("Para Peng-Robinson:", "For Peng-Robinson:"),
    ("Para SRK:", "For SRK:"),
    ("""Este coeficiente es, por lo tanto, el eslabón que conecta un dato macroscópico y fácil de tabular (el factor acéntrico) con el comportamiento microscópico del término de atracción. Un coeficiente m mayor implica una función alfa que crece más rápido al enfriar, es decir, una atracción que se refuerza más al bajar la temperatura, lo cual es propio de las moléculas más pesadas y alargadas.""",
     "This coefficient is therefore the link connecting a macroscopic, easily tabulated datum (the acentric factor) with the microscopic behaviour of the attraction term. A larger m coefficient implies an alpha function that grows faster on cooling, that is, an attraction that strengthens more as the temperature drops, which is characteristic of heavier and more elongated molecules."),

    ("2.4 Reglas de mezclado", "2.4 Mixing rules"),
    ("""Todo lo anterior describe un componente puro. Pero un fluido de yacimiento es una mezcla de muchos componentes. Surge entonces la pregunta de qué valores de a y de b usar para la mezcla, y la respuesta son las reglas de mezclado.""",
     "All of the above describes a pure component. But a reservoir fluid is a mixture of many components. The question then arises of what values of a and b to use for the mixture, and the answer is the mixing rules."),
    ("""Para el covolumen, la regla es lineal, porque el volumen ocupado por las moléculas de la mezcla es simplemente la suma de los volúmenes de cada especie:""",
     "For the co-volume, the rule is linear, because the volume occupied by the molecules of the mixture is simply the sum of the volumes of each species:"),
    ("""Para el término de atracción se emplea una regla cuadrática, que considera las interacciones entre todos los pares de moléculas i y j, incluidos los pares mixtos:""",
     "For the attraction term a quadratic rule is used, which considers the interactions between all pairs of molecules i and j, including mixed pairs:"),
    ("""La raíz del producto de a_i por a_j es la media geométrica, que estima la atracción entre dos moléculas distintas a partir de las atracciones de cada una. El sentido físico del factor (1 menos k_ij) es que esa media geométrica no es exacta: la atracción real entre moléculas de especies diferentes puede ser algo menor o mayor que el promedio, y el coeficiente k_ij corrige esa desviación. Un k_ij positivo reduce la atracción cruzada, es decir, indica que las dos especies se llevan peor de lo que sugeriría la media geométrica, situación típica entre parejas químicamente dispares como el dióxido de carbono y un hidrocarburo.""",
     "The square root of the product of a_i and a_j is the geometric mean, which estimates the attraction between two different molecules from the attractions of each one. The physical meaning of the factor (1 minus k_ij) is that this geometric mean is not exact: the real attraction between molecules of different species may be somewhat lower or higher than the average, and the coefficient k_ij corrects that deviation. A positive k_ij reduces the cross attraction, that is, it indicates that the two species get along worse than the geometric mean would suggest, a typical situation between chemically dissimilar pairs such as carbon dioxide and a hydrocarbon."),

    ("2.5 Coeficientes de interacción binaria", "2.5 Binary interaction coefficients"),
    ("""Los coeficientes de interacción binaria k_ij forman una matriz simétrica: el coeficiente entre i y j es igual al que hay entre j e i, y el de un componente consigo mismo es cero.""",
     "The binary interaction coefficients k_ij form a symmetric matrix: the coefficient between i and j equals the one between j and i, and that of a component with itself is zero."),
    ("""Aunque suelen ser números pequeños, tienen un efecto desproporcionado sobre la forma de la envolvente de fases, sobre todo en las cercanías del punto crítico de la mezcla, donde pequeños cambios en la atracción cruzada desplazan de manera notable las curvas de burbuja y de rocío. Su magnitud sigue un patrón físico claro:""",
     "Although they are usually small numbers, they have a disproportionate effect on the shape of the phase envelope, especially near the critical point of the mixture, where small changes in the cross attraction notably shift the bubble and dew curves. Their magnitude follows a clear physical pattern:"),
    ("""Entre hidrocarburo e hidrocarburo, k_ij es prácticamente cero, porque son moléculas químicamente similares que se mezclan casi de forma ideal.""",
     "Between hydrocarbon and hydrocarbon, k_ij is practically zero, because they are chemically similar molecules that mix almost ideally."),
    ("""Entre dióxido de carbono e hidrocarburo, k_ij ronda 0.08 a 0.12, reflejando que el dióxido de carbono interactúa de manera apreciablemente distinta con las cadenas de hidrocarburos.""",
     "Between carbon dioxide and hydrocarbon, k_ij is around 0.08 to 0.12, reflecting that carbon dioxide interacts appreciably differently with hydrocarbon chains."),
    ("""Entre nitrógeno e hidrocarburo, los valores son intermedios, del orden de 0.03 a 0.08 según la pareja.""",
     "Between nitrogen and hydrocarbon, the values are intermediate, on the order of 0.03 to 0.08 depending on the pair."),

    ("2.6 Base de datos de los coeficientes de interacción binaria", "2.6 Binary interaction coefficient database"),
    ("""Cada una de las cuatro ecuaciones de estado del programa tiene su propia matriz de coeficientes de interacción binaria. En otras palabras, los k_ij no sólo dependen del simulador de referencia, sino también de la forma de la ecuación, de modo que ThermoPhase maneja cuatro fuentes tabuladas, una por variante:""",
     "Each of the program's four equations of state has its own matrix of binary interaction coefficients. In other words, the k_ij depend not only on the reference simulator but also on the form of the equation, so ThermoPhase handles four tabulated sources, one per variant:"),
    ("Peng-Robinson con parámetros HYSYS.", "Peng-Robinson with HYSYS parameters."),
    ("SRK con parámetros HYSYS.", "SRK with HYSYS parameters."),
    ("Peng-Robinson con parámetros PVTsim.", "Peng-Robinson with PVTsim parameters."),
    ("SRK con parámetros PVTsim.", "SRK with PVTsim parameters."),
    ("""Al seleccionar una ecuación de estado, el programa carga automáticamente la matriz de coeficientes que le corresponde. Las matrices de HYSYS replican las del simulador Aspen HYSYS, que ha sido el punto de comparación histórico del proyecto; las de PVTsim se basan en la recopilación de Knapp y colaboradores y en la convención de Calsep, empleada por PVTsim, que fija en cero los pares hidrocarburo con hidrocarburo. Como principio, ThermoPhase no fabrica datos: cuando una tabla autorizada no está disponible, el coeficiente se deja en cero con respaldo documental en lugar de inventarlo.""",
     "When an equation of state is selected, the program automatically loads the corresponding coefficient matrix. The HYSYS matrices replicate those of the Aspen HYSYS simulator, which has been the historical comparison point of the project; the PVTsim ones are based on the compilation of Knapp and coworkers and on the Calsep convention, used by PVTsim, which sets hydrocarbon-with-hydrocarbon pairs to zero. As a principle, ThermoPhase does not fabricate data: when an authorized table is not available, the coefficient is left at zero with documentary support instead of inventing it."),
    ("Correlación de Chueh-Prausnitz (calculada)", "Chueh-Prausnitz correlation (calculated)"),
    ("""Además de las cuatro matrices tabuladas, el programa ofrece una opción en la que los coeficientes no se toman de una tabla sino que se calculan a partir de los volúmenes críticos de cada par de componentes, mediante la correlación de Chueh-Prausnitz. Esta correlación no depende de la ecuación de estado (la misma matriz sirve para PR y para SRK):""",
     "In addition to the four tabulated matrices, the program offers an option in which the coefficients are not taken from a table but computed from the critical volumes of each pair of components, through the Chueh-Prausnitz correlation. This correlation does not depend on the equation of state (the same matrix serves for PR and for SRK):"),
    ("""La idea física de esta correlación es que la incompatibilidad entre dos moléculas depende sobre todo de la diferencia de tamaños, representada por sus volúmenes críticos, y no tanto de su naturaleza química. Por eso reproduce muy bien los pares de hidrocarburos de tamaños graduales, en los que el coeficiente resulta casi idéntico al de HYSYS, pero difiere más en pares como nitrógeno con metano, donde la química (y no sólo el tamaño) juega un papel importante.""",
     "The physical idea of this correlation is that the incompatibility between two molecules depends above all on the difference in sizes, represented by their critical volumes, and not so much on their chemical nature. That is why it reproduces very well the pairs of hydrocarbons of gradual sizes, in which the coefficient turns out almost identical to that of HYSYS, but differs more in pairs such as nitrogen with methane, where chemistry (and not only size) plays an important role."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 3 — El cálculo flash (equilibrio L-V)
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("3.1 El problema del equilibrio de fases", "3.1 The phase equilibrium problem"),
    ("""El cálculo flash responde la pregunta central de la termodinámica de fases: dada una mezcla de composición global z a una presión y temperatura fijas, ¿en cuánto vapor y cuánto líquido se separa, y cuál es la composición de cada fase? Para plantearlo se definen las siguientes cantidades:""",
     "The flash calculation answers the central question of phase thermodynamics: given a mixture of overall composition z at a fixed pressure and temperature, into how much vapour and how much liquid does it separate, and what is the composition of each phase? To pose it, the following quantities are defined:"),
    ("""z_i, la fracción molar del componente i en la alimentación (lo que entra).""",
     "z_i, the mole fraction of component i in the feed (what enters)."),
    ("y_i, la fracción molar de i en la fase vapor.",
     "y_i, the mole fraction of i in the vapour phase."),
    ("x_i, la fracción molar de i en la fase líquida.",
     "x_i, the mole fraction of i in the liquid phase."),
    ("V, la fracción de la mezcla total que resulta vapor, entre 0 y 1.",
     "V, the fraction of the total mixture that becomes vapour, between 0 and 1."),
    ("""La condición que gobierna todo el problema es el equilibrio termodinámico: en el equilibrio, cada componente tiene la misma fugacidad en ambas fases.""",
     "The condition that governs the whole problem is thermodynamic equilibrium: at equilibrium, each component has the same fugacity in both phases."),
    ("""La fugacidad se puede entender como la presión de escape efectiva de un componente, es decir, una medida de sus ganas de abandonar la fase en la que se encuentra. Si un componente tiene mayor fugacidad en el líquido que en el vapor, migrará del líquido al vapor; el proceso continúa hasta que las fugacidades se igualan y ya no hay ganancia en seguir migrando. Ese estado de equilibrio, en el que las ganas de escapar se han igualado en ambas fases para cada componente, es lo que el cálculo flash busca encontrar.""",
     "Fugacity can be understood as the effective escaping pressure of a component, that is, a measure of its tendency to leave the phase it is in. If a component has a higher fugacity in the liquid than in the vapour, it will migrate from liquid to vapour; the process continues until the fugacities equalize and there is no further gain in migrating. That equilibrium state, in which the escaping tendency has equalized in both phases for each component, is what the flash calculation seeks to find."),

    ("3.2 Fugacidad y coeficiente de fugacidad", "3.2 Fugacity and fugacity coefficient"),
    ("""Trabajar con la fugacidad en términos absolutos es incómodo, por lo que se usa el coeficiente de fugacidad φ_i, que compara la fugacidad real de un componente con la que tendría en un gas ideal a la misma presión y composición:""",
     "Working with fugacity in absolute terms is awkward, so the fugacity coefficient φ_i is used, which compares the real fugacity of a component with the one it would have in an ideal gas at the same pressure and composition:"),
    ("""El coeficiente de fugacidad es precisamente lo que la ecuación de estado permite calcular. Para las ecuaciones cúbicas tiene una forma cerrada que depende de los grupos adimensionales A y B, de la raíz Z de la fase, de la composición y de los coeficientes de interacción binaria. Para Peng-Robinson, la expresión que ThermoPhase evalúa (de forma vectorizada para todos los componentes a la vez) es:""",
     "The fugacity coefficient is precisely what the equation of state allows one to compute. For cubic equations it has a closed form that depends on the dimensionless groups A and B, on the phase root Z, on the composition and on the binary interaction coefficients. For Peng-Robinson, the expression that ThermoPhase evaluates (vectorized for all components at once) is:"),
    ("""Para SRK, como el término atractivo tiene otra forma, el coeficiente de fugacidad cambia en su último término, que pasa a depender de ln[(Z+B)/Z] en lugar del factor con raíz de dos:""",
     "For SRK, since the attractive term has another form, the fugacity coefficient changes in its last term, which comes to depend on ln[(Z+B)/Z] instead of the factor with square root of two:"),
    ("""En ambas expresiones, el primer término recoge el efecto del tamaño relativo de la molécula (a través de la relación entre su covolumen y el de la mezcla), el segundo proviene de la corrección por volumen excluido (la repulsión), y el tercero condensa toda la contribución de la atracción y de las interacciones cruzadas. La condición de equilibrio de fugacidades se escribe entonces en términos de los coeficientes de fugacidad de cada fase:""",
     "In both expressions, the first term captures the effect of the relative size of the molecule (through the ratio between its co-volume and that of the mixture), the second comes from the excluded-volume correction (the repulsion), and the third condenses the whole contribution of attraction and cross interactions. The fugacity equilibrium condition is then written in terms of the fugacity coefficients of each phase:"),
    ("""Aquí se ve por qué la ecuación de estado es imprescindible: es la que traduce presión, temperatura y composición en las ganas de escapar de cada componente en cada fase. El grueso del trabajo de cómputo de un flash consiste en evaluar estos coeficientes de fugacidad una y otra vez.""",
     "Here one sees why the equation of state is indispensable: it is what translates pressure, temperature and composition into the escaping tendency of each component in each phase. The bulk of the computational work of a flash consists of evaluating these fugacity coefficients over and over."),

    ("3.3 Constante de equilibrio", "3.3 Equilibrium constant"),
    ("""De la igualdad de fugacidades surge de forma natural la constante de equilibrio, o relación de reparto, que indica cuánto prefiere un componente la fase vapor frente a la líquida:""",
     "From the equality of fugacities the equilibrium constant, or distribution ratio, arises naturally, indicating how much a component prefers the vapour phase over the liquid:"),
    ("""Un valor de K_i mayor que 1 significa que el componente se concentra preferentemente en el vapor: es un componente ligero y volátil, como el metano. Un valor menor que 1 indica que el componente tiende a quedarse en el líquido: es un componente pesado, como el nonano.""",
     "A value of K_i greater than 1 means the component concentrates preferentially in the vapour: it is a light, volatile component, such as methane. A value less than 1 indicates that the component tends to stay in the liquid: it is a heavy component, such as nonane."),
    ("""Conviene notar que los coeficientes de fugacidad dependen de las composiciones x e y, que a su vez dependen de los K. El problema es, por lo tanto, implícito: los K definen las composiciones y las composiciones redefinen los K. Ésta es la razón por la cual el cálculo del equilibrio no es una fórmula directa, sino un proceso iterativo.""",
     "It is worth noting that the fugacity coefficients depend on the compositions x and y, which in turn depend on the K. The problem is therefore implicit: the K define the compositions and the compositions redefine the K. This is why the equilibrium calculation is not a direct formula but an iterative process."),

    ("3.4 Estimación inicial de las constantes de equilibrio", "3.4 Initial estimate of the equilibrium constants"),
    ("""Todo procedimiento iterativo necesita un punto de partida. Para los coeficientes de reparto K_i, ThermoPhase emplea la correlación de Wilson, que entrega una primera aproximación razonable usando únicamente las propiedades críticas y el factor acéntrico de cada componente:""",
     "Every iterative procedure needs a starting point. For the distribution coefficients K_i, ThermoPhase uses the Wilson correlation, which delivers a reasonable first approximation using only the critical properties and the acentric factor of each component:"),
    ("""La correlación de Wilson no es exacta, pero coloca a cada componente del lado correcto (los ligeros con K mayor que 1 y los pesados con K menor que 1) y proporciona un arranque estable. En ThermoPhase, estos valores de Wilson sirven como semilla del análisis de estabilidad, que es el paso que decide si hay una o dos fases y que refina los coeficientes de reparto. Como se detalla en las subsecciones siguientes, los coeficientes con los que finalmente arranca el flash provienen de ese análisis.""",
     "The Wilson correlation is not exact, but it places each component on the correct side (the light ones with K greater than 1 and the heavy ones with K less than 1) and provides a stable start. In ThermoPhase, these Wilson values serve as the seed of the stability analysis, which is the step that decides whether there are one or two phases and that refines the distribution coefficients. As detailed in the following subsections, the coefficients with which the flash finally starts come from that analysis."),

    ("3.5 La ecuación de Rachford-Rice", "3.5 The Rachford-Rice equation"),
    ("""Una vez que se sabe que la mezcla es bifásica, hace falta determinar cuánta mezcla se vaporiza, es decir, el valor de V. Se parte del balance de materia por componente, que reparte lo que entra entre las dos fases:""",
     "Once the mixture is known to be two-phase, one must determine how much of it vaporizes, that is, the value of V. One starts from the component material balance, which distributes what enters between the two phases:"),
    ("""Combinando este balance con la definición de los coeficientes de reparto (y_i igual a K_i por x_i) y exigiendo que las fracciones molares de cada fase sumen 1, se llega a la ecuación de Rachford-Rice, que es una única ecuación en la incógnita V:""",
     "Combining this balance with the definition of the distribution coefficients (y_i equal to K_i times x_i) and requiring that the mole fractions of each phase sum to 1, one arrives at the Rachford-Rice equation, which is a single equation in the unknown V:"),
    ("""Esta ecuación no es un método de flash por sí sola; es una herramienta matemática que permite resolver V de forma eficiente dado un conjunto de K_i. Tiene la ventaja de ser estrictamente monótona en el intervalo físico de V (entre cero y uno), lo que garantiza una solución única y una convergencia estable. ThermoPhase la resuelve numéricamente por el método de Newton acotado al intervalo válido. Su sentido físico es simple contabilidad: todo lo que entra en la alimentación debe repartirse exactamente entre el vapor y el líquido. El algoritmo que la invoca, y que constituye el verdadero cálculo del equilibrio, se describe en la subsección siguiente.""",
     "This equation is not a flash method by itself; it is a mathematical tool that allows V to be solved efficiently given a set of K_i. It has the advantage of being strictly monotonic in the physical interval of V (between zero and one), which guarantees a unique solution and stable convergence. ThermoPhase solves it numerically by Newton's method bounded to the valid interval. Its physical meaning is simple accounting: everything entering the feed must be distributed exactly between the vapour and the liquid. The algorithm that invokes it, and which constitutes the actual equilibrium calculation, is described in the next subsection."),

    ("3.6 Análisis de estabilidad", "3.6 Stability analysis"),
    ("""Antes de resolver el flash conviene saber si la mezcla realmente se separa en dos fases o si permanece como una sola. De esto se encarga el análisis de estabilidad, que en ThermoPhase reproduce el procedimiento de Michelsen implementado y validado en la referencia del proyecto. La idea de fondo es la del plano tangente a la energía de Gibbs: una fase es estable si ninguna fase incipiente de otra composición tiene menor energía de Gibbs; si se encuentra una composición de prueba que baja por debajo del plano tangente, la mezcla es inestable y se separará.""",
     "Before solving the flash it is useful to know whether the mixture really separates into two phases or remains as one. This is handled by the stability analysis, which in ThermoPhase reproduces the Michelsen procedure implemented and validated in the project reference. The underlying idea is that of the Gibbs energy tangent plane: a phase is stable if no incipient phase of another composition has lower Gibbs energy; if a trial composition is found that drops below the tangent plane, the mixture is unstable and will separate."),
    ("""El procedimiento concreto que sigue el programa parte de dos juegos de coeficientes de reparto, ambos inicializados con la correlación de Wilson: uno para ensayar una fase vapor incipiente (K^V) y otro para una fase líquida incipiente (K^L). Con ellos se construyen las composiciones normalizadas de esas fases de prueba:""",
     "The concrete procedure the program follows starts from two sets of distribution coefficients, both initialized with the Wilson correlation: one to test an incipient vapour phase (K^V) and another for an incipient liquid phase (K^L). With them the normalized compositions of those trial phases are built:"),
    ("""Para cada fase de prueba y para la alimentación se evalúan las fugacidades con la ecuación de estado, seleccionando la raíz de vapor o de líquido según corresponda. A partir de la comparación de esas fugacidades se actualizan los coeficientes de reparto, con un esquema normalizado por las sumas de cada fase incipiente:""",
     "For each trial phase and for the feed, the fugacities are evaluated with the equation of state, selecting the vapour or liquid root as appropriate. From the comparison of those fugacities the distribution coefficients are updated, with a scheme normalized by the sums of each incipient phase:"),
    ("""La normalización por S_V y S_L evita que la búsqueda diverja: en un sistema monofásico hace que los coeficientes converjan de manera controlada hacia la solución trivial, en la que todos los K tienden a 1, en lugar de dispararse hacia los límites numéricos. Al terminar la iteración, el programa decide la estabilidad con dos criterios. Por un lado, si alguna de las sumas S_V o S_L supera la unidad, existe una fase incipiente con menor energía de Gibbs y la mezcla es inestable, es decir, bifásica. Por otro, para distinguir la solución trivial de una genuina, se evalúa la suma de los logaritmos de los coeficientes al cuadrado, considerando sólo los componentes presentes:""",
     "The normalization by S_V and S_L prevents the search from diverging: in a single-phase system it makes the coefficients converge in a controlled way toward the trivial solution, in which all the K tend to 1, instead of shooting toward the numerical limits. At the end of the iteration, the program decides stability with two criteria. On one hand, if either of the sums S_V or S_L exceeds unity, there is an incipient phase with lower Gibbs energy and the mixture is unstable, that is, two-phase. On the other, to distinguish the trivial solution from a genuine one, the sum of the squared logarithms of the coefficients is evaluated, considering only the components present:"),
    ("""El punto clave es qué coeficientes de reparto quedan para el flash. Cuando el análisis concluye que la mezcla es inestable, los coeficientes que se pasan al flash no son los de Wilson, sino el producto de los dos juegos refinados durante la propia búsqueda de estabilidad:""",
     "The key point is which distribution coefficients remain for the flash. When the analysis concludes that the mixture is unstable, the coefficients passed to the flash are not the Wilson ones, but the product of the two sets refined during the stability search itself:"),
    ("""De este modo el flash arranca desde una estimación mucho más cercana a la solución. Si en cambio el análisis concluye que la mezcla es estable, el flash arranca con los coeficientes de Wilson. En ambos casos, como se explica en la subsección siguiente, el flash siempre se ejecuta a continuación.""",
     "In this way the flash starts from an estimate much closer to the solution. If instead the analysis concludes that the mixture is stable, the flash starts with the Wilson coefficients. In both cases, as explained in the next subsection, the flash is always executed afterward."),

    ("3.7 El algoritmo completo del flash", "3.7 The complete flash algorithm"),
    ("""El método que ThermoPhase implementa para el cálculo del equilibrio líquido-vapor es el de Muskat-McDowell, un esquema iterativo de sustitución sucesiva que actualiza los coeficientes de reparto hasta que las fugacidades se igualan en ambas fases. A diferencia de Rachford-Rice, que es únicamente una ecuación para resolver V dados los K_i, el método de Muskat-McDowell es el algoritmo completo que envuelve ese paso como una herramienta interna.""",
     "The method ThermoPhase implements for the vapour-liquid equilibrium calculation is that of Muskat-McDowell, an iterative successive-substitution scheme that updates the distribution coefficients until the fugacities equalize in both phases. Unlike Rachford-Rice, which is only an equation to solve V given the K_i, the Muskat-McDowell method is the complete algorithm that wraps that step as an internal tool."),
    ("Preparación de los coeficientes de reparto iniciales", "Preparation of the initial distribution coefficients"),
    ("""Antes de entrar al flash, se ejecuta el análisis de estabilidad descrito en la subsección anterior. Si la mezcla resulta inestable, el flash arrancará con el producto de los dos juegos de coeficientes refinados en la estabilidad (K^V por K^L), que es una estimación mucho más cercana a la solución que la de Wilson. Si la mezcla resulta estable, el flash arrancará con los coeficientes de Wilson. En ambos casos el flash siempre se ejecuta; la clasificación final en una o dos fases la produce el propio algoritmo.""",
     "Before entering the flash, the stability analysis described in the previous subsection is executed. If the mixture turns out unstable, the flash will start with the product of the two sets of coefficients refined in the stability (K^V times K^L), which is an estimate much closer to the solution than Wilson's. If the mixture turns out stable, the flash will start with the Wilson coefficients. In both cases the flash is always executed; the final classification into one or two phases is produced by the algorithm itself."),
    ("El bucle de Muskat-McDowell", "The Muskat-McDowell loop"),
    ("""Con los coeficientes de reparto del paso anterior, el algoritmo entra en un lazo iterativo. En cada iteración se evalúan primero dos sumatorios que actúan como criterio de fase:""",
     "With the distribution coefficients from the previous step, the algorithm enters an iterative loop. In each iteration two summations are evaluated first that act as a phase criterion:"),
    ("""Si el primer sumatorio no supera la unidad, toda la mezcla es líquida y se asigna x_i = z_i; si el segundo no supera la unidad, toda la mezcla es vapor y se asigna y_i = z_i. Cuando ninguno de los dos criterios se cumple, la mezcla es bifásica: en ese caso se invoca la ecuación de Rachford-Rice para resolver la fracción vaporizada V, y con ella se calculan las composiciones de cada fase:""",
     "If the first summation does not exceed unity, the whole mixture is liquid and x_i = z_i is assigned; if the second does not exceed unity, the whole mixture is vapour and y_i = z_i is assigned. When neither criterion is met, the mixture is two-phase: in that case the Rachford-Rice equation is invoked to solve the vaporized fraction V, and with it the compositions of each phase are computed:"),
    ("""Con las composiciones de cada fase se evalúan los coeficientes de fugacidad mediante la ecuación de estado, resolviendo el cúbico en Z y tomando la raíz que corresponde a cada fase. Cuando una de las fases es evanescente (composición prácticamente cero), su coeficiente de fugacidad se fija en 1 para todos los componentes: esto evita que los coeficientes de reparto colapsen a la solución trivial y deja que la clasificación de fase dependa únicamente de los sumatorios anteriores, tal como lo hace la referencia del proyecto.""",
     "With the compositions of each phase the fugacity coefficients are evaluated through the equation of state, solving the cubic in Z and taking the root corresponding to each phase. When one of the phases is evanescent (composition practically zero), its fugacity coefficient is set to 1 for all components: this prevents the distribution coefficients from collapsing to the trivial solution and lets the phase classification depend solely on the previous summations, as the project reference does."),
    ("""A partir de las fugacidades de cada fase se actualizan los coeficientes de reparto como el cociente entre el coeficiente de fugacidad del líquido y el del vapor:""",
     "From the fugacities of each phase the distribution coefficients are updated as the ratio between the fugacity coefficient of the liquid and that of the vapour:"),
    ("""El lazo se repite hasta que las fugacidades de cada componente coinciden en ambas fases dentro de la tolerancia. Cuando converge, se tiene la solución del equilibrio: la fracción vaporizada V, las composiciones x e y de cada fase y el número de fases presentes. En el fondo, el método de Muskat-McDowell es un proceso que ajusta iterativamente el reparto de los componentes hasta que cada uno tiene las mismas ganas de escapar en el líquido y en el vapor, usando la ecuación de estado para calcular fugacidades y la ecuación de Rachford-Rice como herramienta interna para resolver el balance de materia en los casos bifásicos.""",
     "The loop repeats until the fugacities of each component coincide in both phases within tolerance. When it converges, one has the equilibrium solution: the vaporized fraction V, the compositions x and y of each phase and the number of phases present. At bottom, the Muskat-McDowell method is a process that iteratively adjusts the distribution of the components until each one has the same escaping tendency in the liquid and in the vapour, using the equation of state to compute fugacities and the Rachford-Rice equation as an internal tool to solve the material balance in the two-phase cases."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 4 — Envolvente de fases
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("4.1 Envolvente de fases", "4.1 Phase envelope"),
    ("""La envolvente de fases es la curva que delimita, en el plano presión-temperatura, la región donde una mezcla de composición fija coexiste como líquido y como vapor simultáneamente. Dentro de esa curva el sistema es bifásico; fuera de ella, a la izquierda o debajo, es monofásico líquido o vapor según el caso.""",
     "The phase envelope is the curve that delimits, in the pressure-temperature plane, the region where a mixture of fixed composition coexists as liquid and as vapour simultaneously. Inside that curve the system is two-phase; outside it, to the left or below, it is single-phase liquid or vapour as the case may be."),
    ("""La curva tiene dos ramas que parten del mismo punto a baja presión y se cierran en el punto crítico de la mezcla:""",
     "The curve has two branches that start from the same point at low pressure and close at the critical point of the mixture:"),
    ("""La <b>curva de burbuja</b> representa las condiciones en las que el líquido está a punto de comenzar a vaporizarse: la fracción de vapor es prácticamente cero y una burbuja incipiente acaba de aparecer.""",
     "The <b>bubble curve</b> represents the conditions at which the liquid is about to begin to vaporize: the vapour fraction is practically zero and an incipient bubble has just appeared."),
    ("""La <b>curva de rocío</b> representa las condiciones en las que el vapor está a punto de comenzar a condensar: la fracción de líquido es prácticamente cero y una gota incipiente acaba de aparecer.""",
     "The <b>dew curve</b> represents the conditions at which the vapour is about to begin to condense: the liquid fraction is practically zero and an incipient drop has just appeared."),
    ("""En ambos casos la condición matemática es la misma que la del flash monofásico fronterizo:""",
     "In both cases the mathematical condition is the same as that of the boundary single-phase flash:"),
    ("""La envolvente es uno de los resultados más valiosos de la termodinámica de mezclas porque permite conocer, de un solo vistazo, si una mezcla producida en un yacimiento estará en una o dos fases en cualquier punto del sistema de producción, desde la presión del yacimiento hasta las condiciones de la superficie, o en cualquier equipo de proceso.""",
     "The envelope is one of the most valuable results of mixture thermodynamics because it allows one to know, at a glance, whether a mixture produced in a reservoir will be in one or two phases at any point of the production system, from reservoir pressure to surface conditions, or in any piece of process equipment."),

    ("4.2 El método de Ziervogel (GoalSeek con continuación de curva)",
     "4.2 The Ziervogel method (GoalSeek with curve continuation)"),
    ("""El método que ThermoPhase emplea como base para trazar la envolvente sigue el esquema de Ziervogel. La idea central es que cada punto de la curva de burbuja o de rocío se obtiene resolviendo un GoalSeek de una sola variable, alternando entre temperatura y presión como variable de búsqueda, mientras la otra se impone desde el punto anterior.""",
     "The method ThermoPhase uses as the basis for tracing the envelope follows the Ziervogel scheme. The central idea is that each point of the bubble or dew curve is obtained by solving a single-variable GoalSeek, alternating between temperature and pressure as the search variable, while the other is imposed from the previous point."),
    ("La condición de saturación y la composición fija",
     "The saturation condition and the fixed composition"),
    ("""En un punto de burbuja, el líquido tiene la composición global de la mezcla (x_i = z_i) y el vapor incipiente tiene una composición que hay que calcular. La condición de saturación exige que las fracciones molares del vapor sumen la unidad, lo que equivale a la ecuación:""",
     "At a bubble point, the liquid has the overall composition of the mixture (x_i = z_i) and the incipient vapour has a composition that must be computed. The saturation condition requires that the mole fractions of the vapour sum to unity, which is equivalent to the equation:"),
    ("""En un punto de rocío el rol se invierte: el vapor tiene la composición global (y_i = z_i) y el líquido incipiente es el que se calcula:""",
     "At a dew point the role is reversed: the vapour has the overall composition (y_i = z_i) and it is the incipient liquid that is computed:"),
    ("""El detalle clave de la implementación es que la composición de la fase incipiente se mantiene <b>fija</b> durante cada GoalSeek: solo la variable de búsqueda (temperatura o presión) se mueve, mientras la composición de la fase incipiente permanece constante. Solo después de que el GoalSeek converge se actualiza la composición de la fase incipiente con los K_i recién calculados, y el proceso se repite hasta que esa composición ya no cambia entre una iteración y la siguiente.""",
     "The key implementation detail is that the composition of the incipient phase is kept <b>fixed</b> during each GoalSeek: only the search variable (temperature or pressure) moves, while the composition of the incipient phase remains constant. Only after the GoalSeek converges is the composition of the incipient phase updated with the freshly computed K_i, and the process repeats until that composition no longer changes from one iteration to the next."),
    ("Inicio de la curva con la correlación de Wilson",
     "Starting the curve with the Wilson correlation"),
    ("""Para arrancar el trazado, el programa necesita un primer punto de saturación. Fija la presión en un valor bajo (10 psia) y busca la temperatura de burbuja inicial resolviendo por Newton-Raphson la ecuación de Wilson, que es una aproximación analítica de los K_i válida lejos del punto crítico:""",
     "To start the trace, the program needs a first saturation point. It fixes the pressure at a low value (10 psia) and finds the initial bubble temperature by solving, via Newton-Raphson, the Wilson equation, which is an analytical approximation of the K_i valid far from the critical point:"),
    ("""Con esa temperatura inicial se evalúan los K_i de Wilson, se construye la composición de la fase incipiente (vapor para burbuja, líquido para rocío) y se ejecuta el primer GoalSeek, que refina la temperatura usando ya los coeficientes de fugacidad de la ecuación de estado en lugar de la aproximación de Wilson.""",
     "With that initial temperature the Wilson K_i are evaluated, the composition of the incipient phase is built (vapour for bubble, liquid for dew) and the first GoalSeek is executed, which refines the temperature already using the fugacity coefficients of the equation of state instead of the Wilson approximation."),
    ("Continuación de la curva punto a punto",
     "Point-by-point curve continuation"),
    ("""Con el primer punto convergido, el algoritmo avanza a lo largo de la curva usando un esquema de predictor simple: da un pequeño paso en temperatura o en presión (el que resulte más adecuado según la pendiente local de la curva) y usa el resultado anterior como punto de partida para el GoalSeek del siguiente. La elección de qué variable mover en cada tramo se basa en el parámetro β, que mide la inclinación local de la curva en escala logarítmica:""",
     "With the first point converged, the algorithm advances along the curve using a simple predictor scheme: it takes a small step in temperature or pressure (whichever is more suitable according to the local slope of the curve) and uses the previous result as the starting point for the next GoalSeek. The choice of which variable to move in each segment is based on the parameter β, which measures the local slope of the curve on a logarithmic scale:"),
    ("""Cuando β es grande (la curva es casi vertical, la presión cambia mucho con poca variación de temperatura), se avanza fijando temperatura y buscando presión; cuando β es pequeño (la curva es casi horizontal), se avanza fijando presión y buscando temperatura. Este ajuste automático permite seguir la curva de manera estable en todas las zonas, incluidas las regiones de alta pendiente cerca del cricondenterm (temperatura máxima) y la cricondenbar (presión máxima).""",
     "When β is large (the curve is nearly vertical, pressure changes a lot with little variation in temperature), one advances by fixing temperature and searching for pressure; when β is small (the curve is nearly horizontal), one advances by fixing pressure and searching for temperature. This automatic adjustment allows the curve to be followed stably in all zones, including the high-slope regions near the cricondentherm (maximum temperature) and the cricondenbar (maximum pressure)."),
    ("Cercanía al punto crítico y cambio de solucionador",
     "Proximity to the critical point and solver switch"),
    ("""A medida que la curva se aproxima al punto crítico de la mezcla, los K_i tienden a 1 y las fases se vuelven casi indistinguibles. En esa zona el GoalSeek con el método secante (que usa derivadas) puede diverger porque la función se vuelve muy plana. Para detectar esta situación el programa evalúa en cada punto el criterio de Gallardo:""",
     "As the curve approaches the critical point of the mixture, the K_i tend to 1 and the phases become almost indistinguishable. In that zone the GoalSeek with the secant method (which uses derivatives) can diverge because the function becomes very flat. To detect this situation the program evaluates, at each point, the Gallardo criterion:"),
    ("""Cuando ϖ cae por debajo de 0.2, las fases son casi idénticas y el programa cambia automáticamente el solucionador del GoalSeek: abandona el método de la secante y pasa a <b>bisección</b>, que no usa derivadas y nunca diverge, aunque converge más lentamente. Cuando ϖ vuelve a crecer, se retoma la secante. El trazado se detiene cuando todos los K_i se acercan suficientemente a 1, señal de que se ha alcanzado el punto crítico.""",
     "When ϖ falls below 0.2, the phases are almost identical and the program automatically changes the GoalSeek solver: it abandons the secant method and switches to <b>bisection</b>, which uses no derivatives and never diverges, although it converges more slowly. When ϖ grows again, the secant is resumed. The trace stops when all the K_i are close enough to 1, a sign that the critical point has been reached."),

    ("4.3 El método de Michelsen (continuación por pseudo-longitud de arco)",
     "4.3 The Michelsen method (pseudo-arc-length continuation)"),
    ("""El método de Michelsen (1980) es un algoritmo de continuación mucho más sofisticado que el GoalSeek punto a punto. En lugar de resolver una ecuación escalar en una variable, plantea un sistema de ecuaciones no lineales que incluye todas las condiciones de equilibrio simultáneamente, junto con una ecuación adicional de restricción de arco que fija cuánto avanza el trazado en cada paso. ThermoPhase lo usa como complemento cuando el método de Ziervogel no logra cerrar la envolvente en la zona del punto crítico.""",
     "The Michelsen method (1980) is a continuation algorithm much more sophisticated than the point-by-point GoalSeek. Instead of solving a scalar equation in one variable, it poses a system of nonlinear equations that includes all the equilibrium conditions simultaneously, together with an additional arc-restriction equation that fixes how much the trace advances at each step. ThermoPhase uses it as a complement when the Ziervogel method fails to close the envelope in the region of the critical point."),
    ("Variables y sistema de ecuaciones", "Variables and system of equations"),
    ("""El método trabaja en el espacio logarítmico de las variables de estado. Para una mezcla con m componentes presentes (z_i mayor que cero), el vector de incógnitas en cada punto de la curva es:""",
     "The method works in the logarithmic space of the state variables. For a mixture with m components present (z_i greater than zero), the vector of unknowns at each point of the curve is:"),
    ("""El sistema de ecuaciones que debe satisfacerse en cada punto de la envolvente consta de m ecuaciones de igualdad de fugacidades (una por componente presente), una ecuación de saturación y una restricción de pseudo-longitud de arco:""",
     "The system of equations that must be satisfied at each point of the envelope consists of m fugacity-equality equations (one per component present), a saturation equation and a pseudo-arc-length restriction:"),
    ("""La última ecuación es la restricción de arco: el vector tangente t (calculado en el punto anterior) proyectado sobre el desplazamiento desde el punto de referencia debe ser igual al tamaño de paso Δs. Esto garantiza que el trazado avance una distancia controlada a lo largo de la curva, sin que el algoritmo pueda retroceder ni saltar a una solución distante.""",
     "The last equation is the arc restriction: the tangent vector t (computed at the previous point) projected onto the displacement from the reference point must equal the step size Δs. This guarantees that the trace advances a controlled distance along the curve, without the algorithm being able to go backward or jump to a distant solution."),
    ("Newton-Raphson con Jacobiano analítico", "Newton-Raphson with analytical Jacobian"),
    ("""El sistema anterior se resuelve con Newton-Raphson multivariable. La clave de la eficiencia y la robustez del método está en que el Jacobiano (la matriz de derivadas parciales del sistema respecto a las incógnitas) se calcula de forma analítica a partir de las derivadas de los coeficientes de fugacidad respecto a temperatura, presión y composición. Eso hace que cada iteración de Newton converja cuadráticamente cuando está cerca de la solución.""",
     "The above system is solved with multivariable Newton-Raphson. The key to the efficiency and robustness of the method is that the Jacobian (the matrix of partial derivatives of the system with respect to the unknowns) is computed analytically from the derivatives of the fugacity coefficients with respect to temperature, pressure and composition. This makes each Newton iteration converge quadratically when it is close to the solution."),
    ("El vector tangente y la predicción del siguiente punto",
     "The tangent vector and the prediction of the next point"),
    ("""El vector tangente al arco en cada punto convergido se obtiene como el vector nulo del Jacobiano del sistema (sin la restricción de arco), calculado por descomposición en valores singulares (SVD). Ese vector tangente actúa como predictor del siguiente punto: la solución del paso anterior, desplazada en la dirección del tangente una distancia Δs, sirve como punto de partida para el Newton-Raphson del paso siguiente. La magnitud de Δs se ajusta automáticamente: se agranda cuando Newton converge en pocas iteraciones (zona suave de la curva) y se reduce cuando le cuesta más (zona compleja, cerca del crítico).""",
     "The tangent vector to the arc at each converged point is obtained as the null vector of the Jacobian of the system (without the arc restriction), computed by singular value decomposition (SVD). That tangent vector acts as a predictor of the next point: the solution of the previous step, displaced in the direction of the tangent a distance Δs, serves as the starting point for the Newton-Raphson of the next step. The magnitude of Δs is adjusted automatically: it is enlarged when Newton converges in few iterations (smooth zone of the curve) and reduced when it struggles more (complex zone, near the critical point)."),
    ("Estrategia bidireccional para la cola de rocío",
     "Bidirectional strategy for the dew tail"),
    ("""Un problema frecuente en gases livianos es que la rama de rocío a bajas presiones forma una cola larga y con pendiente pronunciada que el trazado unidireccional puede perder. ThermoPhase lo resuelve con una estrategia bidireccional: traza la envolvente desde un punto de burbuja de baja presión en sentido ascendente, rodea el punto crítico y desciende por la rama de rocío superior; luego arranca un segundo trazado desde un punto de rocío de baja presión en sentido ascendente hasta conectarse con el primero. Los dos tramos se combinan para formar la envolvente completa, incluida la cola inferior de rocío que el trazado simple habría omitido.""",
     "A frequent problem in light gases is that the dew branch at low pressures forms a long, steeply sloped tail that unidirectional tracing can miss. ThermoPhase solves it with a bidirectional strategy: it traces the envelope from a low-pressure bubble point in the upward direction, goes around the critical point and descends along the upper dew branch; then it starts a second trace from a low-pressure dew point upward until it connects with the first. The two segments are combined to form the complete envelope, including the lower dew tail that the simple trace would have omitted."),
    ("Subespaciado activo", "Active subspacing"),
    ("""Para mejorar la eficiencia, el sistema de ecuaciones se construye únicamente con los componentes que tienen fracción molar positiva (z_i mayor que cero). Esto reduce el Jacobiano de (NC+2) filas y columnas a (m+2), donde m es el número de componentes presentes, lo que es especialmente ventajoso en mezclas de producción donde varios componentes de la base de datos tienen fracción nula.""",
     "To improve efficiency, the system of equations is built only with the components that have positive mole fraction (z_i greater than zero). This reduces the Jacobian from (NC+2) rows and columns to (m+2), where m is the number of components present, which is especially advantageous in production mixtures where several components of the database have zero fraction."),

    ("4.4 Flujo de cálculo: Ziervogel con fallback a Michelsen",
     "4.4 Calculation flow: Ziervogel with fallback to Michelsen"),
    ("""Cuando se solicita el trazado de la envolvente completa, ThermoPhase sigue un flujo de decisión automático que combina los dos métodos para obtener siempre la mejor envolvente posible con el menor tiempo de cómputo:""",
     "When the trace of the complete envelope is requested, ThermoPhase follows an automatic decision flow that combines the two methods to always obtain the best possible envelope with the least computation time:"),
    ("""Se trazan las curvas de burbuja y de rocío por el método de Ziervogel, que es rápido y robusto para la gran mayoría de mezclas.""",
     "The bubble and dew curves are traced by the Ziervogel method, which is fast and robust for the vast majority of mixtures."),
    ("""Se mide el hueco que queda entre las últimas puntas de las dos curvas (la distancia geométrica en el plano P-T entre el último punto de burbuja y el último punto de rocío). Si ese hueco es menor que la tolerancia de cierre (15 unidades en el plano adimensional), Ziervogel ha cerrado bien y la envolvente se devuelve directamente.""",
     "The gap remaining between the last tips of the two curves is measured (the geometric distance in the P-T plane between the last bubble point and the last dew point). If that gap is smaller than the closing tolerance (15 units in the dimensionless plane), Ziervogel has closed well and the envelope is returned directly."),
    ("""Si el hueco es mayor, Michelsen entra como complemento: traza el arco del ápice que Ziervogel no pudo cerrar, extrae de él el tramo comprendido entre las dos puntas de Ziervogel, lo divide por la cricondenbar (el punto de máxima presión del arco) en lado-burbuja y lado-rocío, y empalma ese tramo con los extremos de Ziervogel para completar la envolvente.""",
     "If the gap is larger, Michelsen comes in as a complement: it traces the apex arc that Ziervogel could not close, extracts from it the segment between the two Ziervogel tips, splits it by the cricondenbar (the point of maximum pressure of the arc) into bubble-side and dew-side, and splices that segment with the Ziervogel ends to complete the envelope."),
    ("""Esta estrategia combina lo mejor de ambos métodos: la fidelidad al modelo de referencia de Ziervogel y la robustez en la zona crítica de Michelsen. En la gran mayoría de las mezclas típicas de producción, Ziervogel cierra por sí solo y Michelsen no llega a ejecutarse.""",
     "This strategy combines the best of both methods: the fidelity to the reference model of Ziervogel and the robustness in the critical zone of Michelsen. In the vast majority of typical production mixtures, Ziervogel closes on its own and Michelsen does not get to run."),
    ("Caso especial: mezclas casi azeotrópicas", "Special case: near-azeotropic mixtures"),
    ("""Cuando todos los componentes presentes tienen temperaturas críticas muy similares (razón Tc_max/Tc_min menor que 1.10, como ocurre en mezclas de CO2 con etano o de isopentano con pentano normal), la envolvente es muy estrecha y los coeficientes de interacción binaria cruzados dificultan la convergencia de Ziervogel. En ese caso el programa anula internamente los coeficientes k_ij del par casi ideal, ejecuta el trazado con k_ij = 0 (que converge con facilidad), y restaura los k_ij originales en el resultado. Los puntos (P, T) trazados con k_ij = 0 son prácticamente idénticos a los que se obtendrían con los k_ij originales, porque para pares casi ideales esos coeficientes son ya muy cercanos a cero.""",
     "When all the components present have very similar critical temperatures (Tc_max/Tc_min ratio less than 1.10, as occurs in mixtures of CO2 with ethane or of isopentane with normal pentane), the envelope is very narrow and the cross binary interaction coefficients hamper the convergence of Ziervogel. In that case the program internally zeroes the k_ij coefficients of the near-ideal pair, runs the trace with k_ij = 0 (which converges easily), and restores the original k_ij in the result. The (P, T) points traced with k_ij = 0 are practically identical to those that would be obtained with the original k_ij, because for near-ideal pairs those coefficients are already very close to zero."),

    ("4.5 Punto crítico y líneas de calidad", "4.5 Critical point and quality lines"),
    ("""Además de las curvas de burbuja y de rocío, ThermoPhase calcula y muestra sobre la envolvente información adicional que enriquece su interpretación.""",
     "In addition to the bubble and dew curves, ThermoPhase computes and displays on the envelope additional information that enriches its interpretation."),
    ("Punto crítico de la mezcla", "Critical point of the mixture"),
    ("""El punto crítico es el vértice donde las dos ramas se unen. En él las fases líquida y vapor se vuelven idénticas: sus densidades, composiciones y todas sus propiedades coinciden. Matemáticamente corresponde al límite en el que todos los coeficientes de reparto K_i tienden simultáneamente a 1. El programa lo identifica como el punto de la envolvente donde se cumple el criterio:""",
     "The critical point is the vertex where the two branches meet. There the liquid and vapour phases become identical: their densities, compositions and all their properties coincide. Mathematically it corresponds to the limit in which all the distribution coefficients K_i tend simultaneously to 1. The program identifies it as the point of the envelope where the criterion is met:"),
    ("Cricondenterm y cricondenbar", "Cricondentherm and cricondenbar"),
    ("""Dos puntos especiales de la envolvente tienen nombre propio. La <b>cricondenterm</b> es la temperatura máxima de la envolvente: por encima de ella, la mezcla no puede condensar a ninguna presión. La <b>cricondenbar</b> es la presión máxima de la envolvente: por encima de ella no puede existir una mezcla bifásica a ninguna temperatura. Ambos puntos se identifican automáticamente como los extremos de la curva en cada coordenada.""",
     "Two special points of the envelope have their own names. The <b>cricondentherm</b> is the maximum temperature of the envelope: above it, the mixture cannot condense at any pressure. The <b>cricondenbar</b> is the maximum pressure of the envelope: above it a two-phase mixture cannot exist at any temperature. Both points are identified automatically as the extremes of the curve in each coordinate."),
    ("Líneas de calidad", "Quality lines"),
    ("""Las líneas de calidad son curvas interiores de la envolvente que unen los puntos con la misma fracción de vapor (la calidad del vapor, Q). La línea Q = 0 es la curva de burbuja y la línea Q = 1 es la de rocío; las intermedias (Q = 0.1, 0.2, ..., 0.9) muestran cómo cambia la proporción de vapor dentro de la región bifásica. Para calcular cada punto interior de una línea de calidad, el programa ejecuta un flash isotérmico a la fracción de vapor deseada, determinando las condiciones de presión y composición de cada fase a esa calidad fija sobre la isoterma correspondiente.""",
     "The quality lines are interior curves of the envelope that join the points with the same vapour fraction (the vapour quality, Q). The line Q = 0 is the bubble curve and the line Q = 1 is the dew curve; the intermediate ones (Q = 0.1, 0.2, ..., 0.9) show how the vapour proportion changes within the two-phase region. To compute each interior point of a quality line, the program runs an isothermal flash at the desired vapour fraction, determining the pressure conditions and composition of each phase at that fixed quality on the corresponding isotherm."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 5 — Identificación de fase monofásica
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("5.1 El problema de la identificación de fase", "5.1 The phase identification problem"),
    ("""Cuando el cálculo flash converge a una sola fase, la ecuación de estado produce un único factor de compresibilidad Z. A partir de ese resultado es necesario determinar si el fluido monofásico tiene carácter líquido o carácter vapor, porque los modelos de densidad, viscosidad y conductividad térmica aplican correlaciones distintas según la fase.""",
     "When the flash calculation converges to a single phase, the equation of state produces a single compressibility factor Z. From that result it is necessary to determine whether the single-phase fluid has liquid or vapour character, because the density, viscosity and thermal conductivity models apply different correlations depending on the phase."),
    ("""Esta determinación es directa cuando el fluido está claramente fuera de la envolvente de fases: un gas a baja presión tiene Z cercano a 1 y baja densidad; un líquido comprimido tiene Z pequeño y alta densidad. La dificultad aparece en la región densa, donde la presión supera la cricondenbar de la mezcla y el fluido no puede existir como dos fases a ninguna temperatura. En esa región el fluido es termodinámicamente único, pero puede tener comportamiento más cercano al líquido o al vapor, y el programa necesita decidir qué conjunto de modelos de propiedades lo representa mejor.""",
     "This determination is straightforward when the fluid is clearly outside the phase envelope: a low-pressure gas has Z close to 1 and low density; a compressed liquid has small Z and high density. The difficulty appears in the dense region, where the pressure exceeds the cricondenbar of the mixture and the fluid cannot exist as two phases at any temperature. In that region the fluid is thermodynamically unique, but it can have behaviour closer to liquid or to vapour, and the program needs to decide which set of property models best represents it."),
    ("""ThermoPhase aplica un algoritmo de tres criterios en cascada para las variantes PR y SRK (y sus homólogas con parámetros PVTsim). Los criterios se evalúan en orden de prioridad: el primero se basa en los parámetros de la ecuación de estado, el segundo en la compresibilidad isotérmica, y el tercero en la composición de la mezcla.""",
     "ThermoPhase applies a three-criteria cascade algorithm for the PR and SRK variants (and their counterparts with PVTsim parameters). The criteria are evaluated in order of priority: the first is based on the parameters of the equation of state, the second on the isothermal compressibility, and the third on the composition of the mixture."),

    ("5.2 Compresibilidad isotérmica", "5.2 Isothermal compressibility"),
    ("""La compresibilidad isotérmica mide la variación relativa del volumen molar con la presión a temperatura constante:""",
     "The isothermal compressibility measures the relative variation of the molar volume with pressure at constant temperature:"),
    ("""Para el gas ideal κ = 1/P. Para trabajar con una magnitud adimensional independiente de las unidades de presión se define el factor de compresibilidad isotérmica β:""",
     "For the ideal gas κ = 1/P. To work with a dimensionless magnitude independent of the pressure units, the isothermal compressibility factor β is defined:"),
    ("""Para el gas ideal β = 1; para un líquido β es mucho menor que 1. El umbral β = 0.75 separa estados con comportamiento predominantemente gaseoso de estados con comportamiento líquido.""",
     "For the ideal gas β = 1; for a liquid β is much less than 1. The threshold β = 0.75 separates states with predominantly gaseous behaviour from states with liquid behaviour."),
    ("Cálculo analítico", "Analytical calculation"),
    ("""ThermoPhase calcula β mediante la derivada analítica de la ecuación de estado. Para Peng-Robinson:""",
     "ThermoPhase computes β through the analytical derivative of the equation of state. For Peng-Robinson:"),
    ("Para Soave-Redlich-Kwong:", "For Soave-Redlich-Kwong:"),
    ("La compresibilidad adimensional resulta:", "The dimensionless compressibility results:"),
    ("""Esta expresión es algebraicamente equivalente a la forma cerrada en función de A = aₘP/(RT)² y B = bₘP/(RT):""",
     "This expression is algebraically equivalent to the closed form in terms of A = aₘP/(RT)² and B = bₘP/(RT):"),
    ("""donde z es el factor de compresibilidad de la mezcla. La diferencia numérica entre ambas formas es del orden de 10⁻¹⁶, confirmando que son la misma expresión.""",
     "where z is the compressibility factor of the mixture. The numerical difference between the two forms is on the order of 10⁻¹⁶, confirming that they are the same expression."),

    ("5.3 Criterio de la relación A/B", "5.3 The A/B ratio criterion"),
    ("""A presiones superiores a la cricondenbar de la mezcla, el factor Z permanece por encima de 0.75 en todo el rango de temperatura y los criterios de compresibilidad y composición no producen ninguna frontera. Sin embargo, el fluido puede ser un líquido comprimido si su temperatura está por debajo de un valor característico que no depende de la presión: en el plano P-T esta frontera es una línea vertical.""",
     "At pressures above the cricondenbar of the mixture, the factor Z remains above 0.75 over the whole temperature range and the compressibility and composition criteria produce no boundary. However, the fluid can be a compressed liquid if its temperature is below a characteristic value that does not depend on pressure: in the P-T plane this boundary is a vertical line."),
    ("""La cantidad que determina esa línea es la razón de parámetros adimensionales de la EOS:""",
     "The quantity that determines that line is the ratio of dimensionless parameters of the EOS:"),
    ("""El factor P se cancela en la razón, lo que explica directamente que la frontera sea independiente de la presión. La transición ocurre cuando A/B iguala la razón de las constantes universales de la ecuación de estado, Ω_a/Ω_b:""",
     "The factor P cancels in the ratio, which directly explains that the boundary is independent of pressure. The transition occurs when A/B equals the ratio of the universal constants of the equation of state, Ω_a/Ω_b:"),
    ("""Cuando A/B supera el umbral Ω_a/Ω_b, el término atractivo de la mezcla domina sobre la energía cinética y el fluido tiene carácter líquido; por debajo del umbral el término repulsivo prevalece y el fluido puede ser vapor. Los valores para cada EOS son:""",
     "When A/B exceeds the threshold Ω_a/Ω_b, the attractive term of the mixture dominates over the kinetic energy and the fluid has liquid character; below the threshold the repulsive term prevails and the fluid can be vapour. The values for each EOS are:"),
    ("""Estos valores son consecuencia directa de las constantes de Peng y Robinson (1976) y de Soave (1972); no son parámetros ajustados a datos experimentales.""",
     "These values are a direct consequence of the constants of Peng and Robinson (1976) and Soave (1972); they are not parameters fitted to experimental data."),

    ("5.4 Algoritmo completo", "5.4 Complete algorithm"),
    ("""Los tres criterios se evalúan en cascada. En cuanto uno produce una clasificación definitiva, los restantes no se evalúan.""",
     "The three criteria are evaluated in cascade. As soon as one produces a definitive classification, the rest are not evaluated."),
    ("""<b>Criterio A/B.</b> Si A/B = aₘ/(bₘRT) supera Ω_a/Ω_b de la EOS activa, el fluido se clasifica como <b>líquido</b> comprimido. Esta condición cubre la región de alta presión sin necesidad del punto crítico de la mezcla.""",
     "<b>A/B criterion.</b> If A/B = aₘ/(bₘRT) exceeds Ω_a/Ω_b of the active EOS, the fluid is classified as compressed <b>liquid</b>. This condition covers the high-pressure region without needing the critical point of the mixture."),
    ("""<b>Compresibilidad isotérmica.</b> Si Z &gt; 0.3 y β &gt; 0.75 simultáneamente, el fluido se clasifica como <b>vapor</b>. La condición Z &gt; 0.3 descarta líquidos muy comprimidos donde β puede ser elevado.""",
     "<b>Isothermal compressibility.</b> If Z &gt; 0.3 and β &gt; 0.75 simultaneously, the fluid is classified as <b>vapour</b>. The condition Z &gt; 0.3 rules out very compressed liquids where β can be high."),
    ("""<b>Composición de ligeros.</b> Si Z &gt; 0.75 y la suma de fracciones molares de los compuestos con punto normal de ebullición menor a 230 K supera la de los pesados, el fluido se clasifica como <b>vapor</b>; en caso contrario como <b>líquido</b>.""",
     "<b>Light-component composition.</b> If Z &gt; 0.75 and the sum of mole fractions of the compounds with normal boiling point below 230 K exceeds that of the heavy ones, the fluid is classified as <b>vapour</b>; otherwise as <b>liquid</b>."),
    ("""El criterio β tiene prioridad sobre el criterio A/B porque β &gt; 0.75 es condición suficiente de comportamiento gaseoso incluso a alta presión (por ejemplo, cerca del punto crítico de la mezcla). El criterio A/B tiene prioridad sobre la regla de composición porque sin esa compuerta, en la región densa donde Z permanece por encima de 0.75, la regla de composición devolvería vapor en todo el rango de temperatura.""",
     "The β criterion has priority over the A/B criterion because β &gt; 0.75 is a sufficient condition for gaseous behaviour even at high pressure (for example, near the critical point of the mixture). The A/B criterion has priority over the composition rule because without that gate, in the dense region where Z remains above 0.75, the composition rule would return vapour over the entire temperature range."),
    ("""Los compuestos con NBP &lt; 230 K en el sistema de ThermoPhase son N₂ (77 K), metano (111 K), etano (185 K) y CO₂ (195 K). El propano (NBP ≈ 231 K) y los restantes quedan clasificados como pesados.""",
     "The compounds with NBP &lt; 230 K in the ThermoPhase system are N₂ (77 K), methane (111 K), ethane (185 K) and CO₂ (195 K). Propane (NBP ≈ 231 K) and the rest are classified as heavy."),

    ("5.5 Variante con parámetros PVTsim", "5.5 Variant with PVTsim parameters"),
    ("""Las variantes PR_PVT y SRK_PVT aplican el mismo algoritmo de identificación. Las constantes Ω_a/Ω_b son idénticas porque la forma cúbica de las EOS no varía entre bases de datos.""",
     "The PR_PVT and SRK_PVT variants apply the same identification algorithm. The Ω_a/Ω_b constants are identical because the cubic form of the EOS does not vary between databases."),
    ("""Los valores de aₘ y bₘ sí dependen de los parámetros de componente. PVTsim sigue las tablas de Pedersen y Christensen (2007), que para los componentes puros ligeros difieren ligeramente de las propiedades de la base de datos de HYSYS, principalmente en Tc y ω del metano y el etano. Esas diferencias desplazan la temperatura de frontera en la misma magnitud que el error en los parámetros de componente.""",
     "The values of aₘ and bₘ do depend on the component parameters. PVTsim follows the tables of Pedersen and Christensen (2007), which for the light pure components differ slightly from the properties of the HYSYS database, mainly in the Tc and ω of methane and ethane. Those differences shift the boundary temperature by the same magnitude as the error in the component parameters."),
    ("""Peng, D.Y. y Robinson, D.B. (1976). A Two-Constant Equation of State. <em>Industrial and Engineering Chemistry Fundamentals</em>, 15(1), 59-64.""",
     "Peng, D.Y. and Robinson, D.B. (1976). A Two-Constant Equation of State. <em>Industrial and Engineering Chemistry Fundamentals</em>, 15(1), 59-64."),
    ("""Soave, G. (1972). Equilibrium constants from a modified Redlich-Kwong equation of state. <em>Chemical Engineering Science</em>, 27(6), 1197-1203.""",
     "Soave, G. (1972). Equilibrium constants from a modified Redlich-Kwong equation of state. <em>Chemical Engineering Science</em>, 27(6), 1197-1203."),
    ("""Pedersen, K.S. y Christensen, P.L. (2007). <em>Phase Behavior of Petroleum Reservoir Fluids</em>. CRC Press.""",
     "Pedersen, K.S. and Christensen, P.L. (2007). <em>Phase Behavior of Petroleum Reservoir Fluids</em>. CRC Press."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 6 — Densidad de líquido y vapor
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("6.1 Densidad de líquido y vapor", "6.1 Liquid and vapour density"),
    ("""La densidad es una de las propiedades derivadas más utilizadas en el diseño de procesos: interviene en el dimensionamiento de tuberías y recipientes, en el cálculo de la caída de presión y en la medición de inventarios. Una vez resuelto el equilibrio y conocido el factor de compresibilidad de cada fase, la densidad puede obtenerse directamente de la ecuación de estado; sin embargo, las ecuaciones cúbicas predicen el volumen del líquido con un error apreciable, típicamente entre 5 y 15 por ciento, mientras que reproducen el volumen del vapor con buena exactitud.""",
     "Density is one of the most widely used derived properties in process design: it is involved in the sizing of pipes and vessels, in the calculation of pressure drop and in inventory measurement. Once the equilibrium is solved and the compressibility factor of each phase is known, the density can be obtained directly from the equation of state; however, cubic equations predict the liquid volume with an appreciable error, typically between 5 and 15 per cent, while they reproduce the vapour volume with good accuracy."),
    ("""Por esta razón el programa ofrece dos rutas de cálculo de densidad. La fase vapor se evalúa siempre con la ecuación de estado. Para la fase líquida el usuario puede elegir entre la densidad de la propia ecuación de estado o el método de estados correspondientes COSTALD, que fue desarrollado específicamente para densidades de líquido y alcanza errores inferiores al uno por ciento en el rango de hidrocarburos. Adicionalmente, cuando se usa la densidad de la ecuación de estado puede aplicarse la corrección de volumen de Peneloux, que mejora la densidad de líquido mediante un traslado del volumen molar.""",
     "For this reason the program offers two density calculation routes. The vapour phase is always evaluated with the equation of state. For the liquid phase the user can choose between the density of the equation of state itself or the COSTALD corresponding-states method, which was developed specifically for liquid densities and achieves errors below one per cent in the hydrocarbon range. Additionally, when the density of the equation of state is used, the Peneloux volume correction can be applied, which improves the liquid density through a molar-volume shift."),
    ("""El programa aplica la ruta seleccionada de forma consistente en todos los puntos donde reporta densidad: el resultado del flash, la pestaña de propiedades, la pestaña de saturación y el mapa de densidad comparten la misma función de cálculo, de modo que un mismo estado siempre produce el mismo valor de densidad y de factor de compresibilidad.""",
     "The program applies the selected route consistently at all points where it reports density: the flash result, the properties tab, the saturation tab and the density map share the same calculation function, so that the same state always produces the same density and compressibility factor value."),

    ("6.2 Densidad por la ecuación de estado", "6.2 Density from the equation of state"),
    ("""La ruta más directa obtiene el volumen molar del factor de compresibilidad de la fase. Resuelto el equilibrio, la ecuación cúbica entrega el factor Z de cada fase; el volumen molar se despeja de la definición del factor de compresibilidad:""",
     "The most direct route obtains the molar volume from the compressibility factor of the phase. Once the equilibrium is solved, the cubic equation delivers the Z factor of each phase; the molar volume is solved from the definition of the compressibility factor:"),
    ("""y la densidad másica se obtiene dividiendo el peso molecular de la fase entre el volumen molar:""",
     "and the mass density is obtained by dividing the molecular weight of the phase by the molar volume:"),
    ("""donde M es el peso molecular de la mezcla en la fase considerada, calculado como la suma de las fracciones molares por los pesos moleculares de cada componente. Esta ruta es la que el programa usa siempre para la fase vapor y la que emplea para la fase líquida cuando el usuario selecciona el método de la ecuación de estado.""",
     "where M is the molecular weight of the mixture in the phase considered, computed as the sum of the mole fractions times the molecular weights of each component. This route is the one the program always uses for the vapour phase and the one it uses for the liquid phase when the user selects the equation-of-state method."),
    ("""El motor interno opera en unidades de campo, con la presión en psia, la temperatura en grados Rankine y la constante universal de los gases igual a 10.7316 psi·ft³/(lbmol·°R). El volumen molar resulta en ft³/lbmol y la densidad en lb/ft³; la conversión al sistema de unidades activo se aplica en la capa de presentación.""",
     "The internal engine operates in field units, with pressure in psia, temperature in degrees Rankine and the universal gas constant equal to 10.7316 psi·ft³/(lbmol·°R). The molar volume results in ft³/lbmol and the density in lb/ft³; the conversion to the active unit system is applied in the presentation layer."),

    ("6.3 El método COSTALD", "6.3 The COSTALD method"),
    ("""El método de estados correspondientes para densidad de líquido (Corresponding States Liquid Density) predice el volumen del líquido a partir de la temperatura reducida y de un parámetro característico de cada componente. Fue formulado por Hankinson y Thomson y adoptado como norma por el American Petroleum Institute. El programa lo utiliza para la densidad de la fase líquida cuando el usuario elige este método.""",
     "The corresponding-states method for liquid density (Corresponding States Liquid Density) predicts the liquid volume from the reduced temperature and a characteristic parameter of each component. It was formulated by Hankinson and Thomson and adopted as a standard by the American Petroleum Institute. The program uses it for the density of the liquid phase when the user chooses this method."),
    ("""Cada componente aporta dos parámetros propios: el volumen característico V*, que tiene unidades de volumen molar, y un factor acéntrico específico del método. El cálculo se organiza en cuatro etapas: primero se combinan los parámetros de los componentes en parámetros de mezcla; después se evalúa el volumen del líquido saturado; luego se estima la presión de saturación de la mezcla; y finalmente se corrige el volumen por el efecto de la presión para obtener el líquido comprimido.""",
     "Each component contributes two of its own parameters: the characteristic volume V*, which has units of molar volume, and a method-specific acentric factor. The calculation is organized in four stages: first the component parameters are combined into mixture parameters; then the saturated liquid volume is evaluated; then the saturation pressure of the mixture is estimated; and finally the volume is corrected for the effect of pressure to obtain the compressed liquid."),
    ("Parámetros de mezcla", "Mixture parameters"),
    ("""El volumen característico de la mezcla combina los volúmenes de los componentes mediante una regla de tercios que pondera la contribución lineal y las contribuciones de las potencias dos tercios y un tercio:""",
     "The characteristic volume of the mixture combines the component volumes through a rule of thirds that weights the linear contribution and the contributions of the two-thirds and one-third powers:"),
    ("""La temperatura pseudocrítica de la mezcla se obtiene de una doble suma sobre todos los pares de componentes, ponderada por el producto de los volúmenes característicos y las temperaturas críticas:""",
     "The pseudocritical temperature of the mixture is obtained from a double sum over all pairs of components, weighted by the product of the characteristic volumes and the critical temperatures:"),
    ("""El factor acéntrico de la mezcla es el promedio molar de los factores acéntricos de los componentes:""",
     "The acentric factor of the mixture is the molar average of the acentric factors of the components:"),
    ("""La presión pseudocrítica de la mezcla se deriva de un factor de compresibilidad crítico que depende del factor acéntrico:""",
     "The pseudocritical pressure of the mixture is derived from a critical compressibility factor that depends on the acentric factor:"),

    ("6.4 Volumen del líquido saturado", "6.4 Saturated liquid volume"),
    ("""El volumen del líquido saturado se expresa como el producto del volumen característico de la mezcla por una función de volumen reducido, corregida por una función de desviación que escala con el factor acéntrico:""",
     "The saturated liquid volume is expressed as the product of the characteristic volume of the mixture by a reduced-volume function, corrected by a deviation function that scales with the acentric factor:"),
    ("""La función de volumen reducido de referencia depende únicamente de la temperatura reducida a través de la variable auxiliar τ = 1 − T<sub>r</sub>, y es válida en el intervalo 0.25 &lt; T<sub>r</sub> &lt; 0.95:""",
     "The reference reduced-volume function depends only on the reduced temperature through the auxiliary variable τ = 1 − T<sub>r</sub>, and is valid in the interval 0.25 &lt; T<sub>r</sub> &lt; 0.95:"),
    ("""La función de desviación introduce la dependencia con el factor acéntrico y se expresa como un cociente de polinomios en la temperatura reducida:""",
     "The deviation function introduces the dependence on the acentric factor and is expressed as a ratio of polynomials in the reduced temperature:"),
    ("""El término constante 1.00001 en el denominador desplaza ligeramente la singularidad fuera del punto crítico para evitar la división por cero en T<sub>r</sub> = 1. La densidad del líquido saturado es el peso molecular dividido entre el volumen saturado.""",
     "The constant term 1.00001 in the denominator slightly shifts the singularity away from the critical point to avoid division by zero at T<sub>r</sub> = 1. The saturated liquid density is the molecular weight divided by the saturated volume."),

    ("6.5 Presión de saturación de la mezcla", "6.5 Saturation pressure of the mixture"),
    ("""La corrección por presión requiere conocer la presión de saturación de la mezcla a la temperatura de trabajo. Se emplea la ecuación de vapor de Riedel en la formulación de Hankinson, Estes y Coker, que expresa la presión de saturación reducida como suma de un término de referencia y un término proporcional al factor acéntrico:""",
     "The pressure correction requires knowing the saturation pressure of the mixture at the working temperature. The Riedel vapour equation is used in the formulation of Hankinson, Estes and Coker, which expresses the reduced saturation pressure as the sum of a reference term and a term proportional to the acentric factor:"),
    ("""Los dos términos se construyen a partir de dos funciones auxiliares de la temperatura reducida:""",
     "The two terms are built from two auxiliary functions of the reduced temperature:"),
    ("""La presión de saturación dimensional resulta del producto de la presión reducida por la presión pseudocrítica de la mezcla:""",
     "The dimensional saturation pressure results from the product of the reduced pressure and the pseudocritical pressure of the mixture:"),

    ("6.6 Corrección por presión del líquido comprimido", "6.6 Pressure correction of the compressed liquid"),
    ("""El volumen saturado corresponde al líquido en equilibrio con su vapor. A presiones mayores que la de saturación el líquido se comprime, y su volumen disminuye según una ecuación de tipo Tait generalizada que relaciona el volumen comprimido con el saturado a través de un término logarítmico en la presión:""",
     "The saturated volume corresponds to the liquid in equilibrium with its vapour. At pressures greater than the saturation pressure the liquid is compressed, and its volume decreases according to a generalized Tait-type equation that relates the compressed volume to the saturated one through a logarithmic term in the pressure:"),
    ("""El parámetro B tiene unidades de presión y establece la escala característica de la compresión. Se obtiene multiplicando la presión pseudocrítica por un polinomio en τ = 1 − T<sub>r</sub>:""",
     "The parameter B has units of pressure and establishes the characteristic scale of the compression. It is obtained by multiplying the pseudocritical pressure by a polynomial in τ = 1 − T<sub>r</sub>:"),
    ("""El coeficiente e₁ y el coeficiente C dependen del factor acéntrico de la mezcla:""",
     "The coefficient e₁ and the coefficient C depend on the acentric factor of the mixture:"),
    ("""La densidad del líquido comprimido es el peso molecular de la fase dividido entre este volumen corregido. La corrección solo se aplica cuando la presión de trabajo supera la de saturación; en caso contrario se conserva el volumen saturado.""",
     "The density of the compressed liquid is the molecular weight of the phase divided by this corrected volume. The correction is only applied when the working pressure exceeds the saturation pressure; otherwise the saturated volume is kept."),

    ("6.7 Transición al régimen supercrítico", "6.7 Transition to the supercritical regime"),
    ("""La correlación del volumen saturado pierde validez cuando la temperatura reducida se acerca a la unidad, porque las funciones de volumen reducido divergen en las proximidades del punto crítico. Para evitar una discontinuidad en la densidad al pasar del líquido al fluido supercrítico, el programa distingue tres regímenes según la temperatura pseudo-reducida de la mezcla.""",
     "The saturated-volume correlation loses validity when the reduced temperature approaches unity, because the reduced-volume functions diverge near the critical point. To avoid a discontinuity in the density when passing from liquid to supercritical fluid, the program distinguishes three regimes according to the pseudo-reduced temperature of the mixture."),
    ("""Por debajo de T<sub>r</sub> = 0.95 se aplica el método COSTALD completo con la corrección por presión. Por encima de T<sub>r</sub> = 1.0 el método deja de tener sentido físico y la densidad del líquido se toma directamente de la ecuación de estado. En la banda intermedia, entre T<sub>r</sub> = 0.95 y T<sub>r</sub> = 1.0, la densidad se interpola con un perfil cuadrático entre la densidad de líquido en T<sub>r</sub> = 0.95 obtenida por COSTALD y la densidad de la ecuación de estado en T<sub>r</sub> = 1.0:""",
     "Below T<sub>r</sub> = 0.95 the full COSTALD method with the pressure correction is applied. Above T<sub>r</sub> = 1.0 the method loses physical meaning and the liquid density is taken directly from the equation of state. In the intermediate band, between T<sub>r</sub> = 0.95 and T<sub>r</sub> = 1.0, the density is interpolated with a quadratic profile between the liquid density at T<sub>r</sub> = 0.95 obtained by COSTALD and the equation-of-state density at T<sub>r</sub> = 1.0:"),
    ("""El perfil cuadrático reproduce la curvatura de la densidad hacia el punto crítico y garantiza una transición suave hacia el régimen supercrítico. Esta banda de suavizado corresponde al comportamiento estándar del cálculo de densidad de líquido con estados correspondientes.""",
     "The quadratic profile reproduces the curvature of the density toward the critical point and guarantees a smooth transition to the supercritical regime. This smoothing band corresponds to the standard behaviour of the liquid density calculation with corresponding states."),
    ("Alcance del método", "Scope of the method"),
    ("""El método COSTALD alcanza su máxima exactitud para hidrocarburos con factor acéntrico moderado. Para mezclas muy ligeras dominadas por metano, con peso molecular por debajo de 30, la correlación conserva un residuo pequeño inherente al modelo de estados correspondientes, documentado por sus autores. En el rango habitual de gas natural y condensados el método reproduce las densidades de referencia con error inferior al uno por ciento.""",
     "The COSTALD method reaches its maximum accuracy for hydrocarbons with moderate acentric factor. For very light mixtures dominated by methane, with molecular weight below 30, the correlation retains a small residual inherent to the corresponding-states model, documented by its authors. In the usual range of natural gas and condensates the method reproduces the reference densities with an error below one per cent."),
    ("""Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for saturated densities of liquids and their mixtures. <em>AIChE Journal</em>, 25(4), 653-663.""",
     "Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for saturated densities of liquids and their mixtures. <em>AIChE Journal</em>, 25(4), 653-663."),
    ("""Thomson, G.H., Brobst, K.R. y Hankinson, R.W. (1982). An improved correlation for densities of compressed liquids and liquid mixtures. <em>AIChE Journal</em>, 28(4), 671-676.""",
     "Thomson, G.H., Brobst, K.R. and Hankinson, R.W. (1982). An improved correlation for densities of compressed liquids and liquid mixtures. <em>AIChE Journal</em>, 28(4), 671-676."),

    ("6.8 Corrección de volumen de Peneloux", "6.8 Peneloux volume correction"),
    ("""La corrección de volumen de Peneloux (traslado de volumen o volume shift) es un método empírico que mejora la densidad de líquido predicha por la ecuación de estado sin alterar el equilibrio de fases. Se aplica cuando el usuario selecciona la densidad de la ecuación de estado y activa la corrección desde el selector correspondiente.""",
     "The Peneloux volume correction (volume translation or volume shift) is an empirical method that improves the liquid density predicted by the equation of state without altering the phase equilibrium. It is applied when the user selects the density of the equation of state and activates the correction from the corresponding selector."),
    ("""La idea es sencilla: las ecuaciones cúbicas predicen un volumen molar de líquido sistemáticamente desviado del real. Peneloux propuso trasladar el volumen calculado una cantidad constante para cada componente, de modo que el volumen corregido reproduzca mejor la densidad. El volumen trasladado de la mezcla es el de la ecuación de estado menos el parámetro de traslado:""",
     "The idea is simple: cubic equations predict a liquid molar volume systematically deviated from the real one. Peneloux proposed shifting the calculated volume by a constant amount for each component, so that the corrected volume better reproduces the density. The shifted volume of the mixture is that of the equation of state minus the shift parameter:"),
    ("""El parámetro de traslado de cada componente se estima a partir de sus propiedades críticas y del factor de compresibilidad de Rackett, con constantes distintas para cada ecuación de estado:""",
     "The shift parameter of each component is estimated from its critical properties and the Rackett compressibility factor, with different constants for each equation of state:"),
    ("Neutralidad frente al equilibrio", "Neutrality with respect to equilibrium"),
    ("""El traslado de volumen es algebraicamente neutro en el cálculo del equilibrio de fases. Al aplicarse el mismo desplazamiento al volumen de ambas fases, la contribución del traslado se cancela en la relación de fugacidades que gobierna el reparto de componentes, de modo que las fracciones molares de vapor y líquido, las constantes de equilibrio y la propia frontera de la envolvente no se modifican. Lo que cambia es el volumen molar reportado de cada fase y, en consecuencia, su densidad y su factor de compresibilidad.""",
     "The volume shift is algebraically neutral in the phase equilibrium calculation. Since the same displacement is applied to the volume of both phases, the contribution of the shift cancels in the ratio of fugacities that governs the distribution of components, so that the vapour and liquid mole fractions, the equilibrium constants and the envelope boundary itself are not modified. What changes is the reported molar volume of each phase and, consequently, its density and its compressibility factor."),
    ("Efecto sobre el factor de compresibilidad", "Effect on the compressibility factor"),
    ("""Como el factor de compresibilidad es proporcional al volumen molar, el traslado se refleja directamente en el Z de cada fase. Sustituyendo el volumen corregido en la definición del factor de compresibilidad se obtiene una expresión que resta al Z de la ecuación de estado un término proporcional al parámetro de traslado:""",
     "Since the compressibility factor is proportional to the molar volume, the shift is reflected directly in the Z of each phase. Substituting the corrected volume into the definition of the compressibility factor yields an expression that subtracts from the equation-of-state Z a term proportional to the shift parameter:"),
    ("""La corrección se aplica tanto a la fase líquida como a la fase vapor, de manera que el factor de compresibilidad y la densidad de ambas fases son coherentes con el volumen trasladado. En la fase vapor el efecto es pequeño porque el volumen molar es grande frente al parámetro de traslado, pero no es nulo; en la fase líquida el efecto es mayor y es donde el método aporta la mejora buscada.""",
     "The correction is applied to both the liquid phase and the vapour phase, so that the compressibility factor and the density of both phases are consistent with the shifted volume. In the vapour phase the effect is small because the molar volume is large compared with the shift parameter, but it is not zero; in the liquid phase the effect is larger and is where the method provides the sought improvement."),
    ("""Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase Equilibria</em>, 8(1), 7-23.""",
     "Péneloux, A., Rauzy, E. and Fréze, R. (1982). A consistent correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase Equilibria</em>, 8(1), 7-23."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 7 — Entalpía y entropía
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("7.1 Entalpía y entropía de la mezcla", "7.1 Enthalpy and entropy of the mixture"),
    ("""La entalpía y la entropía son las propiedades termodinámicas que gobiernan los balances de energía de un proceso: la entalpía interviene en el cálculo de cargas térmicas de intercambiadores y en el trabajo de compresión, y la entropía permite evaluar procesos ideales de referencia como la compresión isentrópica. El programa calcula ambas propiedades para cada fase a partir de la composición, la temperatura y la presión.""",
     "Enthalpy and entropy are the thermodynamic properties that govern the energy balances of a process: enthalpy is involved in the calculation of heat exchanger duties and in compression work, and entropy allows the evaluation of ideal reference processes such as isentropic compression. The program computes both properties for each phase from the composition, temperature and pressure."),
    ("""El cálculo sigue el esquema de estado de referencia más desviación. Cada propiedad se descompone en una contribución de gas ideal, que depende solo de la temperatura y la composición, y una contribución de desviación que recoge el efecto de las fuerzas intermoleculares a la presión de trabajo. La contribución de gas ideal se evalúa componente por componente a partir de la capacidad calorífica; la desviación se obtiene de la ecuación de estado de Peng-Robinson.""",
     "The calculation follows the reference-state-plus-departure scheme. Each property is decomposed into an ideal-gas contribution, which depends only on temperature and composition, and a departure contribution that captures the effect of intermolecular forces at the working pressure. The ideal-gas contribution is evaluated component by component from the heat capacity; the departure is obtained from the Peng-Robinson equation of state."),
    ("""El término entre corchetes es la desviación respecto al gas ideal. Este esquema permite usar una base de capacidad calorífica de alta exactitud para la parte ideal y reservar la ecuación de estado para el efecto de la presión, que es donde las ecuaciones cúbicas son más fiables.""",
     "The term in brackets is the departure from the ideal gas. This scheme allows a high-accuracy heat capacity basis to be used for the ideal part and the equation of state to be reserved for the pressure effect, which is where cubic equations are most reliable."),

    ("7.2 Contribución de gas ideal", "7.2 Ideal-gas contribution"),
    ("""La entalpía de gas ideal de cada componente se obtiene de un polinomio de temperatura de quinto grado que representa la entalpía específica referida a la base interna del banco de propiedades, ajustada por un desplazamiento que sitúa el origen en la entalpía de formación a 25 grados Celsius:""",
     "The ideal-gas enthalpy of each component is obtained from a fifth-degree temperature polynomial that represents the specific enthalpy referred to the internal basis of the properties bank, adjusted by an offset that places the origin at the enthalpy of formation at 25 degrees Celsius:"),
    ("""El polinomio se evalúa con la temperatura en kelvin y entrega la entalpía específica en kJ/kg; el factor que contiene el peso molecular la convierte a unidades molares de campo. El desplazamiento de entalpía de cada componente es el valor tabulado en la base de propiedades y garantiza que las entalpías de distintos componentes compartan un origen común consistente con las entalpías de formación.""",
     "The polynomial is evaluated with temperature in kelvin and delivers the specific enthalpy in kJ/kg; the factor containing the molecular weight converts it to molar field units. The enthalpy offset of each component is the value tabulated in the properties bank and guarantees that the enthalpies of different components share a common origin consistent with the enthalpies of formation."),
    ("""La capacidad calorífica de gas ideal es la derivada del polinomio de entalpía respecto a la temperatura, multiplicada por el peso molecular para convertirla a base molar:""",
     "The ideal-gas heat capacity is the derivative of the enthalpy polynomial with respect to temperature, multiplied by the molecular weight to convert it to a molar basis:"),
    ("""La entropía de gas ideal de cada componente parte de un desplazamiento tabulado y añade la integral de la capacidad calorífica sobre la temperatura, más el término de presión que refiere la entropía a la presión de una atmósfera:""",
     "The ideal-gas entropy of each component starts from a tabulated offset and adds the integral of the heat capacity over temperature, plus the pressure term that refers the entropy to the pressure of one atmosphere:"),
    ("""La integral se resuelve numéricamente por la regla de Simpson compuesta. Para la mezcla, las contribuciones ideales se suman ponderadas por las fracciones molares y la entropía incorpora además el término de mezclado ideal, que refleja el aumento de entropía al combinar componentes puros:""",
     "The integral is solved numerically by the composite Simpson's rule. For the mixture, the ideal contributions are summed weighted by the mole fractions and the entropy additionally incorporates the ideal-mixing term, which reflects the increase of entropy when combining pure components:"),

    ("7.3 Desviación por la ecuación de estado", "7.3 Departure from the equation of state"),
    ("""La desviación respecto al gas ideal recoge el efecto de las fuerzas intermoleculares y se deriva analíticamente de la ecuación de Peng-Robinson. La desviación de entalpía combina el término del factor de compresibilidad con un término que depende del parámetro atractivo y de su derivada respecto a la temperatura:""",
     "The departure from the ideal gas captures the effect of intermolecular forces and is derived analytically from the Peng-Robinson equation. The enthalpy departure combines the compressibility-factor term with a term that depends on the attractive parameter and its derivative with respect to temperature:"),
    ("""La desviación de entropía tiene una estructura análoga, con el término del factor de compresibilidad y el término logarítmico ponderado por la derivada del parámetro atractivo:""",
     "The entropy departure has an analogous structure, with the compressibility-factor term and the logarithmic term weighted by the derivative of the attractive parameter:"),
    ("""donde B es el parámetro adimensional de covolumen de la mezcla, B = b<sub>m</sub>·P/(R·T), y Z es el factor de compresibilidad de la fase. La derivada del parámetro atractivo respecto a la temperatura se obtiene de la regla de mezclado aplicada a las derivadas de cada componente:""",
     "where B is the dimensionless co-volume parameter of the mixture, B = b<sub>m</sub>·P/(R·T), and Z is the compressibility factor of the phase. The derivative of the attractive parameter with respect to temperature is obtained from the mixing rule applied to the derivatives of each component:"),
    ("""El término de presión de la entropía se contabiliza dentro de la contribución ideal, por lo que la desviación de entropía conserva únicamente el residual asociado a la no idealidad. Las desviaciones se evalúan con el factor de compresibilidad de la fase correspondiente: la raíz de líquido para la fase líquida y la raíz de vapor para la fase vapor.""",
     "The pressure term of the entropy is accounted for within the ideal contribution, so the entropy departure retains only the residual associated with non-ideality. The departures are evaluated with the compressibility factor of the corresponding phase: the liquid root for the liquid phase and the vapour root for the vapour phase."),

    ("7.4 Ensamblaje por fase", "7.4 Assembly by phase"),
    ("""La entalpía de una fase reúne la contribución ideal de cada componente y la desviación de la mezcla evaluada con el factor de compresibilidad de esa fase:""",
     "The enthalpy of a phase gathers the ideal contribution of each component and the mixture departure evaluated with the compressibility factor of that phase:"),
    ("""La entropía de una fase reúne las contribuciones ideales por componente, el término de mezclado ideal y la desviación de la mezcla:""",
     "The entropy of a phase gathers the ideal contributions per component, the ideal-mixing term and the mixture departure:"),
    ("""Cuando el sistema se encuentra en equilibrio de dos fases, la entalpía y la entropía globales se obtienen combinando las propiedades de cada fase ponderadas por la fracción de vapor. La base de entalpía y de entropía es la misma que emplea el simulador de referencia, de modo que los valores absolutos son directamente comparables además de las diferencias.""",
     "When the system is in two-phase equilibrium, the overall enthalpy and entropy are obtained by combining the properties of each phase weighted by the vapour fraction. The enthalpy and entropy basis is the same as that used by the reference simulator, so that the absolute values are directly comparable in addition to the differences."),
    ("""Las propiedades ideales se calculan siempre con los parámetros de Peng-Robinson, porque los desplazamientos de entalpía y de entropía están referidos a esa ecuación de estado; la contribución de desviación es la única que cambiaría con otra ecuación, y su efecto sobre el valor absoluto es pequeño frente a la contribución ideal.""",
     "The ideal properties are always computed with the Peng-Robinson parameters, because the enthalpy and entropy offsets are referred to that equation of state; the departure contribution is the only one that would change with another equation, and its effect on the absolute value is small compared with the ideal contribution."),
    ("""Smith, J.M., Van Ness, H.C. y Abbott, M.M. (2005). <em>Introduction to Chemical Engineering Thermodynamics</em>, 7ª ed. McGraw-Hill.""",
     "Smith, J.M., Van Ness, H.C. and Abbott, M.M. (2005). <em>Introduction to Chemical Engineering Thermodynamics</em>, 7th ed. McGraw-Hill."),
])


# ══════════════════════════════════════════════════════════════════════
# Sección 8 — Viscosidad
# ══════════════════════════════════════════════════════════════════════
registrar([
    ("8.1 El método Lohrenz-Bray-Clark", "8.1 The Lohrenz-Bray-Clark method"),
    ("""La viscosidad dinámica de una mezcla de hidrocarburos puede ser necesaria para el dimensionamiento de líneas de flujo, el cálculo de caídas de presión y la simulación de procesos de transporte. El programa calcula la viscosidad por el método de Lohrenz, Bray y Clark (1964), conocido por sus siglas LBC, que expresa la viscosidad de gas y de líquido a partir de una sola correlación polinómica en la densidad reducida. Este enfoque unificado es el que adopta el software de referencia para fluidos de yacimiento.""",
     "The dynamic viscosity of a hydrocarbon mixture may be needed for the sizing of flow lines, the calculation of pressure drops and the simulation of transport processes. The program computes the viscosity by the method of Lohrenz, Bray and Clark (1964), known by its acronym LBC, which expresses the viscosity of gas and liquid from a single polynomial correlation in the reduced density. This unified approach is the one adopted by the reference software for reservoir fluids."),
    ("""El método LBC descompone la viscosidad de la mezcla en dos contribuciones: la viscosidad del gas diluido a baja presión, que depende solo de la temperatura y la composición, y un residual de densidad que recoge el efecto de la presión. El residual se expresa como un polinomio de cuarto grado en la densidad reducida ρ<sub>r</sub> = ρ/ρ<sub>c</sub>, donde ρ<sub>c</sub> es la densidad crítica de la mezcla. La misma expresión es válida para la fase vapor y para la fase líquida.""",
     "The LBC method decomposes the viscosity of the mixture into two contributions: the dilute-gas viscosity at low pressure, which depends only on temperature and composition, and a density residual that captures the pressure effect. The residual is expressed as a fourth-degree polynomial in the reduced density ρ<sub>r</sub> = ρ/ρ<sub>c</sub>, where ρ<sub>c</sub> is the critical density of the mixture. The same expression is valid for the vapour phase and for the liquid phase."),
    ("""La viscosidad se calcula en cada flash para cada fase presente y se reporta en centipoise (cP), que coincide numéricamente con el milipascal- segundo (mPa·s) del Sistema Internacional. Solo se reporta la viscosidad por fase: la fase vapor y la fase líquida por separado. No existe un valor de viscosidad de mezcla bifásica porque la viscosidad no es una propiedad aditiva entre fases.""",
     "The viscosity is computed in each flash for each phase present and reported in centipoise (cP), which coincides numerically with the millipascal-second (mPa·s) of the International System. Only the per-phase viscosity is reported: the vapour phase and the liquid phase separately. There is no two-phase mixture viscosity value because viscosity is not an additive property between phases."),

    ("8.2 Viscosidad de gas diluido por componente", "8.2 Dilute-gas viscosity per component"),
    ("""La viscosidad del gas diluido de cada componente puro se obtiene de la correlación de Stiel y Thodos (1961), que distingue dos regímenes según la temperatura reducida T<sub>r,i</sub> = T/T<sub>c,i</sub>:""",
     "The dilute-gas viscosity of each pure component is obtained from the correlation of Stiel and Thodos (1961), which distinguishes two regimes according to the reduced temperature T<sub>r,i</sub> = T/T<sub>c,i</sub>:"),
    ("""El parámetro reductor de viscosidad individual ξ<sub>i</sub> combina las propiedades críticas del componente y su peso molecular:""",
     "The individual viscosity-reducing parameter ξ<sub>i</sub> combines the critical properties of the component and its molecular weight:"),
    ("""donde T<sub>ci</sub> se evalúa en kelvin y P<sub>ci</sub> en atmósferas para obtener η<sup>*</sup><sub>i</sub> en centipoise.""",
     "where T<sub>ci</sub> is evaluated in kelvin and P<sub>ci</sub> in atmospheres to obtain η<sup>*</sup><sub>i</sub> in centipoise."),
    ("""Las viscosidades de los componentes puros se combinan para obtener la viscosidad de la mezcla de gas diluido mediante la regla de Herning y Zippener (1936), que pondera cada contribución por la raíz cuadrada del peso molecular:""",
     "The viscosities of the pure components are combined to obtain the dilute-gas mixture viscosity through the rule of Herning and Zippener (1936), which weights each contribution by the square root of the molecular weight:"),
    ("""donde z<sub>i</sub> es la fracción molar del componente i en la fase considerada y N es el número de componentes con presencia en esa fase. Esta regla de mezcla reproduce la dependencia de la viscosidad del gas diluido con el peso molecular mejor que un promedio molar simple.""",
     "where z<sub>i</sub> is the mole fraction of component i in the phase considered and N is the number of components present in that phase. This mixing rule reproduces the dependence of the dilute-gas viscosity on the molecular weight better than a simple molar average."),

    ("8.3 Parámetro reductor y densidad crítica", "8.3 Reducing parameter and critical density"),
    ("""El parámetro reductor de viscosidad de la mezcla ξ tiene la misma forma que el de un componente puro pero usa las propiedades pseudocríticas de la mezcla calculadas como promedios molares:""",
     "The viscosity-reducing parameter of the mixture ξ has the same form as that of a pure component but uses the pseudocritical properties of the mixture computed as molar averages:"),
    ("con T<sub>c</sub> en kelvin y P<sub>c</sub> en atmósferas.",
     "with T<sub>c</sub> in kelvin and P<sub>c</sub> in atmospheres."),
    ("""La densidad crítica de la mezcla se obtiene del volumen crítico molar de cada componente mediante la regla de mezcla aditiva inversa:""",
     "The critical density of the mixture is obtained from the molar critical volume of each component through the inverse-additive mixing rule:"),
    ("""donde V<sub>ci</sub> es el volumen crítico molar del componente i, que para los componentes definidos se toma de la base de datos de propiedades. La densidad reducida de la fase es la densidad molar dividida entre la densidad crítica:""",
     "where V<sub>ci</sub> is the molar critical volume of component i, which for the defined components is taken from the properties database. The reduced density of the phase is the molar density divided by the critical density:"),
    ("""Una densidad reducida de uno corresponde al punto crítico de la mezcla. Para la fase vapor a baja presión ρ<sub>r</sub> es pequeño y el residual de densidad tiene poca influencia; para la fase líquida ρ<sub>r</sub> puede alcanzar valores de 2 a 3 y el residual domina sobre la contribución de gas diluido.""",
     "A reduced density of one corresponds to the critical point of the mixture. For the vapour phase at low pressure ρ<sub>r</sub> is small and the density residual has little influence; for the liquid phase ρ<sub>r</sub> can reach values of 2 to 3 and the residual dominates over the dilute-gas contribution."),

    ("8.4 Polinomio LBC y viscosidad de la mezcla", "8.4 LBC polynomial and mixture viscosity"),
    ("""El polinomio de cuarto grado en densidad reducida relaciona la viscosidad total de la fase con su viscosidad de gas diluido mediante la expresión central del método LBC:""",
     "The fourth-degree polynomial in reduced density relates the total viscosity of the phase to its dilute-gas viscosity through the central expression of the LBC method:"),
    ("""Los cinco coeficientes son constantes universales ajustadas por Lohrenz, Bray y Clark sobre datos de componentes puros y mezclas:""",
     "The five coefficients are universal constants fitted by Lohrenz, Bray and Clark on data of pure components and mixtures:"),
    ("Despejando la viscosidad de la fase:", "Solving for the viscosity of the phase:"),
    ("""El término 10<sup>-4</sup> garantiza que cuando ρ<sub>r</sub> = 0 la expresión se reduce exactamente a η<sup>*</sup>, asegurando continuidad con la viscosidad de gas diluido en el límite de baja densidad.""",
     "The term 10<sup>-4</sup> guarantees that when ρ<sub>r</sub> = 0 the expression reduces exactly to η<sup>*</sup>, ensuring continuity with the dilute-gas viscosity in the low-density limit."),
    ("""El método LBC es aplicable a gases y líquidos de yacimiento en el rango de condiciones habitual de la ingeniería de producción. Su principal ventaja es que usa los mismos parámetros de la ecuación de estado (T<sub>c</sub>, P<sub>c</sub>, volúmenes críticos) sin necesitar datos adicionales. La precisión típica para mezclas de hidrocarburos ligeros es de 5 a 10 por ciento, suficiente para la mayor parte de los cálculos de ingeniería. Para aceites pesados con alto contenido de fracciones C7+ la precisión puede ser menor.""",
     "The LBC method is applicable to reservoir gases and liquids in the usual range of conditions of production engineering. Its main advantage is that it uses the same parameters of the equation of state (T<sub>c</sub>, P<sub>c</sub>, critical volumes) without needing additional data. The typical accuracy for light hydrocarbon mixtures is 5 to 10 per cent, sufficient for most engineering calculations. For heavy oils with high content of C7+ fractions the accuracy may be lower."),
    ("""Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating Viscosities of Reservoir Fluids from Their Compositions. <em>Journal of Petroleum Technology</em>, octubre 1964, pp. 1171-1176.""",
     "Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating Viscosities of Reservoir Fluids from Their Compositions. <em>Journal of Petroleum Technology</em>, October 1964, pp. 1171-1176."),
    ("""Stiel, L.I. y Thodos, G. (1961). The Viscosity of Non-Polar Gases at Normal Pressures. <em>AIChE Journal</em>, 7, pp. 611-615.""",
     "Stiel, L.I. and Thodos, G. (1961). The Viscosity of Non-Polar Gases at Normal Pressures. <em>AIChE Journal</em>, 7, pp. 611-615."),
    ("""Herning, F. y Zippener, L. (1936). Calculation of the Viscosity of Technical Gas Mixtures from the Viscosity of the Individual Gases. <em>Gas und Wasserfach</em>, 79, pp. 69-73.""",
     "Herning, F. and Zippener, L. (1936). Calculation of the Viscosity of Technical Gas Mixtures from the Viscosity of the Individual Gases. <em>Gas und Wasserfach</em>, 79, pp. 69-73."),
    ("""Pedersen, K.S. y Christensen, P.L. (2007). <em>Phase Behavior of Petroleum Reservoir Fluids</em>. CRC Press.""",
     "Pedersen, K.S. and Christensen, P.L. (2007). <em>Phase Behavior of Petroleum Reservoir Fluids</em>. CRC Press."),
])


def traducir_titulo(titulo_es, idioma):
    """Traduce un título de sección/subsección del árbol.

    El árbol muestra los títulos SIN numeración (p.ej. 'Ecuación de estado'),
    mientras que TRAD_DOC los almacena CON numeración (p.ej.
    '1.1 Ecuación de estado'). Esta función normaliza y busca por el texto sin
    número, devolviendo el título en inglés también sin número.
    """
    if idioma != 'EN':
        return titulo_es
    clave_norm = _norm(titulo_es)
    # Buscar en TRAD_DOC una entrada cuyo texto sin número coincida.
    for es, en in TRAD_DOC.items():
        es_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', es).strip()
        if es_sin == clave_norm:
            return re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', en).strip()
    return titulo_es


# Índice invertido para acelerar traducir_titulo (se construye una vez).
_TITULO_INDEX = {}
for _es, _en in TRAD_DOC.items():
    _es_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', _es).strip()
    _en_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', _en).strip()
    _TITULO_INDEX[_es_sin] = _en_sin


def traducir_titulo_rapido(titulo_es, idioma):
    """Versión con índice del traductor de títulos."""
    if idioma != 'EN':
        return titulo_es
    return _TITULO_INDEX.get(_norm(titulo_es), titulo_es)


# Títulos de sección de nivel superior (encabezados del árbol sin contenido
# HTML propio). Se añaden al índice de títulos para que el árbol se traduzca.
_SECCIONES_TITULOS = {
    "Fundamentos de las EOS cúbicas": "Fundamentals of cubic EOS",
    "Parámetros de la ecuación de estado": "Equation of state parameters",
    "El cálculo flash (equilibrio L-V)": "The flash calculation (L-V equilibrium)",
    "Envolvente de fases": "Phase envelope",
    "Identificación de fase monofásica": "Single-phase identification",
    "Densidad de líquido y vapor": "Liquid and vapour density",
    "Entalpía y entropía": "Enthalpy and entropy",
    "Viscosidad": "Viscosity",
    "Poder calorífico y GPM": "Heating Value and GPM",
    "Formación de hidratos": "Hydrate Formation",
}
for _es, _en in _SECCIONES_TITULOS.items():
    _TITULO_INDEX[_norm(_es)] = _en


# Títulos del ÁRBOL que difieren de su encabezado <h2> (versiones abreviadas).
# Se registran con su traducción abreviada para que el árbol se traduzca.
_TITULOS_ARBOL = {
    "El coeficiente m y la función alfa": "The coefficient m and the alpha function",
    "Base de datos de los coeficientes": "Coefficient database",
    "Estimación inicial de las K": "Initial estimate of the K values",
    "Algoritmo completo del flash": "The complete flash algorithm",
    "Método de Ziervogel": "The Ziervogel method",
    "Método de Michelsen": "The Michelsen method",
    "Flujo de cálculo combinado": "Combined calculation flow",
    "El problema monofásico": "The single-phase problem",
    "Criterio de alta presión (A/B)": "High-pressure criterion (A/B)",
    "Variante PVTsim": "PVTsim variant",
    "Corrección por presión": "Pressure correction",
}
for _es, _en in _TITULOS_ARBOL.items():
    _TITULO_INDEX[_norm(_es)] = _en
