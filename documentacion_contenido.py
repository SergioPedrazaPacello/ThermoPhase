# -*- coding: utf-8 -*-
"""
Contenido de la Documentación técnica de ThermoPhase (español e inglés).

Cada capítulo tiene un título (es, en) y subsecciones; cada subsección es una
lista de bloques:
    ("p",  texto_es, texto_en)     párrafo
    ("h3", texto_es, texto_en)     subtítulo
    ("eq", latex)                  ecuación (mathtext de matplotlib)
    ("ul", [(es, en), ...])        lista
La numeración de capítulos y subsecciones se asigna automáticamente.
"""

CAPITULOS = [{'titulo': ('Introducción y datos de componentes', 'Introduction and component data'),
  'subsecciones': [{'titulo': ('Alcance del programa', 'Program scope'),
                    'bloques': [('p',
                                 'ThermoPhase es un simulador termodinámico de equilibrio de fases '
                                 'para gas natural y condensados basado en ecuaciones de estado '
                                 'cúbicas. Reproduce los procedimientos de cálculo de Aspen HYSYS '
                                 'y de PVTsim para un sistema definido de hasta catorce '
                                 'componentes: trece compuestos de hidrocarburos e inertes, y agua '
                                 'como componente opcional.',
                                 'ThermoPhase is a thermodynamic phase-equilibrium simulator for '
                                 'natural gas and condensates based on cubic equations of state. '
                                 'It reproduces the calculation procedures of Aspen HYSYS and '
                                 'PVTsim for a defined system of up to fourteen components: '
                                 'thirteen hydrocarbon and inert compounds, plus water as an '
                                 'optional component.'),
                                ('p',
                                 'Todos los cálculos se ejecutan con una de cuatro ecuaciones de '
                                 'estado seleccionables (Peng-Robinson y Soave-Redlich-Kwong, cada '
                                 'una con el juego de parámetros de HYSYS o de PVTsim). La '
                                 'ecuación seleccionada, sus parámetros de componente y su matriz '
                                 'de coeficientes de interacción binaria definen el equilibrio de '
                                 'fases y las propiedades derivadas de la ecuación de estado.',
                                 'All calculations are performed with one of four selectable '
                                 'equations of state (Peng-Robinson and Soave-Redlich-Kwong, each '
                                 'with either the HYSYS or the PVTsim parameter set). The selected '
                                 'equation, its component parameters, and its binary interaction '
                                 'coefficient matrix define the phase equilibrium and the '
                                 'properties derived from the equation of state.'),
                                ('h3', 'Funciones de cálculo', 'Calculation functions'),
                                ('ul',
                                 [('Flash isotérmico bifásico vapor-líquido con análisis de '
                                   'estabilidad de Michelsen.',
                                   'Two-phase vapor-liquid isothermal flash with Michelsen '
                                   'stability analysis.'),
                                  ('Flash trifásico (vapor, líquido de hidrocarburos y fase '
                                   'acuosa) cuando el agua está presente, con la regla de mezcla '
                                   'de Huron-Vidal para los pares con agua.',
                                   'Three-phase flash (vapor, hydrocarbon liquid, and aqueous '
                                   'phase) when water is present, with the Huron-Vidal mixing rule '
                                   'for the water pairs.'),
                                  ('Envolventes de fases de la mezcla sin agua y con agua '
                                   '(incluidas las fronteras de la fase acuosa), con punto crítico '
                                   'y líneas de calidad.',
                                   'Phase envelopes of the water-free and water-containing mixture '
                                   '(including the aqueous-phase boundaries), with critical point '
                                   'and quality lines.'),
                                  ('Puntos de saturación: presión y temperatura de burbuja y de '
                                   'rocío, cricondenbara y cricondenterma.',
                                   'Saturation points: bubble and dew pressure and temperature, '
                                   'cricondenbar and cricondentherm.'),
                                  ('Condiciones de formación de hidratos de gas (estructuras sI, '
                                   'sII y sH).',
                                   'Gas hydrate formation conditions (structures sI, sII, and '
                                   'sH).'),
                                  ('Propiedades volumétricas (factor de compresibilidad, densidad '
                                   'por la ecuación de estado, con corrección de volumen de '
                                   'Peneloux o por COSTALD), propiedades térmicas (entalpía y '
                                   'entropía) y propiedades de transporte (viscosidad de '
                                   'Lohrenz-Bray-Clark).',
                                   'Volumetric properties (compressibility factor, density from '
                                   'the equation of state, with the Peneloux volume correction, or '
                                   'from COSTALD), thermal properties (enthalpy and entropy), and '
                                   'transport properties (Lohrenz-Bray-Clark viscosity).'),
                                  ('Poder calorífico superior e inferior (GPSA), contenido de '
                                   'licuables GPM C3+ y contenido y capacidad de agua del gas.',
                                   'Higher and lower heating values (GPSA), GPM C3+ liquefiable '
                                   'content, and water content and water capacity of the gas.'),
                                  ('Análisis de sensibilidad de las propiedades frente a presión y '
                                   'temperatura.',
                                   'Sensitivity analysis of properties versus pressure and '
                                   'temperature.'),
                                  ('Reporte en PDF de los resultados.',
                                   'PDF report of the results.')]),
                                ('p',
                                 'La interfaz permite definir varios fluidos, cada uno con su '
                                 'composición, su ecuación de estado y su propia matriz de '
                                 'coeficientes de interacción binaria. Las propiedades de '
                                 'componente se consultan en una hoja por componente y los '
                                 'parámetros de la ecuación de estado se revisan y editan en la '
                                 'ventana de parámetros.',
                                 'The interface allows several fluids to be defined, each with its '
                                 'own composition, equation of state, and binary interaction '
                                 'coefficient matrix. Component properties are displayed on a '
                                 'per-component sheet, and the equation-of-state parameters are '
                                 'reviewed and edited in the parameters window.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Componentes del sistema', 'Component slate'),
                    'bloques': [('p',
                                 'ThermoPhase trabaja con una lista fija de componentes definidos, '
                                 'en el orden interno N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, '
                                 'nC6, nC7, nC8, nC9 y H₂O. Los trece primeros forman el sistema '
                                 'base de hidrocarburos e inertes; el agua ocupa la posición '
                                 'catorce y se incorpora al fluido solo cuando se activa en el '
                                 'gestor de componentes.',
                                 'ThermoPhase works with a fixed list of defined components, in '
                                 'the internal order N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, nC6, '
                                 'nC7, nC8, nC9, and H₂O. The first thirteen form the base '
                                 'hydrocarbon and inert system; water occupies position fourteen '
                                 'and enters the fluid only when it is activated in the component '
                                 'manager.'),
                                ('ul',
                                 [('Inertes: nitrógeno (N₂) y dióxido de carbono (CO₂).',
                                   'Inerts: nitrogen (N₂) and carbon dioxide (CO₂).'),
                                  ('Hidrocarburos livianos: metano (C1), etano (C2) y propano '
                                   '(C3).',
                                   'Light hydrocarbons: methane (C1), ethane (C2), and propane '
                                   '(C3).'),
                                  ('Butanos y pentanos: isobutano o 2-metilpropano (iC4), n-butano '
                                   '(nC4), isopentano o 2-metilbutano (iC5) y n-pentano (nC5).',
                                   'Butanes and pentanes: isobutane or 2-methylpropane (iC4), '
                                   'n-butane (nC4), isopentane or 2-methylbutane (iC5), and '
                                   'n-pentane (nC5).'),
                                  ('Fracción pesada como n-alcanos: n-hexano (nC6), n-heptano '
                                   '(nC7), n-octano (nC8) y n-nonano (nC9).',
                                   'Heavy fraction as n-alkanes: n-hexane (nC6), n-heptane (nC7), '
                                   'n-octane (nC8), and n-nonane (nC9).'),
                                  ('Agua (H₂O), componente opcional.',
                                   'Water (H₂O), optional component.')]),
                                ('p',
                                 'Sin agua, el equilibrio de fases se resuelve con el motor '
                                 'bifásico de trece componentes. Con agua activa, el cálculo pasa '
                                 'al motor multifásico de catorce componentes, que admite una fase '
                                 'acuosa y aplica la regla de mezcla de Huron-Vidal a los pares '
                                 'agua-hidrocarburo.',
                                 'Without water, phase equilibrium is solved with the '
                                 'thirteen-component two-phase engine. With water active, the '
                                 'calculation moves to the fourteen-component multiphase engine, '
                                 'which allows an aqueous phase and applies the Huron-Vidal mixing '
                                 'rule to the water-hydrocarbon pairs.'),
                                ('p',
                                 'Cada componente tiene además una temperatura normal de '
                                 'ebullición tabulada (valores API/NIST). Esta propiedad clasifica '
                                 'los componentes en livianos (T<sub>b</sub> &lt; 230 K) y pesados '
                                 'en el criterio de identificación de fase de HYSYS; en el sistema '
                                 'de trece componentes son livianos N₂, CO₂, C1 y C2.',
                                 'Each component also has a tabulated normal boiling point '
                                 '(API/NIST values). This property classifies the components as '
                                 'light (T<sub>b</sub> &lt; 230 K) or heavy in the HYSYS phase '
                                 'identification criterion; in the thirteen-component system N₂, '
                                 'CO₂, C1, and C2 are light.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 "Poling, B.E., Prausnitz, J.M. y O'Connell, J.P. (2001). <em>The "
                                 'Properties of Gases and Liquids</em>, 5.ª ed. McGraw-Hill.',
                                 "Poling, B.E., Prausnitz, J.M. and O'Connell, J.P. (2001). "
                                 '<em>The Properties of Gases and Liquids</em>, 5th ed. '
                                 'McGraw-Hill.')]},
                   {'titulo': ('Parámetros de componente de HYSYS', 'HYSYS component parameters'),
                    'bloques': [('p',
                                 'El juego de parámetros de HYSYS corresponde a los valores que '
                                 'Aspen HYSYS reporta en su paquete de fluidos para los métodos '
                                 'Peng-Robinson y SRK. Se emplea en las ecuaciones de estado PR '
                                 '(HYSYS) y SRK (HYSYS).',
                                 'The HYSYS parameter set corresponds to the values that Aspen '
                                 'HYSYS reports in its fluid package for the Peng-Robinson and SRK '
                                 'methods. It is used by the PR (HYSYS) and SRK (HYSYS) equations '
                                 'of state.'),
                                ('ul',
                                 [('Temperatura crítica T<sub>c</sub> (°R) y presión crítica '
                                   'P<sub>c</sub> (psia): un único juego para PR y SRK, pues HYSYS '
                                   'no varía las propiedades críticas entre ambos paquetes.',
                                   'Critical temperature T<sub>c</sub> (°R) and critical pressure '
                                   'P<sub>c</sub> (psia): a single set for PR and SRK, because '
                                   'HYSYS does not change the critical properties between the two '
                                   'packages.'),
                                  ('Factor acéntrico: dos juegos distintos, ω<sub>PR</sub> para '
                                   'Peng-Robinson y ω<sub>SRK</sub> para SRK (por ejemplo, '
                                   '0.011498 y 0.00740 para el metano). Cada ecuación toma su '
                                   'propio factor acéntrico en la función α(T).',
                                   'Acentric factor: two different sets, ω<sub>PR</sub> for '
                                   'Peng-Robinson and ω<sub>SRK</sub> for SRK (for example, '
                                   '0.011498 and 0.00740 for methane). Each equation uses its own '
                                   'acentric factor in the α(T) function.'),
                                  ('Peso molecular M (lb/lbmol).',
                                   'Molecular weight M (lb/lbmol).'),
                                  ('Volumen crítico V<sub>c</sub> (cm³/mol) de Reid, Prausnitz y '
                                   'Sherwood, empleado en la viscosidad de Lohrenz-Bray-Clark.',
                                   'Critical volume V<sub>c</sub> (cm³/mol) from Reid, Prausnitz, '
                                   'and Sherwood, used in the Lohrenz-Bray-Clark viscosity.'),
                                  ('Volumen característico V* de COSTALD (ft³/lbmol), con los '
                                   'valores de HYSYS; la correlación COSTALD usa junto con él el '
                                   'factor acéntrico ω<sub>SRK</sub>.',
                                   'COSTALD characteristic volume V* (ft³/lbmol), with the HYSYS '
                                   'values; the COSTALD correlation uses it together with the '
                                   'ω<sub>SRK</sub> acentric factor.'),
                                  ('Capacidad calorífica de gas ideal, polinomio cúbico en T con '
                                   'los coeficientes de Reid, Prausnitz y Sherwood (1977) (véase '
                                   '«Contribución de gas ideal»).',
                                   'Ideal-gas heat capacity, cubic polynomial in T with the Reid, '
                                   'Prausnitz, and Sherwood (1977) coefficients (see “Ideal-gas '
                                   'contribution”).')]),
                                ('h3', 'Agua', 'Water'),
                                ('p',
                                 'Con las ecuaciones de HYSYS, el agua toma T<sub>c</sub> = '
                                 '1165.14 °R (647.30 K), P<sub>c</sub> = 3208.23 psia, ω = 0.344 '
                                 '(igual para PR y SRK), M = 18.0151, V<sub>c</sub> = 55.9 '
                                 'cm³/mol, V* igual a su volumen crítico (0.8954 ft³/lbmol) y el '
                                 'polinomio de C<sub>p</sub><sup>ig</sup> de Reid, Prausnitz y '
                                 'Sherwood.',
                                 'With the HYSYS equations, water uses T<sub>c</sub> = 1165.14 °R '
                                 '(647.30 K), P<sub>c</sub> = 3208.23 psia, ω = 0.344 (same for PR '
                                 'and SRK), M = 18.0151, V<sub>c</sub> = 55.9 cm³/mol, V* equal to '
                                 'its critical volume (0.8954 ft³/lbmol), and the Reid, Prausnitz, '
                                 'and Sherwood C<sub>p</sub><sup>ig</sup> polynomial.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen Physical Property System: Physical Property '
                                 'Methods</em>, métodos HYSPR y HYSSRK. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen Physical Property System: Physical Property '
                                 'Methods</em>, HYSPR and HYSSRK methods. Aspen Technology, Inc.'),
                                ('p',
                                 'Reid, R.C., Prausnitz, J.M. y Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3.ª ed. McGraw-Hill.',
                                 'Reid, R.C., Prausnitz, J.M. and Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3rd ed. McGraw-Hill.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.')]},
                   {'titulo': ('Parámetros de componente de PVTsim', 'PVTsim component parameters'),
                    'bloques': [('p',
                                 'El juego de parámetros de PVTsim corresponde a la base de datos '
                                 'de componentes de PVTsim (valores de Reid, Prausnitz y '
                                 'Sherwood), con toda la precisión almacenada. Se emplea en las '
                                 'ecuaciones de estado PR (PVTsim) y SRK (PVTsim).',
                                 'The PVTsim parameter set corresponds to the PVTsim component '
                                 'database (Reid, Prausnitz, and Sherwood values), with full '
                                 'stored precision. It is used by the PR (PVTsim) and SRK (PVTsim) '
                                 'equations of state.'),
                                ('ul',
                                 [('T<sub>c</sub>: almacenada en K y convertida a °R con el factor '
                                   '1.8.',
                                   'T<sub>c</sub>: stored in K and converted to °R with the factor '
                                   '1.8.'),
                                  ('P<sub>c</sub>: almacenada en atm y convertida a psia con '
                                   '14.69594878 psia/atm; en la ecuación de estado se reescala a '
                                   'la convención de 14.696 psia/atm (véase «Convención de '
                                   'unidades de PVTsim»).',
                                   'P<sub>c</sub>: stored in atm and converted to psia with '
                                   '14.69594878 psia/atm; within the equation of state it is '
                                   'rescaled to the 14.696 psia/atm convention (see “PVTsim unit '
                                   'convention”).'),
                                  ('Factor acéntrico único ω para PR y SRK: PVTsim no separa el '
                                   'factor acéntrico por ecuación.',
                                   'A single acentric factor ω for PR and SRK: PVTsim does not '
                                   'separate the acentric factor by equation.'),
                                  ('Peso molecular M propio de la base de PVTsim (por ejemplo, '
                                   '16.042879 para el metano).',
                                   'Molecular weight M from the PVTsim database (for example, '
                                   '16.042879 for methane).'),
                                  ('Volumen crítico almacenado en forma reducida V<sub>c</sub>/R '
                                   '(K/atm) y convertido a cm³/mol con R = 82.05736 '
                                   'cm³·atm/(mol·K).',
                                   'Critical volume stored in reduced form V<sub>c</sub>/R (K/atm) '
                                   'and converted to cm³/mol with R = 82.05736 cm³·atm/(mol·K).'),
                                  ("Traslado de volumen de Peneloux c', distinto para PR y para "
                                   "SRK, almacenado como c'/R (K/atm), para los catorce "
                                   'componentes (véase «Corrección de volumen de Peneloux»).',
                                   "Peneloux volume shift c', different for PR and SRK, stored as "
                                   "c'/R (K/atm), for all fourteen components (see “Peneloux "
                                   'volume correction”).'),
                                  ('Coeficientes de C<sub>p</sub><sup>ig</sup> de gas ideal de la '
                                   'base de PVTsim, almacenados divididos por R y multiplicados '
                                   'por R = 8.3147295 J/(mol·K) al usarse.',
                                   'Ideal-gas C<sub>p</sub><sup>ig</sup> coefficients from the '
                                   'PVTsim database, stored divided by R and multiplied by R = '
                                   '8.3147295 J/(mol·K) when used.'),
                                  ('Constantes de Langmuir de hidratos (parámetros A y B por '
                                   'cavidad y estructura) para los componentes formadores de '
                                   'hidrato.',
                                   'Hydrate Langmuir constants (A and B parameters per cavity and '
                                   'structure) for the hydrate-forming components.')]),
                                ('h3', 'Agua', 'Water'),
                                ('p',
                                 'Con las ecuaciones de PVTsim, el agua toma T<sub>c</sub> = '
                                 '647.30 K (1165.14 °R), P<sub>c</sub> = 218 atm (3203.72 psia), ω '
                                 "= 0.344, M = 18.015341, V<sub>c</sub> = 56.0 cm³/mol y c'/R = "
                                 '0.037110969 K/atm (PR) y 0.068562075 K/atm (SRK).',
                                 'With the PVTsim equations, water uses T<sub>c</sub> = 647.30 K '
                                 '(1165.14 °R), P<sub>c</sub> = 218 atm (3203.72 psia), ω = 0.344, '
                                 "M = 18.015341, V<sub>c</sub> = 56.0 cm³/mol, and c'/R = "
                                 '0.037110969 K/atm (PR) and 0.068562075 K/atm (SRK).'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.',
                                 'Péneloux, A., Rauzy, E. and Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.'),
                                ('p',
                                 'Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.',
                                 'Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.')]},
                   {'titulo': ('Hoja de componente', 'Component property sheet'),
                    'bloques': [('p',
                                 'La hoja de componente es una ventana de solo lectura que reúne, '
                                 'para el componente seleccionado en el árbol de componentes, '
                                 'todos los parámetros que utiliza ThermoPhase. Los valores se '
                                 'almacenan en unidades de campo y se presentan convertidos al '
                                 'sistema de unidades activo.',
                                 'The component sheet is a read-only window that gathers, for the '
                                 'component selected in the component tree, all the parameters '
                                 'that ThermoPhase uses. Values are stored in field units and are '
                                 'displayed converted to the active unit system.'),
                                ('ul',
                                 [('Propiedades generales: nombre, símbolo, temperatura normal de '
                                   'ebullición y estructuras de hidrato en las que el componente '
                                   'participa como huésped (sI, sII, sH); el agua figura como '
                                   'anfitrión de la red del hidrato.',
                                   'General properties: name, symbol, normal boiling point, and '
                                   'hydrate structures in which the component acts as a guest (sI, '
                                   'sII, sH); water is shown as the host of the hydrate lattice.'),
                                  ('Parámetros de HYSYS: T<sub>c</sub>, P<sub>c</sub>, factor '
                                   'acéntrico PR, factor acéntrico SRK, peso molecular, volumen '
                                   'crítico para la viscosidad LBC, volumen característico V* de '
                                   'COSTALD y C<sub>p</sub><sup>ig</sup> de gas ideal a 60 °F.',
                                   'HYSYS parameters: T<sub>c</sub>, P<sub>c</sub>, PR acentric '
                                   'factor, SRK acentric factor, molecular weight, critical volume '
                                   'for LBC viscosity, COSTALD characteristic volume V*, and '
                                   'ideal-gas C<sub>p</sub><sup>ig</sup> at 60 °F.'),
                                  ('Parámetros de PVTsim: T<sub>c</sub>, P<sub>c</sub>, factor '
                                   'acéntrico, peso molecular, volumen crítico para la viscosidad '
                                   'LBC, traslado de volumen de Peneloux para PR y para SRK, y '
                                   'C<sub>p</sub><sup>ig</sup> de gas ideal a 60 °F.',
                                   'PVTsim parameters: T<sub>c</sub>, P<sub>c</sub>, acentric '
                                   'factor, molecular weight, critical volume for LBC viscosity, '
                                   'Peneloux volume shift for PR and for SRK, and ideal-gas '
                                   'C<sub>p</sub><sup>ig</sup> at 60 °F.')]),
                                ('p',
                                 'La temperatura crítica y la temperatura de ebullición se '
                                 'muestran como temperatura absoluta (°R en FIELD, K en SI y '
                                 'Métrico); la presión crítica en la unidad de presión del '
                                 'sistema; el volumen crítico en cm³/mol en todos los sistemas; V* '
                                 "y c' en la unidad de volumen molar; y C<sub>p</sub><sup>ig</sup> "
                                 'en la unidad de entropía molar.',
                                 'Critical temperature and boiling point are shown as absolute '
                                 'temperature (°R in FIELD, K in SI and Metric); critical pressure '
                                 'in the pressure unit of the system; critical volume in cm³/mol '
                                 "in all systems; V* and c' in the molar-volume unit; and "
                                 'C<sub>p</sub><sup>ig</sup> in the molar-entropy unit.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Sistemas de unidades y constantes', 'Unit systems and constants'),
                    'bloques': [('p',
                                 'El motor de cálculo trabaja siempre en unidades internas de '
                                 'campo: temperatura en °R, presión en psia, volumen molar en '
                                 'ft³/lbmol, densidad en lb/ft³, entalpía en BTU/lbmol y entropía '
                                 'en BTU/(lbmol·°R). La interfaz convierte los datos al ingresar y '
                                 'los resultados al mostrarlos, según el sistema de unidades '
                                 'seleccionado.',
                                 'The calculation engine always works in internal field units: '
                                 'temperature in °R, pressure in psia, molar volume in ft³/lbmol, '
                                 'density in lb/ft³, enthalpy in BTU/lbmol, and entropy in '
                                 'BTU/(lbmol·°R). The interface converts input data and displayed '
                                 'results according to the selected unit system.'),
                                ('ul',
                                 [('FIELD: psia, °F (°R absoluta), lb/ft³, BTU/lbmol, '
                                   'BTU/(lbmol·°F), ft³/lbmol.',
                                   'FIELD: psia, °F (°R absolute), lb/ft³, BTU/lbmol, '
                                   'BTU/(lbmol·°F), ft³/lbmol.'),
                                  ('SI: kPa, °C (K absoluta), kg/m³, kJ/kgmol, kJ/(kgmol·°C), '
                                   'm³/kgmol.',
                                   'SI: kPa, °C (K absolute), kg/m³, kJ/kgmol, kJ/(kgmol·°C), '
                                   'm³/kgmol.'),
                                  ('Métrico: bar, °C (K absoluta), kg/m³, kcal/kgmol, '
                                   'kcal/(kgmol·°C), m³/kgmol.',
                                   'Metric: bar, °C (K absolute), kg/m³, kcal/kgmol, '
                                   'kcal/(kgmol·°C), m³/kgmol.'),
                                  ('La viscosidad se expresa en cP en los tres sistemas.',
                                   'Viscosity is expressed in cP in all three systems.')]),
                                ('p',
                                 'Los factores de conversión desde las unidades internas son: 1 '
                                 'psia = 6.8947573 kPa = 0.068947573 bar; 1 lb/ft³ = 16.018463 '
                                 'kg/m³; 1 BTU/lbmol = 2.326 kJ/kgmol = 0.5555556 kcal/kgmol; 1 '
                                 'BTU/(lbmol·°F) = 4.1868 kJ/(kgmol·°C) = 1 kcal/(kgmol·°C); 1 '
                                 'ft³/lbmol = 0.062427961 m³/kgmol. Las temperaturas se convierten '
                                 'con T(°R) = T(°F) + 459.67, T(°C) = [T(°F) − 32]/1.8 y T(K) = '
                                 'T(°R)/1.8.',
                                 'The conversion factors from internal units are: 1 psia = '
                                 '6.8947573 kPa = 0.068947573 bar; 1 lb/ft³ = 16.018463 kg/m³; 1 '
                                 'BTU/lbmol = 2.326 kJ/kgmol = 0.5555556 kcal/kgmol; 1 '
                                 'BTU/(lbmol·°F) = 4.1868 kJ/(kgmol·°C) = 1 kcal/(kgmol·°C); 1 '
                                 'ft³/lbmol = 0.062427961 m³/kgmol. Temperatures are converted '
                                 'with T(°R) = T(°F) + 459.67, T(°C) = [T(°F) − 32]/1.8, and T(K) '
                                 '= T(°R)/1.8.'),
                                ('h3', 'Constantes', 'Constants'),
                                ('ul',
                                 [('Constante de los gases en la ecuación de estado: R = 10.7316 '
                                   'psia·ft³/(lbmol·°R).',
                                   'Gas constant in the equation of state: R = 10.7316 '
                                   'psia·ft³/(lbmol·°R).'),
                                  ('Constante de los gases en las propiedades térmicas: R = '
                                   '8.3147295 J/(mol·K), equivalente a 1.98594 BTU/(lbmol·°R) y '
                                   'coherente con R = 0.08206 L·atm/(mol·K) de PVTsim.',
                                   'Gas constant in the thermal properties: R = 8.3147295 '
                                   'J/(mol·K), equivalent to 1.98594 BTU/(lbmol·°R) and consistent '
                                   'with the PVTsim value R = 0.08206 L·atm/(mol·K).'),
                                  ('Condiciones estándar: 60 °F (519.67 °R) y 14.696 psia; el '
                                   'volumen molar del gas ideal en esas condiciones es R·T/P = '
                                   '379.48 ft³/lbmol.',
                                   'Standard conditions: 60 °F (519.67 °R) and 14.696 psia; the '
                                   'ideal-gas molar volume at these conditions is R·T/P = 379.48 '
                                   'ft³/lbmol.'),
                                  ('Peso molecular del aire para la gravedad específica del gas: '
                                   '28.9625.',
                                   'Molecular weight of air for gas specific gravity: 28.9625.')]),
                                ('eq',
                                 'V_{m}^{\\,\\mathrm{std}} = '
                                 '\\frac{R\\,T_{\\mathrm{std}}}{P_{\\mathrm{std}}} = '
                                 '\\frac{10.7316 \\times 519.67}{14.696} = 379.48\\ '
                                 '\\mathrm{ft^{3}/lbmol}'),
                                ('p',
                                 'donde V<sub>m</sub><sup>std</sup> es el volumen molar del gas '
                                 'ideal en condiciones estándar, T<sub>std</sub> = 519.67 °R y '
                                 'P<sub>std</sub> = 14.696 psia. Este valor es la base del poder '
                                 'calorífico volumétrico, del GPM y del contenido de agua por '
                                 'millón de pies cúbicos estándar.',
                                 'where V<sub>m</sub><sup>std</sup> is the ideal-gas molar volume '
                                 'at standard conditions, T<sub>std</sub> = 519.67 °R, and '
                                 'P<sub>std</sub> = 14.696 psia. This value is the basis of the '
                                 'volumetric heating value, the GPM, and the water content per '
                                 'million standard cubic feet.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.')]},
                   {'titulo': ('Convención de unidades de PVTsim', 'PVTsim unit convention'),
                    'bloques': [('p',
                                 'PVTsim trabaja internamente en atmósferas y en kelvin. Convierte '
                                 'la presión de entrada con 1 atm = 14.696 psia, mientras que sus '
                                 'presiones críticas están almacenadas en atm. Para que el '
                                 'cociente P/P<sub>c</sub> de ThermoPhase coincida con el de '
                                 'PVTsim, las presiones críticas en psia (obtenidas con '
                                 '14.69594878 psia/atm) se reescalan en las ecuaciones de estado '
                                 'de PVTsim a una presión crítica efectiva:',
                                 'PVTsim works internally in atmospheres and kelvin. It converts '
                                 'the input pressure with 1 atm = 14.696 psia, whereas its '
                                 'critical pressures are stored in atm. For the P/P<sub>c</sub> '
                                 'ratio in ThermoPhase to match that of PVTsim, the critical '
                                 'pressures in psia (obtained with 14.69594878 psia/atm) are '
                                 'rescaled in the PVTsim equations of state to an effective '
                                 'critical pressure:'),
                                ('eq',
                                 'P_{c}^{\\,\\mathrm{ef}} = P_{c}\\;\\frac{14.696}{14.69594878}'),
                                ('p',
                                 'donde P<sub>c</sub> es la presión crítica en psia y '
                                 'P<sub>c</sub><sup>ef</sup> la presión crítica efectiva en psia '
                                 'que entra en los parámetros a y b.',
                                 'where P<sub>c</sub> is the critical pressure in psia and '
                                 'P<sub>c</sub><sup>ef</sup> is the effective critical pressure in '
                                 'psia that enters the a and b parameters.'),
                                ('p',
                                 'PVTsim obtiene el volumen molar de una fase como V = Z·R·T/P con '
                                 'R = 82.06 cm³·atm/(mol·K), T en K y la presión convertida a atm '
                                 'con 14.696 psia/atm, y la densidad como ρ = M/V. Frente a la '
                                 'expresión en unidades de campo con R = 10.7316, esta convención '
                                 'equivale a un factor multiplicativo constante sobre la densidad '
                                 'de la ecuación de estado:',
                                 'PVTsim obtains the molar volume of a phase as V = Z·R·T/P with R '
                                 '= 82.06 cm³·atm/(mol·K), T in K, and pressure converted to atm '
                                 'with 14.696 psia/atm, and the density as ρ = M/V. Compared with '
                                 'the field-unit expression with R = 10.7316, this convention is '
                                 'equivalent to a constant multiplicative factor on the '
                                 'equation-of-state density:'),
                                ('eq', '\\rho = \\frac{P\\,M}{Z\\,R\\,T}\\;f_{\\rho}'),
                                ('eq',
                                 'f_{\\rho} = \\frac{10.7316 \\times 1.8 \\times 62.42796}{82.06 '
                                 '\\times 14.696} = 1 - 3.35\\times 10^{-5}'),
                                ('p',
                                 'donde ρ es la densidad másica (lb/ft³), P la presión (psia), M '
                                 'el peso molecular de la fase, Z el factor de compresibilidad, R '
                                 '= 10.7316 psia·ft³/(lbmol·°R), T la temperatura (°R), 62.42796 '
                                 'el factor de g/cm³ a lb/ft³ y f<sub>ρ</sub> el factor de '
                                 'convención. ThermoPhase aplica f<sub>ρ</sub> a las densidades de '
                                 'todas las fases con las ecuaciones de PVTsim; con las de HYSYS '
                                 'f<sub>ρ</sub> = 1.',
                                 'where ρ is the mass density (lb/ft³), P is the pressure (psia), '
                                 'M is the phase molecular weight, Z is the compressibility '
                                 'factor, R = 10.7316 psia·ft³/(lbmol·°R), T is the temperature '
                                 '(°R), 62.42796 is the factor from g/cm³ to lb/ft³, and '
                                 'f<sub>ρ</sub> is the convention factor. ThermoPhase applies '
                                 'f<sub>ρ</sub> to the densities of all phases with the PVTsim '
                                 'equations; with the HYSYS equations f<sub>ρ</sub> = 1.'),
                                ('p',
                                 'La misma convención se aplica al traslado de volumen de '
                                 'Peneloux, cuyo término P·c/(R·T) se evalúa con 14.696 psia/atm, '
                                 'y a la densidad reducida de la viscosidad de Lohrenz-Bray-Clark, '
                                 'que se evalúa con la presión en atm y el volumen crítico '
                                 'reducido V<sub>c</sub>/R, de modo que la constante de los gases '
                                 'se cancela.',
                                 'The same convention is applied to the Peneloux volume shift, '
                                 'whose term P·c/(R·T) is evaluated with 14.696 psia/atm, and to '
                                 'the reduced density of the Lohrenz-Bray-Clark viscosity, which '
                                 'is evaluated with pressure in atm and the reduced critical '
                                 'volume V<sub>c</sub>/R, so that the gas constant cancels out.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]}]},
 {'titulo': ('Ecuaciones de estado cúbicas', 'Cubic equations of state'),
  'subsecciones': [{'titulo': ('Forma general de las ecuaciones cúbicas',
                               'General form of the cubic equations'),
                    'bloques': [('p',
                                 'Una ecuación de estado relaciona la presión, el volumen molar y '
                                 'la temperatura de un fluido y, a partir de ella, se derivan '
                                 'todas sus propiedades termodinámicas residuales. Las ecuaciones '
                                 'cúbicas de Peng-Robinson (PR) y Soave-Redlich-Kwong (SRK) '
                                 'corrigen el gas ideal con un término repulsivo, que representa '
                                 'el volumen propio de las moléculas mediante el covolumen b, y un '
                                 'término atractivo, que representa las fuerzas intermoleculares '
                                 'mediante el parámetro a(T).',
                                 'An equation of state relates the pressure, molar volume, and '
                                 'temperature of a fluid, and all of its residual thermodynamic '
                                 'properties are derived from it. The Peng-Robinson (PR) and '
                                 'Soave-Redlich-Kwong (SRK) cubic equations correct the ideal gas '
                                 'with a repulsive term, which represents the molecular volume '
                                 'through the covolume b, and an attractive term, which represents '
                                 'intermolecular forces through the parameter a(T).'),
                                ('p',
                                 'Ambas ecuaciones admiten una forma general común de dos '
                                 'parámetros:',
                                 'Both equations share a common two-parameter general form:'),
                                ('eq',
                                 'P = \\frac{R\\,T}{V - b} - \\frac{a(T)}{\\left(V + \\delta_1 '
                                 'b\\right)\\left(V + \\delta_2 b\\right)}'),
                                ('p',
                                 'donde P es la presión (psia), T la temperatura absoluta (°R), V '
                                 'el volumen molar (ft³/lbmol), R = 10.7316 psia·ft³/(lbmol·°R), b '
                                 'el covolumen (ft³/lbmol), a(T) el parámetro atractivo '
                                 '(psia·ft⁶/lbmol²) y δ<sub>1</sub>, δ<sub>2</sub> constantes que '
                                 'definen la ecuación.',
                                 'where P is the pressure (psia), T is the absolute temperature '
                                 '(°R), V is the molar volume (ft³/lbmol), R = 10.7316 '
                                 'psia·ft³/(lbmol·°R), b is the covolume (ft³/lbmol), a(T) is the '
                                 'attractive parameter (psia·ft⁶/lbmol²), and δ<sub>1</sub>, '
                                 'δ<sub>2</sub> are constants that define the equation.'),
                                ('h3', 'Peng-Robinson', 'Peng-Robinson'),
                                ('eq',
                                 'P = \\frac{R\\,T}{V - b} - \\frac{a(T)}{V\\,(V + b) + b\\,(V - '
                                 'b)}'),
                                ('p',
                                 'donde los símbolos son los de la forma general, con '
                                 'δ<sub>1</sub> = 1 + √2 y δ<sub>2</sub> = 1 − √2. La forma del '
                                 'denominador atractivo mejora la predicción de la densidad de la '
                                 'fase líquida respecto de las ecuaciones anteriores.',
                                 'where the symbols are those of the general form, with '
                                 'δ<sub>1</sub> = 1 + √2 and δ<sub>2</sub> = 1 − √2. The form of '
                                 'the attractive denominator improves the prediction of '
                                 'liquid-phase density with respect to earlier equations.'),
                                ('h3', 'Soave-Redlich-Kwong', 'Soave-Redlich-Kwong'),
                                ('eq', 'P = \\frac{R\\,T}{V - b} - \\frac{a(T)}{V\\,(V + b)}'),
                                ('p',
                                 'donde los símbolos son los de la forma general, con '
                                 'δ<sub>1</sub> = 1 y δ<sub>2</sub> = 0. SRK conserva la forma de '
                                 'Redlich-Kwong e introduce la dependencia de la atracción con la '
                                 'temperatura a través del factor acéntrico.',
                                 'where the symbols are those of the general form, with '
                                 'δ<sub>1</sub> = 1 and δ<sub>2</sub> = 0. SRK retains the '
                                 'Redlich-Kwong form and introduces the temperature dependence of '
                                 'the attraction through the acentric factor.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.'),
                                ('p',
                                 'Redlich, O. y Kwong, J.N.S. (1949). On the thermodynamics of '
                                 'solutions. V. An equation of state. Fugacities of gaseous '
                                 'solutions. <em>Chemical Reviews</em>, 44(1), 233–244.',
                                 'Redlich, O. and Kwong, J.N.S. (1949). On the thermodynamics of '
                                 'solutions. V. An equation of state. Fugacities of gaseous '
                                 'solutions. <em>Chemical Reviews</em>, 44(1), 233–244.')]},
                   {'titulo': ('Parámetros a y b del componente puro',
                               'Pure-component parameters a and b'),
                    'bloques': [('p',
                                 'Los parámetros de cada componente se obtienen imponiendo a la '
                                 'ecuación las condiciones del punto crítico: la isoterma crítica '
                                 'presenta un punto de inflexión con tangente horizontal en el '
                                 'plano presión-volumen.',
                                 'The parameters of each component are obtained by imposing the '
                                 'critical-point conditions on the equation: the critical isotherm '
                                 'has an inflection point with a horizontal tangent in the '
                                 'pressure-volume plane.'),
                                ('eq',
                                 '\\left(\\frac{\\partial P}{\\partial V}\\right)_{T_c} = 0 '
                                 '\\qquad \\left(\\frac{\\partial^{2} P}{\\partial '
                                 'V^{2}}\\right)_{T_c} = 0'),
                                ('p',
                                 'donde las derivadas se evalúan a la temperatura crítica '
                                 'T<sub>c</sub> y al volumen crítico de la ecuación. Estas dos '
                                 'condiciones fijan las constantes adimensionales Ω<sub>a</sub> y '
                                 'Ω<sub>b</sub> y ligan los parámetros a las propiedades críticas:',
                                 'where the derivatives are evaluated at the critical temperature '
                                 'T<sub>c</sub> and at the critical volume of the equation. These '
                                 'two conditions fix the dimensionless constants Ω<sub>a</sub> and '
                                 'Ω<sub>b</sub> and relate the parameters to the critical '
                                 'properties:'),
                                ('eq',
                                 'a_{c,i} = \\Omega_a\\,\\frac{R^{2}\\,T_{c,i}^{\\,2}}{P_{c,i}} '
                                 '\\qquad b_i = \\Omega_b\\,\\frac{R\\,T_{c,i}}{P_{c,i}}'),
                                ('eq', 'a_i(T) = a_{c,i}\\;\\alpha_i(T)'),
                                ('p',
                                 'donde a<sub>c,i</sub> es el parámetro atractivo en el punto '
                                 'crítico, b<sub>i</sub> el covolumen, T<sub>c,i</sub> (°R) y '
                                 'P<sub>c,i</sub> (psia) las propiedades críticas del componente '
                                 'i, y α<sub>i</sub>(T) la función adimensional de temperatura, '
                                 'que vale 1 en T = T<sub>c,i</sub>. El covolumen es independiente '
                                 'de la temperatura.',
                                 'where a<sub>c,i</sub> is the attractive parameter at the '
                                 'critical point, b<sub>i</sub> is the covolume, T<sub>c,i</sub> '
                                 '(°R) and P<sub>c,i</sub> (psia) are the critical properties of '
                                 'component i, and α<sub>i</sub>(T) is the dimensionless '
                                 'temperature function, equal to 1 at T = T<sub>c,i</sub>. The '
                                 'covolume is independent of temperature.'),
                                ('h3', 'Constantes de SRK', 'SRK constants'),
                                ('p',
                                 'Para SRK las condiciones críticas conducen a expresiones '
                                 'cerradas:',
                                 'For SRK the critical conditions lead to closed-form '
                                 'expressions:'),
                                ('eq',
                                 '\\Omega_a = \\frac{1}{9\\left(2^{1/3} - 1\\right)} = '
                                 '0.42748023354 \\qquad \\Omega_b = \\frac{2^{1/3} - 1}{3} = '
                                 '0.08664034996'),
                                ('p',
                                 'donde 2<sup>1/3</sup> es la raíz cúbica de 2. ThermoPhase emplea '
                                 'estos valores exactos en las dos ecuaciones SRK (HYSYS y '
                                 'PVTsim); el manual de HYSYS publica los mismos valores '
                                 'truncados, 0.42748 y 0.08664.',
                                 'where 2<sup>1/3</sup> is the cube root of 2. ThermoPhase uses '
                                 'these exact values in both SRK equations (HYSYS and PVTsim); the '
                                 'HYSYS manual publishes the same values truncated to 0.42748 and '
                                 '0.08664.'),
                                ('h3', 'Constantes de Peng-Robinson', 'Peng-Robinson constants'),
                                ('p',
                                 'Para Peng-Robinson las condiciones críticas conducen a '
                                 'Ω<sub>b</sub> = 0.0777960739 y Ω<sub>a</sub> = 0.4572355289. '
                                 'ThermoPhase usa:',
                                 'For Peng-Robinson the critical conditions lead to Ω<sub>b</sub> '
                                 '= 0.0777960739 and Ω<sub>a</sub> = 0.4572355289. ThermoPhase '
                                 'uses:'),
                                ('ul',
                                 [('PR (HYSYS): Ω<sub>a</sub> = 0.45724 y Ω<sub>b</sub> = 0.07780, '
                                   'los valores redondeados publicados por Peng y Robinson.',
                                   'PR (HYSYS): Ω<sub>a</sub> = 0.45724 and Ω<sub>b</sub> = '
                                   '0.07780, the rounded values published by Peng and Robinson.'),
                                  ('PR (PVTsim): Ω<sub>a</sub> = 0.4572355289 (valor exacto) y '
                                   'Ω<sub>b</sub> = 0.07780 (valor redondeado), combinación que '
                                   'corresponde a los cálculos de PVTsim.',
                                   'PR (PVTsim): Ω<sub>a</sub> = 0.4572355289 (exact value) and '
                                   'Ω<sub>b</sub> = 0.07780 (rounded value), the combination that '
                                   'corresponds to the PVTsim calculations.')]),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los parámetros a<sub>c,i</sub> y b<sub>i</sub> de las cuatro '
                                 'ecuaciones se calculan una sola vez a partir de la base de datos '
                                 'de la ecuación correspondiente; con las ecuaciones de PVTsim se '
                                 'usa la presión crítica efectiva P<sub>c</sub><sup>ef</sup>. En '
                                 'cada temperatura se evalúa el vector a<sub>i</sub>(T) de todos '
                                 'los componentes, que se reutiliza durante todo el cálculo a esa '
                                 'temperatura.',
                                 'The a<sub>c,i</sub> and b<sub>i</sub> parameters of the four '
                                 'equations are computed once from the database of the '
                                 'corresponding equation; with the PVTsim equations the effective '
                                 'critical pressure P<sub>c</sub><sup>ef</sup> is used. At each '
                                 'temperature, the vector a<sub>i</sub>(T) of all components is '
                                 'evaluated and reused throughout the calculation at that '
                                 'temperature.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.')]},
                   {'titulo': ('Función α(T) y factor acéntrico',
                               'The α(T) function and the acentric factor'),
                    'bloques': [('p',
                                 'La función α(T) introduce la dependencia del parámetro atractivo '
                                 'con la temperatura. Crece al disminuir la temperatura y vale 1 '
                                 'en la temperatura crítica, de modo que la ecuación reproduce la '
                                 'presión de vapor del componente puro.',
                                 'The α(T) function introduces the temperature dependence of the '
                                 'attractive parameter. It increases as temperature decreases and '
                                 'equals 1 at the critical temperature, so that the equation '
                                 'reproduces the vapor pressure of the pure component.'),
                                ('p',
                                 'El factor acéntrico de Pitzer caracteriza la desviación de la '
                                 'presión de vapor respecto de la de un fluido simple de moléculas '
                                 'esféricas:',
                                 "Pitzer's acentric factor characterizes the deviation of the "
                                 'vapor pressure from that of a simple fluid of spherical '
                                 'molecules:'),
                                ('eq',
                                 '\\omega = '
                                 '-\\log_{10}\\left(\\frac{P^{\\mathrm{sat}}}{P_c}\\right)_{T/T_c '
                                 '= 0.7} - 1'),
                                ('p',
                                 'donde ω es el factor acéntrico, P<sup>sat</sup> la presión de '
                                 'vapor evaluada a la temperatura reducida T/T<sub>c</sub> = 0.7 y '
                                 'P<sub>c</sub> la presión crítica.',
                                 'where ω is the acentric factor, P<sup>sat</sup> is the vapor '
                                 'pressure evaluated at the reduced temperature T/T<sub>c</sub> = '
                                 '0.7, and P<sub>c</sub> is the critical pressure.'),
                                ('h3', 'Función α clásica', 'Classical α function'),
                                ('p',
                                 'Las cuatro ecuaciones de ThermoPhase emplean la función α de '
                                 'Soave:',
                                 'All four ThermoPhase equations use the Soave α function:'),
                                ('eq',
                                 '\\alpha_i(T) = \\left[1 + m_i\\left(1 - '
                                 '\\sqrt{T/T_{c,i}}\\right)\\right]^{2}'),
                                ('p',
                                 'donde m<sub>i</sub> es un coeficiente que depende del factor '
                                 'acéntrico del componente i y T/T<sub>c,i</sub> la temperatura '
                                 'reducida. La correlación de m depende de la ecuación:',
                                 'where m<sub>i</sub> is a coefficient that depends on the '
                                 'acentric factor of component i and T/T<sub>c,i</sub> is the '
                                 'reduced temperature. The m correlation depends on the equation:'),
                                ('eq',
                                 'm_{\\mathrm{PR}} = 0.37464 + 1.54226\\,\\omega - '
                                 '0.26992\\,\\omega^{2}'),
                                ('eq',
                                 'm_{\\mathrm{SRK}} = 0.480 + 1.574\\,\\omega - '
                                 '0.176\\,\\omega^{2}'),
                                ('p',
                                 'donde m<sub>PR</sub> es la correlación original de Peng y '
                                 'Robinson (1976) y m<sub>SRK</sub> la correlación original de '
                                 'Soave (1972). La misma expresión se aplica a todo el intervalo '
                                 'de temperatura, incluida la región T &gt; T<sub>c,i</sub>.',
                                 'where m<sub>PR</sub> is the original Peng and Robinson (1976) '
                                 'correlation and m<sub>SRK</sub> is the original Soave (1972) '
                                 'correlation. The same expression is applied over the entire '
                                 'temperature range, including the region T &gt; T<sub>c,i</sub>.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('ul',
                                 [('PR (HYSYS) usa ω<sub>PR</sub> de HYSYS; SRK (HYSYS) usa '
                                   'ω<sub>SRK</sub> de HYSYS, un juego de factores acéntricos '
                                   'distinto.',
                                   'PR (HYSYS) uses the HYSYS ω<sub>PR</sub>; SRK (HYSYS) uses the '
                                   'HYSYS ω<sub>SRK</sub>, a different set of acentric factors.'),
                                  ('PR (PVTsim) y SRK (PVTsim) usan el factor acéntrico único de '
                                   'PVTsim, cada una con su propia correlación de m.',
                                   'PR (PVTsim) and SRK (PVTsim) use the single PVTsim acentric '
                                   'factor, each with its own m correlation.'),
                                  ('El agua usa la misma función α clásica con ω = 0.344 en las '
                                   'cuatro ecuaciones. Los coeficientes de Mathias-Copeman de la '
                                   'base de datos de PVTsim no se emplean: la solubilidad mutua '
                                   'agua-hidrocarburo se representa con la función α clásica '
                                   'combinada con la regla de Huron-Vidal y los parámetros de '
                                   'Pedersen y colaboradores (2001).',
                                   'Water uses the same classical α function with ω = 0.344 in all '
                                   'four equations. The Mathias-Copeman coefficients of the PVTsim '
                                   'database are not used: the water-hydrocarbon mutual solubility '
                                   'is represented with the classical α function combined with the '
                                   'Huron-Vidal rule and the parameters of Pedersen et al. '
                                   '(2001).')]),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Pitzer, K.S., Lippmann, D.Z., Curl, R.F., Huggins, C.M. y '
                                 'Petersen, D.E. (1955). The volumetric and thermodynamic '
                                 'properties of fluids. II. Compressibility factor, vapor pressure '
                                 'and entropy of vaporization. <em>Journal of the American '
                                 'Chemical Society</em>, 77(13), 3433–3440.',
                                 'Pitzer, K.S., Lippmann, D.Z., Curl, R.F., Huggins, C.M. and '
                                 'Petersen, D.E. (1955). The volumetric and thermodynamic '
                                 'properties of fluids. II. Compressibility factor, vapor pressure '
                                 'and entropy of vaporization. <em>Journal of the American '
                                 'Chemical Society</em>, 77(13), 3433–3440.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.'),
                                ('p',
                                 'Pedersen, K.S., Milter, J. y Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.',
                                 'Pedersen, K.S., Milter, J. and Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.'),
                                ('p',
                                 'Mathias, P.M. y Copeman, T.W. (1983). Extension of the '
                                 'Peng-Robinson equation of state to complex mixtures: evaluation '
                                 'of the various forms of the local composition concept. <em>Fluid '
                                 'Phase Equilibria</em>, 13, 91–108.',
                                 'Mathias, P.M. and Copeman, T.W. (1983). Extension of the '
                                 'Peng-Robinson equation of state to complex mixtures: evaluation '
                                 'of the various forms of the local composition concept. <em>Fluid '
                                 'Phase Equilibria</em>, 13, 91–108.')]},
                   {'titulo': ('Las cuatro variantes PR y SRK', 'The four PR and SRK variants'),
                    'bloques': [('p',
                                 'ThermoPhase ofrece cuatro ecuaciones de estado seleccionables, '
                                 'que resultan de combinar las dos formas cúbicas con los juegos '
                                 'de parámetros de HYSYS y de PVTsim. Dentro de cada familia la '
                                 'forma de la ecuación, la correlación de m y el coeficiente de '
                                 'fugacidad son idénticos; las variantes difieren en los datos de '
                                 'entrada y en las constantes Ω.',
                                 'ThermoPhase offers four selectable equations of state, obtained '
                                 'by combining the two cubic forms with the HYSYS and PVTsim '
                                 'parameter sets. Within each family the form of the equation, the '
                                 'm correlation, and the fugacity coefficient are identical; the '
                                 'variants differ in the input data and in the Ω constants.'),
                                ('ul',
                                 [('Peng-Robinson (HYSYS): T<sub>c</sub>, P<sub>c</sub>, '
                                   'ω<sub>PR</sub> y M de HYSYS; Ω<sub>a</sub> = 0.45724, '
                                   'Ω<sub>b</sub> = 0.07780; matriz k<sub>ij</sub> de PR de HYSYS.',
                                   'Peng-Robinson (HYSYS): HYSYS T<sub>c</sub>, P<sub>c</sub>, '
                                   'ω<sub>PR</sub>, and M; Ω<sub>a</sub> = 0.45724, Ω<sub>b</sub> '
                                   '= 0.07780; HYSYS PR k<sub>ij</sub> matrix.'),
                                  ('SRK (HYSYS): las mismas T<sub>c</sub>, P<sub>c</sub> y M de '
                                   'HYSYS, con ω<sub>SRK</sub>; Ω<sub>a</sub> y Ω<sub>b</sub> '
                                   'exactos de SRK; matriz k<sub>ij</sub> de SRK de HYSYS.',
                                   'SRK (HYSYS): the same HYSYS T<sub>c</sub>, P<sub>c</sub>, and '
                                   'M, with ω<sub>SRK</sub>; exact SRK Ω<sub>a</sub> and '
                                   'Ω<sub>b</sub>; HYSYS SRK k<sub>ij</sub> matrix.'),
                                  ('Peng-Robinson (PVTsim): T<sub>c</sub>, '
                                   'P<sub>c</sub><sup>ef</sup>, ω y M de PVTsim; Ω<sub>a</sub> = '
                                   '0.4572355289, Ω<sub>b</sub> = 0.07780; matriz k<sub>ij</sub> '
                                   'de PR de PVTsim.',
                                   'Peng-Robinson (PVTsim): PVTsim T<sub>c</sub>, '
                                   'P<sub>c</sub><sup>ef</sup>, ω, and M; Ω<sub>a</sub> = '
                                   '0.4572355289, Ω<sub>b</sub> = 0.07780; PVTsim PR '
                                   'k<sub>ij</sub> matrix.'),
                                  ('SRK (PVTsim): T<sub>c</sub>, P<sub>c</sub><sup>ef</sup>, ω y M '
                                   'de PVTsim; Ω<sub>a</sub> y Ω<sub>b</sub> exactos de SRK; '
                                   'matriz k<sub>ij</sub> de SRK de PVTsim.',
                                   'SRK (PVTsim): PVTsim T<sub>c</sub>, '
                                   'P<sub>c</sub><sup>ef</sup>, ω, and M; exact SRK Ω<sub>a</sub> '
                                   'and Ω<sub>b</sub>; PVTsim SRK k<sub>ij</sub> matrix.')]),
                                ('p',
                                 'La ecuación seleccionada determina además otros métodos '
                                 'asociados. Con las ecuaciones de PVTsim la densidad incorpora el '
                                 'factor de convención f<sub>ρ</sub> (véase «Convención de '
                                 'unidades de PVTsim») y la identificación de la fase de una raíz '
                                 'única sigue el criterio de PVTsim, basado en el punto crítico de '
                                 'la mezcla; con las ecuaciones de HYSYS esa identificación sigue '
                                 'el criterio de HYSYS (véase el capítulo «Identificación de '
                                 'fases»). El peso molecular de las fases se calcula con los pesos '
                                 'moleculares de la base de datos de la ecuación activa.',
                                 'The selected equation also determines other associated methods. '
                                 'With the PVTsim equations the density includes the convention '
                                 'factor f<sub>ρ</sub> (see “PVTsim unit convention”), and the '
                                 'phase identification of a single root follows the PVTsim '
                                 'criterion, based on the mixture critical point; with the HYSYS '
                                 'equations that identification follows the HYSYS criterion (see '
                                 'the “Phase identification” chapter). The phase molecular weight '
                                 "is computed with the molecular weights of the active equation's "
                                 'database.'),
                                ('p',
                                 'Las diferencias de parámetros entre HYSYS y PVTsim son pequeñas '
                                 'en los componentes individuales, pero producen diferencias '
                                 'apreciables en la envolvente de fases, especialmente en la '
                                 'cercanía del punto crítico de la mezcla. Disponer de ambos '
                                 'juegos permite reproducir cada simulador de referencia con su '
                                 'propia base de datos.',
                                 'The parameter differences between HYSYS and PVTsim are small for '
                                 'individual components, but they produce noticeable differences '
                                 'in the phase envelope, especially near the mixture critical '
                                 'point. Having both sets available allows each reference '
                                 'simulator to be reproduced with its own database.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Forma cúbica en Z y su resolución',
                               'Cubic form in Z and its solution'),
                    'bloques': [('p',
                                 'Para el cálculo se reescribe la ecuación de estado en función '
                                 'del factor de compresibilidad Z = P·V/(R·T), mediante dos grupos '
                                 'adimensionales que concentran la información de la fase y del '
                                 'estado:',
                                 'For calculation purposes the equation of state is rewritten in '
                                 'terms of the compressibility factor Z = P·V/(R·T), by means of '
                                 'two dimensionless groups that contain the phase and state '
                                 'information:'),
                                ('eq',
                                 'A = \\frac{a_m\\,P}{(R\\,T)^{2}} \\qquad B = '
                                 '\\frac{b_m\\,P}{R\\,T}'),
                                ('p',
                                 'donde a<sub>m</sub> y b<sub>m</sub> son los parámetros de la '
                                 'fase obtenidos con la regla de mezcla (psia·ft⁶/lbmol² y '
                                 'ft³/lbmol), P la presión (psia) y T la temperatura (°R).',
                                 'where a<sub>m</sub> and b<sub>m</sub> are the phase parameters '
                                 'obtained from the mixing rule (psia·ft⁶/lbmol² and ft³/lbmol), P '
                                 'is the pressure (psia), and T is the temperature (°R).'),
                                ('p',
                                 'Para Peng-Robinson se obtiene el polinomio:',
                                 'For Peng-Robinson the following polynomial is obtained:'),
                                ('eq',
                                 'Z^{3} - (1 - B)\\,Z^{2} + \\left(A - 3B^{2} - 2B\\right)Z - '
                                 '\\left(AB - B^{2} - B^{3}\\right) = 0'),
                                ('p', 'y para SRK:', 'and for SRK:'),
                                ('eq', 'Z^{3} - Z^{2} + \\left(A - B - B^{2}\\right)Z - A\\,B = 0'),
                                ('p',
                                 'donde Z es el factor de compresibilidad y A, B los grupos '
                                 'adimensionales definidos arriba.',
                                 'where Z is the compressibility factor and A, B are the '
                                 'dimensionless groups defined above.'),
                                ('h3', 'Resolución de la cúbica', 'Solution of the cubic'),
                                ('p',
                                 'ThermoPhase resuelve la cúbica de forma analítica. Escrita como '
                                 'Z³ + p<sub>2</sub>Z² + p<sub>1</sub>Z + p<sub>0</sub> = 0, se '
                                 'reduce a la forma deprimida con el cambio Z = t − '
                                 'p<sub>2</sub>/3:',
                                 'ThermoPhase solves the cubic analytically. Written as Z³ + '
                                 'p<sub>2</sub>Z² + p<sub>1</sub>Z + p<sub>0</sub> = 0, it is '
                                 'reduced to the depressed form with the substitution Z = t − '
                                 'p<sub>2</sub>/3:'),
                                ('eq',
                                 't^{3} + p\\,t + q = 0 \\qquad p = p_1 - \\frac{p_2^{2}}{3} '
                                 '\\qquad q = \\frac{2\\,p_2^{3}}{27} - \\frac{p_2\\,p_1}{3} + '
                                 'p_0'),
                                ('eq', 'D = \\frac{q^{2}}{4} + \\frac{p^{3}}{27}'),
                                ('p',
                                 'donde p<sub>2</sub>, p<sub>1</sub>, p<sub>0</sub> son los '
                                 'coeficientes del polinomio en Z, t la variable deprimida y D el '
                                 'discriminante. Si D &gt; 0 existe una sola raíz real, que se '
                                 'obtiene por la fórmula de Cardano; si D ≤ 0 existen tres raíces '
                                 'reales, que se obtienen por la solución trigonométrica:',
                                 'where p<sub>2</sub>, p<sub>1</sub>, p<sub>0</sub> are the '
                                 'coefficients of the polynomial in Z, t is the depressed '
                                 'variable, and D is the discriminant. If D &gt; 0 there is a '
                                 "single real root, obtained with Cardano's formula; if D ≤ 0 "
                                 'there are three real roots, obtained with the trigonometric '
                                 'solution:'),
                                ('eq',
                                 't_k = 2\\sqrt{-p/3}\\;\\cos\\left(\\theta - \\frac{2\\pi '
                                 'k}{3}\\right) \\qquad k = 0, 1, 2'),
                                ('eq',
                                 '\\theta = '
                                 '\\frac{1}{3}\\arccos\\left(\\frac{3q}{2p}\\sqrt{-3/p}\\right)'),
                                ('p',
                                 'donde t<sub>k</sub> son las tres raíces de la cúbica deprimida y '
                                 'θ el ángulo auxiliar. Se descartan las raíces con Z ≤ B, que '
                                 'corresponden a volúmenes menores que el covolumen y carecen de '
                                 'sentido físico. En los cálculos con agua, cada raíz analítica se '
                                 'refina además con dos pasos de Newton sobre el polinomio.',
                                 'where t<sub>k</sub> are the three roots of the depressed cubic '
                                 'and θ is the auxiliary angle. Roots with Z ≤ B, which correspond '
                                 'to volumes smaller than the covolume and have no physical '
                                 'meaning, are discarded. In the water-containing calculations, '
                                 'each analytical root is additionally refined with two Newton '
                                 'steps on the polynomial.'),
                                ('p',
                                 'Cuando existen tres raíces reales, la mayor corresponde a una '
                                 'fase de tipo vapor, la menor a una fase de tipo líquido y la '
                                 'intermedia a un estado mecánicamente inestable, que no se '
                                 'utiliza.',
                                 'When three real roots exist, the largest corresponds to a '
                                 'vapor-like phase, the smallest to a liquid-like phase, and the '
                                 'intermediate one to a mechanically unstable state, which is not '
                                 'used.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Selección de raíz por mínima energía de Gibbs',
                               'Root selection by minimum Gibbs energy'),
                    'bloques': [('p',
                                 'Cuando la cúbica tiene dos raíces con significado físico, cada '
                                 'una representa un estado posible de la fase a la misma '
                                 'temperatura, presión y composición. A temperatura y presión '
                                 'constantes el estado estable es el de menor energía de Gibbs, de '
                                 'modo que la raíz físicamente correcta es la que minimiza esa '
                                 'energía.',
                                 'When the cubic has two physically meaningful roots, each one '
                                 'represents a possible state of the phase at the same '
                                 'temperature, pressure, and composition. At constant temperature '
                                 'and pressure the stable state is the one with the lowest Gibbs '
                                 'energy, so the physically correct root is the one that minimizes '
                                 'that energy.'),
                                ('p',
                                 'Para una fase de composición x, la energía de Gibbs adimensional '
                                 '(sin los términos que son iguales para ambas raíces) es:',
                                 'For a phase of composition x, the dimensionless Gibbs energy '
                                 '(without the terms that are equal for both roots) is:'),
                                ('eq',
                                 '\\frac{G}{R\\,T} = \\sum_{i} x_i '
                                 '\\ln\\left(x_i\\,\\phi_i\\right)'),
                                ('p',
                                 'donde x<sub>i</sub> es la fracción molar del componente i y '
                                 'φ<sub>i</sub> su coeficiente de fugacidad evaluado con la raíz '
                                 'considerada. Como la composición es la misma para ambas raíces, '
                                 'la comparación equivale a comparar la energía de Gibbs residual '
                                 'de la fase:',
                                 'where x<sub>i</sub> is the mole fraction of component i and '
                                 'φ<sub>i</sub> is its fugacity coefficient evaluated with the '
                                 'root under consideration. Since the composition is the same for '
                                 'both roots, the comparison is equivalent to comparing the '
                                 'residual Gibbs energy of the phase:'),
                                ('eq',
                                 '\\left(\\frac{G^{\\mathrm{res}}}{R\\,T}\\right)_{\\mathrm{PR}} = '
                                 'Z - 1 - \\ln(Z - B) - '
                                 '\\frac{A}{2\\sqrt{2}\\,B}\\ln\\left[\\frac{Z + (1+\\sqrt{2})B}{Z '
                                 '+ (1-\\sqrt{2})B}\\right]'),
                                ('eq',
                                 '\\left(\\frac{G^{\\mathrm{res}}}{R\\,T}\\right)_{\\mathrm{SRK}} '
                                 '= Z - 1 - \\ln(Z - B) - \\frac{A}{B}\\ln\\left(\\frac{Z + '
                                 'B}{Z}\\right)'),
                                ('p',
                                 'donde G<sup>res</sup> es la energía de Gibbs residual molar, Z '
                                 'la raíz evaluada y A, B los grupos adimensionales de la fase. Se '
                                 'selecciona la raíz de menor valor.',
                                 'where G<sup>res</sup> is the molar residual Gibbs energy, Z is '
                                 'the root being evaluated, and A, B are the dimensionless groups '
                                 'of the phase. The root with the lowest value is selected.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('ul',
                                 [('Cuando el rol de la fase es conocido (vapor o líquido de un '
                                   'flash bifásico, fases de prueba vapor y líquido del análisis '
                                   'de estabilidad del flash de hidrocarburos), ThermoPhase asigna '
                                   'directamente la raíz mayor a la fase vapor y la raíz menor a '
                                   'la fase líquida.',
                                   'When the phase role is known (vapor or liquid of a two-phase '
                                   'flash, vapor and liquid trial phases of the stability analysis '
                                   'in the water-free engine), ThermoPhase directly assigns the '
                                   'largest root to the vapor phase and the smallest root to the '
                                   'liquid phase.'),
                                  ('En el trazado de la envolvente de fases por el método de '
                                   'Michelsen, los coeficientes de fugacidad de cada fase se '
                                   'evalúan con la raíz de menor energía de Gibbs residual, de '
                                   'modo que la selección es válida tanto en la rama de burbuja '
                                   'como en la de rocío.',
                                   'In the phase-envelope tracing by the Michelsen method, the '
                                   'fugacity coefficients of each phase are evaluated with the '
                                   'root of lowest residual Gibbs energy, so that the selection is '
                                   'valid on both the bubble and the dew branch.'),
                                  ('En los cálculos con agua, las fases de prueba del análisis de '
                                   'distancia al plano tangente se evalúan con la raíz de menor '
                                   'Σx<sub>i</sub> ln(x<sub>i</sub>φ<sub>i</sub>), y un fluido '
                                   'monofásico se clasifica como vapor o líquido comparando la '
                                   'energía de Gibbs de sus dos raíces.',
                                   'In the water-containing calculations, the trial phases of the '
                                   'tangent-plane-distance analysis are evaluated with the root of '
                                   'lowest Σx<sub>i</sub> ln(x<sub>i</sub>φ<sub>i</sub>), and a '
                                   'single-phase fluid is classified as vapor or liquid by '
                                   'comparing the Gibbs energy of its two roots.'),
                                  ('Cuando existe una sola raíz real, el criterio de Gibbs no '
                                   'discrimina la fase; su identificación como vapor o líquido '
                                   'sigue el criterio de HYSYS o de PVTsim según la ecuación '
                                   'activa (véase el capítulo «Identificación de fases»).',
                                   'When a single real root exists, the Gibbs criterion does not '
                                   'discriminate the phase; its identification as vapor or liquid '
                                   'follows the HYSYS or PVTsim criterion according to the active '
                                   'equation (see the “Phase identification” chapter).')]),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.')]},
                   {'titulo': ('Coeficiente de fugacidad', 'Fugacity coefficient'),
                    'bloques': [('p',
                                 'El coeficiente de fugacidad de cada componente en una fase es la '
                                 'magnitud que gobierna el equilibrio de fases: en el equilibrio, '
                                 'la fugacidad f<sub>i</sub> = x<sub>i</sub>·φ<sub>i</sub>·P de '
                                 'cada componente es igual en todas las fases. Se obtiene por '
                                 'derivación de la energía de Helmholtz residual de la ecuación de '
                                 'estado respecto del número de moles del componente.',
                                 'The fugacity coefficient of each component in a phase is the '
                                 'quantity that governs phase equilibrium: at equilibrium, the '
                                 'fugacity f<sub>i</sub> = x<sub>i</sub>·φ<sub>i</sub>·P of each '
                                 'component is equal in all phases. It is obtained by '
                                 'differentiating the residual Helmholtz energy of the equation of '
                                 'state with respect to the number of moles of the component.'),
                                ('h3', 'Peng-Robinson', 'Peng-Robinson'),
                                ('eq',
                                 '\\ln\\phi_i = \\frac{b_i}{b_m}(Z - 1) - \\ln(Z - B) - '
                                 '\\frac{A}{2\\sqrt{2}\\,B}\\left(\\frac{2\\,\\psi_i}{a_m} - '
                                 '\\frac{b_i}{b_m}\\right)\\ln\\left[\\frac{Z + (1+\\sqrt{2})B}{Z '
                                 '+ (1-\\sqrt{2})B}\\right]'),
                                ('h3', 'Soave-Redlich-Kwong', 'Soave-Redlich-Kwong'),
                                ('eq',
                                 '\\ln\\phi_i = \\frac{b_i}{b_m}(Z - 1) - \\ln(Z - B) - '
                                 '\\frac{A}{B}\\left(\\frac{2\\,\\psi_i}{a_m} - '
                                 '\\frac{b_i}{b_m}\\right)\\ln\\left(\\frac{Z + B}{Z}\\right)'),
                                ('p',
                                 'donde φ<sub>i</sub> es el coeficiente de fugacidad del '
                                 'componente i, Z el factor de compresibilidad de la fase, A y B '
                                 'los grupos adimensionales de la fase, a<sub>m</sub> y '
                                 'b<sub>m</sub> los parámetros de la mezcla, b<sub>i</sub> el '
                                 'covolumen del componente y ψ<sub>i</sub> el término de '
                                 'interacción atractiva del componente i con la fase.',
                                 'where φ<sub>i</sub> is the fugacity coefficient of component i, '
                                 'Z is the phase compressibility factor, A and B are the '
                                 'dimensionless groups of the phase, a<sub>m</sub> and '
                                 'b<sub>m</sub> are the mixture parameters, b<sub>i</sub> is the '
                                 'component covolume, and ψ<sub>i</sub> is the attractive '
                                 'interaction term of component i with the phase.'),
                                ('p',
                                 'El término ψ<sub>i</sub> es la derivada parcial del parámetro '
                                 'atractivo total respecto de los moles del componente. Con la '
                                 'regla de mezcla clásica toma la forma:',
                                 'The term ψ<sub>i</sub> is the partial derivative of the total '
                                 'attractive parameter with respect to the moles of the component. '
                                 'With the classical mixing rule it takes the form:'),
                                ('eq',
                                 '\\psi_i = '
                                 '\\frac{1}{2}\\left(\\frac{\\partial\\,(n^{2}a_m)}{\\partial '
                                 'n_i}\\right)_{T,\\,n_j} = \\sum_{j} '
                                 'x_j\\,\\sqrt{a_i\\,a_j}\\left(1 - k_{ij}\\right)'),
                                ('p',
                                 'donde n es el número total de moles, n<sub>i</sub> los moles del '
                                 'componente i, x<sub>j</sub> la fracción molar del componente j '
                                 'en la fase, a<sub>i</sub> y a<sub>j</sub> los parámetros '
                                 'atractivos a la temperatura del sistema y k<sub>ij</sub> el '
                                 'coeficiente de interacción binaria. Con la regla de Huron-Vidal, '
                                 'ψ<sub>i</sub> se obtiene por derivación analítica de esa regla '
                                 '(véase «Reducción a la regla clásica y derivada para la '
                                 'fugacidad»).',
                                 'where n is the total number of moles, n<sub>i</sub> is the '
                                 'number of moles of component i, x<sub>j</sub> is the mole '
                                 'fraction of component j in the phase, a<sub>i</sub> and '
                                 'a<sub>j</sub> are the attractive parameters at the system '
                                 'temperature, and k<sub>ij</sub> is the binary interaction '
                                 'coefficient. With the Huron-Vidal rule, ψ<sub>i</sub> is '
                                 'obtained by analytical differentiation of that rule (see '
                                 '“Reduction to the classical rule and derivative for the '
                                 'fugacity”).'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'ThermoPhase evalúa los coeficientes de fugacidad de todos los '
                                 'componentes de una fase en una sola operación vectorial: calcula '
                                 'una vez los vectores √a<sub>i</sub>, '
                                 'x<sub>i</sub>√a<sub>i</sub>, A, B y b<sub>i</sub>/b<sub>m</sub>, '
                                 'y obtiene ψ<sub>i</sub> para todos los componentes con un '
                                 'producto matriz-vector sobre la matriz k<sub>ij</sub>. Si Z ≤ B, '
                                 'Z se desplaza a B + 10<sup>−12</sup> para mantener definido el '
                                 'logaritmo, y ln φ<sub>i</sub> se limita a ±500 antes de calcular '
                                 'φ<sub>i</sub>.',
                                 'ThermoPhase evaluates the fugacity coefficients of all '
                                 'components of a phase in a single vector operation: it computes '
                                 'once the vectors √a<sub>i</sub>, x<sub>i</sub>√a<sub>i</sub>, A, '
                                 'B, and b<sub>i</sub>/b<sub>m</sub>, and obtains ψ<sub>i</sub> '
                                 'for all components with a matrix-vector product over the '
                                 'k<sub>ij</sub> matrix. If Z ≤ B, Z is shifted to B + '
                                 '10<sup>−12</sup> to keep the logarithm defined, and ln '
                                 'φ<sub>i</sub> is bounded to ±500 before φ<sub>i</sub> is '
                                 'computed.'),
                                ('p',
                                 'Los coeficientes de fugacidad se calculan siempre con la '
                                 'ecuación sin traslado de volumen, ya que el traslado de Peneloux '
                                 'no modifica el equilibrio de fases (véase «Corrección de volumen '
                                 'de Peneloux»).',
                                 'The fugacity coefficients are always computed with the unshifted '
                                 'equation, since the Peneloux volume shift does not modify the '
                                 'phase equilibrium (see “Peneloux volume correction”).'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]}]},
 {'titulo': ('Reglas de mezcla y coeficientes de interacción',
             'Mixing rules and interaction coefficients'),
  'subsecciones': [{'titulo': ('Regla de mezcla clásica de van der Waals',
                               'Classical van der Waals mixing rule'),
                    'bloques': [('p',
                                 'Las reglas de mezcla definen los parámetros a<sub>m</sub> y '
                                 'b<sub>m</sub> de una fase a partir de los parámetros de los '
                                 'componentes puros y de la composición. ThermoPhase aplica la '
                                 'regla clásica de un fluido de van der Waals en todos los '
                                 'cálculos sin agua y en todos los pares sin agua de los cálculos '
                                 'con agua.',
                                 'Mixing rules define the phase parameters a<sub>m</sub> and '
                                 'b<sub>m</sub> from the pure-component parameters and the '
                                 'composition. ThermoPhase applies the classical van der Waals '
                                 'one-fluid rule in all water-free calculations and in all pairs '
                                 'without water in the water-containing calculations.'),
                                ('eq', 'b_m = \\sum_{i} x_i\\,b_i'),
                                ('eq',
                                 'a_m = \\sum_{i}\\sum_{j} x_i\\,x_j\\,a_{ij} \\qquad a_{ij} = '
                                 '\\sqrt{a_i(T)\\,a_j(T)}\\,\\left(1 - k_{ij}\\right)'),
                                ('p',
                                 'donde x<sub>i</sub> es la fracción molar del componente i en la '
                                 'fase, b<sub>i</sub> su covolumen, a<sub>i</sub>(T) = '
                                 'a<sub>c,i</sub>·α<sub>i</sub>(T) su parámetro atractivo a la '
                                 'temperatura del sistema, a<sub>ij</sub> el parámetro atractivo '
                                 'cruzado y k<sub>ij</sub> el coeficiente de interacción binaria '
                                 'del par i-j.',
                                 'where x<sub>i</sub> is the mole fraction of component i in the '
                                 'phase, b<sub>i</sub> is its covolume, a<sub>i</sub>(T) = '
                                 'a<sub>c,i</sub>·α<sub>i</sub>(T) is its attractive parameter at '
                                 'the system temperature, a<sub>ij</sub> is the cross attractive '
                                 'parameter, and k<sub>ij</sub> is the binary interaction '
                                 'coefficient of the pair i-j.'),
                                ('p',
                                 'La regla lineal del covolumen expresa que el volumen excluido de '
                                 'la mezcla es la suma de los volúmenes excluidos de sus '
                                 'componentes. La regla cuadrática del término atractivo suma las '
                                 'interacciones de todos los pares de moléculas; la media '
                                 'geométrica estima la atracción entre moléculas distintas y el '
                                 'factor (1 − k<sub>ij</sub>) corrige su desviación respecto de '
                                 'ese promedio.',
                                 'The linear covolume rule expresses that the excluded volume of '
                                 'the mixture is the sum of the excluded volumes of its '
                                 'components. The quadratic rule of the attractive term sums the '
                                 'interactions of all molecular pairs; the geometric mean '
                                 'estimates the attraction between unlike molecules and the factor '
                                 '(1 − k<sub>ij</sub>) corrects its deviation from that average.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La doble suma se evalúa en forma vectorial. Con s<sub>i</sub> = '
                                 'x<sub>i</sub>√a<sub>i</sub> y la matriz simétrica K = '
                                 '[k<sub>ij</sub>] de diagonal nula, el parámetro atractivo '
                                 'resulta:',
                                 'The double sum is evaluated in vector form. With s<sub>i</sub> = '
                                 'x<sub>i</sub>√a<sub>i</sub> and the symmetric matrix K = '
                                 '[k<sub>ij</sub>] with zero diagonal, the attractive parameter '
                                 'is:'),
                                ('eq',
                                 'a_m = \\left(\\sum_{i} s_i\\right)^{2} - '
                                 '\\mathbf{s}^{T}\\,\\mathbf{K}\\,\\mathbf{s}'),
                                ('p',
                                 'donde s es el vector de componentes s<sub>i</sub> y K la matriz '
                                 'de coeficientes de interacción binaria. En los cálculos sin agua '
                                 'la matriz K empleada es la del fluido activo, que por defecto es '
                                 'la de la ecuación de estado seleccionada.',
                                 'where s is the vector of components s<sub>i</sub> and K is the '
                                 'binary interaction coefficient matrix. In the water-free '
                                 'calculations the matrix K used is that of the active fluid, '
                                 'which by default is the one of the selected equation of state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Coeficientes de interacción binaria',
                               'Binary interaction coefficients'),
                    'bloques': [('p',
                                 'Los coeficientes de interacción binaria forman una matriz '
                                 'simétrica de diagonal nula. Aunque sus valores son pequeños, '
                                 'tienen un efecto importante sobre la envolvente de fases, '
                                 'especialmente cerca del punto crítico de la mezcla, donde '
                                 'pequeños cambios de la atracción cruzada desplazan las curvas de '
                                 'burbuja y de rocío.',
                                 'Binary interaction coefficients form a symmetric matrix with '
                                 'zero diagonal. Although their values are small, they have a '
                                 'significant effect on the phase envelope, especially near the '
                                 'mixture critical point, where small changes in the cross '
                                 'attraction shift the bubble and dew curves.'),
                                ('eq', 'k_{ij} = k_{ji} \\qquad k_{ii} = 0'),
                                ('p',
                                 'donde k<sub>ij</sub> es el coeficiente de interacción entre los '
                                 'componentes i y j.',
                                 'where k<sub>ij</sub> is the interaction coefficient between '
                                 'components i and j.'),
                                ('p',
                                 'Cada una de las cuatro ecuaciones de estado tiene su propia '
                                 'matriz de trece por trece componentes, ya que los coeficientes '
                                 'dependen tanto del simulador de referencia como de la forma de '
                                 'la ecuación.',
                                 'Each of the four equations of state has its own '
                                 'thirteen-by-thirteen component matrix, because the coefficients '
                                 'depend both on the reference simulator and on the form of the '
                                 'equation.'),
                                ('h3', 'Base de datos de HYSYS', 'HYSYS database'),
                                ('p',
                                 'Las matrices de PR (HYSYS) y SRK (HYSYS) reproducen las que '
                                 'Aspen HYSYS reporta en su paquete de fluidos para cada método. '
                                 'En la matriz de PR, el par N₂-CO₂ vale −0.02, los pares '
                                 'N₂-hidrocarburo varían entre 0.036 (N₂-C1) y 0.149 (N₂-nC6), los '
                                 'pares CO₂-hidrocarburo entre 0.10 y 0.135, y los pares '
                                 'hidrocarburo-hidrocarburo son todos no nulos y pequeños, '
                                 'crecientes con la diferencia de tamaño molecular (del orden de '
                                 '10<sup>−6</sup> a 0.039, este último para C1-nC9). La matriz de '
                                 'SRK comparte prácticamente los valores hidrocarburo-hidrocarburo '
                                 'y difiere en las filas de N₂ y CO₂.',
                                 'The PR (HYSYS) and SRK (HYSYS) matrices reproduce those that '
                                 'Aspen HYSYS reports in its fluid package for each method. In the '
                                 'PR matrix, the N₂-CO₂ pair is −0.02, the N₂-hydrocarbon pairs '
                                 'range from 0.036 (N₂-C1) to 0.149 (N₂-nC6), the CO₂-hydrocarbon '
                                 'pairs from 0.10 to 0.135, and the hydrocarbon-hydrocarbon pairs '
                                 'are all nonzero and small, increasing with the molecular size '
                                 'difference (from the order of 10<sup>−6</sup> up to 0.039, the '
                                 'latter for C1-nC9). The SRK matrix shares essentially the same '
                                 'hydrocarbon-hydrocarbon values and differs in the N₂ and CO₂ '
                                 'rows.'),
                                ('h3', 'Base de datos de PVTsim', 'PVTsim database'),
                                ('p',
                                 'Las matrices de PR (PVTsim) y SRK (PVTsim) provienen de la base '
                                 'de datos de PVTsim, basada en la recopilación de Knapp y '
                                 'colaboradores (1982), con nC7, nC8 y nC9 tratados como '
                                 'n-alcanos. ThermoPhase almacena su triangular inferior y '
                                 'construye la matriz simétrica completa. En PR (PVTsim) el par '
                                 'N₂-CO₂ vale −0.017, los pares N₂-hidrocarburo entre 0.031 y '
                                 '0.150, y los pares CO₂-hidrocarburo 0.12 hasta nC6 y 0.10 desde '
                                 'nC7. Los pares entre hidrocarburos livianos (C1 a nC6) son '
                                 'nulos; solo tienen valores distintos de cero algunos pares con '
                                 'nC7, nC8 y nC9 (por ejemplo, C1-nC7 = 0.0352, C1-nC8 = 0.0496 y '
                                 'C1-nC9 = 0.0474).',
                                 'The PR (PVTsim) and SRK (PVTsim) matrices come from the PVTsim '
                                 'database, based on the compilation by Knapp et al. (1982), with '
                                 'nC7, nC8, and nC9 treated as n-alkanes. ThermoPhase stores their '
                                 'lower triangle and builds the complete symmetric matrix. In PR '
                                 '(PVTsim) the N₂-CO₂ pair is −0.017, the N₂-hydrocarbon pairs '
                                 'range from 0.031 to 0.150, and the CO₂-hydrocarbon pairs are '
                                 '0.12 up to nC6 and 0.10 from nC7 onward. Pairs among light '
                                 'hydrocarbons (C1 to nC6) are zero; only some pairs with nC7, '
                                 'nC8, and nC9 have nonzero values (for example, C1-nC7 = 0.0352, '
                                 'C1-nC8 = 0.0496, and C1-nC9 = 0.0474).'),
                                ('h3', 'Pares con agua', 'Water pairs'),
                                ('p',
                                 'Cuando el agua está activa, el cálculo de catorce componentes '
                                 'forma su matriz con la matriz por defecto de la ecuación activa '
                                 'para los trece primeros componentes y la fila del agua de la '
                                 'misma familia de ecuaciones. En HYSYS (PR) los valores '
                                 'agua-hidrocarburo son del orden de 0.5, con −0.3156 para N₂ y '
                                 '0.0445 para CO₂; en PVTsim (PR) son 0.45 a 0.53, con −0.48 para '
                                 'N₂ y 0.0952 para CO₂. Estos coeficientes clásicos solo '
                                 'intervienen en los pares del agua con nC7, nC8 y nC9; los pares '
                                 'del agua con N₂ a nC6 se calculan con la regla de Huron-Vidal.',
                                 'When water is active, the fourteen-component calculation builds '
                                 'its matrix from the default matrix of the active equation for '
                                 'the first thirteen components and the water row of the same '
                                 'equation family. In HYSYS (PR) the water-hydrocarbon values are '
                                 'of the order of 0.5, with −0.3156 for N₂ and 0.0445 for CO₂; in '
                                 'PVTsim (PR) they are 0.45 to 0.53, with −0.48 for N₂ and 0.0952 '
                                 'for CO₂. These classical coefficients only enter the water pairs '
                                 'with nC7, nC8, and nC9; the water pairs with N₂ to nC6 are '
                                 'computed with the Huron-Vidal rule.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Knapp, H., Döring, R., Oellrich, L., Plöcker, U. y Prausnitz, '
                                 'J.M. (1982). <em>Vapor-Liquid Equilibria for Mixtures of Low '
                                 'Boiling Substances</em>. DECHEMA Chemistry Data Series, vol. VI. '
                                 'DECHEMA.',
                                 'Knapp, H., Döring, R., Oellrich, L., Plöcker, U. and Prausnitz, '
                                 'J.M. (1982). <em>Vapor-Liquid Equilibria for Mixtures of Low '
                                 'Boiling Substances</em>. DECHEMA Chemistry Data Series, vol. VI. '
                                 'DECHEMA.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Edición de los coeficientes de interacción',
                               'Editing the interaction coefficients'),
                    'bloques': [('p',
                                 'La ventana de parámetros de la ecuación de estado presenta dos '
                                 'tablas: las propiedades críticas y el factor acéntrico de la '
                                 'ecuación del contexto, y la matriz de coeficientes de '
                                 'interacción binaria. La primera es de solo lectura y se expresa '
                                 'en el sistema de unidades activo; la segunda es editable.',
                                 'The equation-of-state parameters window presents two tables: the '
                                 'critical properties and acentric factor of the equation in '
                                 'context, and the binary interaction coefficient matrix. The '
                                 'first is read-only and is expressed in the active unit system; '
                                 'the second is editable.'),
                                ('ul',
                                 [('La matriz activa es la global o la propia del fluido '
                                   'seleccionado; cada fluido conserva una matriz independiente.',
                                   'The active matrix is either the global one or that of the '
                                   'selected fluid; each fluid keeps an independent matrix.'),
                                  ('Un selector de fuente permite cargar la matriz por defecto de '
                                   'cualquiera de las cuatro ecuaciones (PR o SRK de HYSYS, PR o '
                                   'SRK de PVTsim).',
                                   'A source selector allows the default matrix of any of the four '
                                   'equations (HYSYS PR or SRK, PVTsim PR or SRK) to be loaded.'),
                                  ('Al modificar un coeficiente k<sub>ij</sub>, ThermoPhase '
                                   'actualiza automáticamente su simétrico k<sub>ji</sub>; la '
                                   'diagonal no es editable.',
                                   'When a coefficient k<sub>ij</sub> is modified, ThermoPhase '
                                   'automatically updates its symmetric counterpart '
                                   'k<sub>ji</sub>; the diagonal is not editable.'),
                                  ('El comando de restauración devuelve la matriz a los valores '
                                   'por defecto de la fuente seleccionada.',
                                   'The restore command returns the matrix to the default values '
                                   'of the selected source.'),
                                  ('Con el agua activa se muestran su fila y su columna con los '
                                   'coeficientes clásicos agua-hidrocarburo de la ecuación del '
                                   'contexto, como valores informativos de solo lectura, ya que '
                                   'los pares del agua con N₂ a nC6 se rigen por la regla de '
                                   'Huron-Vidal.',
                                   'With water active, its row and column are shown with the '
                                   'classical water-hydrocarbon coefficients of the equation in '
                                   'context, as read-only informative values, because the water '
                                   'pairs with N₂ to nC6 are governed by the Huron-Vidal rule.'),
                                  ('Las filas y columnas de los componentes no incluidos en el '
                                   'fluido se ocultan.',
                                   'Rows and columns of components not included in the fluid are '
                                   'hidden.')]),
                                ('p',
                                 'La matriz editada se utiliza en los cálculos sin agua: flash '
                                 'bifásico, envolventes, puntos de saturación y demás funciones '
                                 'que evalúan la ecuación de estado de trece componentes. Los '
                                 'cálculos con agua emplean la matriz por defecto de la ecuación '
                                 'activa, y los parámetros de la regla de Huron-Vidal no se editan '
                                 'desde la interfaz.',
                                 'The edited matrix is used in the water-free calculations: '
                                 'two-phase flash, envelopes, saturation points, and the other '
                                 'functions that evaluate the thirteen-component equation of '
                                 'state. The water-containing calculations use the default matrix '
                                 'of the active equation, and the Huron-Vidal rule parameters are '
                                 'not edited from the interface.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Regla de mezcla de Huron-Vidal para agua',
                               'Huron-Vidal mixing rule for water'),
                    'bloques': [('p',
                                 'La regla clásica con un k<sub>ij</sub> constante no representa '
                                 'simultáneamente la solubilidad de los hidrocarburos en la fase '
                                 'acuosa y la del agua en las fases de hidrocarburos. Para los '
                                 'pares agua-hidrocarburo ThermoPhase aplica la regla de '
                                 'Huron-Vidal, que iguala la energía de Gibbs de exceso de la '
                                 'ecuación de estado a presión infinita con la de un modelo de '
                                 'composición local del tipo NRTL, con los parámetros publicados '
                                 'por Pedersen y colaboradores (2001) y empleados por PVTsim.',
                                 'The classical rule with a constant k<sub>ij</sub> does not '
                                 'simultaneously represent the solubility of hydrocarbons in the '
                                 'aqueous phase and that of water in the hydrocarbon phases. For '
                                 'the water-hydrocarbon pairs ThermoPhase applies the Huron-Vidal '
                                 'rule, which equates the equation-of-state excess Gibbs energy at '
                                 'infinite pressure with that of an NRTL-type local-composition '
                                 'model, with the parameters published by Pedersen et al. (2001) '
                                 'and used by PVTsim.'),
                                ('eq',
                                 'a_m = b_m\\left[\\sum_{i} x_i\\,\\frac{a_i}{b_i} - '
                                 '\\frac{G^{E}_{\\infty}}{\\lambda}\\right] \\qquad b_m = '
                                 '\\sum_{i} x_i\\,b_i'),
                                ('eq',
                                 '\\frac{G^{E}_{\\infty}}{R\\,T} = \\sum_{i} '
                                 'x_i\\,\\frac{\\sum_{j} '
                                 '\\tau_{ji}\\,b_j\\,x_j\\,\\exp\\left(-\\alpha_{ji}\\tau_{ji}\\right)}{\\sum_{k} '
                                 'b_k\\,x_k\\,\\exp\\left(-\\alpha_{ki}\\tau_{ki}\\right)}'),
                                ('p',
                                 'donde G<sup>E</sup><sub>∞</sub> es la energía de Gibbs de exceso '
                                 'molar a presión infinita (en unidades coherentes con R), '
                                 'τ<sub>ji</sub> el parámetro adimensional de interacción, '
                                 'α<sub>ji</sub> el parámetro de no aleatoriedad del modelo NRTL y '
                                 'λ una constante que depende de la ecuación de estado.',
                                 'where G<sup>E</sup><sub>∞</sub> is the molar excess Gibbs energy '
                                 'at infinite pressure (in units consistent with R), '
                                 'τ<sub>ji</sub> is the dimensionless interaction parameter, '
                                 'α<sub>ji</sub> is the NRTL nonrandomness parameter, and λ is a '
                                 'constant that depends on the equation of state.'),
                                ('eq',
                                 '\\lambda_{\\mathrm{SRK}} = \\ln 2 = 0.69315 \\qquad '
                                 '\\lambda_{\\mathrm{PR}} = '
                                 '\\frac{1}{2\\sqrt{2}}\\ln\\left(\\frac{1+\\sqrt{2}}{\\sqrt{2}-1}\\right) '
                                 '= 0.62323'),
                                ('p',
                                 'donde λ<sub>SRK</sub> y λ<sub>PR</sub> son los valores de λ para '
                                 'SRK y Peng-Robinson.',
                                 'where λ<sub>SRK</sub> and λ<sub>PR</sub> are the values of λ for '
                                 'SRK and Peng-Robinson.'),
                                ('h3', 'Pares agua-hidrocarburo', 'Water-hydrocarbon pairs'),
                                ('p',
                                 'Para los pares del agua con N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, '
                                 'nC5 y nC6, el parámetro de interacción depende linealmente de la '
                                 'temperatura:',
                                 'For the water pairs with N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, '
                                 'nC5, and nC6, the interaction parameter depends linearly on '
                                 'temperature:'),
                                ('eq',
                                 '\\tau_{ji} = \\frac{g_{ji} - g_{ii}}{R\\,T} = '
                                 '\\frac{G^{(0)}_{ji} + G^{(T)}_{ji}\\,T}{T}'),
                                ('p',
                                 'donde g<sub>ji</sub> es la energía de interacción del par j-i, '
                                 'g<sub>ii</sub> la energía de interacción del componente i '
                                 'consigo mismo, T la temperatura absoluta en K, '
                                 'G<sup>(0)</sup><sub>ji</sub> = (g<sub>ji</sub> − '
                                 'g<sub>ii</sub>)<sup>(0)</sup>/R el término constante en K y '
                                 'G<sup>(T)</sup><sub>ji</sub> el coeficiente adimensional de '
                                 'temperatura. Los parámetros G<sup>(0)</sup>, G<sup>(T)</sup> y α '
                                 'son distintos para PR y para SRK y no son simétricos en '
                                 'G<sup>(0)</sup> y G<sup>(T)</sup> (τ<sub>ij</sub> ≠ '
                                 'τ<sub>ji</sub>); α<sub>ij</sub> = α<sub>ji</sub>. Por ejemplo, '
                                 'con PR: G<sup>(0)</sup> agua-C1 = −557.66 K y G<sup>(0)</sup> '
                                 'C1-agua = 4629.50 K, con G<sup>(T)</sup> = 3.26 y −6.53, '
                                 'respectivamente, y α = 0.1444.',
                                 'where g<sub>ji</sub> is the interaction energy of pair j-i, '
                                 'g<sub>ii</sub> is the interaction energy of component i with '
                                 'itself, T is the absolute temperature in K, '
                                 'G<sup>(0)</sup><sub>ji</sub> = (g<sub>ji</sub> − '
                                 'g<sub>ii</sub>)<sup>(0)</sup>/R is the constant term in K, and '
                                 'G<sup>(T)</sup><sub>ji</sub> is the dimensionless temperature '
                                 'coefficient. The G<sup>(0)</sup>, G<sup>(T)</sup>, and α '
                                 'parameters are different for PR and for SRK and are not '
                                 'symmetric in G<sup>(0)</sup> and G<sup>(T)</sup> (τ<sub>ij</sub> '
                                 '≠ τ<sub>ji</sub>); α<sub>ij</sub> = α<sub>ji</sub>. For example, '
                                 'with PR: G<sup>(0)</sup> water-C1 = −557.66 K and '
                                 'G<sup>(0)</sup> C1-water = 4629.50 K, with G<sup>(T)</sup> = '
                                 '3.26 and −6.53, respectively, and α = 0.1444.'),
                                ('h3', 'Pares con regla clásica', 'Pairs with the classical rule'),
                                ('p',
                                 'Los pares del agua con nC7, nC8 y nC9 tienen α = 0 en la base de '
                                 'datos de PVTsim y se tratan con la regla clásica, usando el '
                                 'k<sub>ij</sub> agua-hidrocarburo de la fila del agua de la '
                                 'ecuación activa (HYSYS o PVTsim). Todos los pares sin agua '
                                 '(hidrocarburo-hidrocarburo e inertes) usan igualmente la regla '
                                 'clásica, con la matriz k<sub>ij</sub> por defecto de la ecuación '
                                 'activa. Para estos pares la energía de interacción se construye '
                                 'de modo que la regla de Huron-Vidal reproduzca exactamente la '
                                 'regla cuadrática:',
                                 'The water pairs with nC7, nC8, and nC9 have α = 0 in the PVTsim '
                                 'database and are treated with the classical rule, using the '
                                 'water-hydrocarbon k<sub>ij</sub> from the water row of the '
                                 'active equation (HYSYS or PVTsim). All pairs without water '
                                 '(hydrocarbon-hydrocarbon and inerts) likewise use the classical '
                                 'rule, with the default k<sub>ij</sub> matrix of the active '
                                 'equation. For these pairs the interaction energy is built so '
                                 'that the Huron-Vidal rule exactly reproduces the quadratic '
                                 'rule:'),
                                ('eq',
                                 'g_{ii} = -\\lambda\\,\\frac{a_i}{b_i} \\qquad g_{ji} = '
                                 '-\\frac{2\\sqrt{b_i\\,b_j}}{b_i + '
                                 'b_j}\\,\\sqrt{g_{ii}\\,g_{jj}}\\,\\left(1 - k_{ij}\\right) '
                                 '\\qquad \\alpha_{ji} = 0'),
                                ('p',
                                 'donde a<sub>i</sub> y b<sub>i</sub> son los parámetros del '
                                 'componente i a la temperatura del sistema y k<sub>ij</sub> el '
                                 'coeficiente de interacción clásico del par.',
                                 'where a<sub>i</sub> and b<sub>i</sub> are the parameters of '
                                 'component i at the system temperature and k<sub>ij</sub> is the '
                                 'classical interaction coefficient of the pair.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('ul',
                                 [('La regla de Huron-Vidal se aplica en todos los cálculos con '
                                   'agua (flash trifásico, envolventes con agua, puntos de '
                                   'saturación con agua, hidratos, contenido de agua y análisis de '
                                   'sensibilidad), con cualquiera de las cuatro ecuaciones de '
                                   'estado; con las de HYSYS se aplica sobre las propiedades '
                                   'críticas y los k<sub>ij</sub> de HYSYS.',
                                   'The Huron-Vidal rule is applied in all water-containing '
                                   'calculations (three-phase flash, envelopes with water, '
                                   'saturation points with water, hydrates, water content, and '
                                   'sensitivity analysis), with any of the four equations of '
                                   'state; with the HYSYS equations it is applied on top of the '
                                   'HYSYS critical properties and k<sub>ij</sub>.'),
                                  ('Los parámetros G<sup>(0)</sup>, G<sup>(T)</sup> y α se toman '
                                   'de la tabla de PR o de SRK según la familia de la ecuación '
                                   'activa.',
                                   'The G<sup>(0)</sup>, G<sup>(T)</sup>, and α parameters are '
                                   'taken from the PR or SRK table according to the family of the '
                                   'active equation.'),
                                  ('En una fase sin agua, o cuando la fracción de agua es '
                                   'despreciable (≤ 10<sup>−12</sup>), la regla se reduce a la '
                                   'clásica y ThermoPhase evalúa directamente la forma cuadrática.',
                                   'In a water-free phase, or when the water fraction is '
                                   'negligible (≤ 10<sup>−12</sup>), the rule reduces to the '
                                   'classical one and ThermoPhase directly evaluates the quadratic '
                                   'form.'),
                                  ('La matriz τ y los factores exp(−α<sub>ji</sub>τ<sub>ji</sub>) '
                                   'dependen solo de la temperatura y se calculan una vez por '
                                   'temperatura.',
                                   'The τ matrix and the factors '
                                   'exp(−α<sub>ji</sub>τ<sub>ji</sub>) depend only on temperature '
                                   'and are computed once per temperature.')]),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Renon, H. y Prausnitz, J.M. (1968). Local compositions in '
                                 'thermodynamic excess functions for liquid mixtures. <em>AIChE '
                                 'Journal</em>, 14(1), 135–144.',
                                 'Renon, H. and Prausnitz, J.M. (1968). Local compositions in '
                                 'thermodynamic excess functions for liquid mixtures. <em>AIChE '
                                 'Journal</em>, 14(1), 135–144.'),
                                ('p',
                                 'Pedersen, K.S., Milter, J. y Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.',
                                 'Pedersen, K.S., Milter, J. and Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.'),
                                ('p',
                                 'Lindeloff, N. y Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.',
                                 'Lindeloff, N. and Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Reducción a la regla clásica y derivada para la fugacidad',
                               'Reduction to the classical rule and derivative for the fugacity'),
                    'bloques': [('p',
                                 'Con α<sub>ji</sub> = 0 y las energías de interacción de los '
                                 'pares clásicos, la energía de Gibbs de exceso de Huron-Vidal se '
                                 'reduce a una suma cuadrática y el parámetro a<sub>m</sub> '
                                 'coincide exactamente con el de la regla de van der Waals. Esta '
                                 'propiedad garantiza que, en una mezcla sin agua, el cálculo con '
                                 'agua reproduce los resultados de la regla clásica.',
                                 'With α<sub>ji</sub> = 0 and the interaction energies of the '
                                 'classical pairs, the Huron-Vidal excess Gibbs energy reduces to '
                                 'a quadratic sum and the a<sub>m</sub> parameter coincides '
                                 'exactly with that of the van der Waals rule. This property '
                                 'ensures that, in a water-free mixture, the water-containing '
                                 'calculation reproduces the results of the classical rule.'),
                                ('eq',
                                 'G^{E}_{\\infty} = \\frac{1}{b_m}\\sum_{i}\\sum_{j} '
                                 'x_i\\,x_j\\,b_j\\left(g_{ji} - g_{ii}\\right) \\quad (\\alpha = '
                                 '0)'),
                                ('eq',
                                 'a_m = \\sum_{i}\\sum_{j} x_i\\,x_j\\,\\frac{2\\,b_j}{b_i + '
                                 'b_j}\\sqrt{a_i\\,a_j}\\left(1 - k_{ij}\\right) = '
                                 '\\sum_{i}\\sum_{j} x_i\\,x_j\\,\\sqrt{a_i\\,a_j}\\left(1 - '
                                 'k_{ij}\\right)'),
                                ('p',
                                 'donde la segunda igualdad resulta de simetrizar la doble suma, '
                                 'ya que 2b<sub>j</sub>/(b<sub>i</sub> + b<sub>j</sub>) + '
                                 '2b<sub>i</sub>/(b<sub>i</sub> + b<sub>j</sub>) = 2. El factor λ '
                                 'incluido en g<sub>ii</sub> es el que hace exacta esta identidad.',
                                 'where the second equality results from symmetrizing the double '
                                 'sum, since 2b<sub>j</sub>/(b<sub>i</sub> + b<sub>j</sub>) + '
                                 '2b<sub>i</sub>/(b<sub>i</sub> + b<sub>j</sub>) = 2. The factor λ '
                                 'included in g<sub>ii</sub> is what makes this identity exact.'),
                                ('h3', 'Término de fugacidad', 'Fugacity term'),
                                ('p',
                                 'El coeficiente de fugacidad requiere el término ψ<sub>i</sub>, '
                                 'derivada parcial de n²a<sub>m</sub> respecto de n<sub>i</sub>. '
                                 'Con la regla de Huron-Vidal, ThermoPhase lo obtiene por '
                                 'derivación analítica:',
                                 'The fugacity coefficient requires the term ψ<sub>i</sub>, the '
                                 'partial derivative of n²a<sub>m</sub> with respect to '
                                 'n<sub>i</sub>. With the Huron-Vidal rule, ThermoPhase obtains it '
                                 'by analytical differentiation:'),
                                ('eq',
                                 'F = \\sum_{k} x_k\\,\\frac{a_k}{b_k} - '
                                 '\\frac{G^{E}_{\\infty}}{\\lambda} \\qquad a_m = b_m\\,F'),
                                ('eq',
                                 '\\psi_i = '
                                 '\\frac{1}{2}\\,\\frac{\\partial\\,(n^{2}a_m)}{\\partial n_i} = '
                                 '\\frac{1}{2}\\left[b_i\\,F + b_m\\left(\\frac{a_i}{b_i} - '
                                 '\\frac{1}{\\lambda}\\,\\frac{\\partial\\,(n\\,G^{E}_{\\infty})}{\\partial '
                                 'n_i}\\right)\\right]'),
                                ('eq',
                                 '\\frac{\\partial\\,(n\\,G^{E}_{\\infty}/RT)}{\\partial n_i} = '
                                 'S_i + \\sum_{k} x_k\\,\\frac{\\partial S_k}{\\partial x_i} '
                                 '\\qquad S_k = '
                                 '\\frac{\\sum_{j}\\tau_{jk}\\,b_j\\,x_j\\,E_{jk}}{\\sum_{j} '
                                 'b_j\\,x_j\\,E_{jk}}'),
                                ('p',
                                 'donde F es la función auxiliar de la regla, S<sub>k</sub> la '
                                 'contribución del componente k a G<sup>E</sup><sub>∞</sub>/(R·T), '
                                 'E<sub>jk</sub> = exp(−α<sub>jk</sub>τ<sub>jk</sub>) y n el '
                                 'número total de moles. El término ψ<sub>i</sub> así obtenido '
                                 'sustituye a Σ<sub>j</sub> x<sub>j</sub>a<sub>ij</sub> en las '
                                 'expresiones de ln φ<sub>i</sub> de PR y SRK, lo que mantiene la '
                                 'consistencia termodinámica entre la regla de mezcla y las '
                                 'fugacidades.',
                                 'where F is the auxiliary function of the rule, S<sub>k</sub> is '
                                 'the contribution of component k to '
                                 'G<sup>E</sup><sub>∞</sub>/(R·T), E<sub>jk</sub> = '
                                 'exp(−α<sub>jk</sub>τ<sub>jk</sub>), and n is the total number of '
                                 'moles. The term ψ<sub>i</sub> thus obtained replaces '
                                 'Σ<sub>j</sub> x<sub>j</sub>a<sub>ij</sub> in the PR and SRK ln '
                                 'φ<sub>i</sub> expressions, which maintains thermodynamic '
                                 'consistency between the mixing rule and the fugacities.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]}]},
 {'titulo': ('Equilibrio líquido-vapor', 'Vapor-liquid equilibrium'),
  'subsecciones': [{'titulo': ('Planteamiento del equilibrio de fases',
                               'Formulation of phase equilibrium'),
                    'bloques': [('p',
                                 'El cálculo flash isotérmico-isobárico (flash PT) determina, para '
                                 'una alimentación de composición global z a presión P y '
                                 'temperatura T fijas, el número de fases en equilibrio, la '
                                 'fracción molar de cada fase y la composición de cada una. En el '
                                 'caso líquido-vapor las incógnitas son la fracción molar de vapor '
                                 'β<sub>V</sub> (con β<sub>L</sub> = 1 − β<sub>V</sub>), las '
                                 'fracciones molares del vapor y<sub>i</sub> y las del líquido '
                                 'x<sub>i</sub>.',
                                 'The isothermal-isobaric flash (PT flash) determines, for a feed '
                                 'of overall composition z at fixed pressure P and temperature T, '
                                 'the number of phases at equilibrium, the mole fraction of each '
                                 'phase, and the composition of each one. In the vapor-liquid case '
                                 'the unknowns are the vapor mole fraction β<sub>V</sub> (with '
                                 'β<sub>L</sub> = 1 − β<sub>V</sub>), the vapor mole fractions '
                                 'y<sub>i</sub>, and the liquid mole fractions x<sub>i</sub>.'),
                                ('p',
                                 'La condición de equilibrio termodinámico a T y P constantes, '
                                 'obtenida de la minimización de la energía de Gibbs, exige la '
                                 'igualdad de la fugacidad de cada componente en todas las fases '
                                 'presentes:',
                                 'The thermodynamic equilibrium condition at constant T and P, '
                                 'obtained from the minimization of the Gibbs energy, requires '
                                 'equality of the fugacity of each component in all phases '
                                 'present:'),
                                ('eq', 'f_i^{\\,V} = f_i^{\\,L} \\quad (i = 1, \\ldots, N_c)'),
                                ('p',
                                 'donde f<sub>i</sub><sup>V</sup> y f<sub>i</sub><sup>L</sup> son '
                                 'las fugacidades del componente i en el vapor y en el líquido '
                                 '(psia) y N<sub>c</sub> es el número de componentes.',
                                 'where f<sub>i</sub><sup>V</sup> and f<sub>i</sub><sup>L</sup> '
                                 'are the fugacities of component i in the vapor and in the liquid '
                                 '(psia) and N<sub>c</sub> is the number of components.'),
                                ('p',
                                 'La fugacidad se expresa mediante el coeficiente de fugacidad, '
                                 'que la ecuación de estado cúbica proporciona en forma cerrada:',
                                 'The fugacity is expressed through the fugacity coefficient, '
                                 'which the cubic equation of state provides in closed form:'),
                                ('eq',
                                 'f_i^{\\,V} = \\phi_i^{\\,V}\\, y_i\\, P \\qquad f_i^{\\,L} = '
                                 '\\phi_i^{\\,L}\\, x_i\\, P'),
                                ('p',
                                 'donde φ<sub>i</sub><sup>V</sup> y φ<sub>i</sub><sup>L</sup> son '
                                 'los coeficientes de fugacidad (adimensionales) evaluados con la '
                                 'composición de cada fase según las expresiones de «Coeficiente '
                                 'de fugacidad»: la fase vapor con la raíz mayor de la cúbica y la '
                                 'fase líquida con la raíz menor mayor que B (véase «Forma cúbica '
                                 'en Z y su resolución»).',
                                 'where φ<sub>i</sub><sup>V</sup> and φ<sub>i</sub><sup>L</sup> '
                                 'are the (dimensionless) fugacity coefficients evaluated with the '
                                 'composition of each phase according to the expressions in '
                                 '“Fugacity coefficient”: the vapor phase with the largest root of '
                                 'the cubic and the liquid phase with the smallest root greater '
                                 'than B (see “Cubic form in Z and its solution”).'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Constantes de equilibrio y estimación inicial de Wilson',
                               'Equilibrium ratios and Wilson initial estimate'),
                    'bloques': [('p',
                                 'De la igualdad de fugacidades se obtiene la constante de '
                                 'equilibrio, o relación de reparto, de cada componente:',
                                 'From the equality of fugacities the equilibrium ratio, or '
                                 'K-value, of each component is obtained:'),
                                ('eq',
                                 'K_i = \\frac{y_i}{x_i} = \\frac{\\phi_i^{\\,L}}{\\phi_i^{\\,V}}'),
                                ('p',
                                 'donde K<sub>i</sub> es la constante de equilibrio del componente '
                                 'i (adimensional). Un valor K<sub>i</sub> &gt; 1 indica que el '
                                 'componente se concentra en el vapor (componentes livianos como '
                                 'N₂ o metano) y K<sub>i</sub> &lt; 1 que se concentra en el '
                                 'líquido (componentes pesados).',
                                 'where K<sub>i</sub> is the equilibrium ratio of component i '
                                 '(dimensionless). A value K<sub>i</sub> &gt; 1 indicates that the '
                                 'component concentrates in the vapor (light components such as N₂ '
                                 'or methane) and K<sub>i</sub> &lt; 1 that it concentrates in the '
                                 'liquid (heavy components).'),
                                ('p',
                                 'Los coeficientes de fugacidad dependen de las composiciones x e '
                                 'y, que a su vez dependen de las K<sub>i</sub>; el problema es '
                                 'implícito y se resuelve de forma iterativa a partir de una '
                                 'estimación inicial. ThermoPhase emplea la correlación de Wilson:',
                                 'The fugacity coefficients depend on the compositions x and y, '
                                 'which in turn depend on the K<sub>i</sub>; the problem is '
                                 'implicit and is solved iteratively from an initial estimate. '
                                 'ThermoPhase uses the Wilson correlation:'),
                                ('eq',
                                 'K_i^{W} = '
                                 '\\frac{P_{c,i}}{P}\\,\\exp\\left[\\,5.373\\,(1+\\omega_i)\\left(1-\\frac{T_{c,i}}{T}\\right)\\right]'),
                                ('p',
                                 'donde P<sub>c,i</sub> es la presión crítica (psia), '
                                 'T<sub>c,i</sub> la temperatura crítica (°R) y ω<sub>i</sub> el '
                                 'factor acéntrico del componente i; P y T son la presión (psia) y '
                                 'la temperatura (°R) del sistema.',
                                 'where P<sub>c,i</sub> is the critical pressure (psia), '
                                 'T<sub>c,i</sub> the critical temperature (°R) and ω<sub>i</sub> '
                                 'the acentric factor of component i; P and T are the system '
                                 'pressure (psia) and temperature (°R).'),
                                ('p',
                                 'La correlación de Wilson se basa en la aproximación de solución '
                                 'ideal y en una presión de vapor tipo Clausius-Clapeyron ajustada '
                                 'al punto crítico y al factor acéntrico. Ubica a cada componente '
                                 'del lado correcto de la unidad y proporciona un arranque '
                                 'estable, aunque no reproduce la no idealidad de las fases.',
                                 'The Wilson correlation is based on the ideal-solution '
                                 'approximation and on a Clausius-Clapeyron type vapor pressure '
                                 'fitted to the critical point and the acentric factor. It places '
                                 'each component on the correct side of unity and provides a '
                                 'stable start, although it does not reproduce the non-ideality of '
                                 'the phases.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'En el flash de hidrocarburos, los valores de Wilson se calculan '
                                 'con las propiedades críticas y los factores acéntricos de la '
                                 'base de componentes de HYSYS para todas las variantes de '
                                 'ecuación de estado, dado que solo constituyen el punto de '
                                 'partida. Sirven como semilla de los dos juegos de constantes del '
                                 'análisis de estabilidad y, cuando dicho análisis declara estable '
                                 'la mezcla, también como valores iniciales del flash. En el flash '
                                 'trifásico, la estimación de Wilson usa las propiedades de los 14 '
                                 'componentes de la ecuación de estado seleccionada.',
                                 'In the hydrocarbon flash, the Wilson values are computed with '
                                 'the critical properties and acentric factors of the HYSYS '
                                 'component database for all equation-of-state variants, since '
                                 'they are only the starting point. They seed the two sets of '
                                 'ratios of the stability analysis and, when that analysis '
                                 'declares the mixture stable, also serve as the initial values of '
                                 'the flash. In the three-phase flash, the Wilson estimate uses '
                                 'the properties of the 14 components of the selected equation of '
                                 'state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Ecuación de Rachford-Rice', 'Rachford-Rice equation'),
                    'bloques': [('p',
                                 'Dado un conjunto de constantes de equilibrio, la fracción de '
                                 'vapor se obtiene del balance de materia por componente:',
                                 'For a given set of equilibrium ratios, the vapor fraction is '
                                 'obtained from the component material balance:'),
                                ('eq', 'z_i = \\beta\\,y_i + (1-\\beta)\\,x_i'),
                                ('p',
                                 'donde z<sub>i</sub> es la fracción molar del componente i en la '
                                 'alimentación y β la fracción molar de vapor.',
                                 'where z<sub>i</sub> is the mole fraction of component i in the '
                                 'feed and β is the vapor mole fraction.'),
                                ('p',
                                 'Al sustituir y<sub>i</sub> = K<sub>i</sub>x<sub>i</sub> y exigir '
                                 'que las fracciones de ambas fases sumen la unidad '
                                 '(Σy<sub>i</sub> − Σx<sub>i</sub> = 0) se obtiene la ecuación de '
                                 'Rachford-Rice, con β como única incógnita:',
                                 'Substituting y<sub>i</sub> = K<sub>i</sub>x<sub>i</sub> and '
                                 'requiring the fractions of both phases to add up to unity '
                                 '(Σy<sub>i</sub> − Σx<sub>i</sub> = 0) yields the Rachford-Rice '
                                 'equation, with β as the only unknown:'),
                                ('eq',
                                 'g(\\beta) = \\sum_{i} \\frac{z_i\\,(K_i-1)}{1+\\beta\\,(K_i-1)} '
                                 '= 0'),
                                ('p',
                                 'donde g(β) es la función de Rachford-Rice (adimensional).',
                                 'where g(β) is the Rachford-Rice function (dimensionless).'),
                                ('p',
                                 'La derivada de g es negativa para cualquier β entre los polos de '
                                 'la función, por lo que g es estrictamente decreciente y la raíz '
                                 'es única en ese intervalo:',
                                 'The derivative of g is negative for any β between the poles of '
                                 'the function, so g is strictly decreasing and the root is unique '
                                 'in that interval:'),
                                ('eq',
                                 "g'(\\beta) = -\\sum_{i} "
                                 '\\frac{z_i\\,(K_i-1)^2}{\\left[1+\\beta\\,(K_i-1)\\right]^2} < '
                                 '0'),
                                ('p',
                                 "donde g'(β) es la derivada de g respecto de β. Como g(0) = "
                                 'Σz<sub>i</sub>K<sub>i</sub> − 1 y g(1) = 1 − '
                                 'Σz<sub>i</sub>/K<sub>i</sub>, existe una raíz en el intervalo '
                                 'físico 0 &lt; β &lt; 1 si y solo si Σz<sub>i</sub>K<sub>i</sub> '
                                 '&gt; 1 y Σz<sub>i</sub>/K<sub>i</sub> &gt; 1.',
                                 "where g'(β) is the derivative of g with respect to β. Since g(0) "
                                 '= Σz<sub>i</sub>K<sub>i</sub> − 1 and g(1) = 1 − '
                                 'Σz<sub>i</sub>/K<sub>i</sub>, a root exists in the physical '
                                 'interval 0 &lt; β &lt; 1 if and only if '
                                 'Σz<sub>i</sub>K<sub>i</sub> &gt; 1 and '
                                 'Σz<sub>i</sub>/K<sub>i</sub> &gt; 1.'),
                                ('p',
                                 'Una vez resuelta β, las composiciones de fase se obtienen de '
                                 'forma explícita:',
                                 'Once β is solved, the phase compositions are obtained '
                                 'explicitly:'),
                                ('eq',
                                 'x_i = \\frac{z_i}{1+\\beta\\,(K_i-1)} \\qquad y_i = K_i\\,x_i'),
                                ('p',
                                 'donde x<sub>i</sub> e y<sub>i</sub> son las fracciones molares '
                                 'del líquido y del vapor.',
                                 'where x<sub>i</sub> and y<sub>i</sub> are the liquid and vapor '
                                 'mole fractions.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'ThermoPhase resuelve la ecuación de Rachford-Rice por el método '
                                 'de Newton acotado. El intervalo de búsqueda se delimita con los '
                                 'polos 1/(1 − K<sub>i</sub>) de la función y con los límites '
                                 'físicos 0 y 1, con márgenes de 10⁻¹⁰; la iteración parte del '
                                 'punto medio del intervalo y, si un paso de Newton sale de él, el '
                                 'nuevo valor se toma como el punto medio entre el valor actual y '
                                 'el límite correspondiente. La convergencia se declara cuando '
                                 '|Δβ| &lt; 10⁻¹⁴, con un máximo de 500 iteraciones. Si todas las '
                                 'constantes son iguales a la unidad, la ecuación es indeterminada '
                                 'y se devuelve β = 0.5. En el flash bifásico, β se restringe '
                                 'finalmente al intervalo [10⁻¹⁰, 1 − 10⁻¹⁰].',
                                 'ThermoPhase solves the Rachford-Rice equation by a bounded '
                                 'Newton method. The search interval is delimited by the poles '
                                 '1/(1 − K<sub>i</sub>) of the function and by the physical limits '
                                 '0 and 1, with margins of 10⁻¹⁰; the iteration starts at the '
                                 'midpoint of the interval and, if a Newton step leaves it, the '
                                 'new value is taken as the midpoint between the current value and '
                                 'the corresponding bound. Convergence is declared when |Δβ| &lt; '
                                 '10⁻¹⁴, with a maximum of 500 iterations. If all ratios equal '
                                 'unity, the equation is indeterminate and β = 0.5 is returned. In '
                                 'the two-phase flash, β is finally restricted to the interval '
                                 '[10⁻¹⁰, 1 − 10⁻¹⁰].'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Rachford, H.H. y Rice, J.D. (1952). Procedure for use of '
                                 'electronic digital computers in calculating flash vaporization '
                                 'hydrocarbon equilibrium. <em>Journal of Petroleum '
                                 'Technology</em>, 4(10), 19 (sección 1) y 3 (sección 2).',
                                 'Rachford, H.H. and Rice, J.D. (1952). Procedure for use of '
                                 'electronic digital computers in calculating flash vaporization '
                                 'hydrocarbon equilibrium. <em>Journal of Petroleum '
                                 'Technology</em>, 4(10), 19 (section 1) and 3 (section 2).'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Análisis de estabilidad de Michelsen',
                               'Michelsen stability analysis'),
                    'bloques': [('p',
                                 'El análisis de estabilidad determina si la alimentación, tratada '
                                 'como una sola fase, es termodinámicamente estable o si se separa '
                                 'en dos fases. Se basa en el criterio del plano tangente a la '
                                 'superficie de energía de Gibbs: la fase de composición z es '
                                 'estable si ninguna fase de prueba de composición W tiene una '
                                 'distancia al plano tangente negativa.',
                                 'The stability analysis determines whether the feed, treated as a '
                                 'single phase, is thermodynamically stable or splits into two '
                                 'phases. It is based on the tangent plane criterion applied to '
                                 'the Gibbs energy surface: the phase of composition z is stable '
                                 'if no trial phase of composition W has a negative tangent plane '
                                 'distance.'),
                                ('p',
                                 'En la forma modificada de Michelsen, con W<sub>i</sub> expresado '
                                 'en moles no normalizados, la distancia al plano tangente es:',
                                 "In Michelsen's modified form, with W<sub>i</sub> expressed as "
                                 'non-normalized moles, the tangent plane distance is:'),
                                ('eq',
                                 'tm(W) = 1 + \\sum_i W_i\\left[\\ln W_i + \\ln\\phi_i(W) - d_i - '
                                 '1\\right]'),
                                ('eq', 'd_i = \\ln z_i + \\ln\\phi_i(z)'),
                                ('p',
                                 'donde tm es la distancia al plano tangente modificada '
                                 '(adimensional), W<sub>i</sub> los moles del componente i en la '
                                 'fase de prueba, φ<sub>i</sub>(W) y φ<sub>i</sub>(z) los '
                                 'coeficientes de fugacidad de la fase de prueba y de la '
                                 'alimentación, y d<sub>i</sub> el potencial químico reducido de '
                                 'referencia.',
                                 'where tm is the modified tangent plane distance (dimensionless), '
                                 'W<sub>i</sub> the moles of component i in the trial phase, '
                                 'φ<sub>i</sub>(W) and φ<sub>i</sub>(z) the fugacity coefficients '
                                 'of the trial phase and of the feed, and d<sub>i</sub> the '
                                 'reference reduced chemical potential.'),
                                ('p',
                                 'En un punto estacionario ln W<sub>i</sub> + ln φ<sub>i</sub>(W) '
                                 '= d<sub>i</sub> y la distancia se reduce a tm = 1 − '
                                 'ΣW<sub>i</sub>. La mezcla es inestable si en algún punto '
                                 'estacionario ΣW<sub>i</sub> &gt; 1.',
                                 'At a stationary point ln W<sub>i</sub> + ln φ<sub>i</sub>(W) = '
                                 'd<sub>i</sub> and the distance reduces to tm = 1 − '
                                 'ΣW<sub>i</sub>. The mixture is unstable if ΣW<sub>i</sub> &gt; 1 '
                                 'at some stationary point.'),
                                ('h3', 'Pruebas de vapor y de líquido', 'Vapor and liquid tests'),
                                ('p',
                                 'ThermoPhase realiza dos búsquedas simultáneas, una con una fase '
                                 'de prueba de tipo vapor y otra con una de tipo líquido, ambas '
                                 'inicializadas con los valores de Wilson. Las fases de prueba se '
                                 'construyen como:',
                                 'ThermoPhase performs two simultaneous searches, one with a '
                                 'vapor-like trial phase and another with a liquid-like trial '
                                 'phase, both initialized with the Wilson values. The trial phases '
                                 'are constructed as:'),
                                ('eq',
                                 'W_i^{V} = z_i\\,K_i^{V} \\qquad W_i^{L} = \\frac{z_i}{K_i^{L}}'),
                                ('eq',
                                 'S_V = \\sum_i z_i\\,K_i^{V} \\qquad S_L = \\sum_i '
                                 '\\frac{z_i}{K_i^{L}} \\qquad Y_i^{V} = \\frac{W_i^{V}}{S_V} '
                                 '\\qquad Y_i^{L} = \\frac{W_i^{L}}{S_L}'),
                                ('p',
                                 'donde K<sub>i</sub><sup>V</sup> y K<sub>i</sub><sup>L</sup> son '
                                 'las constantes de las pruebas de vapor y de líquido, '
                                 'S<sub>V</sub> y S<sub>L</sub> los moles totales de las fases de '
                                 'prueba e Y<sub>i</sub><sup>V</sup>, Y<sub>i</sub><sup>L</sup> '
                                 'sus composiciones normalizadas.',
                                 'where K<sub>i</sub><sup>V</sup> and K<sub>i</sub><sup>L</sup> '
                                 'are the ratios of the vapor and liquid tests, S<sub>V</sub> and '
                                 'S<sub>L</sub> the total moles of the trial phases and '
                                 'Y<sub>i</sub><sup>V</sup>, Y<sub>i</sub><sup>L</sup> their '
                                 'normalized compositions.'),
                                ('p',
                                 'La fase de prueba de vapor se evalúa con la raíz de vapor y la '
                                 'de líquido con la raíz de líquido; la alimentación se evalúa con '
                                 'la raíz de vapor para la prueba de vapor y con la raíz de '
                                 'líquido para la prueba de líquido. Las constantes se actualizan '
                                 'por sustitución sucesiva:',
                                 'The vapor trial phase is evaluated with the vapor root and the '
                                 'liquid trial phase with the liquid root; the feed is evaluated '
                                 'with the vapor root for the vapor test and with the liquid root '
                                 'for the liquid test. The ratios are updated by successive '
                                 'substitution:'),
                                ('eq',
                                 'K_i^{V} \\leftarrow \\frac{\\phi_i^{V}(z)}{\\phi_i^{V}(Y^{V})} '
                                 '\\qquad K_i^{L} \\leftarrow '
                                 '\\frac{\\phi_i^{L}(Y^{L})}{\\phi_i^{L}(z)}'),
                                ('p',
                                 'donde los superíndices V y L de φ indican la raíz empleada. En '
                                 'la formulación de ThermoPhase esta actualización se escribe como '
                                 'el cociente de fugacidades normalizado por S<sub>V</sub> o '
                                 'S<sub>L</sub>, que es algebraicamente idéntico; la normalización '
                                 'hace que, en un sistema monofásico, las constantes converjan de '
                                 'forma controlada a la solución trivial (K<sub>i</sub> → 1).',
                                 'where the superscripts V and L of φ indicate the root used. In '
                                 'the ThermoPhase formulation this update is written as the '
                                 'fugacity ratio normalized by S<sub>V</sub> or S<sub>L</sub>, '
                                 'which is algebraically identical; the normalization makes the '
                                 'ratios converge in a controlled manner to the trivial solution '
                                 '(K<sub>i</sub> → 1) in a single-phase system.'),
                                ('p',
                                 'La iteración termina cuando las sumas de los residuos al '
                                 'cuadrado de ambas pruebas son menores que 10⁻¹² o al cumplirse '
                                 '1000 iteraciones:',
                                 'The iteration ends when the sums of squared residuals of both '
                                 'tests are below 10⁻¹² or after 1000 iterations:'),
                                ('eq',
                                 '\\sum_i \\left[\\ln\\frac{f_i(Y)}{f_i(z)}\\right]^{2} \\leq '
                                 '10^{-12}'),
                                ('p',
                                 'donde f<sub>i</sub>(Y) y f<sub>i</sub>(z) son las fugacidades de '
                                 'la fase de prueba y de la alimentación (psia).',
                                 'where f<sub>i</sub>(Y) and f<sub>i</sub>(z) are the fugacities '
                                 'of the trial phase and of the feed (psia).'),
                                ('h3', 'Criterios de decisión', 'Decision criteria'),
                                ('p',
                                 'La mezcla se declara inestable si S<sub>V</sub> &gt; 1 + 10⁻⁴ o '
                                 'S<sub>L</sub> &gt; 1 + 10⁻⁴. En ese caso las constantes con que '
                                 'arranca el flash son el producto de los dos juegos refinados, '
                                 'que constituye una estimación mucho más próxima a la solución '
                                 'que la de Wilson:',
                                 'The mixture is declared unstable if S<sub>V</sub> &gt; 1 + 10⁻⁴ '
                                 'or S<sub>L</sub> &gt; 1 + 10⁻⁴. In that case the flash starts '
                                 'from the product of the two refined sets, which is a much closer '
                                 'estimate of the solution than the Wilson values:'),
                                ('eq', 'K_i^{\\mathrm{flash}} = K_i^{V}\\,K_i^{L}'),
                                ('p',
                                 'donde K<sub>i</sub><sup>flash</sup> es la constante de '
                                 'equilibrio inicial del flash. Si la mezcla es estable, el flash '
                                 'arranca con los valores de Wilson. Para caracterizar el '
                                 'resultado estable se evalúa además la proximidad a la solución '
                                 'trivial, considerando solo los componentes presentes '
                                 '(z<sub>i</sub> &gt; 0):',
                                 'where K<sub>i</sub><sup>flash</sup> is the initial equilibrium '
                                 'ratio of the flash. If the mixture is stable, the flash starts '
                                 'with the Wilson values. To characterize the stable result, the '
                                 'proximity to the trivial solution is also evaluated, considering '
                                 'only the components present (z<sub>i</sub> &gt; 0):'),
                                ('eq',
                                 '\\sum_{i:\\,z_i > 0} \\left(\\ln K_i\\right)^{2} < 10^{-4}'),
                                ('p',
                                 'donde K<sub>i</sub> es la constante de la prueba de vapor o de '
                                 'líquido; una prueba que cumple esta condición ha convergido a la '
                                 'solución trivial. Con este criterio el resultado estable se '
                                 'clasifica como alejado de la región bifásica (ambas pruebas '
                                 'triviales), con tendencia a vapor (solo la prueba de vapor '
                                 'trivial), con tendencia a líquido (solo la prueba de líquido '
                                 'trivial) o de fase indeterminada. Esta clasificación es '
                                 'informativa: en todos los casos se ejecuta a continuación el '
                                 'flash, que establece el número de fases definitivo.',
                                 'where K<sub>i</sub> is the ratio of the vapor or liquid test; a '
                                 'test that satisfies this condition has converged to the trivial '
                                 'solution. With this criterion the stable result is classified as '
                                 'far from the two-phase region (both tests trivial), tending to '
                                 'vapor (only the vapor test trivial), tending to liquid (only the '
                                 'liquid test trivial) or of indeterminate phase. This '
                                 'classification is informative: in all cases the flash is run '
                                 'next and establishes the final number of phases.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.'),
                                ('p',
                                 'Baker, L.E., Pierce, A.C. y Luks, K.D. (1982). Gibbs energy '
                                 'analysis of phase equilibria. <em>Society of Petroleum Engineers '
                                 'Journal</em>, 22(5), 731–742.',
                                 'Baker, L.E., Pierce, A.C. and Luks, K.D. (1982). Gibbs energy '
                                 'analysis of phase equilibria. <em>Society of Petroleum Engineers '
                                 'Journal</em>, 22(5), 731–742.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Algoritmo del flash PT', 'PT flash algorithm'),
                    'bloques': [('p',
                                 'El flash PT de hidrocarburos de ThermoPhase combina el análisis '
                                 'de estabilidad con un esquema de sustitución sucesiva del tipo '
                                 'Muskat-McDowell, en el que las constantes de equilibrio se '
                                 'actualizan con los coeficientes de fugacidad de la ecuación de '
                                 'estado hasta igualar las fugacidades de ambas fases. La ecuación '
                                 'de Rachford-Rice actúa como subproblema interno para el balance '
                                 'de materia en cada iteración.',
                                 'The ThermoPhase hydrocarbon PT flash combines the stability '
                                 'analysis with a Muskat-McDowell type successive substitution '
                                 'scheme, in which the equilibrium ratios are updated with the '
                                 'fugacity coefficients of the equation of state until the '
                                 'fugacities of both phases are equal. The Rachford-Rice equation '
                                 'acts as an inner subproblem for the material balance at each '
                                 'iteration.'),
                                ('h3', 'Secuencia de cálculo', 'Calculation sequence'),
                                ('ul',
                                 [('Análisis de estabilidad de la alimentación y selección de las '
                                   'constantes iniciales: '
                                   'K<sub>i</sub><sup>V</sup>·K<sub>i</sub><sup>L</sup> si la '
                                   'mezcla es inestable, valores de Wilson si es estable. El flash '
                                   'se ejecuta siempre.',
                                   'Stability analysis of the feed and selection of the initial '
                                   'ratios: K<sub>i</sub><sup>V</sup>·K<sub>i</sub><sup>L</sup> if '
                                   'the mixture is unstable, Wilson values if it is stable. The '
                                   'flash is always run.'),
                                  ('Prueba de fase con las constantes vigentes: si '
                                   'Σz<sub>i</sub>K<sub>i</sub> ≤ 1 la mezcla es líquido (x = z, '
                                   'β<sub>V</sub> = 0); si Σz<sub>i</sub>/K<sub>i</sub> ≤ 1 es '
                                   'vapor (y = z, β<sub>V</sub> = 1); en otro caso es bifásica.',
                                   'Phase test with the current ratios: if '
                                   'Σz<sub>i</sub>K<sub>i</sub> ≤ 1 the mixture is liquid (x = z, '
                                   'β<sub>V</sub> = 0); if Σz<sub>i</sub>/K<sub>i</sub> ≤ 1 it is '
                                   'vapor (y = z, β<sub>V</sub> = 1); otherwise it is two-phase.'),
                                  ('En el caso bifásico, resolución de Rachford-Rice para '
                                   'β<sub>V</sub> y cálculo de x e y.',
                                   'In the two-phase case, solution of Rachford-Rice for '
                                   'β<sub>V</sub> and calculation of x and y.'),
                                  ('Cálculo de los coeficientes de fugacidad de cada fase con su '
                                   'composición normalizada y su raíz (mayor raíz para el vapor, '
                                   'menor raíz para el líquido).',
                                   'Calculation of the fugacity coefficients of each phase with '
                                   'its normalized composition and its root (largest root for the '
                                   'vapor, smallest root for the liquid).'),
                                  ('Evaluación del residuo de fugacidades y actualización de las '
                                   'constantes K<sub>i</sub> = '
                                   'φ<sub>i</sub><sup>L</sup>/φ<sub>i</sub><sup>V</sup>, limitadas '
                                   'al intervalo [10⁻²⁰, 10²⁰].',
                                   'Evaluation of the fugacity residual and update of the ratios '
                                   'K<sub>i</sub> = '
                                   'φ<sub>i</sub><sup>L</sup>/φ<sub>i</sub><sup>V</sup>, bounded '
                                   'to the interval [10⁻²⁰, 10²⁰].')]),
                                ('p',
                                 'La prueba de fase del segundo paso equivale a los signos de g(0) '
                                 'y g(1) de la función de Rachford-Rice: la solución bifásica '
                                 'existe solo cuando ambas sumas superan la unidad. La prueba se '
                                 'repite en cada iteración, de modo que la clasificación en una o '
                                 'dos fases se actualiza a medida que las constantes convergen.',
                                 'The phase test of the second step is equivalent to the signs of '
                                 'g(0) and g(1) of the Rachford-Rice function: the two-phase '
                                 'solution exists only when both sums exceed unity. The test is '
                                 'repeated at each iteration, so the one- or two-phase '
                                 'classification is updated as the ratios converge.'),
                                ('h3', 'Fases evanescentes', 'Vanishing phases'),
                                ('p',
                                 'Cuando la mezcla se clasifica como monofásica, la fase ausente '
                                 'tiene composición nula y sus parámetros A y B son cero; su '
                                 'coeficiente de fugacidad se fija en φ<sub>i</sub> = 1 para todos '
                                 'los componentes, en lugar de evaluarse con la composición de la '
                                 'fase presente. Las constantes resultan K<sub>i</sub> = '
                                 'φ<sub>i</sub><sup>L</sup>(z) si falta el vapor y K<sub>i</sub> = '
                                 '1/φ<sub>i</sub><sup>V</sup>(z) si falta el líquido; así no '
                                 'colapsan a la solución trivial y las sumas de la prueba de fase '
                                 'comparan la suma de las fugacidades de la alimentación con la '
                                 'presión del sistema:',
                                 'When the mixture is classified as single-phase, the absent phase '
                                 'has zero composition and its parameters A and B are zero; its '
                                 'fugacity coefficient is set to φ<sub>i</sub> = 1 for all '
                                 'components, instead of being evaluated with the composition of '
                                 'the phase present. The ratios become K<sub>i</sub> = '
                                 'φ<sub>i</sub><sup>L</sup>(z) if the vapor is absent and '
                                 'K<sub>i</sub> = 1/φ<sub>i</sub><sup>V</sup>(z) if the liquid is '
                                 'absent; they therefore do not collapse to the trivial solution, '
                                 'and the sums of the phase test compare the sum of the feed '
                                 'fugacities with the system pressure:'),
                                ('eq',
                                 '\\sum_i z_i\\,\\phi_i^{L}(z) = \\frac{1}{P}\\sum_i f_i^{L}(z) '
                                 '\\leq 1 \\;\\Rightarrow\\; \\mathrm{L}'),
                                ('p',
                                 'donde f<sub>i</sub><sup>L</sup>(z) es la fugacidad del '
                                 'componente i en la alimentación evaluada con la raíz de líquido '
                                 '(psia) y L indica fase líquida. La condición análoga para el '
                                 'vapor utiliza Σz<sub>i</sub>/φ<sub>i</sub><sup>V</sup>(z) ≤ 1.',
                                 'where f<sub>i</sub><sup>L</sup>(z) is the fugacity of component '
                                 'i in the feed evaluated with the liquid root (psia) and L '
                                 'denotes the liquid phase. The analogous condition for the vapor '
                                 'uses Σz<sub>i</sub>/φ<sub>i</sub><sup>V</sup>(z) ≤ 1.'),
                                ('h3', 'Criterio de convergencia', 'Convergence criterion'),
                                ('p',
                                 'El residuo de cada iteración es el máximo, sobre los componentes '
                                 'con fugacidad no nula en ambas fases, del logaritmo del cociente '
                                 'de fugacidades:',
                                 'The residual of each iteration is the maximum, over the '
                                 'components with non-zero fugacity in both phases, of the '
                                 'logarithm of the fugacity ratio:'),
                                ('eq',
                                 '\\varepsilon = \\max_i '
                                 '\\left|\\ln\\frac{f_i^{\\,L}}{f_i^{\\,V}}\\right|'),
                                ('p',
                                 'donde ε es el residuo de igualdad de fugacidades (adimensional). '
                                 'ThermoPhase declara la convergencia cuando ε ≤ 10⁻¹⁶ (en la '
                                 'práctica, la precisión de máquina) y se han completado al menos '
                                 'seis iteraciones, con un máximo de 1000 iteraciones. En los '
                                 'casos monofásicos el residuo es nulo por definición y la '
                                 'iteración termina tras el mínimo de iteraciones, una vez '
                                 'estabilizada la prueba de fase. El esquema es de sustitución '
                                 'sucesiva sin aceleración; la calidad de las constantes iniciales '
                                 'provenientes del análisis de estabilidad compensa la '
                                 'convergencia lenta propia de la sustitución sucesiva en las '
                                 'proximidades del punto crítico.',
                                 'where ε is the fugacity equality residual (dimensionless). '
                                 'ThermoPhase declares convergence when ε ≤ 10⁻¹⁶ (in practice, '
                                 'machine precision) and at least six iterations have been '
                                 'completed, with a maximum of 1000 iterations. In the '
                                 'single-phase cases the residual is zero by definition and the '
                                 'iteration ends after the minimum number of iterations, once the '
                                 'phase test has settled. The scheme is successive substitution '
                                 'without acceleration; the quality of the initial ratios coming '
                                 'from the stability analysis compensates for the slow convergence '
                                 'typical of successive substitution in the vicinity of the '
                                 'critical point.'),
                                ('h3',
                                 'Tratamiento posterior del resultado',
                                 'Post-processing of the result'),
                                ('p',
                                 'Si el flash converge a una sola fase y la ecuación de estado '
                                 'evaluada con la composición global tiene una sola raíz real, la '
                                 'etiqueta de la fase se determina con el criterio de HYSYS o de '
                                 'PVTsim según la variante de ecuación de estado activa; si '
                                 'converge a dos fases y el vapor resulta con mayor peso molecular '
                                 'que el líquido, las etiquetas de las fases se intercambian. '
                                 'Ambos tratamientos se describen en el capítulo «Identificación '
                                 'de fases».',
                                 'If the flash converges to a single phase and the equation of '
                                 'state evaluated with the overall composition has a single real '
                                 'root, the phase label is determined with the HYSYS or PVTsim '
                                 'criterion according to the active equation-of-state variant; if '
                                 'it converges to two phases and the vapor has a higher molecular '
                                 'weight than the liquid, the phase labels are swapped. Both '
                                 'treatments are described in the “Phase identification” chapter.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Muskat, M. y McDowell, J.M. (1949). An electrical computer for '
                                 'solving phase equilibrium problems. <em>Transactions of the '
                                 'AIME</em>, 186, 291–298.',
                                 'Muskat, M. and McDowell, J.M. (1949). An electrical computer for '
                                 'solving phase equilibrium problems. <em>Transactions of the '
                                 'AIME</em>, 186, 291–298.'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part II. '
                                 'Phase-split calculation. <em>Fluid Phase Equilibria</em>, 9(1), '
                                 '21–40.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part II. '
                                 'Phase-split calculation. <em>Fluid Phase Equilibria</em>, 9(1), '
                                 '21–40.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Fracciones másicas y propiedades de las fases',
                               'Phase mass fractions and properties'),
                    'bloques': [('p',
                                 'El flash produce las fracciones molares de fase β<sub>V</sub> y '
                                 'β<sub>L</sub>. Para la presentación de resultados y el cálculo '
                                 'de propiedades se obtienen además los pesos moleculares de cada '
                                 'fase y las fracciones másicas de fase.',
                                 'The flash yields the phase mole fractions β<sub>V</sub> and '
                                 'β<sub>L</sub>. For the presentation of results and the '
                                 'calculation of properties, the molecular weight of each phase '
                                 'and the phase mass fractions are also obtained.'),
                                ('eq',
                                 'M_V = \\sum_i y_i\\,M_i \\qquad M_L = \\sum_i x_i\\,M_i \\qquad '
                                 'M_z = \\sum_i z_i\\,M_i'),
                                ('p',
                                 'donde M<sub>V</sub>, M<sub>L</sub> y M<sub>z</sub> son los pesos '
                                 'moleculares del vapor, del líquido y de la alimentación '
                                 '(lb/lbmol) y M<sub>i</sub> el peso molecular del componente i, '
                                 'tomado de la base de datos de la ecuación de estado activa '
                                 '(HYSYS o PVTsim).',
                                 'where M<sub>V</sub>, M<sub>L</sub> and M<sub>z</sub> are the '
                                 'molecular weights of the vapor, the liquid and the feed '
                                 '(lb/lbmol) and M<sub>i</sub> the molecular weight of component '
                                 'i, taken from the database of the active equation of state '
                                 '(HYSYS or PVTsim).'),
                                ('eq',
                                 'w_V = \\frac{\\beta_V\\,M_V}{\\beta_V\\,M_V + \\beta_L\\,M_L} '
                                 '\\qquad w_L = \\frac{\\beta_L\\,M_L}{\\beta_V\\,M_V + '
                                 '\\beta_L\\,M_L}'),
                                ('p',
                                 'donde w<sub>V</sub> y w<sub>L</sub> son las fracciones másicas '
                                 'de vapor y de líquido (adimensionales). Se calculan después del '
                                 'eventual intercambio de etiquetas de fase, con los valores '
                                 'definitivos de β<sub>V</sub>, β<sub>L</sub> y de las '
                                 'composiciones.',
                                 'where w<sub>V</sub> and w<sub>L</sub> are the vapor and liquid '
                                 'mass fractions (dimensionless). They are computed after any swap '
                                 'of phase labels, with the final values of β<sub>V</sub>, '
                                 'β<sub>L</sub>, and the compositions.'),
                                ('p',
                                 'La densidad, la viscosidad y las demás propiedades de cada fase '
                                 'se calculan a continuación con los métodos descritos en los '
                                 'capítulos «Propiedades volumétricas», «Entalpía y entropía» y '
                                 '«Viscosidad».',
                                 'The density, viscosity, and other properties of each phase are '
                                 'then computed with the methods described in the “Volumetric '
                                 'properties”, “Enthalpy and entropy”, and “Viscosity” chapters.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]}]},
 {'titulo': ('Flash trifásico con agua', 'Three-phase flash with water'),
  'subsecciones': [{'titulo': ('Ámbito de aplicación', 'Scope'),
                    'bloques': [('p',
                                 'Las mezclas de hidrocarburos con agua pueden formar hasta tres '
                                 'fases en equilibrio: vapor, líquido de hidrocarburos y fase '
                                 'acuosa. La baja solubilidad mutua entre el agua y los '
                                 'hidrocarburos exige un tratamiento multifásico y una regla de '
                                 'mezcla capaz de representar la fuerte no idealidad de los pares '
                                 'agua-hidrocarburo.',
                                 'Mixtures of hydrocarbons and water can form up to three phases '
                                 'at equilibrium: vapor, hydrocarbon liquid and aqueous phase. The '
                                 'low mutual solubility between water and hydrocarbons requires a '
                                 'multiphase treatment and a mixing rule capable of representing '
                                 'the strong non-ideality of water-hydrocarbon pairs.'),
                                ('p',
                                 'ThermoPhase emplea el flash trifásico cuando el componente agua '
                                 'está activo en la definición del fluido y su fracción molar en '
                                 'la alimentación es mayor que 10⁻¹². En cualquier otro caso se '
                                 'ejecuta el flash líquido-vapor de hidrocarburos de 13 '
                                 'componentes descrito en el capítulo «Equilibrio líquido-vapor», '
                                 'que es independiente del flash trifásico.',
                                 'ThermoPhase uses the three-phase flash when the water component '
                                 'is active in the fluid definition and its mole fraction in the '
                                 'feed is greater than 10⁻¹². In any other case the 13-component '
                                 'hydrocarbon vapor-liquid flash described in the “Vapor-liquid '
                                 'equilibrium” chapter is run, which is independent of the '
                                 'three-phase flash.'),
                                ('p',
                                 'El procedimiento es el mismo para las cuatro variantes de '
                                 'ecuación de estado (PR y SRK con base HYSYS, PR y SRK con base '
                                 'PVTsim): la regla de mezcla de Huron-Vidal para los pares del '
                                 'agua con N₂ hasta n-hexano y la regla clásica para los demás '
                                 'pares, que es la combinación empleada por PVTsim. Cada familia '
                                 'conserva sus propias propiedades de componente y sus '
                                 'coeficientes de interacción binaria.',
                                 'The procedure is the same for the four equation-of-state '
                                 'variants (PR and SRK with the HYSYS database, PR and SRK with '
                                 'the PVTsim database): the Huron-Vidal mixing rule for the pairs '
                                 'of water with N₂ through n-hexane and the classical rule for the '
                                 'remaining pairs, which is the combination used by PVTsim. Each '
                                 'family keeps its own component properties and binary interaction '
                                 'coefficients.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Parámetros de los 14 componentes',
                               'Parameters of the 14 components'),
                    'bloques': [('p',
                                 'El flash trifásico trabaja con 14 componentes: N₂, CO₂, C1 a nC9 '
                                 'y H₂O como decimocuarto componente. Los parámetros '
                                 'a<sub>i</sub>(T) y b<sub>i</sub> se calculan con las expresiones '
                                 'del capítulo «Ecuaciones de estado cúbicas» y las constantes '
                                 'Ω<sub>a</sub> y Ω<sub>b</sub> de cada variante.',
                                 'The three-phase flash works with 14 components: N₂, CO₂, C1 '
                                 'through nC9, and H₂O as the fourteenth component. The '
                                 'a<sub>i</sub>(T) and b<sub>i</sub> parameters are computed with '
                                 'the expressions of the “Cubic equations of state” chapter and '
                                 'the Ω<sub>a</sub> and Ω<sub>b</sub> constants of each variant.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('ul',
                                 [('Variantes con base PVTsim: T<sub>c</sub>, P<sub>c</sub>, ω y '
                                   'peso molecular de la base de PVTsim para los 14 componentes, '
                                   'incluida el agua (T<sub>c</sub> = 1165.14 °R, P<sub>c</sub> = '
                                   '3203.72 psia, ω = 0.344, M = 18.0153). Las presiones críticas '
                                   'se reescalan por 14.696/14.69594878 para reproducir la '
                                   'conversión psia-atm de PVTsim. PR usa Ω<sub>a</sub> = '
                                   '0.4572355289 y Ω<sub>b</sub> = 0.07780; SRK usa Ω<sub>a</sub> '
                                   '= 0.42748023354 y Ω<sub>b</sub> = 0.08664034996.',
                                   'Variants with the PVTsim database: T<sub>c</sub>, '
                                   'P<sub>c</sub>, ω and molecular weight from the PVTsim database '
                                   'for the 14 components, including water (T<sub>c</sub> = '
                                   '1165.14 °R, P<sub>c</sub> = 3203.72 psia, ω = 0.344, M = '
                                   '18.0153). Critical pressures are rescaled by '
                                   '14.696/14.69594878 to reproduce the PVTsim psia-atm '
                                   'conversion. PR uses Ω<sub>a</sub> = 0.4572355289 and '
                                   'Ω<sub>b</sub> = 0.07780; SRK uses Ω<sub>a</sub> = '
                                   '0.42748023354 and Ω<sub>b</sub> = 0.08664034996.'),
                                  ('Variantes con base HYSYS: propiedades de HYSYS para los 13 '
                                   'hidrocarburos (con el factor acéntrico propio de SRK en esa '
                                   'variante) y, para el agua, T<sub>c</sub> = 1165.14 °R, '
                                   'P<sub>c</sub> = 3208.23 psia, ω = 0.344 y M = 18.0151. PR usa '
                                   'Ω<sub>a</sub> = 0.45724 y Ω<sub>b</sub> = 0.07780; SRK usa las '
                                   'constantes exactas indicadas arriba.',
                                   'Variants with the HYSYS database: HYSYS properties for the 13 '
                                   'hydrocarbons (with the SRK-specific acentric factor in that '
                                   'variant) and, for water, T<sub>c</sub> = 1165.14 °R, '
                                   'P<sub>c</sub> = 3208.23 psia, ω = 0.344 and M = 18.0151. PR '
                                   'uses Ω<sub>a</sub> = 0.45724 and Ω<sub>b</sub> = 0.07780; SRK '
                                   'uses the exact constants given above.'),
                                  ('Función α(T): la función clásica de Soave, con la correlación '
                                   'de m de cada ecuación, para todos los componentes, incluida el '
                                   'agua, en las cuatro variantes.',
                                   'α(T) function: the classical Soave function, with the m '
                                   'correlation of each equation, for all components, including '
                                   'water, in the four variants.'),
                                  ('Coeficientes k<sub>ij</sub> hidrocarburo-hidrocarburo: la '
                                   'matriz por defecto de la ecuación de estado activa.',
                                   'Hydrocarbon-hydrocarbon k<sub>ij</sub> coefficients: the '
                                   'default matrix of the active equation of state.'),
                                  ('Coeficientes k<sub>ij</sub> agua-hidrocarburo: la fila del '
                                   'agua de PVTsim (PR: −0.48 con N₂, 0.0952 con CO₂, 0.45 con C1 '
                                   'y C2, 0.53 con C3, 0.52 con los butanos y 0.5 con los '
                                   'restantes; SRK: igual salvo 0.10 con CO₂) o la fila del agua '
                                   'del paquete de fluidos de HYSYS en las variantes con base '
                                   'HYSYS (valores del orden de 0.5 con los hidrocarburos).',
                                   'Water-hydrocarbon k<sub>ij</sub> coefficients: the PVTsim '
                                   'water row (PR: −0.48 with N₂, 0.0952 with CO₂, 0.45 with C1 '
                                   'and C2, 0.53 with C3, 0.52 with the butanes and 0.5 with the '
                                   'rest; SRK: the same except 0.10 with CO₂) or the water row of '
                                   'the HYSYS fluid package in the variants with the HYSYS '
                                   'database (values of the order of 0.5 with the '
                                   'hydrocarbons).')]),
                                ('p',
                                 'Los coeficientes k<sub>ij</sub> agua-hidrocarburo intervienen '
                                 'directamente en la regla clásica de los pares del agua con nC7, '
                                 'nC8 y nC9; no intervienen en los pares del agua con N₂ hasta '
                                 'nC6, que se describen con las energías de interacción de la '
                                 'regla de Huron-Vidal.',
                                 'The water-hydrocarbon k<sub>ij</sub> coefficients enter directly '
                                 'the classical rule of the pairs of water with nC7, nC8 and nC9; '
                                 'they do not enter the pairs of water with N₂ through nC6, which '
                                 'are described by the Huron-Vidal interaction energies.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Regla de mezcla de Huron-Vidal', 'Huron-Vidal mixing rule'),
                    'bloques': [('p',
                                 'La regla cuadrática clásica no reproduce la solubilidad mutua de '
                                 'agua e hidrocarburos. Los pares del agua con N₂, CO₂ y C1 a nC6 '
                                 'se describen con la regla de mezcla de Huron-Vidal, con los '
                                 'parámetros de PVTsim para PR o para SRK según la familia de la '
                                 'ecuación activa; los pares del agua con nC7, nC8 y nC9 y todos '
                                 'los pares sin agua se tratan con la regla clásica, a la que la '
                                 'regla de Huron-Vidal se reduce exactamente con α<sub>ji</sub> = '
                                 '0. En una fase sin agua (fracción de agua ≤ 10⁻¹²) se evalúa '
                                 'directamente la regla cuadrática.',
                                 'The classical quadratic rule does not reproduce the mutual '
                                 'solubility of water and hydrocarbons. The pairs of water with '
                                 'N₂, CO₂, and C1 through nC6 are described with the Huron-Vidal '
                                 'mixing rule, with the PVTsim parameters for PR or for SRK '
                                 'according to the family of the active equation; the pairs of '
                                 'water with nC7, nC8, and nC9 and all pairs without water are '
                                 'treated with the classical rule, to which the Huron-Vidal rule '
                                 'reduces exactly with α<sub>ji</sub> = 0. In a water-free phase '
                                 '(water fraction ≤ 10⁻¹²) the quadratic rule is evaluated '
                                 'directly.'),
                                ('p',
                                 'La formulación, los parámetros y el término del coeficiente de '
                                 'fugacidad se describen en «Regla de mezcla de Huron-Vidal para '
                                 'agua» y en «Reducción a la regla clásica y derivada para la '
                                 'fugacidad».',
                                 'The formulation, the parameters, and the fugacity-coefficient '
                                 'term are described in “Huron-Vidal mixing rule for water” and in '
                                 '“Reduction to the classical rule and derivative for the '
                                 'fugacity”.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Pedersen, K.S., Milter, J. y Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.',
                                 'Pedersen, K.S., Milter, J. and Rasmussen, C.P. (2001). Mutual '
                                 'solubility of water and a reservoir fluid at high temperatures '
                                 'and pressures: experimental and simulated data. <em>Fluid Phase '
                                 'Equilibria</em>, 189(1–2), 85–97.')]},
                   {'titulo': ('Formulación multifásica', 'Multiphase formulation'),
                    'bloques': [('p',
                                 'El flash trifásico resuelve simultáneamente la distribución de '
                                 'la alimentación entre F fases (vapor, líquido de hidrocarburos y '
                                 'fase acuosa) y la composición de cada una. El balance de materia '
                                 'por componente es:',
                                 'The three-phase flash simultaneously solves the distribution of '
                                 'the feed among F phases (vapor, hydrocarbon liquid and aqueous '
                                 'phase) and the composition of each one. The component material '
                                 'balance is:'),
                                ('eq',
                                 'z_i = \\sum_{j=1}^{F} \\beta_j\\,y_{ij} \\qquad \\sum_{j=1}^{F} '
                                 '\\beta_j = 1'),
                                ('p',
                                 'donde β<sub>j</sub> es la fracción molar de la fase j e '
                                 'y<sub>ij</sub> la fracción molar del componente i en la fase j. '
                                 'La igualdad de fugacidades se escribe como '
                                 'y<sub>ij</sub>φ<sub>ij</sub> = constante para cada componente, '
                                 'lo que conduce a:',
                                 'where β<sub>j</sub> is the mole fraction of phase j and '
                                 'y<sub>ij</sub> the mole fraction of component i in phase j. The '
                                 'fugacity equality is written as y<sub>ij</sub>φ<sub>ij</sub> = '
                                 'constant for each component, which leads to:'),
                                ('eq',
                                 'y_{ij} = \\frac{z_i}{E_i\\,\\phi_{ij}} \\qquad E_i = '
                                 '\\sum_{k=1}^{F} \\frac{\\beta_k}{\\phi_{ik}}'),
                                ('p',
                                 'donde φ<sub>ij</sub> es el coeficiente de fugacidad del '
                                 'componente i en la fase j y E<sub>i</sub> una variable auxiliar.',
                                 'where φ<sub>ij</sub> is the fugacity coefficient of component i '
                                 'in phase j and E<sub>i</sub> an auxiliary variable.'),
                                ('h3',
                                 'Rachford-Rice multifásico: minimización de Q',
                                 'Multiphase Rachford-Rice: minimization of Q'),
                                ('p',
                                 'Con los coeficientes de fugacidad fijos, las fracciones de fase '
                                 'se obtienen minimizando la función convexa de Michelsen (1994), '
                                 'sujeta a β<sub>j</sub> ≥ 0:',
                                 'With fixed fugacity coefficients, the phase fractions are '
                                 'obtained by minimizing the convex function of Michelsen (1994), '
                                 'subject to β<sub>j</sub> ≥ 0:'),
                                ('eq', 'Q(\\beta) = \\sum_j \\beta_j - \\sum_i z_i\\,\\ln E_i'),
                                ('eq',
                                 '\\frac{\\partial Q}{\\partial \\beta_j} = 1 - \\sum_i '
                                 '\\frac{z_i}{E_i\\,\\phi_{ij}} \\qquad \\frac{\\partial^2 '
                                 'Q}{\\partial \\beta_j\\,\\partial \\beta_k} = \\sum_i '
                                 '\\frac{z_i}{E_i^{2}\\,\\phi_{ij}\\,\\phi_{ik}}'),
                                ('p',
                                 'donde Q es la función objetivo (adimensional). La condición '
                                 '∂Q/∂β<sub>j</sub> = 0 equivale a Σ<sub>i</sub>y<sub>ij</sub> = 1 '
                                 'en cada fase presente, es decir, a la generalización multifásica '
                                 'de la ecuación de Rachford-Rice. Una fase con β<sub>j</sub> = 0 '
                                 'y ∂Q/∂β<sub>j</sub> ≥ 0 es estable respecto de la mezcla de las '
                                 'demás y queda ausente de la solución, de modo que la aparición y '
                                 'desaparición de fases se resuelve dentro de la minimización.',
                                 'where Q is the objective function (dimensionless). The condition '
                                 '∂Q/∂β<sub>j</sub> = 0 is equivalent to '
                                 'Σ<sub>i</sub>y<sub>ij</sub> = 1 in each phase present, that is, '
                                 'to the multiphase generalization of the Rachford-Rice equation. '
                                 'A phase with β<sub>j</sub> = 0 and ∂Q/∂β<sub>j</sub> ≥ 0 is '
                                 'stable with respect to the mixture of the others and remains '
                                 'absent from the solution, so that the appearance and '
                                 'disappearance of phases is resolved within the minimization.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La minimización de Q se realiza por el método de Newton con '
                                 'conjunto activo: las fases con β<sub>j</sub> = 0 y gradiente no '
                                 'negativo quedan fijas en cero y no intervienen en el paso. El '
                                 'paso se amortigua por búsqueda lineal (reducción a la mitad '
                                 'hasta que Q no aumenta) y los valores de β se proyectan sobre β '
                                 '≥ 0. La minimización termina cuando el gradiente de las fases '
                                 'activas es menor que 10⁻¹³ o el cambio de β es menor que 10⁻¹³, '
                                 'con un máximo de 100 iteraciones.',
                                 'The minimization of Q is performed by an active-set Newton '
                                 'method: phases with β<sub>j</sub> = 0 and non-negative gradient '
                                 'are held at zero and do not take part in the step. The step is '
                                 'damped by a line search (halving until Q does not increase) and '
                                 'the values of β are projected onto β ≥ 0. The minimization ends '
                                 'when the gradient of the active phases is below 10⁻¹³ or the '
                                 'change in β is below 10⁻¹³, with a maximum of 100 iterations.'),
                                ('p',
                                 'El lazo externo es de sustitución sucesiva: con las '
                                 'composiciones vigentes se calculan los coeficientes de fugacidad '
                                 'de cada fase (raíz de vapor para la fase de vapor y raíz de '
                                 'líquido para el líquido de hidrocarburos y la fase acuosa), se '
                                 'minimiza Q y se obtienen las nuevas composiciones normalizadas. '
                                 'La convergencia se declara cuando el cambio máximo de las '
                                 'fracciones molares entre iteraciones es menor que 10⁻¹¹, con un '
                                 'máximo de 400 iteraciones.',
                                 'The outer loop is successive substitution: with the current '
                                 'compositions the fugacity coefficients of each phase are '
                                 'computed (vapor root for the vapor phase and liquid root for the '
                                 'hydrocarbon liquid and the aqueous phase), Q is minimized and '
                                 'the new normalized compositions are obtained. Convergence is '
                                 'declared when the maximum change in mole fractions between '
                                 'iterations is below 10⁻¹¹, with a maximum of 400 iterations.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1994). Calculation of multiphase equilibrium. '
                                 '<em>Computers &amp; Chemical Engineering</em>, 18(7), 545–550.',
                                 'Michelsen, M.L. (1994). Calculation of multiphase equilibrium. '
                                 '<em>Computers &amp; Chemical Engineering</em>, 18(7), 545–550.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Inicialización, reintentos y conservación del balance',
                               'Initialization, retries and material balance preservation'),
                    'bloques': [('p',
                                 'La formulación multifásica converge a un mínimo local que '
                                 'depende de las composiciones iniciales. ThermoPhase inicializa '
                                 'las tres fases a partir de las constantes de Wilson de los 14 '
                                 'componentes y aplica una secuencia de verificaciones que '
                                 'corrigen soluciones con clasificación errónea sin eliminar masa '
                                 'del balance.',
                                 'The multiphase formulation converges to a local minimum that '
                                 'depends on the initial compositions. ThermoPhase initializes the '
                                 'three phases from the Wilson ratios of the 14 components and '
                                 'applies a sequence of checks that correct solutions with an '
                                 'erroneous classification without removing mass from the '
                                 'balance.'),
                                ('eq',
                                 'y_i^{0} \\propto z_i\\,K_i^{W} \\qquad x_i^{0} \\propto '
                                 '\\frac{z_i}{K_i^{W}} \\qquad x_i^{\\mathrm{Aq},0} \\propto '
                                 '\\delta_{i,\\mathrm{H_2O}}'),
                                ('p',
                                 'donde y<sup>0</sup>, x<sup>0</sup> y x<sup>Aq,0</sup> son las '
                                 'composiciones iniciales normalizadas del vapor, del líquido de '
                                 'hidrocarburos y de la fase acuosa, K<sub>i</sub><sup>W</sup> la '
                                 'constante de Wilson y δ<sub>i,H₂O</sub> vale 1 para el agua y 0 '
                                 'para los demás componentes. En x<sup>0</sup> la fracción de agua '
                                 'se fija en 10⁻⁸ y x<sup>Aq,0</sup> es agua prácticamente pura '
                                 '(10⁻⁸ para los demás componentes). Las fracciones de fase '
                                 'iniciales son iguales (β<sub>j</sub> = 1/F).',
                                 'where y<sup>0</sup>, x<sup>0</sup>, and x<sup>Aq,0</sup> are the '
                                 'normalized initial compositions of the vapor, the hydrocarbon '
                                 'liquid, and the aqueous phase, K<sub>i</sub><sup>W</sup> is the '
                                 'Wilson ratio, and δ<sub>i,H₂O</sub> equals 1 for water and 0 for '
                                 'the other components. In x<sup>0</sup> the water fraction is set '
                                 'to 10⁻⁸, and x<sup>Aq,0</sup> is practically pure water (10⁻⁸ '
                                 'for the other components). The initial phase fractions are equal '
                                 '(β<sub>j</sub> = 1/F).'),
                                ('h3', 'Reintento con cuatro fases', 'Four-phase retry'),
                                ('p',
                                 'A temperaturas bajas los hidrocarburos pueden separarse en dos '
                                 'líquidos y la semilla de la fase acuosa puede converger a una '
                                 'fase no acuosa. Si la tercera fase resulta con fracción de agua '
                                 'menor que 0.5, el cálculo se repite con cuatro fases (vapor, dos '
                                 'líquidos de hidrocarburos y fase acuosa), añadiendo una semilla '
                                 'intermedia proporcional a '
                                 'z<sub>i</sub>√K<sub>i</sub><sup>W</sup>. Del resultado se '
                                 'agrupan como fase acuosa las fases con β &gt; 10⁻¹⁰ y fracción '
                                 'de agua mayor que 0.5; las fases de hidrocarburos se ordenan por '
                                 'densidad molar, la menos densa se asigna al vapor y las '
                                 'restantes se combinan en un único líquido de hidrocarburos:',
                                 'At low temperatures the hydrocarbons can split into two liquids '
                                 'and the aqueous seed can converge to a non-aqueous phase. If the '
                                 'third phase has a water fraction below 0.5, the calculation is '
                                 'repeated with four phases (vapor, two hydrocarbon liquids and '
                                 'aqueous phase), adding an intermediate seed proportional to '
                                 'z<sub>i</sub>√K<sub>i</sub><sup>W</sup>. From the result, the '
                                 'phases with β &gt; 10⁻¹⁰ and a water fraction greater than 0.5 '
                                 'are grouped as the aqueous phase; the hydrocarbon phases are '
                                 'ordered by molar density, the least dense is assigned to the '
                                 'vapor and the rest are combined into a single hydrocarbon '
                                 'liquid:'),
                                ('eq',
                                 '\\beta_L = \\sum_{j \\in \\mathrm{L}} \\beta_j \\qquad x_i = '
                                 '\\frac{1}{\\beta_L}\\sum_{j \\in \\mathrm{L}} \\beta_j\\,y_{ij}'),
                                ('p',
                                 'donde L es el conjunto de fases de hidrocarburos combinadas, '
                                 'β<sub>L</sub> la fracción del líquido resultante y x<sub>i</sub> '
                                 'su composición. La combinación ponderada por β conserva '
                                 'exactamente el balance de materia.',
                                 'where L is the set of combined hydrocarbon phases, β<sub>L</sub> '
                                 'the fraction of the resulting liquid and x<sub>i</sub> its '
                                 'composition. The β-weighted combination preserves the material '
                                 'balance exactly.'),
                                ('h3', 'Verificaciones de consistencia', 'Consistency checks'),
                                ('ul',
                                 [('Si el líquido de hidrocarburos es despreciable (β<sub>L</sub> '
                                   '&lt; 10⁻⁴) y existe fase acuosa (β<sub>Aq</sub> &gt; 10⁻⁴), el '
                                   'sistema se resuelve de nuevo con dos fases, vapor y acuosa; el '
                                   'resultado se acepta si la segunda fase es acuosa y el vapor es '
                                   'significativo.',
                                   'If the hydrocarbon liquid is negligible (β<sub>L</sub> &lt; '
                                   '10⁻⁴) and an aqueous phase exists (β<sub>Aq</sub> &gt; 10⁻⁴), '
                                   'the system is solved again with two phases, vapor and aqueous; '
                                   'the result is accepted if the second phase is aqueous and the '
                                   'vapor is significant.'),
                                  ('Si existe líquido de hidrocarburos (β<sub>L</sub> &gt; 10⁻⁵) '
                                   'pero la fase acuosa tiene fracción de agua menor que 0.5 o el '
                                   'líquido de hidrocarburos más de 0.3, se repite el cálculo con '
                                   'vapor y fase acuosa y se acepta si la segunda fase es acuosa.',
                                   'If a hydrocarbon liquid exists (β<sub>L</sub> &gt; 10⁻⁵) but '
                                   'the aqueous phase has a water fraction below 0.5 or the '
                                   'hydrocarbon liquid above 0.3, the calculation is repeated with '
                                   'vapor and aqueous phase and accepted if the second phase is '
                                   'aqueous.'),
                                  ('Un líquido de hidrocarburos con fracción de agua mayor que 0.5 '
                                   'es una segunda fase acuosa y se fusiona con la fase acuosa.',
                                   'A hydrocarbon liquid with a water fraction greater than 0.5 is '
                                   'a second aqueous phase and is merged with the aqueous phase.'),
                                  ('Una fase acuosa con fracción de agua menor que 0.5 (y β ≥ '
                                   '10⁻⁵) es una fase de hidrocarburos y se combina con el líquido '
                                   'de hidrocarburos; nunca se descarta masa del balance.',
                                   'An aqueous phase with a water fraction below 0.5 (and β ≥ '
                                   '10⁻⁵) is a hydrocarbon phase and is combined with the '
                                   'hydrocarbon liquid; mass is never discarded from the balance.'),
                                  ('Las fases con β &lt; 10⁻⁵ se consideran ausentes y, al final, '
                                   'las fracciones de fase se renormalizan a suma unitaria.',
                                   'Phases with β &lt; 10⁻⁵ are considered absent and, at the end, '
                                   'the phase fractions are renormalized to unit sum.')]),
                                ('h3',
                                 'Reconciliación de la fase de hidrocarburos',
                                 'Reconciliation of the hydrocarbon phase'),
                                ('p',
                                 'Si vapor y líquido de hidrocarburos convergen a la misma '
                                 'composición (diferencia máxima menor que 10⁻³), se reúnen en una '
                                 'sola fase. Si queda una sola fase de hidrocarburos, su '
                                 'composición se somete a un flash líquido-vapor de 14 componentes '
                                 'con la misma ecuación de estado y regla de mezcla: el resultado '
                                 'determina si la fase es vapor, líquido o se divide en vapor y '
                                 'líquido. Este flash auxiliar incluye una prueba de estabilidad '
                                 'de Michelsen con una fase de prueba de tipo líquido (semilla '
                                 'z<sub>i</sub>/K<sub>i</sub><sup>W</sup>, raíz de menor energía '
                                 'de Gibbs); si ΣW<sub>i</sub> &gt; 1 + 10⁻⁷ la fase es inestable '
                                 'y las constantes de arranque se toman como '
                                 'z<sub>i</sub>/Y<sub>i</sub>, con Y la composición normalizada de '
                                 'la fase de prueba, lo que permite detectar la condensación '
                                 'incipiente cerca del punto de rocío. Su ecuación de '
                                 'Rachford-Rice se resuelve por bisección y la sustitución '
                                 'sucesiva converge con '
                                 '|ln(K<sub>i</sub><sup>nuevo</sup>/K<sub>i</sub>)| &lt; 10⁻¹².',
                                 'If vapor and hydrocarbon liquid converge to the same composition '
                                 '(maximum difference below 10⁻³), they are merged into a single '
                                 'phase. If a single hydrocarbon phase remains, its composition is '
                                 'subjected to a 14-component vapor-liquid flash with the same '
                                 'equation of state and mixing rule: the result determines whether '
                                 'the phase is vapor, liquid or splits into vapor and liquid. This '
                                 'auxiliary flash includes a Michelsen stability test with a '
                                 'liquid-like trial phase (seed '
                                 'z<sub>i</sub>/K<sub>i</sub><sup>W</sup>, root of minimum Gibbs '
                                 'energy); if ΣW<sub>i</sub> &gt; 1 + 10⁻⁷ the phase is unstable '
                                 'and the starting ratios are taken as '
                                 'z<sub>i</sub>/Y<sub>i</sub>, with Y the normalized trial-phase '
                                 'composition, which allows incipient condensation near the dew '
                                 'point to be detected. Its Rachford-Rice equation is solved by '
                                 'bisection and the successive substitution converges with '
                                 '|ln(K<sub>i</sub><sup>new</sup>/K<sub>i</sub>)| &lt; 10⁻¹².'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1994). Calculation of multiphase equilibrium. '
                                 '<em>Computers &amp; Chemical Engineering</em>, 18(7), 545–550.',
                                 'Michelsen, M.L. (1994). Calculation of multiphase equilibrium. '
                                 '<em>Computers &amp; Chemical Engineering</em>, 18(7), 545–550.'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.')]},
                   {'titulo': ('Identificación de la fase acuosa',
                               'Identification of the aqueous phase'),
                    'bloques': [('p',
                                 'La fase acuosa se identifica por su composición: una fase es '
                                 'acuosa si su fracción molar de agua es mayor que 0.5. Este '
                                 'criterio se aplica en la agrupación del reintento con cuatro '
                                 'fases, en la aceptación de las soluciones de dos fases '
                                 'vapor-acuosa y en la fusión de fases duplicadas.',
                                 'The aqueous phase is identified by its composition: a phase is '
                                 'aqueous if its water mole fraction is greater than 0.5. This '
                                 'criterion is applied in the grouping of the four-phase retry, in '
                                 'the acceptance of the vapor-aqueous two-phase solutions and in '
                                 'the merging of duplicated phases.'),
                                ('eq', 'x_{\\mathrm{H_2O}} > 0.5 \\;\\Rightarrow\\; \\mathrm{Aq}'),
                                ('p',
                                 'donde x<sub>H₂O</sub> es la fracción molar de agua de la fase y '
                                 'Aq indica fase acuosa. Las fases restantes son fases de '
                                 'hidrocarburos y se clasifican como vapor o líquido con los '
                                 'criterios del capítulo «Identificación de fases».',
                                 'where x<sub>H₂O</sub> is the water mole fraction of the phase '
                                 'and Aq denotes the aqueous phase. The remaining phases are '
                                 'hydrocarbon phases and are classified as vapor or liquid with '
                                 'the criteria of the “Phase identification” chapter.'),
                                ('p',
                                 'La fase acuosa se calcula siempre con la raíz de líquido de la '
                                 'ecuación de estado. Su composición incluye los hidrocarburos y '
                                 'el CO₂ disueltos, que la regla de Huron-Vidal reproduce con los '
                                 'parámetros de PVTsim; del mismo modo, las fases de hidrocarburos '
                                 'contienen el agua disuelta en equilibrio.',
                                 'The aqueous phase is always computed with the liquid root of the '
                                 'equation of state. Its composition includes the dissolved '
                                 'hydrocarbons and CO₂, which the Huron-Vidal rule reproduces with '
                                 'the PVTsim parameters; likewise, the hydrocarbon phases contain '
                                 'the dissolved water at equilibrium.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Propiedades por fase y de la mezcla',
                               'Phase and mixture properties'),
                    'bloques': [('p',
                                 'Una vez resuelto el equilibrio, ThermoPhase calcula para cada '
                                 'fase presente (vapor, líquido de hidrocarburos y fase acuosa) el '
                                 'peso molecular, el factor de compresibilidad, la densidad, la '
                                 'gravedad específica, la viscosidad, la entalpía y la entropía, '
                                 'con los mismos parámetros y la misma regla de mezcla empleados '
                                 'en el flash. Los métodos se describen en los capítulos '
                                 '«Propiedades volumétricas», «Entalpía y entropía» y '
                                 '«Viscosidad»; a continuación se resume su aplicación a cada '
                                 'fase.',
                                 'Once the equilibrium is solved, ThermoPhase computes for each '
                                 'phase present (vapor, hydrocarbon liquid, and aqueous phase) the '
                                 'molecular weight, the compressibility factor, the density, the '
                                 'specific gravity, the viscosity, the enthalpy, and the entropy, '
                                 'with the same parameters and mixing rule used in the flash. The '
                                 'methods are described in the “Volumetric properties”, “Enthalpy '
                                 'and entropy”, and “Viscosity” chapters; their application to '
                                 'each phase is summarized below.'),
                                ('ul',
                                 [('Vapor: densidad de la ecuación de estado ρ = PM/(ZRT), o con '
                                   'la corrección de Peneloux si está seleccionada; gravedad '
                                   'específica M/28.9625; viscosidad por Lohrenz-Bray-Clark con '
                                   'los 14 componentes.',
                                   'Vapor: equation-of-state density ρ = PM/(ZRT), or with the '
                                   'Peneloux correction if selected; specific gravity M/28.9625; '
                                   'viscosity by Lohrenz-Bray-Clark with the 14 components.'),
                                  ('Líquido de hidrocarburos: densidad de la ecuación de estado, '
                                   'de Peneloux o de COSTALD; en este último caso se evalúa sobre '
                                   'la composición de hidrocarburos renormalizada sin agua, con '
                                   'transición cuadrática hacia la densidad de la ecuación de '
                                   'estado para 0.95 &lt; T<sub>r</sub> &lt; 1; gravedad '
                                   'específica ρ/62.4; viscosidad por Lohrenz-Bray-Clark.',
                                   'Hydrocarbon liquid: equation-of-state, Peneloux or COSTALD '
                                   'density; in the latter case it is evaluated on the water-free '
                                   'renormalized hydrocarbon composition, with a quadratic '
                                   'transition to the equation-of-state density for 0.95 &lt; '
                                   'T<sub>r</sub> &lt; 1; specific gravity ρ/62.4; viscosity by '
                                   'Lohrenz-Bray-Clark.'),
                                  ('Fase acuosa: densidad de la ecuación de estado, de Peneloux o '
                                   'de COSTALD sobre la composición completa de 14 componentes '
                                   '(con la densidad de la ecuación de estado si T<sub>r</sub> ≥ '
                                   '1); gravedad específica ρ/62.4; viscosidad por la correlación '
                                   'del agua empleada por PVTsim, con Lohrenz-Bray-Clark como '
                                   'respaldo.',
                                   'Aqueous phase: equation-of-state, Peneloux or COSTALD density '
                                   'on the full 14-component composition (with the '
                                   'equation-of-state density if T<sub>r</sub> ≥ 1); specific '
                                   'gravity ρ/62.4; viscosity by the water correlation used by '
                                   'PVTsim, with Lohrenz-Bray-Clark as fallback.'),
                                  ('Entalpía y entropía de cada fase: contribución de gas ideal '
                                   'más la contribución residual de la ecuación de estado con la '
                                   'regla de mezcla de Huron-Vidal, con da<sub>m</sub>/dT evaluada '
                                   'numéricamente.',
                                   'Enthalpy and entropy of each phase: ideal-gas contribution '
                                   'plus the residual contribution of the equation of state with '
                                   'the Huron-Vidal mixing rule, with da<sub>m</sub>/dT evaluated '
                                   'numerically.')]),
                                ('h3', 'Fracciones de fase', 'Phase fractions'),
                                ('p',
                                 'Además de las fracciones molares β<sub>j</sub>, se presentan las '
                                 'fracciones másicas y las fracciones volumétricas de fase:',
                                 'In addition to the mole fractions β<sub>j</sub>, the phase mass '
                                 'fractions and volume fractions are reported:'),
                                ('eq',
                                 'w_j = \\frac{\\beta_j\\,M_j}{\\sum_k \\beta_k\\,M_k} \\qquad '
                                 '\\theta_j = \\frac{\\beta_j\\,M_j/\\rho_j}{\\sum_k '
                                 '\\beta_k\\,M_k/\\rho_k}'),
                                ('p',
                                 'donde w<sub>j</sub> es la fracción másica de la fase j, '
                                 'θ<sub>j</sub> su fracción volumétrica, M<sub>j</sub> su peso '
                                 'molecular (lb/lbmol) y ρ<sub>j</sub> su densidad (lb/ft³), '
                                 'obtenida con el método de densidad seleccionado. La fracción '
                                 'volumétrica corresponde a la magnitud Volume% de PVTsim.',
                                 'where w<sub>j</sub> is the mass fraction of phase j, '
                                 'θ<sub>j</sub> its volume fraction, M<sub>j</sub> its molecular '
                                 'weight (lb/lbmol) and ρ<sub>j</sub> its density (lb/ft³), '
                                 'obtained with the selected density method. The volume fraction '
                                 'corresponds to the PVTsim Volume% quantity.'),
                                ('h3', 'Propiedades de la mezcla', 'Mixture properties'),
                                ('p',
                                 'La densidad de la mezcla se calcula con la hipótesis de '
                                 'volúmenes aditivos de las fases (véase «Densidad de la mezcla y '
                                 'fracción volumétrica de fase»). El peso molecular, la entalpía y '
                                 'la entropía de la mezcla se obtienen como promedios ponderados '
                                 'por las fracciones molares de fase:',
                                 'The mixture density is computed under the assumption of additive '
                                 'phase volumes (see “Mixture density and phase volume fraction”). '
                                 'The molecular weight, enthalpy, and entropy of the mixture are '
                                 'obtained as averages weighted by the phase mole fractions:'),
                                ('eq',
                                 'M_{mix} = \\sum_j \\beta_j\\,M_j \\qquad H_{mix} = \\sum_j '
                                 '\\beta_j\\,H_j \\qquad S_{mix} = \\sum_j \\beta_j\\,S_j'),
                                ('p',
                                 'donde H<sub>j</sub> es la entalpía molar (BTU/lbmol) y '
                                 'S<sub>j</sub> la entropía molar (BTU/(lbmol·°R)) de la fase j. '
                                 'El poder calorífico y el contenido de líquidos (GPM) se calculan '
                                 'sobre la composición de hidrocarburos renormalizada sin agua, '
                                 'dado que el agua es inerte en la combustión.',
                                 'where H<sub>j</sub> is the molar enthalpy (BTU/lbmol) and '
                                 'S<sub>j</sub> the molar entropy (BTU/(lbmol·°R)) of phase j. The '
                                 'heating value and the liquid content (GPM) are computed on the '
                                 'water-free renormalized hydrocarbon composition, since water is '
                                 'inert in combustion.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.',
                                 'Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.')]}]},
 {'titulo': ('Identificación de fases', 'Phase identification'),
  'subsecciones': [{'titulo': ('El problema de la identificación de fase',
                               'The phase identification problem'),
                    'bloques': [('p',
                                 'Cuando el flash converge a una sola fase, es necesario '
                                 'determinar si el fluido tiene carácter de líquido o de vapor, ya '
                                 'que los métodos de densidad, viscosidad y demás propiedades, así '
                                 'como la presentación de resultados, dependen de esa etiqueta. '
                                 'Cuando la ecuación de estado tiene tres raíces reales para la '
                                 'composición global, la prueba de fase del flash '
                                 '(Σz<sub>i</sub>K<sub>i</sub> ≤ 1 para líquido, '
                                 'Σz<sub>i</sub>/K<sub>i</sub> ≤ 1 para vapor) establece la '
                                 'etiqueta, ya que existe una segunda raíz de referencia con la '
                                 'que comparar las fugacidades.',
                                 'When the flash converges to a single phase, it is necessary to '
                                 'determine whether the fluid has liquid or vapor character, since '
                                 'the density, viscosity and other property methods, as well as '
                                 'the presentation of results, depend on that label. When the '
                                 'equation of state has three real roots for the overall '
                                 'composition, the flash phase test (Σz<sub>i</sub>K<sub>i</sub> ≤ '
                                 '1 for liquid, Σz<sub>i</sub>/K<sub>i</sub> ≤ 1 for vapor) '
                                 'establishes the label, since a second reference root exists '
                                 'against which the fugacities can be compared.'),
                                ('p',
                                 'La dificultad aparece cuando la cúbica tiene una sola raíz real: '
                                 'región supercrítica, líquido comprimido a alta presión o gas '
                                 'denso por encima de la cricondenbar. En esa región el fluido es '
                                 'termodinámicamente único y no existe un criterio de fugacidades '
                                 'que distinga líquido de vapor; la etiqueta se asigna con un '
                                 'criterio convencional.',
                                 'The difficulty arises when the cubic has a single real root: '
                                 'supercritical region, compressed liquid at high pressure or '
                                 'dense gas above the cricondenbar. In that region the fluid is '
                                 'thermodynamically unique and no fugacity criterion distinguishes '
                                 'liquid from vapor; the label is assigned by a conventional '
                                 'criterion.'),
                                ('p',
                                 'ThermoPhase aplica en ese caso el criterio del simulador cuya '
                                 'base de datos se emplea: el de HYSYS para las variantes PR y SRK '
                                 'con base HYSYS y el de PVTsim para las variantes PR y SRK con '
                                 'base PVTsim. La condición de raíz única se verifica con la '
                                 'composición global, cuando |Z<sub>V</sub> − Z<sub>L</sub>| &lt; '
                                 '10⁻⁷, y el criterio solo se evalúa si el flash ya convergió a '
                                 'una fase; nunca modifica un resultado bifásico.',
                                 'In that case ThermoPhase applies the criterion of the simulator '
                                 'whose database is used: the HYSYS criterion for the PR and SRK '
                                 'variants with the HYSYS database and the PVTsim criterion for '
                                 'the PR and SRK variants with the PVTsim database. The '
                                 'single-root condition is checked with the overall composition, '
                                 'when |Z<sub>V</sub> − Z<sub>L</sub>| &lt; 10⁻⁷, and the '
                                 'criterion is only evaluated if the flash has already converged '
                                 'to one phase; it never modifies a two-phase result.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Venkatarathnam, G. y Oellrich, L.R. (2011). Identification of '
                                 'the phase of a fluid using partial derivatives of pressure, '
                                 'volume, and temperature without reference to saturation '
                                 'properties: applications in phase equilibria calculations. '
                                 '<em>Fluid Phase Equilibria</em>, 301(2), 225–233.',
                                 'Venkatarathnam, G. and Oellrich, L.R. (2011). Identification of '
                                 'the phase of a fluid using partial derivatives of pressure, '
                                 'volume, and temperature without reference to saturation '
                                 'properties: applications in phase equilibria calculations. '
                                 '<em>Fluid Phase Equilibria</em>, 301(2), 225–233.')]},
                   {'titulo': ('Criterio de HYSYS: compresibilidad isotérmica y composición',
                               'HYSYS criterion: isothermal compressibility and composition'),
                    'bloques': [('p',
                                 'El manual de referencia técnica de HYSYS especifica, para las '
                                 'ecuaciones cúbicas PR y SRK en la región supercrítica, dos '
                                 'reglas de asignación de vapor basadas en el factor de '
                                 'compresibilidad, en la compresibilidad isotérmica y en la '
                                 'composición de la mezcla. Si ninguna se cumple, se asigna '
                                 'fracción de vapor nula y se emplean las correlaciones de '
                                 'líquido.',
                                 'The HYSYS technical reference manual specifies, for the PR and '
                                 'SRK cubic equations in the supercritical region, two vapor '
                                 'assignment rules based on the compressibility factor, the '
                                 'isothermal compressibility and the mixture composition. If '
                                 'neither is satisfied, a zero vapor fraction is assigned and the '
                                 'liquid correlations are used.'),
                                ('p',
                                 'La compresibilidad isotérmica mide la variación relativa del '
                                 'volumen molar con la presión a temperatura constante; su forma '
                                 'adimensional κ<sub>r</sub> vale 1 para el gas ideal y es mucho '
                                 'menor que 1 para un líquido:',
                                 'The isothermal compressibility measures the relative change of '
                                 'molar volume with pressure at constant temperature; its '
                                 'dimensionless form κ<sub>r</sub> equals 1 for the ideal gas and '
                                 'is much smaller than 1 for a liquid:'),
                                ('eq',
                                 '\\kappa = -\\frac{1}{V}\\left(\\frac{\\partial V}{\\partial '
                                 'P}\\right)_T \\qquad \\kappa_r = P\\,\\kappa = '
                                 '-\\frac{P}{V\\,(\\partial P/\\partial V)_T}'),
                                ('p',
                                 'donde κ es la compresibilidad isotérmica (psia⁻¹), κ<sub>r</sub> '
                                 'su forma adimensional y V = ZRT/P el volumen molar (ft³/lbmol). '
                                 'ThermoPhase evalúa la derivada analíticamente con la ecuación de '
                                 'estado activa:',
                                 'where κ is the isothermal compressibility (psia⁻¹), '
                                 'κ<sub>r</sub> its dimensionless form and V = ZRT/P the molar '
                                 'volume (ft³/lbmol). ThermoPhase evaluates the derivative '
                                 'analytically with the active equation of state:'),
                                ('eq',
                                 '\\left(\\frac{\\partial P}{\\partial V}\\right)_T^{PR} = '
                                 '-\\frac{RT}{(V-b_m)^2} + '
                                 '\\frac{2\\,a_m\\,(V+b_m)}{\\left(V^2+2b_mV-b_m^2\\right)^2}'),
                                ('eq',
                                 '\\left(\\frac{\\partial P}{\\partial V}\\right)_T^{SRK} = '
                                 '-\\frac{RT}{(V-b_m)^2} + '
                                 '\\frac{a_m\\,(2V+b_m)}{V^2\\,(V+b_m)^2}'),
                                ('p',
                                 'donde a<sub>m</sub> (psia·ft⁶/lbmol²) y b<sub>m</sub> '
                                 '(ft³/lbmol) son los parámetros de la mezcla con la regla '
                                 'cuadrática y los k<sub>ij</sub> en uso.',
                                 'where a<sub>m</sub> (psia·ft⁶/lbmol²) and b<sub>m</sub> '
                                 '(ft³/lbmol) are the mixture parameters with the quadratic rule '
                                 'and the k<sub>ij</sub> in use.'),
                                ('h3', 'Reglas del manual', 'Manual rules'),
                                ('ul',
                                 [('Regla 1: si Z &gt; 0.3 y κ<sub>r</sub> &gt; 0.75, se asigna '
                                   'vapor.',
                                   'Rule 1: if Z &gt; 0.3 and κ<sub>r</sub> &gt; 0.75, vapor is '
                                   'assigned.'),
                                  ('Regla 2: si Z &gt; 0.75 y la suma de las fracciones molares de '
                                   'los componentes livianos (punto normal de ebullición menor que '
                                   '230 K) supera la de los pesados, se asigna vapor.',
                                   'Rule 2: if Z &gt; 0.75 and the sum of the mole fractions of '
                                   'the light components (normal boiling point below 230 K) '
                                   'exceeds that of the heavy components, vapor is assigned.')]),
                                ('p',
                                 'La condición Z &gt; 0.3 de la regla 1 excluye líquidos muy '
                                 'comprimidos en los que κ<sub>r</sub> puede ser elevado. Con el '
                                 'umbral de 230 K (414 °R), los componentes livianos de '
                                 'ThermoPhase son N₂ (77 K), metano (112 K), CO₂ (195 K) y etano '
                                 '(185 K); el propano (231 K) y los componentes más pesados se '
                                 'clasifican como pesados.',
                                 'The Z &gt; 0.3 condition of rule 1 excludes highly compressed '
                                 'liquids in which κ<sub>r</sub> can be high. With the 230 K (414 '
                                 '°R) threshold, the light components in ThermoPhase are N₂ (77 '
                                 'K), methane (112 K), CO₂ (195 K) and ethane (185 K); propane '
                                 '(231 K) and heavier components are classified as heavy.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>, sección Supercritical Handling. Aspen '
                                 'Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>, Supercritical Handling section. Aspen '
                                 'Technology, Inc.'),
                                ('p',
                                 'Venkatarathnam, G. y Oellrich, L.R. (2011). Identification of '
                                 'the phase of a fluid using partial derivatives of pressure, '
                                 'volume, and temperature without reference to saturation '
                                 'properties: applications in phase equilibria calculations. '
                                 '<em>Fluid Phase Equilibria</em>, 301(2), 225–233.',
                                 'Venkatarathnam, G. and Oellrich, L.R. (2011). Identification of '
                                 'the phase of a fluid using partial derivatives of pressure, '
                                 'volume, and temperature without reference to saturation '
                                 'properties: applications in phase equilibria calculations. '
                                 '<em>Fluid Phase Equilibria</em>, 301(2), 225–233.')]},
                   {'titulo': ('Criterio A/B de alta presión', 'High-pressure A/B criterion'),
                    'bloques': [('p',
                                 'A presiones superiores a la cricondenbar el factor Z permanece '
                                 'por encima de 0.75 en un amplio intervalo de temperatura, y la '
                                 'regla 2 asignaría vapor aun a temperaturas bajas en las que el '
                                 'fluido es un líquido comprimido. HYSYS presenta en esa región '
                                 'una frontera líquido-vapor vertical en el plano P-T, es decir, '
                                 'independiente de la presión. ThermoPhase reproduce esa frontera '
                                 'con la razón de los parámetros adimensionales de la ecuación de '
                                 'estado:',
                                 'At pressures above the cricondenbar the Z factor remains above '
                                 '0.75 over a wide temperature range, and rule 2 would assign '
                                 'vapor even at low temperatures at which the fluid is a '
                                 'compressed liquid. In that region HYSYS exhibits a vertical '
                                 'liquid-vapor boundary in the P-T plane, that is, independent of '
                                 'pressure. ThermoPhase reproduces that boundary with the ratio of '
                                 'the dimensionless equation-of-state parameters:'),
                                ('eq',
                                 '\\frac{A}{B} = \\frac{a_m P/(RT)^2}{b_m P/(RT)} = '
                                 '\\frac{a_m(T)}{b_m\\,R\\,T}'),
                                ('p',
                                 'donde A y B son los parámetros adimensionales de la cúbica. La '
                                 'presión se cancela, por lo que la frontera definida por A/B es '
                                 'una línea de temperatura constante.',
                                 'where A and B are the dimensionless parameters of the cubic. '
                                 'Pressure cancels out, so the boundary defined by A/B is a line '
                                 'of constant temperature.'),
                                ('p',
                                 'El fluido se clasifica como líquido comprimido cuando A/B supera '
                                 'la razón de las constantes universales de la ecuación de estado, '
                                 'condición en la que el término atractivo domina sobre el '
                                 'repulsivo:',
                                 'The fluid is classified as compressed liquid when A/B exceeds '
                                 'the ratio of the universal equation-of-state constants, a '
                                 'condition in which the attractive term dominates over the '
                                 'repulsive one:'),
                                ('eq',
                                 '\\frac{A}{B} > \\frac{\\Omega_a}{\\Omega_b} \\;\\Rightarrow\\; '
                                 '\\mathrm{L} \\qquad T_{f} = '
                                 '\\frac{a_m(T_{f})}{b_m\\,R\\,(\\Omega_a/\\Omega_b)}'),
                                ('p',
                                 'donde Ω<sub>a</sub> y Ω<sub>b</sub> son las constantes de la '
                                 'ecuación de estado, L indica líquido y T<sub>f</sub> es la '
                                 'temperatura de la frontera (°R), definida implícitamente porque '
                                 'a<sub>m</sub> depende de T. Los valores de la razón son:',
                                 'where Ω<sub>a</sub> and Ω<sub>b</sub> are the equation-of-state '
                                 'constants, L denotes liquid, and T<sub>f</sub> is the boundary '
                                 'temperature (°R), implicitly defined because a<sub>m</sub> '
                                 'depends on T. The values of the ratio are:'),
                                ('eq',
                                 '\\left.\\frac{\\Omega_a}{\\Omega_b}\\right|_{PR} = '
                                 '\\frac{0.45724}{0.07780} \\approx 5.877 \\qquad '
                                 '\\left.\\frac{\\Omega_a}{\\Omega_b}\\right|_{SRK} = '
                                 '\\frac{0.42748}{0.08664} \\approx 4.934'),
                                ('p',
                                 'donde los subíndices indican la ecuación de estado. Estos '
                                 'valores son consecuencia directa de las constantes de '
                                 'Peng-Robinson y de Soave-Redlich-Kwong y no contienen parámetros '
                                 'ajustados.',
                                 'where the subscripts indicate the equation of state. These '
                                 'values follow directly from the Peng-Robinson and '
                                 'Soave-Redlich-Kwong constants and contain no fitted parameters.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.')]},
                   {'titulo': ('Algoritmo de identificación de HYSYS',
                               'HYSYS identification algorithm'),
                    'bloques': [('p',
                                 'En las variantes con base HYSYS, los criterios se evalúan en '
                                 'cascada; en cuanto uno produce una clasificación, los siguientes '
                                 'no se evalúan:',
                                 'In the variants with the HYSYS database, the criteria are '
                                 'evaluated in cascade; as soon as one produces a classification, '
                                 'the following ones are not evaluated:'),
                                ('ul',
                                 [('Compresibilidad isotérmica: si Z &gt; 0.3 y κ<sub>r</sub> &gt; '
                                   '0.75, el fluido es vapor.',
                                   'Isothermal compressibility: if Z &gt; 0.3 and κ<sub>r</sub> '
                                   '&gt; 0.75, the fluid is vapor.'),
                                  ('Criterio A/B: si A/B &gt; Ω<sub>a</sub>/Ω<sub>b</sub> de la '
                                   'ecuación activa, el fluido es líquido comprimido.',
                                   'A/B criterion: if A/B &gt; Ω<sub>a</sub>/Ω<sub>b</sub> of the '
                                   'active equation, the fluid is compressed liquid.'),
                                  ('Composición: si Z &gt; 0.75 y la fracción de livianos supera '
                                   'la de pesados, el fluido es vapor; en caso contrario es '
                                   'líquido.',
                                   'Composition: if Z &gt; 0.75 and the light fraction exceeds the '
                                   'heavy fraction, the fluid is vapor; otherwise it is liquid.')]),
                                ('p',
                                 'La compresibilidad isotérmica tiene prioridad sobre el criterio '
                                 'A/B porque κ<sub>r</sub> &gt; 0.75 es condición suficiente de '
                                 'comportamiento gaseoso y gobierna la transición a vapor a '
                                 'presiones moderadas. El criterio A/B tiene prioridad sobre la '
                                 'regla de composición porque, en la región densa donde Z '
                                 'permanece por encima de 0.75, la regla de composición devolvería '
                                 'vapor en todo el intervalo de temperatura.',
                                 'The isothermal compressibility takes precedence over the A/B '
                                 'criterion because κ<sub>r</sub> &gt; 0.75 is a sufficient '
                                 'condition for gas-like behavior and governs the transition to '
                                 'vapor at moderate pressures. The A/B criterion takes precedence '
                                 'over the composition rule because, in the dense region where Z '
                                 'remains above 0.75, the composition rule would return vapor over '
                                 'the whole temperature range.'),
                                ('p',
                                 'El algoritmo no utiliza el punto crítico de la mezcla ni '
                                 'parámetros ajustables: los umbrales 0.3, 0.75 y 230 K provienen '
                                 'del manual de HYSYS y la razón Ω<sub>a</sub>/Ω<sub>b</sub> de la '
                                 'ecuación de estado.',
                                 'The algorithm uses neither the mixture critical point nor '
                                 'adjustable parameters: the thresholds 0.3, 0.75 and 230 K come '
                                 'from the HYSYS manual and the Ω<sub>a</sub>/Ω<sub>b</sub> ratio '
                                 'from the equation of state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>, sección Supercritical Handling. Aspen '
                                 'Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>, Supercritical Handling section. Aspen '
                                 'Technology, Inc.')]},
                   {'titulo': ('Criterio de PVTsim', 'PVTsim criterion'),
                    'bloques': [('p',
                                 'PVTsim identifica la fase de un fluido monofásico comparando la '
                                 'temperatura con el punto crítico real de la mezcla. En las '
                                 'variantes con base PVTsim, ThermoPhase aplica este criterio a '
                                 'los fluidos monofásicos con una sola raíz real:',
                                 'PVTsim identifies the phase of a single-phase fluid by comparing '
                                 'the temperature with the true critical point of the mixture. In '
                                 'the variants with the PVTsim database, ThermoPhase applies this '
                                 'criterion to single-phase fluids with a single real root:'),
                                ('eq',
                                 'T < T_{c,mix} \\;\\Rightarrow\\; \\mathrm{L} \\qquad T \\geq '
                                 'T_{c,mix} \\;\\Rightarrow\\; \\mathrm{V}'),
                                ('p',
                                 'donde T<sub>c,mix</sub> es la temperatura crítica verdadera de '
                                 'la mezcla (°R) calculada con la ecuación de estado activa y los '
                                 'k<sub>ij</sub> en uso, y L y V indican líquido y vapor.',
                                 'where T<sub>c,mix</sub> is the true critical temperature of the '
                                 'mixture (°R) computed with the active equation of state and the '
                                 'k<sub>ij</sub> in use, and L and V denote liquid and vapor.'),
                                ('p',
                                 'El punto crítico de la mezcla se obtiene por el método directo '
                                 'de Heidemann y Khalil, que resuelve simultáneamente la condición '
                                 'de estabilidad límite (valor propio mínimo nulo de la matriz de '
                                 'segundas derivadas de la energía de Helmholtz) y la condición de '
                                 'tercer orden. Si el método directo no converge, se toma el punto '
                                 'crítico localizado por el trazado de la envolvente de fases; si '
                                 'tampoco se dispone de él, se emplea como respaldo la temperatura '
                                 'pseudocrítica de Kay, T<sub>pc</sub> = '
                                 'Σz<sub>i</sub>T<sub>c,i</sub>. El cálculo se describe en «Punto '
                                 'crítico de la mezcla».',
                                 'The mixture critical point is obtained by the direct method of '
                                 'Heidemann and Khalil, which simultaneously solves the '
                                 'limit-of-stability condition (zero minimum eigenvalue of the '
                                 'matrix of second derivatives of the Helmholtz energy) and the '
                                 'third-order condition. If the direct method does not converge, '
                                 'the critical point located by the phase envelope trace is used; '
                                 "if that is not available either, Kay's pseudocritical "
                                 'temperature, T<sub>pc</sub> = Σz<sub>i</sub>T<sub>c,i</sub>, is '
                                 'used as fallback. The calculation is described in “Mixture '
                                 'critical point”.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El punto crítico depende solo de la ecuación de estado, de la '
                                 'composición y de los k<sub>ij</sub>; ThermoPhase lo almacena en '
                                 'memoria para cada combinación, de modo que en los barridos de '
                                 'sensibilidad y en los cálculos repetidos sobre el mismo fluido '
                                 'se calcula una sola vez. El uso del punto crítico verdadero, en '
                                 'lugar del pseudocrítico de Kay, es necesario para ubicar '
                                 'correctamente la frontera líquido-vapor de mezclas ricas en '
                                 'metano.',
                                 'The critical point depends only on the equation of state, the '
                                 'composition and the k<sub>ij</sub>; ThermoPhase stores it in '
                                 'memory for each combination, so that in sensitivity sweeps and '
                                 'repeated calculations on the same fluid it is computed only '
                                 "once. Using the true critical point, instead of Kay's "
                                 'pseudocritical temperature, is necessary to place the '
                                 'liquid-vapor boundary of methane-rich mixtures correctly.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Heidemann, R.A. y Khalil, A.M. (1980). The calculation of '
                                 'critical points. <em>AIChE Journal</em>, 26(5), 769–779.',
                                 'Heidemann, R.A. and Khalil, A.M. (1980). The calculation of '
                                 'critical points. <em>AIChE Journal</em>, 26(5), 769–779.'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.')]},
                   {'titulo': ('Identificación en sistemas bifásicos',
                               'Identification in two-phase systems'),
                    'bloques': [('p',
                                 'En un resultado bifásico del flash de hidrocarburos, la fase '
                                 'calculada con la raíz de vapor recibe la etiqueta de vapor. Para '
                                 'mantener la convención de que el vapor es la fase liviana, si el '
                                 'peso molecular del vapor resulta mayor que el del líquido, '
                                 'ThermoPhase intercambia las composiciones y las fracciones de '
                                 'las fases e invierte las constantes de equilibrio:',
                                 'In a two-phase result of the hydrocarbon flash, the phase '
                                 'computed with the vapor root is labeled vapor. To maintain the '
                                 'convention that the vapor is the light phase, if the molecular '
                                 'weight of the vapor is greater than that of the liquid, '
                                 'ThermoPhase swaps the compositions and fractions of the phases '
                                 'and inverts the equilibrium ratios:'),
                                ('eq',
                                 'M_V > M_L \\;\\Rightarrow\\; (x, y) \\leftarrow (y, x), \\quad '
                                 '(\\beta_V, \\beta_L) \\leftarrow (\\beta_L, \\beta_V), \\quad '
                                 'K_i \\leftarrow 1/K_i'),
                                ('p',
                                 'donde M<sub>V</sub> y M<sub>L</sub> son los pesos moleculares de '
                                 'las fases (lb/lbmol). El intercambio se realiza antes del '
                                 'cálculo de fracciones másicas, densidades y viscosidades, de '
                                 'modo que todas las propiedades corresponden a la etiqueta '
                                 'definitiva.',
                                 'where M<sub>V</sub> and M<sub>L</sub> are the molecular weights '
                                 'of the phases (lb/lbmol). The swap is performed before the '
                                 'calculation of mass fractions, densities and viscosities, so '
                                 'that all properties correspond to the final label.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Identificación de fases en el flash trifásico',
                               'Phase identification in the three-phase flash'),
                    'bloques': [('p',
                                 'En el flash trifásico la fase acuosa se identifica por su '
                                 'contenido de agua (fracción molar mayor que 0.5). Las fases de '
                                 'hidrocarburos reciben, dentro del cálculo multifásico, una '
                                 'clasificación preliminar: con dos raíces reales se elige la de '
                                 'menor energía de Gibbs; con una sola raíz, la fase es vapor si Z '
                                 '≥ 0.5, líquido si la temperatura es menor que la pseudocrítica '
                                 'de Kay y, en otro caso, vapor si el volumen molar supera '
                                 '3b<sub>m</sub>.',
                                 'In the three-phase flash the aqueous phase is identified by its '
                                 'water content (mole fraction greater than 0.5). The hydrocarbon '
                                 'phases receive, within the multiphase calculation, a preliminary '
                                 'classification: with two real roots, the one with lower Gibbs '
                                 'energy is chosen; with a single root, the phase is vapor if Z ≥ '
                                 "0.5, liquid if the temperature is below Kay's pseudocritical "
                                 'temperature and, otherwise, vapor if the molar volume exceeds '
                                 '3b<sub>m</sub>.'),
                                ('p',
                                 'En la ventana de equilibrio y en el cálculo de propiedades, la '
                                 'etiqueta definitiva de las fases de hidrocarburos se asigna con '
                                 'el mismo criterio del flash de hidrocarburos, de modo que un '
                                 'fluido recibe la misma identificación con y sin agua libre:',
                                 'In the equilibrium window and in the property calculation, the '
                                 'final label of the hydrocarbon phases is assigned with the same '
                                 'criterion as the hydrocarbon flash, so that a fluid receives the '
                                 'same identification with and without free water:'),
                                ('ul',
                                 [('Una sola fase de hidrocarburos: su composición, renormalizada '
                                   'sin agua, se somete al flash de 13 componentes con la ecuación '
                                   'de estado y los k<sub>ij</sub> de la ventana (análisis de '
                                   'estabilidad, flash y criterio de HYSYS o de PVTsim según la '
                                   'variante). Si ese flash devuelve vapor, la fase se etiqueta '
                                   'como vapor; si devuelve líquido, como líquido; si devuelve dos '
                                   'fases, se conserva la etiqueta del cálculo multifásico.',
                                   'A single hydrocarbon phase: its composition, renormalized '
                                   'without water, is subjected to the 13-component flash with the '
                                   'equation of state and k<sub>ij</sub> of the window (stability '
                                   'analysis, flash and HYSYS or PVTsim criterion according to the '
                                   'variant). If that flash returns vapor, the phase is labeled '
                                   'vapor; if it returns liquid, liquid; if it returns two phases, '
                                   'the label of the multiphase calculation is kept.'),
                                  ('Dos fases de hidrocarburos: la de menor densidad es el vapor. '
                                   'La comparación se realiza con M/Z, proporcional a la densidad '
                                   'másica a igual temperatura y presión; si la fase etiquetada '
                                   'como vapor es la más densa, se intercambian composiciones, '
                                   'fracciones y factores Z.',
                                   'Two hydrocarbon phases: the less dense one is the vapor. The '
                                   'comparison is made with M/Z, which is proportional to the mass '
                                   'density at the same temperature and pressure; if the phase '
                                   'labeled vapor is the denser one, compositions, fractions and Z '
                                   'factors are swapped.')]),
                                ('h3',
                                 'Fusión de separaciones líquido-líquido espurias',
                                 'Merging of spurious liquid-liquid splits'),
                                ('p',
                                 'A temperaturas criogénicas la formulación multifásica puede '
                                 'dividir los hidrocarburos en dos fases de carácter líquido que '
                                 'el flash de hidrocarburos reconoce como un único líquido '
                                 'estable. Se considera que ambas fases son de tipo líquido cuando '
                                 'su volumen molar reducido es menor que 2.5:',
                                 'At cryogenic temperatures the multiphase formulation can split '
                                 'the hydrocarbons into two liquid-like phases that the '
                                 'hydrocarbon flash recognizes as a single stable liquid. Both '
                                 'phases are considered liquid-like when their reduced molar '
                                 'volume is below 2.5:'),
                                ('eq', '\\frac{V}{b_m} = \\frac{Z\\,R\\,T}{P\\,b_m} < 2.5'),
                                ('p',
                                 'donde V es el volumen molar de la fase (ft³/lbmol) y '
                                 'b<sub>m</sub> su covolumen de mezcla (ft³/lbmol). En ese caso '
                                 'las dos fases se combinan con ponderación por β y la composición '
                                 'resultante, sin agua, se evalúa con el flash de 13 componentes; '
                                 'si este la declara íntegramente líquida, las dos fases se '
                                 'sustituyen por un único líquido de hidrocarburos, con fracción '
                                 'igual a la suma de ambas y factor Z recalculado con la raíz de '
                                 'líquido. El balance de materia se conserva exactamente.',
                                 'where V is the molar volume of the phase (ft³/lbmol) and '
                                 'b<sub>m</sub> its mixture covolume (ft³/lbmol). In that case the '
                                 'two phases are combined with β weighting and the resulting '
                                 'water-free composition is evaluated with the 13-component flash; '
                                 'if it declares the composition entirely liquid, the two phases '
                                 'are replaced by a single hydrocarbon liquid, with a fraction '
                                 'equal to the sum of both and a Z factor recomputed with the '
                                 'liquid root. The material balance is preserved exactly.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]}]},
 {'titulo': ('Envolvente de fases', 'Phase envelope'),
  'subsecciones': [{'titulo': ('Definición de la envolvente de fases', 'Phase envelope definition'),
                    'bloques': [('p',
                                 'La envolvente de fases de una mezcla de composición global fija '
                                 'z es el lugar geométrico, en el plano presión-temperatura, de '
                                 'los estados que separan la región monofásica de la región '
                                 'bifásica líquido-vapor. En el interior de la envolvente '
                                 'coexisten dos fases en equilibrio; fuera de ella la mezcla es '
                                 'monofásica (líquido, vapor o fluido supercrítico).',
                                 'The phase envelope of a mixture with fixed overall composition z '
                                 'is the locus, in the pressure-temperature plane, of the states '
                                 'that separate the single-phase region from the vapor-liquid '
                                 'two-phase region. Inside the envelope two phases coexist in '
                                 'equilibrium; outside it the mixture is single-phase (liquid, '
                                 'vapor or supercritical fluid).'),
                                ('p',
                                 'La envolvente consta de dos ramas que se unen en el punto '
                                 'crítico de la mezcla. La curva de burbuja reúne los estados en '
                                 'los que un líquido de composición z está en equilibrio con una '
                                 'cantidad infinitesimal de vapor (fracción de vapor β = 0); la '
                                 'curva de rocío reúne los estados en los que un vapor de '
                                 'composición z está en equilibrio con una cantidad infinitesimal '
                                 'de líquido (β = 1). La cricondenbara (presión máxima) y la '
                                 'cricondenterma (temperatura máxima) delimitan su extensión.',
                                 'The envelope consists of two branches that meet at the mixture '
                                 'critical point. The bubble-point curve gathers the states in '
                                 'which a liquid of composition z is in equilibrium with an '
                                 'infinitesimal amount of vapor (vapor fraction β = 0); the '
                                 'dew-point curve gathers the states in which a vapor of '
                                 'composition z is in equilibrium with an infinitesimal amount of '
                                 'liquid (β = 1). The cricondenbar (maximum pressure) and the '
                                 'cricondentherm (maximum temperature) bound its extent.'),
                                ('p',
                                 'En cada punto de la envolvente la fase existente tiene la '
                                 'composición global z y la fase incipiente, de composición u, '
                                 'satisface la igualdad de fugacidades de cada componente y la '
                                 'condición de que sus fracciones molares sumen la unidad:',
                                 'At every point of the envelope the existing phase has the '
                                 'overall composition z, and the incipient phase, of composition '
                                 'u, satisfies the equality of fugacities of every component and '
                                 'the condition that its mole fractions add up to unity:'),
                                ('eq',
                                 '\\ln K_i + \\ln \\phi_i(u,T,P) - \\ln \\phi_i(z,T,P) = 0 \\quad '
                                 '(i = 1 \\ldots N)'),
                                ('eq', '\\sum_{i} u_i - 1 = \\sum_{i} K_i\\,z_i - 1 = 0'),
                                ('p',
                                 'donde K<sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> es la '
                                 'constante de equilibrio del componente i referida a la fase '
                                 'existente; u<sub>i</sub> y z<sub>i</sub> son las fracciones '
                                 'molares de la fase incipiente y de la fase existente; '
                                 'φ<sub>i</sub> es el coeficiente de fugacidad del componente i en '
                                 'la fase indicada, evaluado con la ecuación de estado activa; T '
                                 'es la temperatura (°R), P la presión (psia) y N el número de '
                                 'componentes presentes.',
                                 'where K<sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> is the '
                                 'equilibrium ratio of component i referred to the existing phase; '
                                 'u<sub>i</sub> and z<sub>i</sub> are the mole fractions of the '
                                 'incipient and existing phases; φ<sub>i</sub> is the fugacity '
                                 'coefficient of component i in the indicated phase, evaluated '
                                 'with the active equation of state; T is the temperature (°R), P '
                                 'the pressure (psia) and N the number of components present.'),
                                ('p',
                                 'Con la definición convencional K<sub>i</sub> = '
                                 'y<sub>i</sub>/x<sub>i</sub> (vapor sobre líquido), las '
                                 'condiciones de saturación toman la forma clásica:',
                                 'With the conventional definition K<sub>i</sub> = '
                                 'y<sub>i</sub>/x<sub>i</sub> (vapor over liquid), the saturation '
                                 'conditions take the classical form:'),
                                ('eq',
                                 '\\sum_{i} z_i\\,K_i^{B} = 1 \\qquad \\sum_{i} '
                                 '\\frac{z_i}{K_i^{D}} = 1'),
                                ('p',
                                 'donde K<sub>i</sub><sup>B</sup> es la constante de equilibrio en '
                                 'un punto de burbuja (líquido de composición z, vapor incipiente) '
                                 'y K<sub>i</sub><sup>D</sup> la constante de equilibrio en un '
                                 'punto de rocío (vapor de composición z, líquido incipiente).',
                                 'where K<sub>i</sub><sup>B</sup> is the equilibrium ratio at a '
                                 'bubble point (liquid of composition z, incipient vapor) and '
                                 'K<sub>i</sub><sup>D</sup> the equilibrium ratio at a dew point '
                                 '(vapor of composition z, incipient liquid).'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'ThermoPhase traza la envolvente con la ecuación de estado cúbica '
                                 'activa (Peng-Robinson o Soave-Redlich-Kwong, en las variantes de '
                                 'HYSYS o de PVTsim) y los coeficientes de interacción binaria '
                                 'k<sub>ij</sub> vigentes. Para mezclas de hidrocarburos dispone '
                                 'de dos métodos seleccionables: Michelsen (predeterminado) y '
                                 'Ziervogel-Poling (alternativo). Una composición de un solo '
                                 'componente se resuelve como curva de saturación, y una mezcla '
                                 'con agua activa se resuelve por el método de '
                                 'Lindeloff-Michelsen.',
                                 'ThermoPhase traces the envelope with the active cubic equation '
                                 'of state (Peng-Robinson or Soave-Redlich-Kwong, in the HYSYS or '
                                 'PVTsim variants) and the current binary interaction coefficients '
                                 'k<sub>ij</sub>. For hydrocarbon mixtures two selectable methods '
                                 'are available: Michelsen (default) and Ziervogel-Poling '
                                 '(alternative). A single-component composition is solved as a '
                                 'saturation curve, and a mixture with water enabled is solved by '
                                 'the Lindeloff-Michelsen method.'),
                                ('p',
                                 'Internamente los puntos se obtienen como pares (P, T) en psia y '
                                 '°R; la interfaz los convierte al sistema de unidades '
                                 'seleccionado. Sobre el diagrama pueden superponerse las líneas '
                                 'de calidad, el mapa de densidad, la curva de formación de '
                                 'hidratos (recortada en 1.05 veces la cricondenbara y en la '
                                 'temperatura mínima de la envolvente) y un punto (P, T) marcado '
                                 'manualmente. La tabla de puntos puede exportarse en formato CSV '
                                 'con la etiqueta de cada curva, la presión en psia y la '
                                 'temperatura en °R y °F.',
                                 'Internally, points are obtained as (P, T) pairs in psia and °R; '
                                 'the interface converts them to the selected unit system. The '
                                 'following can be overlaid on the diagram: quality lines, the '
                                 'density map, the hydrate formation curve (clipped at 1.05 times '
                                 'the cricondenbar and at the minimum envelope temperature) and a '
                                 'manually marked (P, T) point. The point table can be exported in '
                                 'CSV format with the label of each curve, the pressure in psia '
                                 'and the temperature in °R and °F.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.'),
                                ('p',
                                 'Whitson, C.H. y Brulé, M.R. (2000). <em>Phase Behavior</em>. SPE '
                                 'Monograph Series, vol. 20. Society of Petroleum Engineers.',
                                 'Whitson, C.H. and Brulé, M.R. (2000). <em>Phase Behavior</em>. '
                                 'SPE Monograph Series, vol. 20. Society of Petroleum '
                                 'Engineers.')]},
                   {'titulo': ('Método de Michelsen', 'Michelsen method'),
                    'bloques': [('p',
                                 'El método de Michelsen (1980) traza la envolvente como una curva '
                                 'continua en el espacio de las variables logarítmicas. En cada '
                                 'punto resuelve simultáneamente todas las condiciones de '
                                 'equilibrio por Newton-Raphson multivariable y avanza a lo largo '
                                 'de la curva por continuación, con un predictor construido sobre '
                                 'la tangente. Es el método predeterminado de ThermoPhase (opción '
                                 'Michelsen del selector de método).',
                                 'The Michelsen (1980) method traces the envelope as a continuous '
                                 'curve in the space of logarithmic variables. At each point it '
                                 'solves all equilibrium conditions simultaneously by '
                                 'multivariable Newton-Raphson and advances along the curve by '
                                 'continuation, with a predictor built on the tangent. It is the '
                                 'default method in ThermoPhase (Michelsen option of the method '
                                 'selector).'),
                                ('h3', 'Variables y ecuaciones', 'Variables and equations'),
                                ('p',
                                 'El sistema se construye solo con los m componentes presentes '
                                 '(z<sub>i</sub> &gt; 10<sup>−8</sup>), de modo que su dimensión '
                                 'es m + 2 en lugar de N + 2. El vector de incógnitas es:',
                                 'The system is built only with the m components present '
                                 '(z<sub>i</sub> &gt; 10<sup>−8</sup>), so its dimension is m + 2 '
                                 'instead of N + 2. The vector of unknowns is:'),
                                ('eq',
                                 'X = \\left( \\ln K_1, \\ldots, \\ln K_m, \\ln T, \\ln P '
                                 '\\right)'),
                                ('p',
                                 'donde K<sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> es la razón '
                                 'entre la fracción molar del componente i en la fase incipiente y '
                                 'en la fase existente, T la temperatura (°R) y P la presión '
                                 '(psia).',
                                 'where K<sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> is the ratio '
                                 'of the mole fraction of component i in the incipient phase to '
                                 'that in the existing phase, T the temperature (°R) and P the '
                                 'pressure (psia).'),
                                ('eq',
                                 'g_i = \\ln K_i + \\ln \\phi_i(u) - \\ln \\phi_i(z) = 0 \\quad (i '
                                 '= 1 \\ldots m)'),
                                ('eq', 'g_{m+1} = \\sum_{i=1}^{m} z_i\\,K_i - 1 = 0'),
                                ('eq',
                                 'g_{m+2} = t \\cdot \\left(X - X_{\\mathrm{ref}}\\right) - '
                                 '\\Delta s = 0'),
                                ('p',
                                 'donde u<sub>i</sub> = '
                                 'K<sub>i</sub>z<sub>i</sub>/Σ<sub>j</sub>K<sub>j</sub>z<sub>j</sub> '
                                 'es la composición de la fase incipiente; φ<sub>i</sub> se evalúa '
                                 'a la T y P contenidas en X; t es el vector tangente unitario en '
                                 'el último punto convergido X<sub>ref</sub>; y Δs es la longitud '
                                 'del paso, adimensional por estar expresada en variables '
                                 'logarítmicas.',
                                 'where u<sub>i</sub> = '
                                 'K<sub>i</sub>z<sub>i</sub>/Σ<sub>j</sub>K<sub>j</sub>z<sub>j</sub> '
                                 'is the incipient-phase composition; φ<sub>i</sub> is evaluated '
                                 'at the T and P contained in X; t is the unit tangent vector at '
                                 'the last converged point X<sub>ref</sub>; and Δs is the step '
                                 'length, dimensionless because it is expressed in logarithmic '
                                 'variables.'),
                                ('p',
                                 'La misma formulación sirve para las dos ramas: en la de burbuja '
                                 'la fase incipiente es vapor (K<sub>i</sub> &gt; 1 para los '
                                 'componentes livianos) y en la de rocío es líquida (K<sub>i</sub> '
                                 '&lt; 1 para los livianos). El coeficiente de fugacidad de cada '
                                 'composición se evalúa con la raíz de la cúbica de menor energía '
                                 'de Gibbs residual (véase «Selección de raíz por mínima energía '
                                 'de Gibbs»), de modo que el propio modelo define el carácter de '
                                 'cada fase.',
                                 'The same formulation serves both branches: on the bubble branch '
                                 'the incipient phase is vapor (K<sub>i</sub> &gt; 1 for the light '
                                 'components) and on the dew branch it is liquid (K<sub>i</sub> '
                                 '&lt; 1 for the light components). The fugacity coefficient of '
                                 'each composition is evaluated with the cubic root of lowest '
                                 'residual Gibbs energy (see “Root selection by minimum Gibbs '
                                 'energy”), so that the model itself defines the character of each '
                                 'phase.'),
                                ('h3', 'Resolución de cada punto', 'Solution of each point'),
                                ('p',
                                 'Cada punto se resuelve por un método de Newton modificado. El '
                                 'Jacobiano del sistema se calcula por diferencias centrales con '
                                 'un incremento de 10<sup>−6</sup> en cada variable logarítmica y '
                                 'se reutiliza en las iteraciones siguientes mientras la norma del '
                                 'residuo disminuya al menos un 10 % por iteración; en caso '
                                 'contrario se recalcula. La corrección se escala para que su '
                                 'componente de mayor valor absoluto no supere 0.5. El punto se '
                                 'considera convergido cuando la norma infinito del residuo es '
                                 'menor que 10<sup>−9</sup>, con un máximo de 40 iteraciones.',
                                 'Each point is solved by a modified Newton method. The system '
                                 'Jacobian is computed by central differences with an increment of '
                                 '10<sup>−6</sup> in each logarithmic variable and is reused in '
                                 'subsequent iterations as long as the residual norm decreases by '
                                 'at least 10 % per iteration; otherwise it is recomputed. The '
                                 'correction is scaled so that its largest absolute component does '
                                 'not exceed 0.5. The point is considered converged when the '
                                 'infinity norm of the residual is below 10<sup>−9</sup>, with a '
                                 'maximum of 40 iterations.'),
                                ('h3',
                                 'Tangente, especificación y predictor',
                                 'Tangent, specification and predictor'),
                                ('p',
                                 'La tangente se obtiene como el vector nulo del Jacobiano de las '
                                 'm + 1 ecuaciones físicas (igualdad de fugacidades y suma de '
                                 'fracciones), calculado por descomposición en valores singulares: '
                                 'es el vector singular derecho asociado al menor valor singular. '
                                 'Su signo se elige de modo que el producto escalar con la '
                                 'tangente anterior sea positivo, lo que conserva el sentido de '
                                 'avance en los pliegues de la curva (cricondenterma, '
                                 'cricondenbara y cola de rocío de baja presión).',
                                 'The tangent is obtained as the null vector of the Jacobian of '
                                 'the m + 1 physical equations (fugacity equality and sum of '
                                 'fractions), computed by singular value decomposition: it is the '
                                 'right singular vector associated with the smallest singular '
                                 'value. Its sign is chosen so that the dot product with the '
                                 'previous tangent is positive, which preserves the direction of '
                                 'advance through the folds of the curve (cricondentherm, '
                                 'cricondenbar and low-pressure dew tail).'),
                                ('p',
                                 'La ecuación de cierre g<sub>m+2</sub> es una restricción de '
                                 'pseudo-longitud de arco: el nuevo punto debe estar a la '
                                 'distancia Δs, medida sobre la tangente, del punto anterior. Esta '
                                 'especificación no requiere elegir ni cambiar la variable '
                                 'independiente, a diferencia de la especificación de la variable '
                                 'de mayor sensibilidad propuesta por Michelsen (1980), que '
                                 'ThermoPhase emplea en el método de Lindeloff-Michelsen. El '
                                 'primer punto de cada rama se resuelve especificando ln P = ln '
                                 'P<sub>0</sub>. El predictor del punto siguiente es:',
                                 'The closing equation g<sub>m+2</sub> is a pseudo-arc-length '
                                 'constraint: the new point must lie at distance Δs, measured '
                                 'along the tangent, from the previous point. This specification '
                                 'requires neither choosing nor switching the independent '
                                 'variable, unlike the largest-sensitivity-variable specification '
                                 'proposed by Michelsen (1980), which ThermoPhase uses in the '
                                 'Lindeloff-Michelsen method. The first point of each branch is '
                                 'solved by specifying ln P = ln P<sub>0</sub>. The predictor for '
                                 'the next point is:'),
                                ('eq', 'X^{(0)}_{k+1} = X_k + t_k\\,\\Delta s_k'),
                                ('p',
                                 'donde X<sup>(0)</sup><sub>k+1</sub> es la estimación inicial del '
                                 'punto k + 1, X<sub>k</sub> el punto convergido, t<sub>k</sub> su '
                                 'tangente unitaria y Δs<sub>k</sub> el paso vigente.',
                                 'where X<sup>(0)</sup><sub>k+1</sub> is the initial estimate of '
                                 'point k + 1, X<sub>k</sub> the converged point, t<sub>k</sub> '
                                 'its unit tangent and Δs<sub>k</sub> the current step.'),
                                ('p',
                                 'El corrector se acepta si converge y el desplazamiento '
                                 '‖X<sub>k+1</sub> − X<sub>k</sub>‖ está entre 0.2Δs y 4Δs; en '
                                 'caso contrario el paso se reduce a la mitad, hasta 16 veces y '
                                 'con un mínimo de 5·10<sup>−4</sup>. Tres fallos consecutivos '
                                 'terminan la rama. Tras cada punto el paso se ajusta con el '
                                 'coseno del ángulo entre tangentes sucesivas: se multiplica por '
                                 '0.35 si el coseno es menor que 0.2, por 0.7 si es menor que 0.7 '
                                 'y por 1.25 en los demás casos, con paso inicial 0.05 y máximo '
                                 '0.10.',
                                 'The corrector is accepted if it converges and the displacement '
                                 '‖X<sub>k+1</sub> − X<sub>k</sub>‖ lies between 0.2Δs and 4Δs; '
                                 'otherwise the step is halved, up to 16 times and with a minimum '
                                 'of 5·10<sup>−4</sup>. Three consecutive failures terminate the '
                                 'branch. After each point the step is adjusted with the cosine of '
                                 'the angle between successive tangents: it is multiplied by 0.35 '
                                 'if the cosine is below 0.2, by 0.7 if it is below 0.7 and by '
                                 '1.25 otherwise, with an initial step of 0.05 and a maximum of '
                                 '0.10.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Las ramas de burbuja y de rocío se trazan de manera '
                                 'independiente. Cada una arranca en un punto a presión moderada, '
                                 'probando en orden 80, 50, 120, 30, 160, 200, 100, 250, 20, 300 y '
                                 '14.7 psia. La estimación inicial proviene de la correlación de '
                                 'Wilson (véase «Constantes de equilibrio y estimación inicial de '
                                 'Wilson») con las constantes críticas de la ecuación de estado '
                                 'activa: la temperatura se obtiene por bisección de '
                                 'Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 (burbuja) o '
                                 'Σz<sub>i</sub>/K<sub>i</sub><sup>W</sup> = 1 (rocío) entre '
                                 'max(50 °R; 0.3·T<sub>c,min</sub>) y 1600 °R, y las constantes '
                                 'iniciales son K<sub>i</sub><sup>W</sup> en la rama de burbuja y '
                                 '1/K<sub>i</sub><sup>W</sup> en la de rocío.',
                                 'The bubble and dew branches are traced independently. Each '
                                 'starts at a point at moderate pressure, trying in order 80, 50, '
                                 '120, 30, 160, 200, 100, 250, 20, 300 and 14.7 psia. The initial '
                                 'estimate comes from the Wilson correlation (see “Equilibrium '
                                 'ratios and Wilson initial estimate”) with the critical constants '
                                 'of the active equation of state: the temperature is obtained by '
                                 'bisection of Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 '
                                 '(bubble) or Σz<sub>i</sub>/K<sub>i</sub><sup>W</sup> = 1 (dew) '
                                 'between max(50 °R; 0.3·T<sub>c,min</sub>) and 1600 °R, and the '
                                 'initial ratios are K<sub>i</sub><sup>W</sup> on the bubble '
                                 'branch and 1/K<sub>i</sub><sup>W</sup> on the dew branch.'),
                                ('p',
                                 'Se descarta un arranque con Σ(ln K<sub>i</sub>)<sup>2</sup> ≤ '
                                 '0.05, porque ya se encuentra próximo al punto crítico. Desde el '
                                 'arranque cada rama se continúa en los dos sentidos: hacia '
                                 'presiones crecientes, hasta que Σ(ln K<sub>i</sub>)<sup>2</sup> '
                                 '&lt; 1.5·10<sup>−3</sup>, lo que indica la vecindad del punto '
                                 'crítico, y hacia presiones decrecientes, hasta 0.95 × 14.7 psia. '
                                 'El tramo ascendente se recorta en el mínimo de Σ(ln '
                                 'K<sub>i</sub>)<sup>2</sup>. La envolvente se ensambla como rama '
                                 'de burbuja (presión creciente), punto crítico y rama de rocío '
                                 '(presión decreciente). Una rama también se detiene si la curva '
                                 'regresa a su punto de partida tras un arco apreciable o si 50 '
                                 'puntos consecutivos quedan contenidos en una región de diámetro '
                                 'menor que 0.04 en el plano (ln T, ln P).',
                                 'A start with Σ(ln K<sub>i</sub>)<sup>2</sup> ≤ 0.05 is discarded '
                                 'because it already lies close to the critical point. From the '
                                 'start each branch is continued in both directions: toward '
                                 'increasing pressure, until Σ(ln K<sub>i</sub>)<sup>2</sup> &lt; '
                                 '1.5·10<sup>−3</sup>, which indicates the vicinity of the '
                                 'critical point, and toward decreasing pressure, down to 0.95 × '
                                 '14.7 psia. The ascending segment is trimmed at the minimum of '
                                 'Σ(ln K<sub>i</sub>)<sup>2</sup>. The envelope is assembled as '
                                 'bubble branch (increasing pressure), critical point and dew '
                                 'branch (decreasing pressure). A branch also stops if the curve '
                                 'returns to its starting point after an appreciable arc or if 50 '
                                 'consecutive points remain within a region of diameter smaller '
                                 'than 0.04 in the (ln T, ln P) plane.'),
                                ('ul',
                                 [('Mezclas casi ideales (T<sub>c,max</sub>/T<sub>c,min</sub> &lt; '
                                   '1.10 entre los componentes presentes): el paso máximo se '
                                   'reduce a 0.025 y el umbral de parada junto al crítico se eleva '
                                   'a 2·10<sup>−2</sup>; si la rama de rocío cubre menos de la '
                                   'mitad del intervalo de presión de la de burbuja, se toma la '
                                   'rama de burbuja como rama de rocío.',
                                   'Near-ideal mixtures (T<sub>c,max</sub>/T<sub>c,min</sub> &lt; '
                                   '1.10 among the components present): the maximum step is '
                                   'reduced to 0.025 and the stopping threshold near the critical '
                                   'point is raised to 2·10<sup>−2</sup>; if the dew branch covers '
                                   'less than half of the pressure range of the bubble branch, the '
                                   'bubble branch is taken as the dew branch.'),
                                  ('Mezclas de amplio intervalo de ebullición '
                                   '(T<sub>c,max</sub>/T<sub>c,min</sub> &gt; 2.5): se busca la '
                                   'rama de burbuja de alta presión y baja temperatura y se '
                                   'incorpora a la envolvente cuando produce una curva más '
                                   'continua.',
                                   'Wide-boiling mixtures (T<sub>c,max</sub>/T<sub>c,min</sub> '
                                   '&gt; 2.5): the high-pressure, low-temperature bubble branch is '
                                   'searched for and incorporated into the envelope when it yields '
                                   'a more continuous curve.'),
                                  ('Rama de burbuja incompleta (su último punto por debajo de '
                                   '0.85·P<sub>c</sub>): el tramo superior se obtiene continuando '
                                   'la rama de rocío a través del punto crítico; como último '
                                   'recurso se reconstruye por bisección del borde de la región '
                                   'bifásica con el análisis de estabilidad.',
                                   'Incomplete bubble branch (last point below '
                                   '0.85·P<sub>c</sub>): the upper segment is obtained by '
                                   'continuing the dew branch through the critical point; as a '
                                   'last resort it is rebuilt by bisection of the two-phase region '
                                   'boundary with the stability analysis.'),
                                  ('Filtrado geométrico: se eliminan los vértices en los que la '
                                   'curva gira más de unos 114° (coseno menor que −0.40 en el '
                                   'plano ln T–ln P), que corresponden a artefactos numéricos '
                                   'junto al punto crítico; el punto crítico nunca se elimina.',
                                   'Geometric cleanup: vertices where the curve turns by more than '
                                   'about 114° (cosine below −0.40 in the ln T–ln P plane), which '
                                   'correspond to numerical artifacts near the critical point, are '
                                   'removed; the critical point is never removed.'),
                                  ('Respaldo: si la estrategia de dos ramas produce menos de '
                                   'cuatro puntos, se traza una única curva continua en ambos '
                                   'sentidos desde un arranque robusto que se busca en ambas ramas '
                                   'y en 24 presiones entre 10 y 1500 psia.',
                                   'Fallback: if the two-branch strategy produces fewer than four '
                                   'points, a single continuous curve is traced in both directions '
                                   'from a robust start searched for on both branches and at 24 '
                                   'pressures between 10 and 1500 psia.')]),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Método de Ziervogel-Poling', 'Ziervogel-Poling method'),
                    'bloques': [('p',
                                 'Ziervogel y Poling (1983) construyen la envolvente punto a '
                                 'punto: cada punto se obtiene resolviendo una ecuación escalar en '
                                 'una sola variable (temperatura o presión) con la otra fija, y la '
                                 'curva se recorre desplazando la variable fija con un paso '
                                 'pequeño a partir del punto anterior. ThermoPhase lo ofrece como '
                                 'método alternativo (opción Ziervogel-Poling del selector de '
                                 'método).',
                                 'Ziervogel and Poling (1983) build the envelope point by point: '
                                 'each point is obtained by solving a scalar equation in a single '
                                 'variable (temperature or pressure) with the other fixed, and the '
                                 'curve is traversed by moving the fixed variable by a small step '
                                 'from the previous point. ThermoPhase offers it as the '
                                 'alternative method (Ziervogel-Poling option of the method '
                                 'selector).'),
                                ('h3',
                                 'Ecuaciones con composición incipiente fija',
                                 'Equations with fixed incipient composition'),
                                ('eq',
                                 'F_B(T,P) = \\sum_{i} z_i K_i - 1 = 0, \\quad K_i = '
                                 '\\phi_i^{L}(z) / \\phi_i^{V}(y)'),
                                ('eq',
                                 'F_D(T,P) = \\sum_{i} z_i / K_i - 1 = 0, \\quad K_i = '
                                 '\\phi_i^{L}(x) / \\phi_i^{V}(z)'),
                                ('p',
                                 'donde F<sub>B</sub> y F<sub>D</sub> son las funciones objetivo '
                                 'de burbuja y de rocío; y es la composición del vapor incipiente '
                                 '(burbuja) y x la del líquido incipiente (rocío); '
                                 'φ<sub>i</sub><sup>L</sup> se evalúa con la raíz menor de la '
                                 'cúbica y φ<sub>i</sub><sup>V</sup> con la mayor.',
                                 'where F<sub>B</sub> and F<sub>D</sub> are the bubble and dew '
                                 'objective functions; y is the incipient vapor composition '
                                 '(bubble) and x the incipient liquid composition (dew); '
                                 'φ<sub>i</sub><sup>L</sup> is evaluated with the smallest cubic '
                                 'root and φ<sub>i</sub><sup>V</sup> with the largest.'),
                                ('p',
                                 'Mientras se resuelve la ecuación escalar la composición '
                                 'incipiente permanece fija; una vez convergida la variable '
                                 'buscada, esa composición se actualiza con las nuevas constantes '
                                 'de equilibrio:',
                                 'While the scalar equation is being solved the incipient '
                                 'composition is held fixed; once the unknown variable has '
                                 'converged, that composition is updated with the new equilibrium '
                                 'ratios:'),
                                ('eq',
                                 'y_i = \\frac{z_i K_i}{\\sum_{j} z_j K_j} \\qquad x_i = '
                                 '\\frac{z_i / K_i}{\\sum_{j} z_j / K_j}'),
                                ('p',
                                 'donde y<sub>i</sub> es la fracción molar actualizada del vapor '
                                 'incipiente en un punto de burbuja y x<sub>i</sub> la del líquido '
                                 'incipiente en un punto de rocío. El ciclo se repite hasta que la '
                                 'suma de los cambios absolutos de la composición incipiente es '
                                 'menor que 10<sup>−9</sup>, con un máximo de 400 ciclos.',
                                 'where y<sub>i</sub> is the updated mole fraction of the '
                                 'incipient vapor at a bubble point and x<sub>i</sub> that of the '
                                 'incipient liquid at a dew point. The cycle is repeated until the '
                                 'sum of absolute changes of the incipient composition is below '
                                 '10<sup>−9</sup>, with a maximum of 400 cycles.'),
                                ('h3',
                                 'Solución escalar y cercanía al punto crítico',
                                 'Scalar solution and proximity to the critical point'),
                                ('p',
                                 'La ecuación escalar se resuelve por el método de la secante a '
                                 'partir del valor del punto anterior, con una perturbación '
                                 'inicial del 2 % (mínimo 0.05), tolerancia 10<sup>−7</sup> y '
                                 'límites físicos T entre 20 °R y 1.8·T<sub>c,max</sub> y P entre '
                                 '1 psia y 1.5·P<sub>c,max</sub>. Cerca del punto crítico la '
                                 'función se vuelve plana y el método cambia a bisección, que no '
                                 'depende de derivadas. El cambio se decide con el indicador:',
                                 'The scalar equation is solved by the secant method starting from '
                                 'the value of the previous point, with an initial perturbation of '
                                 '2 % (minimum 0.05), tolerance 10<sup>−7</sup> and physical '
                                 'bounds T between 20 °R and 1.8·T<sub>c,max</sub> and P between 1 '
                                 'psia and 1.5·P<sub>c,max</sub>. Near the critical point the '
                                 'function flattens and the method switches to bisection, which '
                                 'does not rely on derivatives. The switch is decided with the '
                                 'indicator:'),
                                ('eq', '\\varpi = \\left| Z_L - Z_V \\right|'),
                                ('p',
                                 'donde Z<sub>L</sub> es el factor de compresibilidad del líquido '
                                 '(raíz menor con la composición líquida) y Z<sub>V</sub> el del '
                                 'vapor (raíz mayor con la composición vapor). Se emplea bisección '
                                 'cuando ϖ ≤ 0.2: primero se busca un intervalo con cambio de '
                                 'signo alrededor del valor actual (paso inicial del 5 %, ampliado '
                                 '1.5 veces en cada intento) y luego se biseca hasta una '
                                 'tolerancia de 10<sup>−5</sup>.',
                                 'where Z<sub>L</sub> is the liquid compressibility factor '
                                 '(smallest root with the liquid composition) and Z<sub>V</sub> '
                                 'that of the vapor (largest root with the vapor composition). '
                                 'Bisection is used when ϖ ≤ 0.2: first an interval with a sign '
                                 'change is searched around the current value (initial step of 5 '
                                 '%, enlarged 1.5 times on each attempt), and then it is bisected '
                                 'to a tolerance of 10<sup>−5</sup>.'),
                                ('h3', 'Arranque y continuación', 'Start and continuation'),
                                ('p',
                                 'El primer punto se calcula a P<sub>0</sub> = 10 psia: la '
                                 'temperatura inicial se obtiene por Newton sobre la ecuación de '
                                 'Wilson Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 a partir de '
                                 '460 °R, la composición incipiente inicial es la de Wilson y el '
                                 'punto se resuelve en T. El segundo punto se obtiene '
                                 'incrementando la temperatura en 5 °R y resolviendo en P. A '
                                 'partir de ahí la variable que se avanza se elige con la '
                                 'pendiente logarítmica local de la curva:',
                                 'The first point is computed at P<sub>0</sub> = 10 psia: the '
                                 'initial temperature is obtained by Newton on the Wilson equation '
                                 'Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 starting from 460 '
                                 "°R, the initial incipient composition is Wilson's, and the point "
                                 'is solved in T. The second point is obtained by increasing the '
                                 'temperature by 5 °R and solving in P. From then on, the variable '
                                 'to be advanced is chosen with the local logarithmic slope of the '
                                 'curve:'),
                                ('eq',
                                 '\\sigma = \\left| \\frac{\\Delta \\ln P}{\\Delta \\ln T} '
                                 '\\right|'),
                                ('p',
                                 'donde σ es la pendiente logarítmica local y Δln P y Δln T son '
                                 'las diferencias entre los dos últimos puntos convergidos. Si σ '
                                 '&gt; 20 (rama casi vertical en el diagrama P-T) se avanza la '
                                 'presión en ΔP = 5 psia y se resuelve la temperatura; si σ &lt; 2 '
                                 '(rama poco inclinada) se avanza la temperatura en ΔT = 5 °R y se '
                                 'resuelve la presión; entre ambos valores se conserva la elección '
                                 'anterior. El sentido de avance es el del último desplazamiento.',
                                 'where σ is the local logarithmic slope and Δln P and Δln T are '
                                 'the differences between the last two converged points. If σ &gt; '
                                 '20 (nearly vertical branch in the P-T diagram) the pressure is '
                                 'advanced by ΔP = 5 psia and the temperature is solved; if σ &lt; '
                                 '2 (shallow branch) the temperature is advanced by ΔT = 5 °R and '
                                 'the pressure is solved; between these values the previous choice '
                                 'is kept. The direction of advance is that of the last '
                                 'displacement.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Las ramas de burbuja y de rocío se trazan por separado, cada una '
                                 'desde 10 psia. Si un punto no converge, el paso se multiplica '
                                 'por 0.5 hasta ocho veces, con un mínimo de 0.3 °R o 0.3 psia. '
                                 'Una rama termina cuando Σ(K<sub>i</sub> − 1)<sup>2</sup> &lt; '
                                 '10<sup>−4</sup>, criterio de llegada al punto crítico, o al '
                                 'alcanzar 400 puntos. La correlación de Wilson usa las constantes '
                                 'críticas de la base de componentes; los coeficientes de '
                                 'fugacidad provienen de la ecuación de estado activa.',
                                 'The bubble and dew branches are traced separately, each from 10 '
                                 'psia. If a point does not converge, the step is multiplied by '
                                 '0.5 up to eight times, with a minimum of 0.3 °R or 0.3 psia. A '
                                 'branch ends when Σ(K<sub>i</sub> − 1)<sup>2</sup> &lt; '
                                 '10<sup>−4</sup>, the criterion for reaching the critical point, '
                                 'or when 400 points are reached. The Wilson correlation uses the '
                                 'critical constants of the component database; the fugacity '
                                 'coefficients come from the active equation of state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Ziervogel, R.G. y Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.',
                                 'Ziervogel, R.G. and Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Flujo de cálculo y selección del método',
                               'Calculation flow and method selection'),
                    'bloques': [('p',
                                 'El método efectivo depende de la composición y de la opción '
                                 'elegida en el selector. La decisión se toma en el orden '
                                 'siguiente:',
                                 'The effective method depends on the composition and on the '
                                 'option chosen in the selector. The decision is made in the '
                                 'following order:'),
                                ('ul',
                                 [('Agua activa (fracción de agua mayor que cero): envolvente de '
                                   'Lindeloff-Michelsen sobre la composición total, '
                                   'independientemente del selector.',
                                   'Water enabled (water fraction greater than zero): '
                                   'Lindeloff-Michelsen envelope on the total composition, '
                                   'regardless of the selector.'),
                                  ('Un solo componente presente: curva de saturación del '
                                   'componente puro, independientemente del selector.',
                                   'A single component present: pure-component saturation curve, '
                                   'regardless of the selector.'),
                                  ('Selector Michelsen y mezcla no casi azeotrópica: método de '
                                   'Michelsen directo. La envolvente se divide en rama de burbuja '
                                   '(puntos hasta el crítico) y rama de rocío (puntos desde el '
                                   'crítico).',
                                   'Michelsen selector and non-near-azeotropic mixture: direct '
                                   'Michelsen method. The envelope is split into bubble branch '
                                   '(points up to the critical point) and dew branch (points from '
                                   'the critical point).'),
                                  ('Selector Ziervogel-Poling: se trazan las dos ramas por '
                                   'Ziervogel-Poling y se mide la distancia euclidiana entre sus '
                                   'extremos en el plano (P en psia, T en °R). Si es menor o igual '
                                   'que 15, las ramas se cierran en el punto medio de sus '
                                   'extremos, que se toma como punto crítico.',
                                   'Ziervogel-Poling selector: both branches are traced by '
                                   'Ziervogel-Poling and the Euclidean distance between their end '
                                   'points is measured in the (P in psia, T in °R) plane. If it is '
                                   'less than or equal to 15, the branches are closed at the '
                                   'midpoint of their end points, which is taken as the critical '
                                   'point.'),
                                  ('Si Ziervogel-Poling no cierra, la envolvente completa se '
                                   'reemplaza por la de Michelsen, siempre que ésta tenga al menos '
                                   '10 puntos y un punto crítico; en caso contrario se conserva el '
                                   'resultado de Ziervogel-Poling con cierre por el punto medio.',
                                   'If Ziervogel-Poling does not close, the whole envelope is '
                                   'replaced by the Michelsen envelope, provided it has at least '
                                   '10 points and a critical point; otherwise the Ziervogel-Poling '
                                   'result is kept with closure at the midpoint.')]),
                                ('h3', 'Mezclas casi azeotrópicas', 'Near-azeotropic mixtures'),
                                ('p',
                                 'Cuando todos los componentes presentes tienen temperaturas '
                                 'críticas próximas (T<sub>c,max</sub>/T<sub>c,min</sub> &lt; '
                                 '1.10, como CO<sub>2</sub> + etano o isopentano + n-pentano), la '
                                 'envolvente es muy estrecha y las constantes de equilibrio son '
                                 'cercanas a la unidad en toda su extensión. Con cualquiera de las '
                                 'dos opciones del selector, ThermoPhase anula en una copia '
                                 'interna los k<sub>ij</sub> de los pares cuya diferencia relativa '
                                 'de T<sub>c</sub> es menor que 10 %, traza la envolvente por '
                                 'Ziervogel-Poling con esos coeficientes y, si no cierra, recurre '
                                 'a Michelsen con los mismos coeficientes; si ninguno produce '
                                 'resultado, aplica el flujo normal con los k<sub>ij</sub> '
                                 'originales. Los k<sub>ij</sub> definidos en la simulación no se '
                                 'modifican.',
                                 'When all components present have close critical temperatures '
                                 '(T<sub>c,max</sub>/T<sub>c,min</sub> &lt; 1.10, such as '
                                 'CO<sub>2</sub> + ethane or isopentane + n-pentane), the envelope '
                                 'is very narrow and the equilibrium ratios are close to unity '
                                 'over its entire extent. With either selector option, ThermoPhase '
                                 'sets to zero, in an internal copy, the k<sub>ij</sub> of the '
                                 'pairs whose relative T<sub>c</sub> difference is below 10 %, '
                                 'traces the envelope by Ziervogel-Poling with those coefficients '
                                 'and, if it does not close, falls back to Michelsen with the same '
                                 'coefficients; if neither produces a result, it applies the '
                                 'normal flow with the original k<sub>ij</sub>. The k<sub>ij</sub> '
                                 'defined in the simulation are not modified.'),
                                ('h3', 'Cálculos derivados', 'Derived calculations'),
                                ('p',
                                 'Las líneas de calidad y el mapa de densidad recalculan siempre '
                                 'la envolvente por el método de Michelsen con la composición '
                                 'vigente, de modo que las curvas superpuestas y la envolvente '
                                 'correspondan al mismo fluido. Al calcular líneas de calidad, el '
                                 'selector se sitúa en Michelsen.',
                                 'Quality lines and the density map always recompute the envelope '
                                 'by the Michelsen method with the current composition, so that '
                                 'the overlaid curves and the envelope correspond to the same '
                                 'fluid. When quality lines are computed, the selector is set to '
                                 'Michelsen.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.'),
                                ('p',
                                 'Ziervogel, R.G. y Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.',
                                 'Ziervogel, R.G. and Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Punto crítico de la mezcla', 'Mixture critical point'),
                    'bloques': [('p',
                                 'El punto crítico de una mezcla es el estado en el que las fases '
                                 'líquida y vapor en equilibrio se vuelven idénticas: coinciden '
                                 'sus composiciones, densidades y demás propiedades, y las '
                                 'constantes de equilibrio tienden a la unidad. En él confluyen '
                                 'las curvas de burbuja y de rocío y todas las líneas de calidad. '
                                 'ThermoPhase lo obtiene por dos vías: un cálculo directo basado '
                                 'en los criterios de Heidemann y Khalil (1980) y su localización '
                                 'sobre la envolvente trazada.',
                                 'The critical point of a mixture is the state at which the '
                                 'equilibrium liquid and vapor phases become identical: their '
                                 'compositions, densities and other properties coincide, and the '
                                 'equilibrium ratios tend to unity. The bubble and dew curves and '
                                 'all quality lines converge there. ThermoPhase obtains it in two '
                                 'ways: a direct calculation based on the Heidemann and Khalil '
                                 '(1980) criteria, and its location on the traced envelope.'),
                                ('h3',
                                 'Método directo de Heidemann-Khalil',
                                 'Heidemann-Khalil direct method'),
                                ('p',
                                 'La formulación emplea la energía de Helmholtz de la cúbica en '
                                 'las variables (T, V, n). El punto crítico satisface dos '
                                 'condiciones: el límite de estabilidad, expresado como un '
                                 'autovalor mínimo nulo de la matriz Q, y la anulación de la forma '
                                 'cúbica C en la dirección del autovector correspondiente:',
                                 'The formulation uses the Helmholtz energy of the cubic equation '
                                 'in the variables (T, V, n). The critical point satisfies two '
                                 'conditions: the stability limit, expressed as a zero minimum '
                                 'eigenvalue of matrix Q, and the vanishing of the cubic form C in '
                                 'the direction of the corresponding eigenvector:'),
                                ('eq',
                                 'Q_{ij} = \\sqrt{z_i z_j}\\,\\left(\\frac{\\partial \\ln '
                                 'f_i}{\\partial n_j}\\right)_{T,V}'),
                                ('eq',
                                 '\\lambda_{\\mathrm{min}}(Q) = 0, \\qquad Q\\,q = '
                                 '\\lambda_{\\mathrm{min}}\\,q, \\qquad \\Delta n_i = '
                                 '\\sqrt{z_i}\\,q_i'),
                                ('eq',
                                 'C = \\sum_{i}\\sum_{j}\\sum_{k} \\Delta n_i\\,\\Delta '
                                 'n_j\\,\\Delta n_k\\,\\frac{\\partial^{3} A}{\\partial '
                                 'n_i\\,\\partial n_j\\,\\partial n_k} = 0'),
                                ('p',
                                 'donde f<sub>i</sub> es la fugacidad del componente i (psia); '
                                 'n<sub>j</sub> los moles del componente j (lbmol), normalizados a '
                                 '1 lbmol total con n = z; λ<sub>min</sub> el menor autovalor de Q '
                                 'y q el autovector unitario asociado; Δn la dirección de '
                                 'perturbación de la composición; A la energía de Helmholtz (BTU).',
                                 'where f<sub>i</sub> is the fugacity of component i (psia); '
                                 'n<sub>j</sub> the moles of component j (lbmol), normalized to 1 '
                                 'lbmol total with n = z; λ<sub>min</sub> the smallest eigenvalue '
                                 'of Q and q the associated unit eigenvector; Δn the composition '
                                 'perturbation direction; A the Helmholtz energy (BTU).'),
                                ('eq',
                                 '\\ln f_i = \\ln\\left(\\frac{n_i R T}{V}\\right) + '
                                 '\\frac{\\partial (A^{\\mathrm{res}}/RT)}{\\partial n_i}'),
                                ('eq',
                                 '\\frac{A^{\\mathrm{res}}}{RT} = -n \\ln\\left(1 - '
                                 '\\frac{B}{V}\\right) - \\frac{D}{RT\\,B\\,(\\delta_1 - '
                                 '\\delta_2)}\\ln\\left(\\frac{V + \\delta_1 B}{V + \\delta_2 '
                                 'B}\\right)'),
                                ('p',
                                 'donde A<sup>res</sup> es la energía de Helmholtz residual; V el '
                                 'volumen total (ft³); n = Σn<sub>i</sub>; B = '
                                 'Σn<sub>i</sub>b<sub>i</sub>; D = '
                                 'Σ<sub>i</sub>Σ<sub>j</sub>n<sub>i</sub>n<sub>j</sub>(a<sub>i</sub>α<sub>i</sub>a<sub>j</sub>α<sub>j</sub>)<sup>1/2</sup>(1 '
                                 '− k<sub>ij</sub>); a<sub>i</sub>α<sub>i</sub> y b<sub>i</sub> '
                                 'son los parámetros de la ecuación de estado activa; '
                                 'δ<sub>1</sub> = 1 + √2 y δ<sub>2</sub> = 1 − √2 para '
                                 'Peng-Robinson, δ<sub>1</sub> = 1 y δ<sub>2</sub> = 0 para '
                                 'Soave-Redlich-Kwong.',
                                 'where A<sup>res</sup> is the residual Helmholtz energy; V the '
                                 'total volume (ft³); n = Σn<sub>i</sub>; B = '
                                 'Σn<sub>i</sub>b<sub>i</sub>; D = '
                                 'Σ<sub>i</sub>Σ<sub>j</sub>n<sub>i</sub>n<sub>j</sub>(a<sub>i</sub>α<sub>i</sub>a<sub>j</sub>α<sub>j</sub>)<sup>1/2</sup>(1 '
                                 '− k<sub>ij</sub>); a<sub>i</sub>α<sub>i</sub> and b<sub>i</sub> '
                                 'are the parameters of the active equation of state; '
                                 'δ<sub>1</sub> = 1 + √2 and δ<sub>2</sub> = 1 − √2 for '
                                 'Peng-Robinson, δ<sub>1</sub> = 1 and δ<sub>2</sub> = 0 for '
                                 'Soave-Redlich-Kwong.'),
                                ('p',
                                 'La matriz Q se obtiene por diferencias finitas hacia adelante de '
                                 'ln f<sub>i</sub> (incremento relativo 10<sup>−6</sup> en '
                                 'n<sub>j</sub>), se simetriza y se diagonaliza; el autovector q '
                                 'se orienta de modo que ΣΔn<sub>i</sub>b<sub>i</sub> &gt; 0, '
                                 'porque la forma cúbica es impar en q. La forma cúbica se evalúa '
                                 'por diferencias centrales de segundo orden a lo largo de Δn:',
                                 'Matrix Q is obtained by forward finite differences of ln '
                                 'f<sub>i</sub> (relative increment 10<sup>−6</sup> in '
                                 'n<sub>j</sub>), symmetrized and diagonalized; the eigenvector q '
                                 'is oriented so that ΣΔn<sub>i</sub>b<sub>i</sub> &gt; 0, because '
                                 'the cubic form is odd in q. The cubic form is evaluated by '
                                 'second-order central differences along Δn:'),
                                ('eq',
                                 'C \\approx \\frac{b(\\varepsilon) + '
                                 'b(-\\varepsilon)}{\\varepsilon^{2}}, \\qquad b(s) = \\Delta n '
                                 '\\cdot \\left[\\ln f(n + s\\,\\Delta n) - \\ln f(n)\\right]'),
                                ('p',
                                 'donde ε = 10<sup>−4</sup> es el tamaño de la perturbación y b(s) '
                                 'la proyección sobre Δn del cambio del vector de logaritmos de '
                                 'fugacidad.',
                                 'where ε = 10<sup>−4</sup> is the perturbation size and b(s) the '
                                 'projection onto Δn of the change of the log-fugacity vector.'),
                                ('p',
                                 'El volumen se expresa como V = k·B. Para cada valor de k se '
                                 'resuelve la temperatura que anula λ<sub>min</sub> por el método '
                                 'de la secante con salvaguardas, partiendo de '
                                 '1.5·Σz<sub>i</sub>T<sub>c,i</sub> y luego de la temperatura del '
                                 'volumen anterior. Se recorren los valores k = 4.0, 3.5, 3.0, '
                                 '2.6, 2.3, 2.0, 1.8, 1.65, 1.5, 1.4, 1.3, 1.2 y 1.12 (del lado '
                                 'gas al lado líquido) hasta acotar un cambio de signo de C, que '
                                 'se refina por regula falsi modificada (Illinois) hasta un cambio '
                                 'relativo de k menor que 10<sup>−11</sup> o |C| &lt; '
                                 '10<sup>−12</sup>. La presión crítica se obtiene de la ecuación '
                                 'de estado:',
                                 'The volume is expressed as V = k·B. For each value of k the '
                                 'temperature that makes λ<sub>min</sub> vanish is solved by the '
                                 'safeguarded secant method, starting from '
                                 '1.5·Σz<sub>i</sub>T<sub>c,i</sub> and then from the temperature '
                                 'of the previous volume. The values k = 4.0, 3.5, 3.0, 2.6, 2.3, '
                                 '2.0, 1.8, 1.65, 1.5, 1.4, 1.3, 1.2 and 1.12 (from the gas side '
                                 'to the liquid side) are scanned until a sign change of C is '
                                 'bracketed, which is refined by modified regula falsi (Illinois) '
                                 'until the relative change of k is below 10<sup>−11</sup> or |C| '
                                 '&lt; 10<sup>−12</sup>. The critical pressure is obtained from '
                                 'the equation of state:'),
                                ('eq',
                                 'P_c = \\frac{R\\,T_c}{V_c - B} - \\frac{D}{(V_c + \\delta_1 '
                                 'B)(V_c + \\delta_2 B)}'),
                                ('p',
                                 'donde T<sub>c</sub> (°R) y V<sub>c</sub> (ft³/lbmol) son la '
                                 'temperatura y el volumen crítico hallados, y B y D se evalúan '
                                 'con la composición z y a T<sub>c</sub>.',
                                 'where T<sub>c</sub> (°R) and V<sub>c</sub> (ft³/lbmol) are the '
                                 'critical temperature and volume found, and B and D are evaluated '
                                 'with composition z and at T<sub>c</sub>.'),
                                ('h3',
                                 'Punto crítico sobre la envolvente',
                                 'Critical point on the envelope'),
                                ('p',
                                 'Sobre la envolvente el punto crítico se localiza como el punto '
                                 'donde las constantes de equilibrio tienden simultáneamente a la '
                                 'unidad:',
                                 'On the envelope the critical point is located as the point where '
                                 'the equilibrium ratios simultaneously tend to unity:'),
                                ('eq', '\\sum_{i} \\left(\\ln K_i\\right)^{2} \\rightarrow 0'),
                                ('p',
                                 'donde K<sub>i</sub> es la constante de equilibrio del componente '
                                 'i entre la fase incipiente y la existente. En el método de '
                                 'Michelsen, cada rama registra el punto de menor Σ(ln '
                                 'K<sub>i</sub>)<sup>2</sup>; si las dos ramas lo encuentran y '
                                 'difieren menos de un 8 % en presión y en temperatura, el punto '
                                 'crítico es su promedio; si difieren más, se toma el de mayor '
                                 'presión. Si ninguna rama baja de Σ(ln K<sub>i</sub>)<sup>2</sup> '
                                 '= 0.5, se adopta la cricondenbara como estimación para separar '
                                 'las ramas de burbuja y de rocío. En Ziervogel-Poling el punto '
                                 'crítico es el punto medio de los extremos de ambas ramas.',
                                 'where K<sub>i</sub> is the equilibrium ratio of component i '
                                 'between the incipient and existing phases. In the Michelsen '
                                 'method each branch records the point of lowest Σ(ln '
                                 'K<sub>i</sub>)<sup>2</sup>; if both branches find it and they '
                                 'differ by less than 8 % in pressure and temperature, the '
                                 'critical point is their average; if they differ more, the one at '
                                 'higher pressure is taken. If neither branch falls below Σ(ln '
                                 'K<sub>i</sub>)<sup>2</sup> = 0.5, the cricondenbar is adopted as '
                                 'the estimate for splitting the bubble and dew branches. In '
                                 'Ziervogel-Poling the critical point is the midpoint of the end '
                                 'points of both branches.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El punto crítico que se dibuja y se informa en la pestaña de '
                                 'envolvente es el localizado sobre la envolvente trazada (o, con '
                                 'agua, el obtenido sobre la línea 3-HC). El método directo '
                                 'proporciona el punto crítico real de la mezcla allí donde se '
                                 'requiere sin trazar la envolvente, en particular en la '
                                 'identificación de la fase de un fluido monofásico según el '
                                 'criterio de PVTsim. Su resultado se guarda por ecuación de '
                                 'estado y composición. Si el método directo no converge se usa el '
                                 'punto crítico de una envolvente de Michelsen de hasta 400 '
                                 'puntos, y si tampoco se obtiene, las propiedades pseudocríticas '
                                 'de Kay.',
                                 'The critical point drawn and reported in the envelope tab is the '
                                 'one located on the traced envelope (or, with water, the one '
                                 'obtained on the 3-HC line). The direct method provides the true '
                                 'mixture critical point wherever it is needed without tracing the '
                                 'envelope, in particular for the phase identification of a '
                                 'single-phase fluid according to the PVTsim criterion. Its result '
                                 'is cached per equation of state and composition. If the direct '
                                 'method does not converge, the critical point of a Michelsen '
                                 'envelope of up to 400 points is used, and if that is not '
                                 "obtained either, Kay's pseudocritical properties."),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Heidemann, R.A. y Khalil, A.M. (1980). The calculation of '
                                 'critical points. <em>AIChE Journal</em>, 26(5), 769–779.',
                                 'Heidemann, R.A. and Khalil, A.M. (1980). The calculation of '
                                 'critical points. <em>AIChE Journal</em>, 26(5), 769–779.'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Cricondenbara y cricondenterma', 'Cricondenbar and cricondentherm'),
                    'bloques': [('p',
                                 'La cricondenbara es la presión máxima de la envolvente: por '
                                 'encima de ella la mezcla no puede ser bifásica a ninguna '
                                 'temperatura. La cricondenterma es la temperatura máxima de la '
                                 'envolvente: por encima de ella la mezcla no puede ser bifásica a '
                                 'ninguna presión. En un gas condensado el punto crítico se sitúa '
                                 'a la izquierda de ambos puntos y entre ellos se extiende la '
                                 'región de condensación retrógrada.',
                                 'The cricondenbar is the maximum pressure of the envelope: above '
                                 'it the mixture cannot be two-phase at any temperature. The '
                                 'cricondentherm is the maximum temperature of the envelope: above '
                                 'it the mixture cannot be two-phase at any pressure. In a gas '
                                 'condensate the critical point lies to the left of both points, '
                                 'and the retrograde condensation region extends between them.'),
                                ('eq',
                                 'P_{cb} = \\mathrm{max}_{k}\\,P_k \\qquad T_{ct} = '
                                 '\\mathrm{max}_{k}\\,T_k'),
                                ('p',
                                 'donde P<sub>cb</sub> es la cricondenbara (psia), T<sub>ct</sub> '
                                 'la cricondenterma (°R) y (P<sub>k</sub>, T<sub>k</sub>) los '
                                 'puntos calculados de las ramas de burbuja y de rocío.',
                                 'where P<sub>cb</sub> is the cricondenbar (psia), T<sub>ct</sub> '
                                 'the cricondentherm (°R) and (P<sub>k</sub>, T<sub>k</sub>) the '
                                 'computed points of the bubble and dew branches.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Ambos valores se toman como los máximos de presión y de '
                                 'temperatura entre todos los puntos calculados de la envolvente, '
                                 'sin interpolación adicional, y se muestran en el panel Puntos '
                                 'especiales en las unidades activas. El mismo panel puede '
                                 'mostrar, en su lugar, la temperatura y la presión del punto '
                                 'crítico. Para un componente puro estos puntos no están definidos '
                                 'y el panel muestra un guion. Con agua activa se calculan sobre '
                                 'las líneas 3-HC y 2-HC. La cricondenbara fija además el límite '
                                 'superior de la curva de hidratos superpuesta (1.05 veces su '
                                 'valor) y participa en la definición del intervalo de presión del '
                                 'mapa de densidad.',
                                 'Both values are taken as the pressure and temperature maxima '
                                 'among all computed envelope points, without additional '
                                 'interpolation, and are displayed in the Special Points panel in '
                                 'the active units. The same panel can display, instead, the '
                                 'temperature and pressure of the critical point. For a pure '
                                 'component these points are not defined and the panel shows a '
                                 'dash. With water enabled they are computed on the 3-HC and 2-HC '
                                 'lines. The cricondenbar also sets the upper limit of the '
                                 'overlaid hydrate curve (1.05 times its value) and takes part in '
                                 'defining the pressure range of the density map.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.'),
                                ('p',
                                 'Whitson, C.H. y Brulé, M.R. (2000). <em>Phase Behavior</em>. SPE '
                                 'Monograph Series, vol. 20. Society of Petroleum Engineers.',
                                 'Whitson, C.H. and Brulé, M.R. (2000). <em>Phase Behavior</em>. '
                                 'SPE Monograph Series, vol. 20. Society of Petroleum '
                                 'Engineers.')]},
                   {'titulo': ('Líneas de calidad', 'Quality lines'),
                    'bloques': [('p',
                                 'Una línea de calidad (isocalidad) es el lugar geométrico de los '
                                 'estados en los que la fracción molar de vapor de la mezcla tiene '
                                 'un valor fijo β, con 0 &lt; β &lt; 1. La curva de burbuja '
                                 'corresponde al límite β = 0 y la de rocío a β = 1; todas las '
                                 'líneas de calidad convergen en el punto crítico, donde ambas '
                                 'fases son idénticas.',
                                 'A quality (iso-quality) line is the locus of the states at which '
                                 'the vapor mole fraction of the mixture has a fixed value β, with '
                                 '0 &lt; β &lt; 1. The bubble curve corresponds to the limit β = 0 '
                                 'and the dew curve to β = 1; all quality lines converge at the '
                                 'critical point, where both phases are identical.'),
                                ('p',
                                 'ThermoPhase traza cada línea con la misma continuación de '
                                 'Michelsen que la envolvente, sustituyendo la ecuación de suma de '
                                 'fracciones por la ecuación de Rachford-Rice a β fijo. Con X = '
                                 '(ln K<sub>1</sub>, …, ln K<sub>m</sub>, ln T, ln P) y '
                                 'K<sub>i</sub> = y<sub>i</sub>/x<sub>i</sub>, el sistema es:',
                                 'ThermoPhase traces each line with the same Michelsen '
                                 'continuation as the envelope, replacing the sum-of-fractions '
                                 'equation with the Rachford-Rice equation at fixed β. With X = '
                                 '(ln K<sub>1</sub>, …, ln K<sub>m</sub>, ln T, ln P) and '
                                 'K<sub>i</sub> = y<sub>i</sub>/x<sub>i</sub>, the system is:'),
                                ('eq',
                                 'g_i = \\ln K_i + \\ln \\phi_i(y) - \\ln \\phi_i(x) = 0 \\quad (i '
                                 '= 1 \\ldots m)'),
                                ('eq',
                                 'g_{m+1} = \\sum_{i} \\frac{z_i\\,(K_i - 1)}{1 + \\beta\\,(K_i - '
                                 '1)} = 0'),
                                ('eq',
                                 'x_i = \\frac{z_i}{1 + \\beta\\,(K_i - 1)}, \\qquad y_i = '
                                 'K_i\\,x_i'),
                                ('p',
                                 'donde x<sub>i</sub> e y<sub>i</sub> son las fracciones molares '
                                 'del componente i en el líquido y en el vapor (normalizadas antes '
                                 'de evaluar los coeficientes de fugacidad), β la fracción molar '
                                 'de vapor especificada y z<sub>i</sub> la composición global. La '
                                 'tercera ecuación del sistema es la restricción de '
                                 'pseudo-longitud de arco descrita para el método de Michelsen.',
                                 'where x<sub>i</sub> and y<sub>i</sub> are the mole fractions of '
                                 'component i in the liquid and in the vapor (normalized before '
                                 'evaluating the fugacity coefficients), β the specified vapor '
                                 'mole fraction and z<sub>i</sub> the overall composition. The '
                                 'third equation of the system is the pseudo-arc-length constraint '
                                 'described for the Michelsen method.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Cada línea arranca a 14.7 psia: la temperatura inicial se '
                                 'obtiene por Newton sobre la ecuación de Rachford-Rice con '
                                 'constantes de Wilson y derivada numérica, y el primer punto se '
                                 'resuelve con ln P especificado. La continuación avanza hacia '
                                 'presiones crecientes con paso inicial 0.06 y máximo 0.10, con el '
                                 'mismo control de paso que la envolvente, y se detiene al llegar '
                                 'al punto crítico, detectado por Σ(ln K<sub>i</sub>)<sup>2</sup> '
                                 '&lt; 2·10<sup>−3</sup> o por una distancia menor que '
                                 '6·10<sup>−3</sup> al punto crítico de la envolvente en el plano '
                                 '(ln T, ln P). Si la línea termina a menos de 0.05 de ese punto '
                                 'en el mismo plano, se le añade el punto crítico como punto '
                                 'final.',
                                 'Each line starts at 14.7 psia: the initial temperature is '
                                 'obtained by Newton on the Rachford-Rice equation with Wilson '
                                 'ratios and a numerical derivative, and the first point is solved '
                                 'with ln P specified. The continuation proceeds toward increasing '
                                 'pressure with an initial step of 0.06 and a maximum of 0.10, '
                                 'with the same step control as the envelope, and stops on '
                                 'reaching the critical point, detected by Σ(ln '
                                 'K<sub>i</sub>)<sup>2</sup> &lt; 2·10<sup>−3</sup> or by a '
                                 'distance smaller than 6·10<sup>−3</sup> to the envelope critical '
                                 'point in the (ln T, ln P) plane. If the line ends within 0.05 of '
                                 'that point in the same plane, the critical point is appended as '
                                 'the final point.'),
                                ('p',
                                 'La interfaz admite hasta cinco líneas, cada una definida por su '
                                 'calidad en porcentaje molar de vapor entre 0 y 100; los extremos '
                                 'se acotan internamente a β = 10<sup>−4</sup> y β = 1 − '
                                 '10<sup>−4</sup>. Cada cálculo recalcula antes la envolvente por '
                                 'Michelsen con la composición vigente. Las líneas de calidad no '
                                 'están disponibles para componentes puros ni para mezclas con '
                                 'agua activa.',
                                 'The interface accepts up to five lines, each defined by its '
                                 'quality as a vapor mole percentage between 0 and 100; the end '
                                 'values are internally bounded to β = 10<sup>−4</sup> and β = 1 − '
                                 '10<sup>−4</sup>. Each calculation first recomputes the envelope '
                                 'by Michelsen with the current composition. Quality lines are not '
                                 'available for pure components or for mixtures with water '
                                 'enabled.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.'),
                                ('p',
                                 'Rachford, H.H. y Rice, J.D. (1952). Procedure for use of '
                                 'electronic digital computers in calculating flash vaporization '
                                 'hydrocarbon equilibrium. <em>Journal of Petroleum '
                                 'Technology</em>, 4(10), 19 (sección 1) y 3 (sección 2).',
                                 'Rachford, H.H. and Rice, J.D. (1952). Procedure for use of '
                                 'electronic digital computers in calculating flash vaporization '
                                 'hydrocarbon equilibrium. <em>Journal of Petroleum '
                                 'Technology</em>, 4(10), 19 (section 1) and 3 (section 2).'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Componente puro: curva de saturación',
                               'Pure component: saturation curve'),
                    'bloques': [('p',
                                 'Para un componente puro las curvas de burbuja y de rocío '
                                 'coinciden en una única curva de saturación, la presión de vapor '
                                 'P<sub>s</sub>(T), que separa el líquido del vapor y termina en '
                                 'el punto crítico (T<sub>c</sub>, P<sub>c</sub>). No existe '
                                 'región bifásica de área, por lo que la cricondenbara, la '
                                 'cricondenterma y las líneas de calidad no están definidas.',
                                 'For a pure component the bubble and dew curves coincide in a '
                                 'single saturation curve, the vapor pressure P<sub>s</sub>(T), '
                                 'which separates liquid from vapor and ends at the critical point '
                                 '(T<sub>c</sub>, P<sub>c</sub>). There is no two-phase region '
                                 'with area, so the cricondenbar, the cricondentherm and the '
                                 'quality lines are not defined.'),
                                ('p',
                                 'A cada temperatura T &lt; T<sub>c</sub> la presión de saturación '
                                 'es aquella en la que se igualan las fugacidades del líquido y '
                                 'del vapor, evaluadas con las raíces líquida y vapor de la '
                                 'cúbica. ThermoPhase la resuelve por Newton sobre ln P:',
                                 'At each temperature T &lt; T<sub>c</sub> the saturation pressure '
                                 'is the one at which the liquid and vapor fugacities, evaluated '
                                 'with the liquid and vapor roots of the cubic, become equal. '
                                 'ThermoPhase solves it by Newton on ln P:'),
                                ('eq',
                                 '\\ln P_{n+1} = \\ln P_n + \\frac{\\ln \\phi_L - \\ln '
                                 '\\phi_V}{Z_V - Z_L}'),
                                ('p',
                                 'donde φ<sub>L</sub> y φ<sub>V</sub> son los coeficientes de '
                                 'fugacidad del componente con las raíces líquida (Z<sub>L</sub>) '
                                 'y vapor (Z<sub>V</sub>) de la ecuación de estado activa a (T, '
                                 'P<sub>n</sub>); la corrección procede de (∂ ln φ/∂ ln '
                                 'P)<sub>T</sub> = Z − 1.',
                                 'where φ<sub>L</sub> and φ<sub>V</sub> are the fugacity '
                                 'coefficients of the component with the liquid (Z<sub>L</sub>) '
                                 'and vapor (Z<sub>V</sub>) roots of the active equation of state '
                                 'at (T, P<sub>n</sub>); the correction follows from (∂ ln φ/∂ ln '
                                 'P)<sub>T</sub> = Z − 1.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La curva se calcula en 200 temperaturas uniformemente espaciadas '
                                 'en temperatura reducida, desde T<sub>r</sub> = 0.999 hasta '
                                 'T<sub>r</sub> = 0.45. El primer punto parte de la estimación de '
                                 'Wilson y cada punto siguiente parte de la presión del anterior; '
                                 'si la cúbica tiene una sola raíz real en la estimación, el '
                                 'cálculo se reinicia desde Wilson. La corrección de ln P se '
                                 'limita a ±2 por iteración y la convergencia se declara cuando '
                                 '|ln φ<sub>L</sub> − ln φ<sub>V</sub>| &lt; 10<sup>−11</sup> '
                                 '(hasta 80 iteraciones). La curva se cierra en las constantes '
                                 'críticas del componente en la ecuación de estado activa.',
                                 'The curve is computed at 200 temperatures evenly spaced in '
                                 'reduced temperature, from T<sub>r</sub> = 0.999 down to '
                                 'T<sub>r</sub> = 0.45. The first point starts from the Wilson '
                                 'estimate and each subsequent point starts from the pressure of '
                                 'the previous one; if the cubic has a single real root at the '
                                 'estimate, the calculation restarts from Wilson. The ln P '
                                 'correction is limited to ±2 per iteration and convergence is '
                                 'declared when |ln φ<sub>L</sub> − ln φ<sub>V</sub>| &lt; '
                                 '10<sup>−11</sup> (up to 80 iterations). The curve is closed at '
                                 'the critical constants of the component in the active equation '
                                 'of state.'),
                                ('eq',
                                 'P_s^{W}(T) = '
                                 'P_c\\,\\exp\\left[5.373\\,(1+\\omega)\\left(1-\\frac{T_c}{T}\\right)\\right]'),
                                ('p',
                                 'donde P<sub>s</sub><sup>W</sup> es la presión de vapor estimada '
                                 'por Wilson (psia) y T<sub>c</sub>, P<sub>c</sub> y ω las '
                                 'constantes del componente en la ecuación de estado activa.',
                                 'where P<sub>s</sub><sup>W</sup> is the Wilson vapor-pressure '
                                 'estimate (psia) and T<sub>c</sub>, P<sub>c</sub> and ω the '
                                 'constants of the component in the active equation of state.'),
                                ('p',
                                 'El diagrama muestra la curva de saturación y el punto crítico. '
                                 'El mapa de densidad está disponible también para componentes '
                                 'puros; en ese caso se omite el análisis de estabilidad y el '
                                 'sombreado de región bifásica, y la curva de saturación actúa '
                                 'como frontera entre líquido y vapor.',
                                 'The diagram shows the saturation curve and the critical point. '
                                 'The density map is also available for pure components; in that '
                                 'case the stability analysis and the two-phase shading are '
                                 'omitted, and the saturation curve acts as the boundary between '
                                 'liquid and vapor.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Envolvente con agua: método de Lindeloff-Michelsen',
                               'Envelope with water: Lindeloff-Michelsen method'),
                    'bloques': [('p',
                                 'Cuando el agua está activa, ThermoPhase traza el diagrama de '
                                 'fases de la mezcla hidrocarburo-agua por el método de Lindeloff '
                                 'y Michelsen (2003), tal como lo hace PVTsim. Todas las líneas se '
                                 'calculan sobre la composición total, incluida el agua, y con el '
                                 'mismo modelo termodinámico del flash trifásico: ecuación de '
                                 'estado cúbica activa con regla de mezcla de Huron-Vidal para los '
                                 'pares agua-hidrocarburo.',
                                 'When water is enabled, ThermoPhase traces the phase diagram of '
                                 'the hydrocarbon-water mixture by the Lindeloff and Michelsen '
                                 '(2003) method, as PVTsim does. All lines are computed on the '
                                 'total composition, water included, and with the same '
                                 'thermodynamic model as the three-phase flash: active cubic '
                                 'equation of state with the Huron-Vidal mixing rule for '
                                 'water-hydrocarbon pairs.'),
                                ('h3', 'Líneas del diagrama', 'Diagram lines'),
                                ('ul',
                                 [('2-HC (rocío HC): frontera entre la región monofásica y la '
                                   'bifásica en la que la fase incipiente es de hidrocarburo. Es '
                                   'la línea de rocío o de burbuja de hidrocarburos del fluido '
                                   'total, en ausencia de fase acuosa.',
                                   '2-HC (HC dew line): boundary between the single-phase region '
                                   'and the two-phase region in which the incipient phase is a '
                                   'hydrocarbon phase. It is the hydrocarbon dew or bubble line of '
                                   'the total fluid, in the absence of an aqueous phase.'),
                                  ('2-Aq (rocío de agua): frontera entre la región monofásica y la '
                                   'bifásica en la que la fase incipiente es acuosa. Corresponde '
                                   'al punto de rocío de agua del fluido.',
                                   '2-Aq (water dew line): boundary between the single-phase '
                                   'region and the two-phase region in which the incipient phase '
                                   'is aqueous. It corresponds to the water dew point of the '
                                   'fluid.'),
                                  ('3-Aq (aparición de agua): frontera entre la región bifásica '
                                   'vapor + líquido de hidrocarburo y la región trifásica, con '
                                   'fase acuosa incipiente.',
                                   '3-Aq (water appearance): boundary between the vapor + '
                                   'hydrocarbon liquid two-phase region and the three-phase '
                                   'region, with an incipient aqueous phase.'),
                                  ('3-HC (límite trifásico HC): frontera entre la región bifásica '
                                   'hidrocarburo + fase acuosa y la región trifásica, con una fase '
                                   'de hidrocarburo incipiente. Delimita, en presencia de agua '
                                   'libre, la región en la que coexisten vapor y líquido de '
                                   'hidrocarburo, y contiene el punto crítico de las fases de '
                                   'hidrocarburo.',
                                   '3-HC (HC three-phase limit): boundary between the hydrocarbon '
                                   '+ aqueous two-phase region and the three-phase region, with an '
                                   'incipient hydrocarbon phase. In the presence of free water, it '
                                   'bounds the region where hydrocarbon vapor and liquid coexist, '
                                   'and it contains the critical point of the hydrocarbon '
                                   'phases.')]),
                                ('h3', 'Línea de rocío (2-HC y 2-Aq)', 'Dew line (2-HC and 2-Aq)'),
                                ('p',
                                 'La línea de rocío se traza con las ecuaciones de la envolvente '
                                 '(igualdad de fugacidades entre z y la fase incipiente u, y '
                                 'Σu<sub>i</sub> = 1) más una ecuación de especificación, en las '
                                 'variables X = (ln K, ln T, ln P). La raíz de la cúbica se asigna '
                                 'así: la fase acuosa toma la raíz líquida; entre dos fases de '
                                 'hidrocarburo, la de mayor covolumen de mezcla toma la raíz '
                                 'líquida. El primer punto se busca a P<sub>0</sub> = 0.5 atm con '
                                 'los dos tipos de fase incipiente, inicializados con la '
                                 'aproximación de Wilson modificada:',
                                 'The dew line is traced with the envelope equations (fugacity '
                                 'equality between z and the incipient phase u, and Σu<sub>i</sub> '
                                 '= 1) plus a specification equation, in the variables X = (ln K, '
                                 'ln T, ln P). The cubic root is assigned as follows: the aqueous '
                                 'phase takes the liquid root; between two hydrocarbon phases, the '
                                 'one with the larger mixture covolume takes the liquid root. The '
                                 'first point is sought at P<sub>0</sub> = 0.5 atm with both types '
                                 'of incipient phase, initialized with the modified Wilson '
                                 'approximation:'),
                                ('eq', '\\ln \\phi_i^{l} \\approx \\ln K_i^{W} + 10\\,\\delta_i'),
                                ('p',
                                 'donde φ<sub>i</sub><sup>l</sup> es el coeficiente de fugacidad '
                                 'aproximado del componente i en la fase incipiente, '
                                 'K<sub>i</sub><sup>W</sup> la constante de Wilson y δ<sub>i</sub> '
                                 '= 1 para los componentes ajenos a esa fase (el agua si la fase '
                                 'incipiente es de hidrocarburo; los hidrocarburos si es acuosa) y '
                                 '0 en los demás casos.',
                                 'where φ<sub>i</sub><sup>l</sup> is the approximate fugacity '
                                 'coefficient of component i in the incipient phase, '
                                 'K<sub>i</sub><sup>W</sup> the Wilson ratio and δ<sub>i</sub> = 1 '
                                 'for components foreign to that phase (water if the incipient '
                                 'phase is a hydrocarbon phase; the hydrocarbons if it is aqueous) '
                                 'and 0 otherwise.'),
                                ('p',
                                 'Para cada tipo se localiza la raíz de mayor temperatura entre '
                                 '150 y 1500 °R, se refina por Newton parcial en T y luego por '
                                 'Newton completo, y se conserva el tipo que da la temperatura más '
                                 'alta. La línea se continúa hacia presiones crecientes y en cada '
                                 'punto se aplica la prueba de estabilidad de la composición total '
                                 'frente a una fase del otro tipo:',
                                 'For each type the highest-temperature root between 150 and 1500 '
                                 '°R is located, refined by partial Newton in T and then by full '
                                 'Newton, and the type giving the highest temperature is kept. The '
                                 'line is continued toward increasing pressure, and at each point '
                                 'the stability test of the total composition against a phase of '
                                 'the other type is applied:'),
                                ('eq',
                                 'tm = -\\ln \\sum_{i} W_i, \\qquad \\ln W_i = \\ln z_i + \\ln '
                                 '\\phi_i(z) - \\ln \\phi_i(y)'),
                                ('p',
                                 'donde W<sub>i</sub> son los números de moles de la fase de '
                                 'prueba en el punto estacionario, y = W/ΣW su composición y tm la '
                                 'distancia al plano tangente modificada; tm &lt; 0 indica '
                                 'inestabilidad.',
                                 'where W<sub>i</sub> are the mole numbers of the trial phase at '
                                 'the stationary point, y = W/ΣW its composition and tm the '
                                 'modified tangent plane distance; tm &lt; 0 indicates '
                                 'instability.'),
                                ('h3', 'Punto trifásico', 'Three-phase point'),
                                ('p',
                                 'Al detectarse inestabilidad se resuelve el punto trifásico, en '
                                 'el que la composición total z está en equilibrio con dos fases '
                                 'incipientes u y x de distinto tipo:',
                                 'When instability is detected the three-phase point is solved, at '
                                 'which the total composition z is in equilibrium with two '
                                 'incipient phases u and x of different type:'),
                                ('eq',
                                 '\\ln K^{u}_i + \\ln \\phi_i(u) - \\ln \\phi_i(z) = 0, \\qquad '
                                 '\\ln K^{x}_i + \\ln \\phi_i(x) - \\ln \\phi_i(z) = 0'),
                                ('eq', '\\sum_{i} u_i - 1 = 0, \\qquad \\sum_{i} x_i - 1 = 0'),
                                ('p',
                                 'donde K<sup>u</sup><sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> y '
                                 'K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/z<sub>i</sub>; las '
                                 'incógnitas son los 2n logaritmos de K, ln T y ln P. La línea de '
                                 'rocío se recorta en ese punto y se continúa desde él con el otro '
                                 'tipo de fase incipiente, hasta cuatro tramos.',
                                 'where K<sup>u</sup><sub>i</sub> = u<sub>i</sub>/z<sub>i</sub> '
                                 'and K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/z<sub>i</sub>; the '
                                 'unknowns are the 2n logarithms of K, ln T and ln P. The dew line '
                                 'is trimmed at that point and continued from it with the other '
                                 'type of incipient phase, up to four segments.'),
                                ('h3',
                                 'Líneas trifásicas (3-Aq y 3-HC)',
                                 'Three-phase lines (3-Aq and 3-HC)'),
                                ('p',
                                 'Desde cada punto trifásico nacen dos líneas trifásicas, una con '
                                 'fase incipiente acuosa (3-Aq) y otra con fase incipiente de '
                                 'hidrocarburo (3-HC). La fase incipiente u se toma como '
                                 'referencia de las constantes de equilibrio y β es la fracción de '
                                 'la fase y entre las dos fases existentes:',
                                 'From each three-phase point two three-phase lines emanate, one '
                                 'with an incipient aqueous phase (3-Aq) and one with an incipient '
                                 'hydrocarbon phase (3-HC). The incipient phase u is taken as the '
                                 'reference for the equilibrium ratios, and β is the fraction of '
                                 'phase y among the two existing phases:'),
                                ('eq',
                                 'u_i = \\frac{z_i}{\\beta K^{y}_i + (1-\\beta) K^{x}_i}, \\qquad '
                                 'y_i = K^{y}_i u_i, \\qquad x_i = K^{x}_i u_i'),
                                ('eq',
                                 '\\ln K^{y}_i + \\ln \\phi_i(y) - \\ln \\phi_i(u) = 0, \\qquad '
                                 '\\ln K^{x}_i + \\ln \\phi_i(x) - \\ln \\phi_i(u) = 0'),
                                ('eq',
                                 '\\sum_{i} u_i - 1 = 0, \\qquad \\sum_{i} \\left(y_i - '
                                 'x_i\\right) = 0'),
                                ('p',
                                 'donde y y x son las dos fases existentes; '
                                 'K<sup>y</sup><sub>i</sub> = y<sub>i</sub>/u<sub>i</sub> y '
                                 'K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/u<sub>i</sub>; β es '
                                 'adimensional y las incógnitas son los 2n logaritmos de K, ln T, '
                                 'ln P y β, más una ecuación de especificación. Cada línea arranca '
                                 'con β = 1 (y = z) y β especificado en sentido decreciente; '
                                 'termina cuando β sale del intervalo [0, 1], en cuyo caso el '
                                 'último punto se sustituye por la solución exacta con β en el '
                                 'límite, cuando llega a otro punto trifásico o cuando sale de los '
                                 'límites de presión y temperatura.',
                                 'where y and x are the two existing phases; '
                                 'K<sup>y</sup><sub>i</sub> = y<sub>i</sub>/u<sub>i</sub> and '
                                 'K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/u<sub>i</sub>; β is '
                                 'dimensionless and the unknowns are the 2n logarithms of K, ln T, '
                                 'ln P and β, plus a specification equation. Each line starts with '
                                 'β = 1 (y = z) and β specified in decreasing direction; it ends '
                                 'when β leaves the interval [0, 1], in which case the last point '
                                 'is replaced by the exact solution with β at the limit, when it '
                                 'reaches another three-phase point, or when it leaves the '
                                 'pressure and temperature limits.'),
                                ('h3',
                                 'Continuación con especificación de mayor sensibilidad',
                                 'Continuation with largest-sensitivity specification'),
                                ('p',
                                 'Todas las líneas se trazan con la continuación original de '
                                 'Michelsen (1980). En cada punto convergido se calcula el vector '
                                 'de sensibilidades resolviendo:',
                                 'All lines are traced with the original Michelsen (1980) '
                                 'continuation. At each converged point the sensitivity vector is '
                                 'computed by solving:'),
                                ('eq', 'J\\,\\frac{dX}{dS} = e_{\\mathrm{spec}}'),
                                ('p',
                                 'donde J es el Jacobiano del sistema completo (con la fila de '
                                 'especificación), S la variable especificada y e<sub>spec</sub> '
                                 'el vector unitario de la fila de especificación. La nueva '
                                 'variable especificada es la de mayor |dX/dS|; el predictor es X '
                                 '+ (dX/dS)·ΔS, con dX/dS normalizado por su componente mayor. El '
                                 'paso inicial es 0.03 y el máximo 0.12; se multiplica por 1.4 si '
                                 'Newton converge en tres iteraciones o menos, por 0.6 si requiere '
                                 'más de seis, y se reduce a la mitad ante un fallo, hasta '
                                 '10<sup>−5</sup>. Newton usa Jacobiano numérico por diferencias '
                                 'hacia adelante, lo reutiliza mientras el residuo se reduzca al '
                                 'menos a la cuarta parte y aplica búsqueda lineal por mitades.',
                                 'where J is the Jacobian of the complete system (with the '
                                 'specification row), S the specified variable and '
                                 'e<sub>spec</sub> the unit vector of the specification row. The '
                                 'new specified variable is the one with the largest |dX/dS|; the '
                                 'predictor is X + (dX/dS)·ΔS, with dX/dS normalized by its '
                                 'largest component. The initial step is 0.03 and the maximum '
                                 '0.12; it is multiplied by 1.4 if Newton converges in three '
                                 'iterations or fewer, by 0.6 if more than six are needed, and '
                                 'halved upon failure, down to 10<sup>−5</sup>. Newton uses a '
                                 'forward-difference numerical Jacobian, reuses it as long as the '
                                 'residual drops to at least one quarter, and applies a halving '
                                 'line search.'),
                                ('p',
                                 'En la línea 3-HC, cuando la mayor |ln K| cae por debajo de 0.04 '
                                 'mientras disminuye, la continuación cruza el punto crítico de '
                                 'las fases de hidrocarburo especificando el ln K dominante igual '
                                 'a menos su valor actual, con un predictor polinómico cúbico '
                                 'construido con los últimos cuatro puntos. El punto crítico se '
                                 'obtiene por ajuste cúbico de ln P y ln T frente al ln K '
                                 'dominante, evaluado en ln K = 0.',
                                 'On the 3-HC line, when the largest |ln K| falls below 0.04 while '
                                 'decreasing, the continuation crosses the critical point of the '
                                 'hydrocarbon phases by specifying the dominant ln K equal to '
                                 'minus its current value, with a cubic polynomial predictor built '
                                 'from the last four points. The critical point is obtained by a '
                                 'cubic fit of ln P and ln T against the dominant ln K, evaluated '
                                 'at ln K = 0.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los límites de trazado son 0.4 atm y 15000 psia en presión, y '
                                 '150 °R en la línea de rocío y 250 °R en las líneas trifásicas en '
                                 'temperatura. Si no aparece ningún punto trifásico sobre la línea '
                                 'de rocío, se busca una región trifásica aislada por medio del '
                                 'flash trifásico en 12 presiones bajo la línea de rocío y se '
                                 'traza su contorno en ambos sentidos. La línea 2-Aq se recorta en '
                                 '1.05 veces la mayor presión de las demás líneas. En el diagrama '
                                 'se dibujan las cuatro líneas con leyendas propias (Rocío HC, '
                                 'Límite 3 fases HC, Aparición de agua y Rocío de agua) y el punto '
                                 'crítico; para los puntos especiales y la curva de hidratos, la '
                                 'línea 3-HC cumple el papel de rama de burbuja y la 2-HC el de '
                                 'rama de rocío. Las líneas de calidad y el mapa de densidad no '
                                 'están disponibles con agua activa.',
                                 'The tracing limits are 0.4 atm and 15000 psia in pressure, and '
                                 '150 °R on the dew line and 250 °R on the three-phase lines in '
                                 'temperature. If no three-phase point appears on the dew line, an '
                                 'isolated three-phase region is searched for by means of the '
                                 'three-phase flash at 12 pressures below the dew line, and its '
                                 'contour is traced in both directions. The 2-Aq line is clipped '
                                 'at 1.05 times the highest pressure of the other lines. The '
                                 'diagram shows the four lines with their own legends (HC Dew, HC '
                                 'Three-Phase Limit, Water Appearance and Water Dew) and the '
                                 'critical point; for the special points and the hydrate curve, '
                                 'the 3-HC line plays the role of the bubble branch and the 2-HC '
                                 'line that of the dew branch. Quality lines and the density map '
                                 'are not available with water enabled.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lindeloff, N. y Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.',
                                 'Lindeloff, N. and Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Mezcla binaria hidrocarburo + agua',
                               'Binary hydrocarbon + water mixture'),
                    'bloques': [('p',
                                 'En una mezcla de un solo hidrocarburo con agua, la coexistencia '
                                 'de tres fases tiene un único grado de libertad según la regla de '
                                 'las fases de Gibbs, de modo que la región trifásica degenera en '
                                 'una línea univariante V-L-Aq, análoga a la curva de presión de '
                                 'vapor de un componente puro:',
                                 'In a mixture of a single hydrocarbon with water, the coexistence '
                                 'of three phases has a single degree of freedom according to the '
                                 'Gibbs phase rule, so the three-phase region degenerates into a '
                                 'univariant V-L-Aq line, analogous to the vapor-pressure curve of '
                                 'a pure component:'),
                                ('eq', 'F = C - \\pi + 2 = 2 - 3 + 2 = 1'),
                                ('p',
                                 'donde F es el número de grados de libertad, C = 2 el número de '
                                 'componentes y π = 3 el número de fases. La línea termina en el '
                                 'punto crítico final superior (UCEP), donde el líquido de '
                                 'hidrocarburo y el vapor se vuelven idénticos en presencia de la '
                                 'fase acuosa.',
                                 'where F is the number of degrees of freedom, C = 2 the number of '
                                 'components and π = 3 the number of phases. The line ends at the '
                                 'upper critical end point (UCEP), where the hydrocarbon liquid '
                                 'and the vapor become identical in the presence of the aqueous '
                                 'phase.'),
                                ('p',
                                 'A cada temperatura la línea se obtiene resolviendo la igualdad '
                                 'de fugacidades entre el vapor y, el líquido de hidrocarburo x y '
                                 'la fase acuosa x<sup>Aq</sup>:',
                                 'At each temperature the line is obtained by solving the fugacity '
                                 'equality between the vapor y, the hydrocarbon liquid x, and the '
                                 'aqueous phase x<sup>Aq</sup>:'),
                                ('eq',
                                 '\\ln \\frac{x_i}{y_i} + \\ln \\phi_i^{L}(x) - \\ln '
                                 '\\phi_i^{V}(y) = 0, \\qquad \\ln \\frac{x^{\\mathrm{Aq}}_i}{y_i} '
                                 '+ \\ln \\phi_i^{L}(x^{\\mathrm{Aq}}) - \\ln \\phi_i^{V}(y) = 0'),
                                ('eq',
                                 '\\sum_{i} x_i - 1 = 0, \\qquad \\sum_{i} x^{\\mathrm{Aq}}_i - 1 '
                                 '= 0'),
                                ('p',
                                 'donde las incógnitas son ln(x<sub>i</sub>/y<sub>i</sub>) y '
                                 'ln(x<sup>Aq</sup><sub>i</sub>/y<sub>i</sub>) para los dos '
                                 'componentes, la fracción de hidrocarburo en el vapor y ln P; '
                                 'φ<sup>V</sup> se evalúa con la raíz de vapor y φ<sup>L</sup> con '
                                 'la raíz líquida.',
                                 'where the unknowns are ln(x<sub>i</sub>/y<sub>i</sub>) and '
                                 'ln(x<sup>Aq</sup><sub>i</sub>/y<sub>i</sub>) for both '
                                 'components, the hydrocarbon fraction in the vapor and ln P; '
                                 'φ<sup>V</sup> is evaluated with the vapor root and φ<sup>L</sup> '
                                 'with the liquid root.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La estimación inicial toma P como la suma de las presiones de '
                                 'vapor de Wilson del hidrocarburo y del agua, a la temperatura en '
                                 'la que la del hidrocarburo alcanza unos 50 psia (sin superar '
                                 '0.95·T<sub>c</sub> del hidrocarburo). Desde allí la línea se '
                                 'recorre en temperatura con paso inicial de 2 °R (ampliado 1.3 '
                                 'veces hasta 10 °R y reducido a la mitad ante un fallo): hacia '
                                 'abajo hasta 0.4 atm o 250 °R, y hacia arriba hasta que el '
                                 'líquido de hidrocarburo y el vapor se igualan; cuando '
                                 'max|ln(x<sub>i</sub>/y<sub>i</sub>)| &lt; 0.02 el paso se limita '
                                 'a 0.2 °R. El UCEP se obtiene por extrapolación cuadrática de T y '
                                 'ln P frente al ln(x<sub>i</sub>/y<sub>i</sub>) dominante hasta '
                                 'cero, con los últimos cuatro puntos.',
                                 'The initial estimate takes P as the sum of the Wilson vapor '
                                 'pressures of the hydrocarbon and of water, at the temperature '
                                 'where the hydrocarbon value reaches about 50 psia (without '
                                 'exceeding 0.95·T<sub>c</sub> of the hydrocarbon). From there the '
                                 'line is traversed in temperature with an initial step of 2 °R '
                                 '(enlarged 1.3 times up to 10 °R and halved upon failure): '
                                 'downward to 0.4 atm or 250 °R, and upward until the hydrocarbon '
                                 'liquid and the vapor become equal; when '
                                 'max|ln(x<sub>i</sub>/y<sub>i</sub>)| &lt; 0.02 the step is '
                                 'limited to 0.2 °R. The UCEP is obtained by quadratic '
                                 'extrapolation of T and ln P against the dominant '
                                 'ln(x<sub>i</sub>/y<sub>i</sub>) to zero, using the last four '
                                 'points.'),
                                ('p',
                                 'En este caso no se trazan las líneas trifásicas del caso '
                                 'general. La línea V-L-Aq se muestra con la leyenda Línea '
                                 'trifásica V-L-Aq en lugar de la línea 3-HC, y el UCEP se informa '
                                 'como punto crítico del diagrama junto con las líneas 2-HC y '
                                 '2-Aq.',
                                 'In this case the three-phase lines of the general case are not '
                                 'traced. The V-L-Aq line is shown with the legend Three-phase '
                                 'line V-L-Aq in place of the 3-HC line, and the UCEP is reported '
                                 'as the critical point of the diagram together with the 2-HC and '
                                 '2-Aq lines.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lindeloff, N. y Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.',
                                 'Lindeloff, N. and Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Mapa de densidad sobre el diagrama de fases',
                               'Density map on the phase diagram'),
                    'bloques': [('p',
                                 'El mapa de densidad colorea el fondo del diagrama P-T con la '
                                 'densidad másica de la fase estable en cada punto, a la manera de '
                                 'los diagramas de Whitson. Permite apreciar la transición '
                                 'continua entre estados de tipo líquido y de tipo gas fuera de la '
                                 'envolvente. Se activa con la opción Mostrar mapa de densidad, '
                                 'que recalcula la envolvente por Michelsen con la composición '
                                 'vigente antes de calcular el mapa.',
                                 'The density map colors the background of the P-T diagram with '
                                 'the mass density of the stable phase at each point, in the '
                                 "manner of Whitson's diagrams. It shows the continuous transition "
                                 'between liquid-like and gas-like states outside the envelope. It '
                                 'is enabled with the Show density map option, which recomputes '
                                 'the envelope by Michelsen with the current composition before '
                                 'computing the map.'),
                                ('p',
                                 'La densidad de cada nodo se obtiene de la ecuación de estado:',
                                 'The density at each node is obtained from the equation of '
                                 'state:'),
                                ('eq', '\\rho = \\frac{P\\,M}{Z\\,R\\,T}'),
                                ('p',
                                 'donde ρ es la densidad (lb/ft³), M el peso molecular de la '
                                 'mezcla (lb/lbmol), Z el factor de compresibilidad de la raíz '
                                 'seleccionada, R = 10.7316 psia·ft³/(lbmol·°R), P en psia y T en '
                                 '°R. Cuando la cúbica tiene dos raíces reales se selecciona la de '
                                 'menor energía de Gibbs (véase «Selección de raíz por mínima '
                                 'energía de Gibbs»):',
                                 'where ρ is the density (lb/ft³), M the mixture molecular weight '
                                 '(lb/lbmol), Z the compressibility factor of the selected root, R '
                                 '= 10.7316 psia·ft³/(lbmol·°R), P in psia, and T in °R. When the '
                                 'cubic has two real roots, the one with lower Gibbs energy is '
                                 'selected (see “Root selection by minimum Gibbs energy”):'),
                                ('eq',
                                 '\\frac{G}{RT} \\propto \\sum_{i} z_i '
                                 '\\ln\\left(z_i\\,\\phi_i\\right)'),
                                ('p',
                                 'donde φ<sub>i</sub> se evalúa con cada raíz. Con una sola raíz '
                                 'real, el carácter líquido o vapor se decide con el algoritmo de '
                                 'identificación de HYSYS (véase «Algoritmo de identificación de '
                                 'HYSYS»), cualquiera que sea la ecuación de estado activa.',
                                 'where φ<sub>i</sub> is evaluated with each root. With a single '
                                 'real root, the liquid or vapor character is decided with the '
                                 'HYSYS identification algorithm (see “HYSYS identification '
                                 'algorithm”), whatever the active equation of state.'),
                                ('h3', 'Densidad del líquido', 'Liquid density'),
                                ('p',
                                 'La densidad de los nodos de tipo líquido sigue el método de '
                                 'densidad seleccionado en el programa. Con COSTALD se usa la '
                                 'correlación de Hankinson-Thomson con corrección por presión para '
                                 'T<sub>r</sub> ≤ 0.95, la ecuación de estado para T<sub>r</sub> ≥ '
                                 '1 y, entre ambas, la interpolación cuadrática descrita en «Banda '
                                 'de transición y régimen supercrítico». Con los métodos Peneloux '
                                 'y EOS se usa el volumen de la ecuación de estado, con traslado '
                                 'de Peneloux en el primer caso.',
                                 'The density of liquid-like nodes follows the density method '
                                 'selected in the program. With COSTALD, the Hankinson-Thomson '
                                 'correlation with pressure correction is used for T<sub>r</sub> ≤ '
                                 '0.95, the equation of state for T<sub>r</sub> ≥ 1, and, in '
                                 'between, the quadratic interpolation described in “Transition '
                                 'band and supercritical regime”. With the Peneloux and EOS '
                                 'methods the equation-of-state volume is used, shifted by '
                                 'Peneloux in the first case.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La malla es de 100 × 100 nodos (al menos 150 × 150 para un '
                                 'componente puro). La temperatura va de max(50 °R; '
                                 'T<sub>min</sub> − 50 °R) a T<sub>max</sub> + 100 °R, donde '
                                 'T<sub>min</sub> y T<sub>max</sub> son los extremos de la '
                                 'envolvente, y la presión de 10 psia a 1.5 veces el mayor valor '
                                 'entre la cricondenbara y la presión pseudocrítica de Kay; si la '
                                 'envolvente alcanza 9500 psia o más, el límite superior es 1.02 '
                                 'veces su presión máxima y la temperatura empieza en '
                                 'T<sub>min</sub>.',
                                 'The grid has 100 × 100 nodes (at least 150 × 150 for a pure '
                                 'component). The temperature spans from max(50 °R; '
                                 'T<sub>min</sub> − 50 °R) to T<sub>max</sub> + 100 °R, where '
                                 'T<sub>min</sub> and T<sub>max</sub> are the envelope extremes, '
                                 'and the pressure from 10 psia to 1.5 times the larger of the '
                                 "cricondenbar and Kay's pseudocritical pressure; if the envelope "
                                 'reaches 9500 psia or more, the upper limit is 1.02 times its '
                                 'maximum pressure and the temperature starts at T<sub>min</sub>.'),
                                ('p',
                                 'El mapa se dibuja con la escala de color rojo-amarillo-verde, '
                                 'opacidad 0.5, entre cero y el percentil 98 de los valores, con '
                                 'barra de color en la unidad de densidad activa. El interior de '
                                 'la envolvente se cubre con un polígono gris formado por las '
                                 'ramas de burbuja y de rocío, cerrado por el borde inferior del '
                                 'diagrama; sobre él se dibujan las curvas de la envolvente como '
                                 'líneas continuas. Para un componente puro no hay sombreado y la '
                                 'interpolación del mapa conserva la discontinuidad de densidad '
                                 'sobre la curva de saturación. El mapa no está disponible con '
                                 'agua activa.',
                                 'The map is drawn with the red-yellow-green color scale, opacity '
                                 '0.5, between zero and the 98th percentile of the values, with a '
                                 'color bar in the active density unit. The interior of the '
                                 'envelope is covered by a gray polygon formed by the bubble and '
                                 'dew branches, closed along the bottom edge of the diagram; the '
                                 'envelope curves are drawn on top of it as continuous lines. For '
                                 'a pure component there is no shading, and the map interpolation '
                                 'preserves the density discontinuity across the saturation curve. '
                                 'The map is not available with water enabled.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Whitson, C.H. y Brulé, M.R. (2000). <em>Phase Behavior</em>. SPE '
                                 'Monograph Series, vol. 20. Society of Petroleum Engineers.',
                                 'Whitson, C.H. and Brulé, M.R. (2000). <em>Phase Behavior</em>. '
                                 'SPE Monograph Series, vol. 20. Society of Petroleum Engineers.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.'),
                                ('p',
                                 'Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.',
                                 'Péneloux, A., Rauzy, E. and Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Recorrido de presión y temperatura', 'Pressure and temperature path'),
                    'bloques': [('p',
                                 'El recorrido de presión y temperatura dibuja sobre la envolvente '
                                 'una serie de puntos (P, T) unidos por flechas en el orden '
                                 'ingresado, por ejemplo el agotamiento de un yacimiento y el paso '
                                 'por el separador. Se abre desde el menú Gráficos («Recorrido de '
                                 'presión y temperatura»): se elige la composición principal o un '
                                 'fluido del gestor y se ingresan los puntos en las unidades '
                                 'activas. Al aceptar se abre la envolvente de ese fluido, se '
                                 'recalcula con su composición actual y se trazan los puntos '
                                 'numerados. Dejar la lista vacía quita el recorrido.',
                                 'The pressure and temperature path draws on the envelope a series '
                                 'of (P, T) points joined by arrows in the order entered, for '
                                 'example a reservoir depletion followed by the separator. It is '
                                 'opened from the Graphics menu («Pressure and temperature '
                                 'path»): the main composition or a fluid from the manager is '
                                 'chosen and the points are entered in the active units. On '
                                 'accepting, the envelope of that fluid is opened, recalculated '
                                 'with its current composition, and the numbered points are '
                                 'plotted. Leaving the list empty removes the path.')]},
                   {'titulo': ('Marcadores y valores de los puntos', 'Markers and point values'),
                    'bloques': [('p',
                                 'En el menú Gráficos, «Mostrar marcadores» muestra u oculta los '
                                 'triángulos de las curvas de la envolvente y de la comparación de '
                                 'envolventes; sin ellos, las curvas quedan como línea continua. El '
                                 'recorrido de presión y temperatura y el punto crítico conservan su '
                                 'marcador. «Mostrar valores en algunos puntos» marca solo algunos '
                                 'puntos repartidos a lo largo de cada curva de la envolvente y del '
                                 'análisis de sensibilidad, y escribe junto a cada uno su valor en la '
                                 'forma «eje y:eje x», sin nombre ni unidad (las unidades son las de '
                                 'los ejes).',
                                 'In the Graphics menu, «Show markers» shows or hides the triangles '
                                 'of the envelope curves and of the envelope comparison; without '
                                 'them the curves are drawn as a continuous line. The pressure and '
                                 'temperature path and the critical point keep their marker. «Show '
                                 'values at some points» marks only a few points spread along each '
                                 'curve of the envelope and of the sensitivity analysis, and writes '
                                 'next to each one its value as «y axis:x axis», without name or '
                                 'unit (the units are those of the axes).')]},
                   {'titulo': ('Flash múltiple', 'Multiple flash'),
                    'bloques': [('p',
                                 'El flash múltiple repite el cálculo de equilibrio de fases en '
                                 'una lista de condiciones (P, T) para un mismo fluido. Se abre '
                                 'desde el menú Herramientas («Flash múltiple») o desde el '
                                 'Navegador, en Cálculos. En la ventana de entrada se elige la '
                                 'composición principal o un fluido del gestor, se ingresan las '
                                 'condiciones de cada corrida en las unidades activas y se marcan '
                                 'las propiedades a mostrar. Cada punto se resuelve con el mismo '
                                 'motor que la ventana de Equilibrio de fases (flash bifásico, o '
                                 'trifásico si el fluido contiene agua), con la EOS, los kij y el '
                                 'método de densidad del fluido. El resultado es una tabla con el '
                                 'número de corrida, la presión, la temperatura y las propiedades '
                                 'elegidas, que puede exportarse a CSV.',
                                 'The multiple flash repeats the phase equilibrium calculation over '
                                 'a list of (P, T) conditions for one fluid. It is opened from the '
                                 'Tools menu («Multiple flash») or from the Navigator, under '
                                 'Calculations. In the input window the main composition or a '
                                 'fluid from the manager is chosen, the conditions of each run are '
                                 'entered in the active units and the properties to display are '
                                 'checked. Each point is solved with the same engine as the Phase '
                                 'equilibrium window (two-phase flash, or three-phase flash when '
                                 'the fluid contains water), with the EOS, kij and density method '
                                 'of the fluid. The result is a table with the run number, '
                                 'pressure, temperature and the chosen properties, which can be '
                                 'exported to CSV.')]},
                   {'titulo': ('Comparación de envolventes', 'Envelope comparison'),
                    'bloques': [('p',
                                 'La comparación de envolventes traza en un mismo diagrama P-T '
                                 'las envolventes de la composición principal y de los fluidos '
                                 'del gestor de fluidos. Se abre desde el menú Gráficos '
                                 '(«Comparar envolventes») o desde el gestor de fluidos. Una '
                                 'ventana de dos listas permite elegir los fluidos; debe '
                                 'seleccionarse al menos uno.',
                                 'Envelope comparison plots, on the same P-T diagram, the '
                                 'envelopes of the main composition and of the fluids in the '
                                 'fluid manager. It is opened from the Graphics menu («Compare '
                                 'envelopes») or from the fluid manager. A two-list window '
                                 'is used to choose the fluids; at least one must be selected.'),
                                ('ul',
                                 [('Cada fluido se calcula con su propia ecuación de estado y sus '
                                   'coeficientes de interacción; la composición principal usa los '
                                   'de la ventana principal.',
                                   'Each fluid is calculated with its own equation of state and '
                                   'interaction coefficients; the main composition uses those of '
                                   'the main window.'),
                                  ('El método de trazado (Michelsen o Ziervogel-Poling) es el '
                                   'seleccionado en la barra principal. Con agua activa se usa el '
                                   'método de Lindeloff-Michelsen, igual que en la envolvente '
                                   'individual.',
                                   'The tracing method (Michelsen or Ziervogel-Poling) is the one '
                                   'selected in the main bar. With water active, the '
                                   'Lindeloff-Michelsen method is used, as in the individual '
                                   'envelope.'),
                                  ('Los fluidos sin composición, o cuya composición no suma 1 '
                                   '(fracción molar) o 100 (porcentaje molar), se informan y se '
                                   'excluyen; si ninguno es válido no se grafica.',
                                   'Fluids without a composition, or whose composition does not '
                                   'add up to 1 (mole fraction) or 100 (mole percent), are '
                                   'reported and excluded; if none is valid nothing is plotted.'),
                                  ('Cada fluido tiene un color; las curvas conservan el estilo de '
                                   'la envolvente individual (línea fina con marcadores '
                                   'triangulares) y el punto crítico se marca con un cuadrado.',
                                   'Each fluid has its own colour; the curves keep the style of '
                                   'the individual envelope (thin line with triangular markers) '
                                   'and the critical point is marked with a square.'),
                                  ('El panel lateral muestra el punto crítico, la '
                                   'cricondentérmica y la cricondenbárica del fluido elegido, y '
                                   'permite resaltar un fluido: los demás se vuelven '
                                   'translúcidos.',
                                   'The side panel shows the critical point, cricondentherm and '
                                   'cricondenbar of the selected fluid, and allows one fluid to '
                                   'be highlighted: the others become translucent.')])]}]},
 {'titulo': ('Puntos de saturación', 'Saturation points'),
  'subsecciones': [{'titulo': ('Definición y tipos de cálculo', 'Definition and calculation types'),
                    'bloques': [('p',
                                 'Un punto de saturación es un punto de la envolvente de fases '
                                 'obtenido a una condición especificada. ThermoPhase calcula '
                                 'cuatro tipos: la temperatura de rocío y la temperatura de '
                                 'burbuja a una presión dada, y la presión de rocío y la presión '
                                 'de burbuja a una temperatura dada. En un punto de rocío la fase '
                                 'existente es vapor de composición z y la fase incipiente es '
                                 'líquida; en un punto de burbuja la fase existente es líquido de '
                                 'composición z y la incipiente es vapor.',
                                 'A saturation point is a point of the phase envelope obtained at '
                                 'a specified condition. ThermoPhase computes four types: the '
                                 'dew-point temperature and the bubble-point temperature at a '
                                 'given pressure, and the dew-point pressure and the bubble-point '
                                 'pressure at a given temperature. At a dew point the existing '
                                 'phase is vapor of composition z and the incipient phase is '
                                 'liquid; at a bubble point the existing phase is liquid of '
                                 'composition z and the incipient phase is vapor.'),
                                ('p',
                                 'El cálculo sigue el mismo esquema con o sin agua:',
                                 'The calculation follows the same scheme with or without water:'),
                                ('ul',
                                 [('Barrido de la variable libre (T o P) desde el lado monofásico '
                                   'hacia el bifásico, con un indicador de región bifásica de '
                                   'hidrocarburos.',
                                   'Sweep of the free variable (T or P) from the single-phase side '
                                   'toward the two-phase side, with a hydrocarbon two-phase region '
                                   'indicator.'),
                                  ('Bisección del primer cruce encontrado.',
                                   'Bisection of the first crossing found.'),
                                  ('Newton sobre las ecuaciones exactas de saturación, con la '
                                   'composición de la fase de prueba (o del flash) como estimación '
                                   'inicial.',
                                   'Newton on the exact saturation equations, with the trial-phase '
                                   '(or flash) composition as the initial estimate.'),
                                  ('Verificación del tipo de punto: rocío si la fase incipiente es '
                                   'la más pesada; burbuja si es la más liviana.',
                                   'Verification of the point type: dew if the incipient phase is '
                                   'the heavier one; bubble if it is the lighter one.')]),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La pestaña Puntos de saturación ofrece los cuatro tipos en un '
                                 'selector y recibe la condición especificada en las unidades '
                                 'activas (entre 0 y 15000). El cálculo usa la ecuación de estado '
                                 'seleccionada. El resultado muestra el valor buscado; para una '
                                 'temperatura, además su valor en la escala absoluta, y para una '
                                 'presión, la temperatura especificada. Si no existe punto de '
                                 'saturación a la condición dada, el programa lo indica.',
                                 'The Saturation Points tab offers the four types in a selector '
                                 'and receives the specified condition in the active units '
                                 '(between 0 and 15000). The calculation uses the selected '
                                 'equation of state. The result shows the value sought; for a '
                                 'temperature, also its value on the absolute scale, and for a '
                                 'pressure, the specified temperature. If no saturation point '
                                 'exists at the given condition, the program reports it.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Whitson, C.H. y Brulé, M.R. (2000). <em>Phase Behavior</em>. SPE '
                                 'Monograph Series, vol. 20. Society of Petroleum Engineers.',
                                 'Whitson, C.H. and Brulé, M.R. (2000). <em>Phase Behavior</em>. '
                                 'SPE Monograph Series, vol. 20. Society of Petroleum Engineers.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Sistema de ecuaciones y resolución',
                               'Equation system and solution'),
                    'bloques': [('p',
                                 'El punto de saturación se obtiene resolviendo las ecuaciones de '
                                 'equilibrio entre la fase existente z y la fase incipiente u, más '
                                 'una ecuación que fija la variable especificada, en las variables '
                                 'X = (ln K<sub>1</sub>, …, ln K<sub>n</sub>, ln T, ln P):',
                                 'The saturation point is obtained by solving the equilibrium '
                                 'equations between the existing phase z and the incipient phase '
                                 'u, plus an equation that fixes the specified variable, in the '
                                 'variables X = (ln K<sub>1</sub>, …, ln K<sub>n</sub>, ln T, ln '
                                 'P):'),
                                ('eq',
                                 'g_i = \\ln K_i + \\ln \\phi_i(u) - \\ln \\phi_i(z) = 0 \\quad (i '
                                 '= 1 \\ldots n)'),
                                ('eq', 'g_{n+1} = \\sum_{i} u_i - 1 = 0, \\qquad u_i = K_i\\,z_i'),
                                ('eq', 'g_{n+2} = X_s - \\ln S = 0'),
                                ('p',
                                 'donde n es el número de componentes presentes; K<sub>i</sub> = '
                                 'u<sub>i</sub>/z<sub>i</sub>; X<sub>s</sub> es ln P si se '
                                 'especifica la presión (cálculo de temperatura) o ln T si se '
                                 'especifica la temperatura (cálculo de presión); S es el valor '
                                 'especificado (psia o °R).',
                                 'where n is the number of components present; K<sub>i</sub> = '
                                 'u<sub>i</sub>/z<sub>i</sub>; X<sub>s</sub> is ln P if the '
                                 'pressure is specified (temperature calculation) or ln T if the '
                                 'temperature is specified (pressure calculation); S is the '
                                 'specified value (psia or °R).'),
                                ('p',
                                 'Las raíces de la cúbica se asignan por el covolumen de mezcla '
                                 'b<sub>m</sub>, evaluado con la composición de cada fase: de las '
                                 'dos fases, la de mayor b<sub>m</sub> toma la raíz líquida y la '
                                 'otra la raíz de vapor. El mismo criterio fija el tipo del punto: '
                                 'es de rocío si b<sub>m</sub>(u) &gt; b<sub>m</sub>(z) y de '
                                 'burbuja en caso contrario.',
                                 'The cubic roots are assigned by the mixture covolume '
                                 'b<sub>m</sub>, evaluated with the composition of each phase: of '
                                 'the two phases, the one with the larger b<sub>m</sub> takes the '
                                 'liquid root and the other the vapor root. The same criterion '
                                 'determines the point type: it is a dew point if b<sub>m</sub>(u) '
                                 '&gt; b<sub>m</sub>(z) and a bubble point otherwise.'),
                                ('h3', 'Método de Newton', 'Newton method'),
                                ('p',
                                 'El sistema se resuelve por Newton con Jacobiano numérico por '
                                 'diferencias hacia adelante (incremento 10<sup>−7</sup>·max(1, '
                                 '|X<sub>k</sub>|)). El Jacobiano se recalcula solo cuando el '
                                 'residuo no se reduce al menos a la cuarta parte entre '
                                 'iteraciones. La corrección se escala para que su mayor '
                                 'componente no supere 1.0 y se aplica con búsqueda lineal por '
                                 'mitades (hasta 25) hasta que el residuo sea menor que el doble '
                                 'del anterior. La convergencia se declara cuando la norma '
                                 'infinito del residuo es menor que 10<sup>−12</sup> (hasta 60 '
                                 'iteraciones). Se rechaza la solución trivial (max|ln '
                                 'K<sub>i</sub>| &lt; 10<sup>−4</sup>) y la que se aleja más de un '
                                 '5 % en escala logarítmica del valor acotado por el barrido.',
                                 'The system is solved by Newton with a forward-difference '
                                 'numerical Jacobian (increment 10<sup>−7</sup>·max(1, '
                                 '|X<sub>k</sub>|)). The Jacobian is recomputed only when the '
                                 'residual does not drop to at least one quarter between '
                                 'iterations. The correction is scaled so that its largest '
                                 'component does not exceed 1.0 and is applied with a halving line '
                                 'search (up to 25) until the residual is below twice the previous '
                                 'one. Convergence is declared when the infinity norm of the '
                                 'residual is below 10<sup>−12</sup> (up to 60 iterations). The '
                                 'trivial solution (max|ln K<sub>i</sub>| &lt; 10<sup>−4</sup>) is '
                                 'rejected, as is any solution that departs by more than 5 % on a '
                                 'logarithmic scale from the value bracketed by the sweep.'),
                                ('h3',
                                 'Raíz líquida a baja presión',
                                 'Liquid root at low pressure'),
                                ('p',
                                 'Para admitir puntos de rocío de fluidos pesados a presiones muy '
                                 'bajas, el intervalo admisible es de 50 a 3000 °R y de '
                                 '10<sup>−14</sup> a 10<sup>5</sup> psia. Cuando B &lt; '
                                 '10<sup>−3</sup>, la raíz líquida se obtiene por Newton sobre la '
                                 'cúbica en Z (véase «Forma cúbica en Z y su resolución») '
                                 'partiendo de Z = B por la derecha, lo que evita la pérdida de '
                                 'precisión de la solución analítica.',
                                 'To admit dew points of heavy fluids at very low pressures, the '
                                 'admissible range is 50 to 3000 °R and 10<sup>−14</sup> to '
                                 '10<sup>5</sup> psia. When B &lt; 10<sup>−3</sup>, the liquid '
                                 'root is obtained by Newton on the cubic in Z (see “Cubic form in '
                                 'Z and its solution”) starting from Z = B from the right, which '
                                 'avoids the loss of precision of the analytical solution.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.',
                                 'Michelsen, M.L. (1980). Calculation of phase envelopes and '
                                 'critical points for multicomponent mixtures. <em>Fluid Phase '
                                 'Equilibria</em>, 4(1–2), 1–10.')]},
                   {'titulo': ('Estimación inicial: estabilidad, barrido y bisección',
                               'Initial estimate: stability, sweep and bisection'),
                    'bloques': [('p',
                                 'La convergencia de Newton requiere una estimación cercana a la '
                                 'solución buscada y de la rama correcta. ThermoPhase la obtiene '
                                 'localizando la frontera de la región bifásica sobre una malla de '
                                 'la variable libre, con el análisis de estabilidad de Michelsen '
                                 'como indicador, y refinándola por bisección.',
                                 'Newton convergence requires an estimate close to the solution '
                                 'sought and on the correct branch. ThermoPhase obtains it by '
                                 'locating the boundary of the two-phase region on a grid of the '
                                 "free variable, with Michelsen's stability analysis as the "
                                 'indicator, and refining it by bisection.'),
                                ('h3', 'Análisis de estabilidad', 'Stability analysis'),
                                ('eq',
                                 '\\ln W_i^{(k+1)} = \\ln z_i + \\ln \\phi_i(z) - \\ln '
                                 '\\phi_i\\left(Y^{(k)}\\right), \\qquad Y^{(k)} = '
                                 '\\frac{W^{(k)}}{\\sum_{j} W_j^{(k)}}'),
                                ('p',
                                 'donde W<sub>i</sub> son los números de moles de la fase de '
                                 'prueba, Y<sup>(k)</sup> su composición normalizada en la '
                                 'iteración k y φ<sub>i</sub>(z) el coeficiente de fugacidad en la '
                                 'mezcla con la raíz de menor energía de Gibbs. Se emplean dos '
                                 'semillas, de tipo vapor (z<sub>i</sub>K<sub>i</sub><sup>W</sup>) '
                                 'y de tipo líquido (z<sub>i</sub>/K<sub>i</sub><sup>W</sup>), con '
                                 'hasta 400 iteraciones y tolerancia 10<sup>−10</sup> en ln W. Una '
                                 'solución con max|ln(Y<sub>i</sub>/z<sub>i</sub>)| &lt; '
                                 '10<sup>−4</sup> se considera trivial. La mezcla es inestable '
                                 '(bifásica) si ΣW<sub>i</sub> &gt; 1 en alguna solución no '
                                 'trivial; la de mayor ΣW<sub>i</sub> proporciona la estimación de '
                                 'la composición incipiente.',
                                 'where W<sub>i</sub> are the mole numbers of the trial phase, '
                                 'Y<sup>(k)</sup> its normalized composition at iteration k and '
                                 'φ<sub>i</sub>(z) the fugacity coefficient in the mixture with '
                                 'the lowest-Gibbs-energy root. Two seeds are used, vapor-like '
                                 '(z<sub>i</sub>K<sub>i</sub><sup>W</sup>) and liquid-like '
                                 '(z<sub>i</sub>/K<sub>i</sub><sup>W</sup>), with up to 400 '
                                 'iterations and a tolerance of 10<sup>−10</sup> in ln W. A '
                                 'solution with max|ln(Y<sub>i</sub>/z<sub>i</sub>)| &lt; '
                                 '10<sup>−4</sup> is considered trivial. The mixture is unstable '
                                 '(two-phase) if ΣW<sub>i</sub> &gt; 1 for some non-trivial '
                                 'solution; the one with the largest ΣW<sub>i</sub> provides the '
                                 'estimate of the incipient composition.'),
                                ('h3', 'Mallas de barrido', 'Sweep grids'),
                                ('p',
                                 'Las mallas son geométricas. En temperatura van de max(100 °R; '
                                 '0.35·T<sub>c,min</sub>) a 1.15·T<sub>c,max</sub> con razón 1.01; '
                                 'en presión van de min(10<sup>−6</sup>; P<sub>lo</sub>) a 15000 '
                                 'psia con razón 1.08, donde:',
                                 'The grids are geometric. In temperature they span from max(100 '
                                 '°R; 0.35·T<sub>c,min</sub>) to 1.15·T<sub>c,max</sub> with ratio '
                                 '1.01; in pressure they span from min(10<sup>−6</sup>; '
                                 'P<sub>lo</sub>) to 15000 psia with ratio 1.08, where:'),
                                ('eq', 'P_{lo} = \\frac{0.01}{\\sum_{i} z_i / P^{W}_{s,i}(T)}'),
                                ('p',
                                 'donde P<sub>lo</sub> (psia) es el 1 % de la presión de rocío '
                                 'ideal estimada con las presiones de vapor de Wilson '
                                 'P<sup>W</sup><sub>s,i</sub> a la temperatura especificada; '
                                 'T<sub>c,min</sub> y T<sub>c,max</sub> son la menor y la mayor '
                                 'temperatura crítica de los componentes presentes.',
                                 'where P<sub>lo</sub> (psia) is 1 % of the ideal dew-point '
                                 'pressure estimated with the Wilson vapor pressures '
                                 'P<sup>W</sup><sub>s,i</sub> at the specified temperature; '
                                 'T<sub>c,min</sub> and T<sub>c,max</sub> are the lowest and '
                                 'highest critical temperatures of the components present.'),
                                ('p',
                                 'Cada malla se recorre desde el lado monofásico correspondiente '
                                 'al punto buscado: la temperatura de rocío desde temperaturas '
                                 'altas hacia abajo, la temperatura de burbuja desde temperaturas '
                                 'bajas hacia arriba, la presión de rocío desde presiones bajas '
                                 'hacia arriba y la presión de burbuja desde presiones altas hacia '
                                 'abajo. Si el primer nodo ya es inestable (por ejemplo, por '
                                 'separación líquido-líquido a temperatura muy baja), el barrido '
                                 'continúa hasta salir de esa zona antes de buscar el cruce.',
                                 'Each grid is traversed from the single-phase side corresponding '
                                 'to the point sought: the dew-point temperature from high '
                                 'temperatures downward, the bubble-point temperature from low '
                                 'temperatures upward, the dew-point pressure from low pressures '
                                 'upward and the bubble-point pressure from high pressures '
                                 'downward. If the first node is already unstable (for example, '
                                 'due to liquid-liquid separation at very low temperature), the '
                                 'sweep continues until it leaves that zone before looking for the '
                                 'crossing.'),
                                ('h3', 'Bisección', 'Bisection'),
                                ('eq', 'v_m = \\sqrt{v_a\\,v_b}'),
                                ('p',
                                 'donde v<sub>a</sub> es el último nodo estable, v<sub>b</sub> el '
                                 'primero inestable y v<sub>m</sub> el punto medio geométrico. La '
                                 'bisección continúa hasta |ln(v<sub>b</sub>/v<sub>a</sub>)| &lt; '
                                 '2·10<sup>−4</sup> (hasta 60 pasos); el extremo inestable y la '
                                 'composición de su fase de prueba inician Newton.',
                                 'where v<sub>a</sub> is the last stable node, v<sub>b</sub> the '
                                 'first unstable one and v<sub>m</sub> the geometric midpoint. The '
                                 'bisection continues until |ln(v<sub>b</sub>/v<sub>a</sub>)| &lt; '
                                 '2·10<sup>−4</sup> (up to 60 steps); the unstable end and the '
                                 'composition of its trial phase start Newton.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Si el barrido no produce solución, se recurre al procedimiento '
                                 'de Ziervogel-Poling a composición incipiente fija con varios '
                                 'arranques. La estimación de Wilson se obtiene por Newton sobre '
                                 'Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 (burbuja) o '
                                 'Σz<sub>i</sub>/K<sub>i</sub><sup>W</sup> = 1 (rocío); los '
                                 'arranques en temperatura son la estimación de Wilson '
                                 'T<sub>W</sub>, T<sub>W</sub> ± 40, ± 80, T<sub>W</sub> − 120, '
                                 'T<sub>W</sub> − 160 (rocío) o T<sub>W</sub> ± 120 (burbuja) °R y '
                                 'valores fijos entre 250 y 650 °R; en presión, P<sub>W</sub> '
                                 'multiplicada por 1, 1.5, 0.6, 2.5 y 0.3, y 100, 400 y 800 psia. '
                                 'Se descartan las soluciones con Σ(K<sub>i</sub> − 1)<sup>2</sup> '
                                 '&lt; 0.5. Como último recurso el punto se interpola sobre la '
                                 'envolvente completa. El resultado de estos procedimientos se '
                                 'refina por Newton sobre el sistema exacto.',
                                 'If the sweep produces no solution, the Ziervogel-Poling '
                                 'procedure at fixed incipient composition with several starts is '
                                 'used. The Wilson estimate is obtained by Newton on '
                                 'Σz<sub>i</sub>K<sub>i</sub><sup>W</sup> = 1 (bubble) or '
                                 'Σz<sub>i</sub>/K<sub>i</sub><sup>W</sup> = 1 (dew); the '
                                 'temperature starts are the Wilson estimate T<sub>W</sub>, '
                                 'T<sub>W</sub> ± 40, ± 80, T<sub>W</sub> − 120, T<sub>W</sub> − '
                                 '160 (dew) or T<sub>W</sub> ± 120 (bubble) °R and fixed values '
                                 'between 250 and 650 °R; in pressure, P<sub>W</sub> multiplied by '
                                 '1, 1.5, 0.6, 2.5 and 0.3, and 100, 400 and 800 psia. Solutions '
                                 'with Σ(K<sub>i</sub> − 1)<sup>2</sup> &lt; 0.5 are discarded. As '
                                 'a last resort the point is interpolated on the complete '
                                 'envelope. The result of these procedures is refined by Newton on '
                                 'the exact system.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Ziervogel, R.G. y Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.',
                                 'Ziervogel, R.G. and Poling, B.E. (1983). A simple method for '
                                 'constructing phase envelopes for multicomponent mixtures. '
                                 '<em>Fluid Phase Equilibria</em>, 11(2), 127–135.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Existencia de dos raíces y elección de la raíz normal',
                               'Existence of two roots and choice of the normal root'),
                    'bloques': [('p',
                                 'Las ecuaciones de saturación pueden tener más de una solución no '
                                 'trivial para la misma especificación, porque una recta de '
                                 'presión o de temperatura constante puede cortar dos veces la '
                                 'misma rama de la envolvente. En un gas condensado, una isoterma '
                                 'entre la temperatura crítica y la cricondenterma corta la rama '
                                 'de rocío en una presión de rocío superior (retrógrada) y en otra '
                                 'inferior; una isobara entre la presión crítica y la '
                                 'cricondenbara corta la rama de rocío en dos temperaturas. '
                                 'Situaciones análogas se presentan en la rama de burbuja de los '
                                 'aceites y en la cola de rocío de baja presión de los gases '
                                 'ricos.',
                                 'The saturation equations may have more than one non-trivial '
                                 'solution for the same specification, because a line of constant '
                                 'pressure or temperature may intersect the same branch of the '
                                 'envelope twice. In a gas condensate, an isotherm between the '
                                 'critical temperature and the cricondentherm intersects the dew '
                                 'branch at an upper (retrograde) dew-point pressure and at a '
                                 'lower one; an isobar between the critical pressure and the '
                                 'cricondenbar intersects the dew branch at two temperatures. '
                                 'Analogous situations occur on the bubble branch of oils and on '
                                 'the low-pressure dew tail of rich gases.'),
                                ('p',
                                 'ThermoPhase informa la raíz normal según la convención de HYSYS, '
                                 'que corresponde a la frontera alcanzada desde el lado monofásico '
                                 'habitual:',
                                 'ThermoPhase reports the normal root according to the HYSYS '
                                 'convention, which corresponds to the boundary reached from the '
                                 'usual single-phase side:'),
                                ('ul',
                                 [('Temperatura de rocío: la mayor de las soluciones.',
                                   'Dew-point temperature: the largest of the solutions.'),
                                  ('Temperatura de burbuja: la menor de las soluciones.',
                                   'Bubble-point temperature: the smallest of the solutions.'),
                                  ('Presión de rocío: la menor de las soluciones.',
                                   'Dew-point pressure: the smallest of the solutions.'),
                                  ('Presión de burbuja: la mayor de las soluciones.',
                                   'Bubble-point pressure: the largest of the solutions.')]),
                                ('eq',
                                 'T_D = \\mathrm{max}_{k}\\,T_D^{(k)}, \\quad T_B = '
                                 '\\mathrm{min}_{k}\\,T_B^{(k)}, \\quad P_D = '
                                 '\\mathrm{min}_{k}\\,P_D^{(k)}, \\quad P_B = '
                                 '\\mathrm{max}_{k}\\,P_B^{(k)}'),
                                ('p',
                                 'donde T<sub>D</sub>, T<sub>B</sub>, P<sub>D</sub> y '
                                 'P<sub>B</sub> son las temperaturas y presiones de rocío (D) y de '
                                 'burbuja (B) informadas y el superíndice (k) recorre las '
                                 'soluciones candidatas del tipo correspondiente.',
                                 'where T<sub>D</sub>, T<sub>B</sub>, P<sub>D</sub> and '
                                 'P<sub>B</sub> are the reported dew (D) and bubble (B) '
                                 'temperatures and pressures and the superscript (k) runs over the '
                                 'candidate solutions of the corresponding type.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La convención se cumple por construcción: el barrido parte del '
                                 'lado monofásico en el sentido indicado para cada tipo, de modo '
                                 'que el primer cruce encontrado es la raíz normal. Entre los '
                                 'candidatos obtenidos por los distintos procedimientos solo se '
                                 'admiten los del tipo pedido (rocío o burbuja, según el covolumen '
                                 'de la fase incipiente) y se aplica la misma regla de selección. '
                                 'En el cálculo con agua se verifica además que, del lado '
                                 'monofásico inmediato (T × 1.003 para la temperatura de rocío, '
                                 'T/1.003 para la de burbuja, P/1.01 para la presión de rocío y P '
                                 '× 1.01 para la de burbuja), no exista región bifásica de '
                                 'hidrocarburos.',
                                 'The convention is met by construction: the sweep starts from the '
                                 'single-phase side in the direction indicated for each type, so '
                                 'the first crossing found is the normal root. Among the '
                                 'candidates obtained by the various procedures only those of the '
                                 'requested type (dew or bubble, according to the incipient-phase '
                                 'covolume) are admitted, and the same selection rule is applied. '
                                 'In the calculation with water it is additionally verified that, '
                                 'on the immediate single-phase side (T × 1.003 for the dew-point '
                                 'temperature, T/1.003 for the bubble-point temperature, P/1.01 '
                                 'for the dew-point pressure and P × 1.01 for the bubble-point '
                                 'pressure), no hydrocarbon two-phase region exists.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Whitson, C.H. y Brulé, M.R. (2000). <em>Phase Behavior</em>. SPE '
                                 'Monograph Series, vol. 20. Society of Petroleum Engineers.',
                                 'Whitson, C.H. and Brulé, M.R. (2000). <em>Phase Behavior</em>. '
                                 'SPE Monograph Series, vol. 20. Society of Petroleum Engineers.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Puntos de saturación con agua', 'Saturation points with water'),
                    'bloques': [('p',
                                 'Con el agua activa, el punto de saturación se calcula sobre la '
                                 'frontera de la región bifásica de hidrocarburos (vapor y líquido '
                                 'de hidrocarburo) con la composición total, incluida el agua, y '
                                 'con el mismo modelo del flash trifásico (regla de mezcla de '
                                 'Huron-Vidal para los pares agua-hidrocarburo). La fase '
                                 'incipiente es siempre de hidrocarburo; la aparición de la fase '
                                 'acuosa no se considera punto de saturación. En la envolvente de '
                                 'Lindeloff-Michelsen, el punto pertenece a la línea 2-HC cuando '
                                 'no hay fase acuosa presente y a la línea 3-HC cuando la fase '
                                 'acuosa está presente.',
                                 'With water enabled, the saturation point is computed on the '
                                 'boundary of the hydrocarbon two-phase region (hydrocarbon vapor '
                                 'and liquid) with the total composition, water included, and with '
                                 'the same model as the three-phase flash (Huron-Vidal mixing rule '
                                 'for water-hydrocarbon pairs). The incipient phase is always a '
                                 'hydrocarbon phase; the appearance of the aqueous phase is not '
                                 'considered a saturation point. On the Lindeloff-Michelsen '
                                 'envelope, the point belongs to the 2-HC line when no aqueous '
                                 'phase is present and to the 3-HC line when the aqueous phase is '
                                 'present.'),
                                ('p',
                                 'Sin fase acuosa, el sistema es el de «Sistema de ecuaciones y '
                                 'resolución» con la composición total, y se exige además que la '
                                 'mezcla sea estable frente a una fase acuosa (tm ≥ 0). Con fase '
                                 'acuosa presente se resuelven las ecuaciones de la línea '
                                 'trifásica de Lindeloff-Michelsen, con la fase de hidrocarburo '
                                 'incipiente u como referencia, la fase de hidrocarburo existente '
                                 'y con fracción β y la fase acuosa x con fracción 1 − β:',
                                 'Without an aqueous phase, the system is that of “Equation system '
                                 'and solution” with the total composition, and the mixture is '
                                 'additionally required to be stable against an aqueous phase (tm '
                                 '≥ 0). With an aqueous phase present, the equations of the '
                                 'Lindeloff-Michelsen three-phase line are solved, with the '
                                 'incipient hydrocarbon phase u as reference, the existing '
                                 'hydrocarbon phase y with fraction β and the aqueous phase x with '
                                 'fraction 1 − β:'),
                                ('eq',
                                 'u_i = \\frac{z_i}{\\beta K^{y}_i + (1-\\beta) K^{x}_i}, \\qquad '
                                 '\\ln K^{y}_i + \\ln \\phi_i(y) - \\ln \\phi_i(u) = 0'),
                                ('eq',
                                 '\\ln K^{x}_i + \\ln \\phi_i(x) - \\ln \\phi_i(u) = 0, \\qquad '
                                 '\\sum_{i} u_i = 1, \\qquad \\sum_{i} \\left(y_i - x_i\\right) = '
                                 '0'),
                                ('p',
                                 'donde z<sub>i</sub> es la composición total con agua; '
                                 'K<sup>y</sup><sub>i</sub> = y<sub>i</sub>/u<sub>i</sub>; '
                                 'K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/u<sub>i</sub>; β, '
                                 'entre 0 y 1, es la fracción de la fase de hidrocarburo existente '
                                 'entre las fases presentes. La ecuación de especificación fija ln '
                                 'P o ln T. Se exige que u e y sean fases de hidrocarburo y x una '
                                 'fase acuosa (fracción de agua mayor que 0.5).',
                                 'where z<sub>i</sub> is the total composition with water; '
                                 'K<sup>y</sup><sub>i</sub> = y<sub>i</sub>/u<sub>i</sub>; '
                                 'K<sup>x</sup><sub>i</sub> = x<sub>i</sub>/u<sub>i</sub>; β, '
                                 'between 0 and 1, is the fraction of the existing hydrocarbon '
                                 'phase among the phases present. The specification equation fixes '
                                 'ln P or ln T. It is required that u and y be hydrocarbon phases '
                                 'and x an aqueous phase (water fraction greater than 0.5).'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Primero se calcula el punto del mismo tipo para la mezcla de '
                                 'hidrocarburos sin agua (composición renormalizada y '
                                 'k<sub>ij</sub> base de la ecuación de estado). Si ese punto no '
                                 'existe, tampoco existe con agua, porque el agua solo desplaza '
                                 'ligeramente la región bifásica de hidrocarburos. El punto sin '
                                 'agua sirve de semilla: sus composiciones se extienden con una '
                                 'fracción de agua de 10<sup>−4</sup> y se ejecuta el flash '
                                 'trifásico en su (T, P).',
                                 'First, the point of the same type is computed for the '
                                 'hydrocarbon mixture without water (renormalized composition and '
                                 'base k<sub>ij</sub> of the equation of state). If that point '
                                 'does not exist, it does not exist with water either, because '
                                 'water only slightly shifts the hydrocarbon two-phase region. The '
                                 'water-free point serves as the seed: its compositions are '
                                 'extended with a water fraction of 10<sup>−4</sup> and the '
                                 'three-phase flash is run at its (T, P).'),
                                ('ul',
                                 [('Si el flash presenta fase acuosa, se resuelven las ecuaciones '
                                   'trifásicas con la fase incipiente obtenida de una prueba de '
                                   'estabilidad sobre la fase de hidrocarburo existente y β igual '
                                   'a la fracción de hidrocarburo existente entre las fases '
                                   'presentes.',
                                   'If the flash shows an aqueous phase, the three-phase equations '
                                   'are solved with the incipient phase obtained from a stability '
                                   'test on the existing hydrocarbon phase and β equal to the '
                                   'fraction of existing hydrocarbon among the phases present.'),
                                  ('En caso contrario, la fase acuosa inicial se obtiene de una '
                                   'prueba de estabilidad frente a la fase existente, con β = '
                                   'max(10<sup>−3</sup>; 1 − z<sub>agua</sub>).',
                                   'Otherwise, the initial aqueous phase is obtained from a '
                                   'stability test against the existing phase, with β = '
                                   'max(10<sup>−3</sup>; 1 − z<sub>water</sub>).'),
                                  ('Si tampoco converge, se resuelve el sistema bifásico con la '
                                   'composición total y se acepta si la mezcla es estable frente '
                                   'al agua.',
                                   'If that does not converge either, the two-phase system is '
                                   'solved with the total composition and accepted if the mixture '
                                   'is stable against water.')]),
                                ('p',
                                 'Una solución de la semilla se acepta si es del tipo pedido, '
                                 'dista menos de 0.5 en escala logarítmica del punto sin agua y '
                                 'cumple la verificación del lado monofásico. En su defecto se '
                                 'barre con el flash trifásico como indicador: la región es '
                                 'bifásica de hidrocarburos si β<sub>V</sub> &gt; 10<sup>−9</sup>, '
                                 'β<sub>L</sub> &gt; 10<sup>−9</sup> y las composiciones de vapor '
                                 'y líquido difieren (max|ln(y<sub>i</sub>/x<sub>i</sub>)| &gt; '
                                 '10<sup>−4</sup>). Primero se usa una ventana local alrededor del '
                                 'punto sin agua (T/1.12 a 1.12·T con razón 1.004, o P/2.5 a 2.5·P '
                                 'con razón 1.02) y después la malla global. Como último recurso '
                                 'se intersecan las líneas 2-HC y 3-HC de la envolvente de '
                                 'Lindeloff-Michelsen y el resultado se refina por Newton.',
                                 'A seed solution is accepted if it is of the requested type, lies '
                                 'within 0.5 on a logarithmic scale of the water-free point and '
                                 'passes the single-phase-side verification. Otherwise, a sweep is '
                                 'performed with the three-phase flash as the indicator: the '
                                 'region is hydrocarbon two-phase if β<sub>V</sub> &gt; '
                                 '10<sup>−9</sup>, β<sub>L</sub> &gt; 10<sup>−9</sup> and the '
                                 'vapor and liquid compositions differ '
                                 '(max|ln(y<sub>i</sub>/x<sub>i</sub>)| &gt; 10<sup>−4</sup>). A '
                                 'local window around the water-free point is used first (T/1.12 '
                                 'to 1.12·T with ratio 1.004, or P/2.5 to 2.5·P with ratio 1.02), '
                                 'followed by the global grid. As a last resort the 2-HC and 3-HC '
                                 'lines of the Lindeloff-Michelsen envelope are intersected and '
                                 'the result is refined by Newton.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lindeloff, N. y Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.',
                                 'Lindeloff, N. and Michelsen, M.L. (2003). Phase envelope '
                                 'calculations for hydrocarbon-water mixtures. <em>SPE '
                                 'Journal</em>, 8(3), 298–303.'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.',
                                 'Michelsen, M.L. (1982). The isothermal flash problem. Part I. '
                                 'Stability. <em>Fluid Phase Equilibria</em>, 9(1), 1–19.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Propiedades reportadas en el punto de saturación',
                               'Properties reported at the saturation point'),
                    'bloques': [('p',
                                 'Además del valor de saturación, ThermoPhase informa la '
                                 'composición de las fases en equilibrio y sus propiedades. La '
                                 'tabla de composición muestra las columnas Mezcla (z), Fase Vapor '
                                 '(y) y Fase Líquida (x), con sus sumatorias. En un punto de rocío '
                                 'el vapor tiene la composición global y el líquido es la fase '
                                 'incipiente; en un punto de burbuja el líquido tiene la '
                                 'composición global y el vapor es la fase incipiente. Con agua '
                                 'activa se añaden la fila del agua y la columna Fase Acuosa.',
                                 'In addition to the saturation value, ThermoPhase reports the '
                                 'composition of the equilibrium phases and their properties. The '
                                 'composition table shows the Mixture (z), Vapor Phase (y) and '
                                 'Liquid Phase (x) columns, with their sums. At a dew point the '
                                 'vapor has the overall composition and the liquid is the '
                                 'incipient phase; at a bubble point the liquid has the overall '
                                 'composition and the vapor is the incipient phase. With water '
                                 'enabled, the water row and the Aqueous Phase column are added.'),
                                ('p',
                                 'Las propiedades por fase son seleccionables con el botón '
                                 'Propiedades; por defecto se muestran las seis primeras:',
                                 'The properties per phase are selectable with the Properties '
                                 'button; the first six are shown by default:'),
                                ('ul',
                                 [('Peso molecular, factor de compresibilidad, densidad másica y '
                                   'gravedad específica.',
                                   'Molecular weight, compressibility factor, mass density and '
                                   'specific gravity.'),
                                  ('Entalpía molar y entropía molar, con la contribución residual '
                                   'de la misma ecuación de estado.',
                                   'Molar enthalpy and molar entropy, with the residual '
                                   'contribution of the same equation of state.'),
                                  ('Viscosidad por el método de Lohrenz-Bray-Clark (cP).',
                                   'Viscosity by the Lohrenz-Bray-Clark method (cP).'),
                                  ('Poder calorífico superior e inferior, másicos (BTU/lb) y '
                                   'volumétricos (BTU/ft³), según GPSA.',
                                   'Higher and lower heating values, mass-based (BTU/lb) and '
                                   'volumetric (BTU/ft³), according to GPSA.'),
                                  ('GPM C3+ (gal/1000 ft³), solo para la fase vapor.',
                                   'GPM C3+ (gal/1000 ft³), for the vapor phase only.')]),
                                ('p',
                                 'El peso molecular, la densidad y la gravedad específica de cada '
                                 'fase se calculan como se describe en el capítulo «Propiedades '
                                 'volumétricas»; la densidad del vapor es la de su raíz de vapor '
                                 'de la ecuación de estado.',
                                 'The molecular weight, density, and specific gravity of each '
                                 'phase are computed as described in the “Volumetric properties” '
                                 'chapter; the vapor density is that of its equation-of-state '
                                 'vapor root.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Sin agua, la densidad del líquido se calcula con COSTALD para '
                                 'T<sub>r</sub> ≤ 0.95, con la ecuación de estado para '
                                 'T<sub>r</sub> ≥ 1 y, entre ambos valores, con la interpolación '
                                 'cuadrática descrita en «Banda de transición y régimen '
                                 'supercrítico»; el factor de compresibilidad del líquido que se '
                                 'informa es el consistente con esa densidad (Z<sub>L</sub> = '
                                 'PV<sub>L</sub>/RT). Las contribuciones residuales de la entalpía '
                                 'y de la entropía del líquido usan la raíz líquida de la ecuación '
                                 'de estado.',
                                 'Without water, the liquid density is computed with COSTALD for '
                                 'T<sub>r</sub> ≤ 0.95, with the equation of state for '
                                 'T<sub>r</sub> ≥ 1 and, between both values, with the quadratic '
                                 'interpolation described in “Transition band and supercritical '
                                 'regime”; the reported liquid compressibility factor is the one '
                                 'consistent with that density (Z<sub>L</sub> = '
                                 'PV<sub>L</sub>/RT). The enthalpy and entropy residual '
                                 'contributions of the liquid use the liquid root of the equation '
                                 'of state.'),
                                ('p',
                                 'La columna Mezcla coincide con la fase saturada, porque la fase '
                                 'incipiente tiene fracción nula: en un punto de rocío la '
                                 'densidad, la gravedad específica y el factor de compresibilidad '
                                 'de la mezcla son los del vapor, y en un punto de burbuja los del '
                                 'líquido. El peso molecular y los poderes caloríficos de la '
                                 'mezcla se calculan con la composición global; la entalpía, la '
                                 'entropía y la viscosidad no se informan para la mezcla.',
                                 'The Mixture column coincides with the saturated phase, because '
                                 'the incipient phase has zero fraction: at a dew point the '
                                 'density, specific gravity and compressibility factor of the '
                                 'mixture are those of the vapor, and at a bubble point those of '
                                 'the liquid. The molecular weight and heating values of the '
                                 'mixture are computed with the overall composition; enthalpy, '
                                 'entropy and viscosity are not reported for the mixture.'),
                                ('p',
                                 'Con agua activa, las propiedades de cada fase se calculan con el '
                                 'mismo procedimiento del flash trifásico (factores de '
                                 'compresibilidad con la regla de Huron-Vidal y densidad del '
                                 'líquido por COSTALD), y la columna Fase Acuosa muestra la '
                                 'composición y las propiedades de la fase acuosa presente en el '
                                 'punto. La densidad de la mezcla se obtiene por aditividad de '
                                 'volúmenes sobre las fases existentes:',
                                 'With water enabled, the properties of each phase are computed '
                                 'with the same procedure as the three-phase flash '
                                 '(compressibility factors with the Huron-Vidal rule and liquid '
                                 'density by COSTALD), and the Aqueous Phase column shows the '
                                 'composition and properties of the aqueous phase present at the '
                                 'point. The mixture density is obtained by volume additivity over '
                                 'the existing phases:'),
                                ('eq',
                                 '\\frac{1}{\\rho_z} = \\sum_{k} '
                                 '\\frac{\\beta_k\\,M_k}{M_z\\,\\rho_k}'),
                                ('p',
                                 'donde ρ<sub>z</sub> es la densidad de la mezcla (lb/ft³); '
                                 'β<sub>k</sub>, M<sub>k</sub> y ρ<sub>k</sub> la fracción molar, '
                                 'el peso molecular y la densidad de la fase existente k '
                                 '(hidrocarburo saturado y acuosa); M<sub>z</sub> el peso '
                                 'molecular de la composición total. En este caso la gravedad '
                                 'específica, el factor de compresibilidad y el GPM C3+ de la '
                                 'mezcla no se informan, y los poderes caloríficos se calculan '
                                 'sobre la base de hidrocarburos renormalizada, por ser el agua '
                                 'inerte en la combustión.',
                                 'where ρ<sub>z</sub> is the mixture density (lb/ft³); '
                                 'β<sub>k</sub>, M<sub>k</sub> and ρ<sub>k</sub> the mole '
                                 'fraction, molecular weight and density of the existing phase k '
                                 '(saturated hydrocarbon and aqueous); M<sub>z</sub> the molecular '
                                 'weight of the total composition. In this case the specific '
                                 'gravity, compressibility factor and GPM C3+ of the mixture are '
                                 'not reported, and the heating values are computed on the '
                                 'renormalized hydrocarbon basis, since water is inert in '
                                 'combustion.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.',
                                 'Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]}]},
 {'titulo': ('Propiedades volumétricas', 'Volumetric properties'),
  'subsecciones': [{'titulo': ('Densidad y factor de compresibilidad por la ecuación de estado',
                               'Density and compressibility factor from the equation of state'),
                    'bloques': [('p',
                                 'La densidad de cada fase interviene en el dimensionamiento de '
                                 'tuberías y recipientes, en el cálculo de caídas de presión y en '
                                 'la medición de inventarios. Una vez resuelto el equilibrio de '
                                 'fases, ThermoPhase obtiene el factor de compresibilidad de cada '
                                 'fase como la raíz correspondiente de la ecuación cúbica de '
                                 'estado activa (Peng-Robinson o Soave-Redlich-Kwong, con los '
                                 'juegos de parámetros de HYSYS o de PVTsim): la raíz mayor para '
                                 'la fase vapor y la raíz menor para la fase líquida.',
                                 'The density of each phase is required for sizing pipes and '
                                 'vessels, for pressure-drop calculations and for inventory '
                                 'measurement. Once phase equilibrium is solved, ThermoPhase '
                                 'obtains the compressibility factor of each phase as the '
                                 'corresponding root of the active cubic equation of state '
                                 '(Peng-Robinson or Soave-Redlich-Kwong, with either the HYSYS or '
                                 'the PVTsim parameter sets): the largest root for the vapor phase '
                                 'and the smallest root for the liquid phase.'),
                                ('p',
                                 'El volumen molar de la fase se obtiene de la definición del '
                                 'factor de compresibilidad:',
                                 'The molar volume of the phase follows from the definition of the '
                                 'compressibility factor:'),
                                ('eq', '\\tilde{V} = \\frac{Z\\,R\\,T}{P}'),
                                ('p',
                                 'donde Ṽ es el volumen molar de la ecuación de estado '
                                 '(ft³/lbmol), Z el factor de compresibilidad de la fase, R = '
                                 '10.7316 psia·ft³/(lbmol·°R) la constante universal de los gases, '
                                 'T la temperatura (°R) y P la presión (psia).',
                                 'where Ṽ is the equation-of-state molar volume (ft³/lbmol), Z the '
                                 'compressibility factor of the phase, R = 10.7316 '
                                 'psia·ft³/(lbmol·°R) the universal gas constant, T the '
                                 'temperature (°R) and P the pressure (psia).'),
                                ('p',
                                 'La densidad másica es el cociente entre el peso molecular de la '
                                 'fase y su volumen molar:',
                                 'The mass density is the ratio of the phase molecular weight to '
                                 'its molar volume:'),
                                ('eq',
                                 '\\rho = \\frac{M}{\\tilde{V}}\\,f_{\\rho} = '
                                 '\\frac{M\\,P}{Z\\,R\\,T}\\,f_{\\rho}'),
                                ('p',
                                 'donde ρ es la densidad másica (lb/ft³), M el peso molecular de '
                                 'la fase (lb/lbmol) y f<sub>ρ</sub> el factor de convención de '
                                 'unidades, igual a 1 − 3.35·10<sup>−5</sup> con los juegos de '
                                 'parámetros de PVTsim y a 1 con los de HYSYS (véase «Convención '
                                 'de unidades de PVTsim»). El factor afecta a la densidad de todas '
                                 'las fases calculadas con la ecuación de estado, incluida la '
                                 'corrección de Peneloux, y se descuenta al reconstruir el factor '
                                 'de compresibilidad a partir de la densidad, por ejemplo en el '
                                 'cálculo de la viscosidad.',
                                 'where ρ is the mass density (lb/ft³), M the phase molecular '
                                 'weight (lb/lbmol), and f<sub>ρ</sub> the unit-convention factor, '
                                 'equal to 1 − 3.35·10<sup>−5</sup> with the PVTsim parameter sets '
                                 'and to 1 with the HYSYS sets (see “PVTsim unit convention”). The '
                                 'factor applies to the density of every phase computed from the '
                                 'equation of state, including the Peneloux correction, and is '
                                 'removed when the compressibility factor is reconstructed from '
                                 'the density, for example in the viscosity calculation.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El motor opera en unidades de campo: presión en psia, '
                                 'temperatura en °R, volumen molar en ft³/lbmol y densidad en '
                                 'lb/ft³; la interfaz convierte los resultados al sistema de '
                                 'unidades activo (FIELD, SI o Métrico). La fase vapor se evalúa '
                                 'siempre con la ecuación de estado, con o sin corrección de '
                                 'Peneloux; la fase líquida se evalúa con el método de densidad '
                                 'seleccionado (véase «Métodos de densidad de líquido»). El factor '
                                 'de compresibilidad reportado para cada fase es coherente con la '
                                 'densidad reportada: cuando la densidad proviene de COSTALD o de '
                                 'la corrección de Peneloux, el Z reportado es P·V/(R·T) con el '
                                 'volumen de ese método, mientras que la raíz original de la '
                                 'ecuación de estado se conserva para el cálculo de entalpía y '
                                 'entropía.',
                                 'The engine works in field units: pressure in psia, temperature '
                                 'in °R, molar volume in ft³/lbmol and density in lb/ft³; the '
                                 'interface converts results to the active unit system (FIELD, SI '
                                 'or Metric). The vapor phase is always evaluated with the '
                                 'equation of state, with or without the Peneloux correction; the '
                                 'liquid phase is evaluated with the selected density method (see '
                                 '“Liquid density methods”). The compressibility factor reported '
                                 'for each phase is consistent with the reported density: when the '
                                 'density comes from COSTALD or from the Peneloux correction, the '
                                 "reported Z is P·V/(R·T) with that method's volume, while the "
                                 'original equation-of-state root is retained for the enthalpy and '
                                 'entropy calculation.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Métodos de densidad de líquido', 'Liquid density methods'),
                    'bloques': [('p',
                                 'Las ecuaciones cúbicas reproducen con buena exactitud el volumen '
                                 'del vapor, pero predicen el volumen del líquido con desviaciones '
                                 'típicas de 5 a 15 %. Por esta razón ThermoPhase ofrece tres '
                                 'rutas para la densidad de las fases condensadas: la densidad de '
                                 'la propia ecuación de estado, el método de estados '
                                 'correspondientes COSTALD y la ecuación de estado con traslado de '
                                 'volumen de Peneloux.',
                                 'Cubic equations reproduce vapor volumes accurately but predict '
                                 'liquid volumes with typical deviations of 5 to 15 %. For this '
                                 'reason ThermoPhase offers three routes for the density of '
                                 'condensed phases: the equation-of-state density itself, the '
                                 'COSTALD corresponding-states method and the equation of state '
                                 'with the Peneloux volume shift.'),
                                ('ul',
                                 [('EOS: la densidad de todas las fases se obtiene de la raíz de '
                                   'la ecuación de estado, sin corrección.',
                                   'EOS: the density of all phases is obtained from the '
                                   'equation-of-state root, without correction.'),
                                  ('COSTALD: la densidad de las fases líquidas se obtiene del '
                                   'volumen de líquido de Hankinson-Thomson con corrección por '
                                   'presión; la fase vapor se evalúa con la ecuación de estado.',
                                   'COSTALD: the density of the liquid phases is obtained from the '
                                   'Hankinson-Thomson liquid volume with pressure correction; the '
                                   'vapor phase is evaluated with the equation of state.'),
                                  ('Peneloux: el volumen de la ecuación de estado de todas las '
                                   'fases (vapor, líquido y fase acuosa) se traslada con el '
                                   'parámetro de Peneloux de PVTsim.',
                                   'Peneloux: the equation-of-state volume of all phases (vapor, '
                                   'liquid and aqueous phase) is shifted with the PVTsim Peneloux '
                                   'parameter.')]),
                                ('h3', 'Selección en la interfaz', 'Interface selection'),
                                ('p',
                                 'La interfaz dispone de dos selectores: el método de densidad '
                                 '(COSTALD o EOS, con COSTALD por defecto) y la corrección de '
                                 'volumen (Ninguna o Peneloux). Como la corrección de Peneloux se '
                                 'aplica al volumen de la ecuación de estado, es incompatible con '
                                 'COSTALD: al activar Peneloux, el selector de densidad se fija en '
                                 'EOS y se bloquea; al volver a Ninguna, el selector se rehabilita '
                                 'y recupera el método previamente elegido. El método efectivo es '
                                 'Peneloux cuando la corrección está activa y, en caso contrario, '
                                 'el método de densidad seleccionado.',
                                 'The interface provides two selectors: the density method '
                                 '(COSTALD or EOS, with COSTALD as default) and the volume '
                                 'correction (None or Peneloux). Because the Peneloux correction '
                                 'applies to the equation-of-state volume, it is incompatible with '
                                 'COSTALD: when Peneloux is activated, the density selector is set '
                                 'to EOS and locked; when the correction returns to None, the '
                                 'selector is re-enabled and restores the previously chosen '
                                 'method. The effective method is Peneloux when the correction is '
                                 'active and otherwise the selected density method.'),
                                ('p',
                                 'Cada ventana de equilibrio tiene sus propios selectores. El '
                                 'método efectivo se transmite al flash bifásico, al flash '
                                 'trifásico, a la pestaña de propiedades y al mapa de densidad de '
                                 'la envolvente. El método de densidad no modifica el equilibrio '
                                 'de fases: las composiciones, las fracciones de fase y las '
                                 'constantes de equilibrio son las mismas con los tres métodos.',
                                 'Each equilibrium window has its own selectors. The effective '
                                 'method is passed to the two-phase flash, to the three-phase '
                                 'flash, to the properties tab and to the envelope density map. '
                                 'The density method does not affect phase equilibrium: '
                                 'compositions, phase fractions and equilibrium ratios are the '
                                 'same with all three methods.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Método COSTALD: parámetros de mezcla y volumen saturado',
                               'COSTALD method: mixture parameters and saturated volume'),
                    'bloques': [('p',
                                 'El método de estados correspondientes para densidad de líquido '
                                 'COSTALD (Corresponding States Liquid Density), formulado por '
                                 'Hankinson y Thomson, predice el volumen del líquido saturado a '
                                 'partir de la temperatura reducida y de dos parámetros '
                                 'característicos de cada componente: el volumen característico V* '
                                 'y un factor acéntrico. Es el método de densidad de líquido que '
                                 'emplea HYSYS para sistemas con temperatura pseudorreducida menor '
                                 'que la unidad.',
                                 'The COSTALD (Corresponding States Liquid Density) method, '
                                 'formulated by Hankinson and Thomson, predicts the saturated '
                                 'liquid volume from the reduced temperature and two '
                                 'characteristic parameters of each component: the characteristic '
                                 'volume V* and an acentric factor. It is the liquid density '
                                 'method used by HYSYS for systems whose pseudo-reduced '
                                 'temperature is below unity.'),
                                ('p',
                                 'El cálculo se organiza en cuatro etapas: parámetros de mezcla, '
                                 'volumen del líquido saturado, presión de saturación de la mezcla '
                                 'y corrección por presión para el líquido comprimido. Esta '
                                 'subsección cubre las dos primeras.',
                                 'The calculation is organized in four stages: mixture parameters, '
                                 'saturated liquid volume, mixture saturation pressure and '
                                 'pressure correction for the compressed liquid. This subsection '
                                 'covers the first two.'),
                                ('h3', 'Parámetros de mezcla', 'Mixture parameters'),
                                ('eq',
                                 'V^*_m = \\frac{1}{4}\\left[\\sum_i x_i V^*_i + 3\\left(\\sum_i '
                                 'x_i {V^*_i}^{2/3}\\right)\\left(\\sum_i x_i '
                                 '{V^*_i}^{1/3}\\right)\\right]'),
                                ('p',
                                 'donde V*<sub>m</sub> es el volumen característico de la mezcla '
                                 '(ft³/lbmol), x<sub>i</sub> la fracción molar del componente i en '
                                 'la fase líquida y V*<sub>i</sub> su volumen característico '
                                 '(ft³/lbmol).',
                                 'where V*<sub>m</sub> is the mixture characteristic volume '
                                 '(ft³/lbmol), x<sub>i</sub> the mole fraction of component i in '
                                 'the liquid phase and V*<sub>i</sub> its characteristic volume '
                                 '(ft³/lbmol).'),
                                ('eq',
                                 'T_{cm} = \\frac{1}{V^*_m}\\sum_i\\sum_j x_i x_j \\sqrt{V^*_i '
                                 'T_{c,i} V^*_j T_{cj}}'),
                                ('p',
                                 'donde T<sub>cm</sub> es la temperatura pseudocrítica de la '
                                 'mezcla (°R) y T<sub>c,i</sub> la temperatura crítica del '
                                 'componente i (°R).',
                                 'where T<sub>cm</sub> is the mixture pseudocritical temperature '
                                 '(°R) and T<sub>c,i</sub> the critical temperature of component i '
                                 '(°R).'),
                                ('eq', '\\omega_m = \\sum_i x_i\\,\\omega_{SRK,i}'),
                                ('p',
                                 'donde ω<sub>m</sub> es el factor acéntrico de la mezcla y '
                                 'ω<sub>SRK,i</sub> el factor acéntrico SRK del componente i, que '
                                 'HYSYS emplea como factor acéntrico de COSTALD.',
                                 'where ω<sub>m</sub> is the mixture acentric factor and '
                                 'ω<sub>SRK,i</sub> the SRK acentric factor of component i, which '
                                 'HYSYS uses as the COSTALD acentric factor.'),
                                ('eq',
                                 'Z_{cm} = 0.291 - 0.080\\,\\omega_m \\qquad P_{cm} = '
                                 '\\frac{Z_{cm}\\,R\\,T_{cm}}{V^*_m}'),
                                ('p',
                                 'donde Z<sub>cm</sub> es el factor de compresibilidad crítico de '
                                 'la mezcla y P<sub>cm</sub> su presión pseudocrítica (psia), '
                                 'según Thomson, Brobst y Hankinson.',
                                 'where Z<sub>cm</sub> is the mixture critical compressibility '
                                 'factor and P<sub>cm</sub> its pseudocritical pressure (psia), '
                                 'according to Thomson, Brobst and Hankinson.'),
                                ('h3', 'Volumen del líquido saturado', 'Saturated liquid volume'),
                                ('eq',
                                 'V_s = V^*_m\\,V^{(0)}_R\\left(1 - '
                                 '\\omega_m\\,V^{(\\delta)}_R\\right)'),
                                ('p',
                                 'donde V<sub>s</sub> es el volumen molar del líquido saturado '
                                 '(ft³/lbmol), V<sup>(0)</sup><sub>R</sub> la función de volumen '
                                 'reducido de referencia y V<sup>(δ)</sup><sub>R</sub> la función '
                                 'de desviación.',
                                 'where V<sub>s</sub> is the saturated liquid molar volume '
                                 '(ft³/lbmol), V<sup>(0)</sup><sub>R</sub> the reference '
                                 'reduced-volume function and V<sup>(δ)</sup><sub>R</sub> the '
                                 'deviation function.'),
                                ('eq',
                                 'V^{(0)}_R = 1 - 1.52816\\,\\tau^{1/3} + 1.43907\\,\\tau^{2/3} - '
                                 '0.81446\\,\\tau + 0.190454\\,\\tau^{4/3}'),
                                ('p',
                                 'donde τ = 1 − T<sub>r</sub> y T<sub>r</sub> = T/T<sub>cm</sub> '
                                 'es la temperatura pseudorreducida de la mezcla.',
                                 'where τ = 1 − T<sub>r</sub> and T<sub>r</sub> = T/T<sub>cm</sub> '
                                 'is the mixture pseudo-reduced temperature.'),
                                ('eq',
                                 'V^{(\\delta)}_R = \\frac{-0.296123 + 0.386914\\,T_r - '
                                 '0.0427258\\,T_r^2 - 0.0480645\\,T_r^3}{T_r - 1.00001}'),
                                ('p',
                                 'donde el término 1.00001 del denominador desplaza la '
                                 'singularidad fuera de T<sub>r</sub> = 1. La densidad del líquido '
                                 'es M/V, con V el volumen saturado o, por encima de la presión de '
                                 'saturación, el volumen comprimido.',
                                 'where the term 1.00001 in the denominator shifts the singularity '
                                 'away from T<sub>r</sub> = 1. The liquid density is M/V, with V '
                                 'the saturated volume or, above the saturation pressure, the '
                                 'compressed volume.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los volúmenes característicos V* de los trece componentes son '
                                 'los de la base de datos de HYSYS (Characteristic Volume). La '
                                 'regla de mezcla usa las temperaturas críticas del banco de HYSYS '
                                 'y los factores acéntricos SRK con independencia de la ecuación '
                                 'de estado activa; el peso molecular de la fase es el del juego '
                                 'de parámetros activo. Para T<sub>r</sub> ≥ 1 el volumen saturado '
                                 'no se evalúa y la densidad se toma de la ecuación de estado.',
                                 'The characteristic volumes V* of the thirteen components are '
                                 'those of the HYSYS database (Characteristic Volume). The mixing '
                                 'rule uses the critical temperatures of the HYSYS database and '
                                 'the SRK acentric factors regardless of the active equation of '
                                 'state; the phase molecular weight is that of the active '
                                 'parameter set. For T<sub>r</sub> ≥ 1 the saturated volume is not '
                                 'evaluated and the density is taken from the equation of state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.'),
                                ('p',
                                 'Thomson, G.H., Brobst, K.R. y Hankinson, R.W. (1982). An '
                                 'improved correlation for densities of compressed liquids and '
                                 'liquid mixtures. <em>AIChE Journal</em>, 28(4), 671–676.',
                                 'Thomson, G.H., Brobst, K.R. and Hankinson, R.W. (1982). An '
                                 'improved correlation for densities of compressed liquids and '
                                 'liquid mixtures. <em>AIChE Journal</em>, 28(4), 671–676.')]},
                   {'titulo': ('Presión de saturación de la mezcla', 'Mixture saturation pressure'),
                    'bloques': [('p',
                                 'La corrección por presión del volumen COSTALD requiere la '
                                 'presión de saturación de la mezcla líquida a la temperatura de '
                                 'trabajo, que actúa como presión de referencia del líquido '
                                 'saturado. ThermoPhase emplea como presión de saturación la '
                                 'presión de burbuja de la mezcla calculada con la ecuación de '
                                 'estado activa, que es la referencia que emplea HYSYS al disponer '
                                 'de la ecuación de estado completa.',
                                 'The pressure correction of the COSTALD volume requires the '
                                 'saturation pressure of the liquid mixture at the working '
                                 'temperature, which acts as the reference pressure of the '
                                 'saturated liquid. ThermoPhase uses as saturation pressure the '
                                 'bubble-point pressure of the mixture computed with the active '
                                 'equation of state, which is the reference HYSYS uses when the '
                                 'full equation of state is available.'),
                                ('h3',
                                 'Presión de burbuja por la ecuación de estado',
                                 'Equation-of-state bubble pressure'),
                                ('p',
                                 'El cálculo parte de la estimación de Wilson y aplica sustitución '
                                 'sucesiva sobre la presión:',
                                 'The calculation starts from the Wilson estimate and applies '
                                 'successive substitution on pressure:'),
                                ('eq',
                                 'P^{(0)} = \\sum_i x_i '
                                 'P_{c,i}\\exp\\left[5.373\\,(1+\\omega_i)\\left(1 - '
                                 '\\frac{T_{c,i}}{T}\\right)\\right]'),
                                ('p',
                                 'donde P<sup>(0)</sup> es la presión inicial (psia), '
                                 'P<sub>c,i</sub>, T<sub>c,i</sub> y ω<sub>i</sub> la presión '
                                 'crítica (psia), la temperatura crítica (°R) y el factor '
                                 'acéntrico del componente i.',
                                 'where P<sup>(0)</sup> is the initial pressure (psia), and '
                                 'P<sub>c,i</sub>, T<sub>c,i</sub> and ω<sub>i</sub> the critical '
                                 'pressure (psia), critical temperature (°R) and acentric factor '
                                 'of component i.'),
                                ('eq',
                                 'K_i = \\frac{\\phi_i^L(x,T,P)}{\\phi_i^V(y,T,P)} \\qquad y_i = '
                                 '\\frac{K_i x_i}{\\sum_j K_j x_j} \\qquad P^{(k+1)} = '
                                 'P^{(k)}\\sum_i K_i x_i'),
                                ('p',
                                 'donde K<sub>i</sub> es la constante de equilibrio, '
                                 'φ<sub>i</sub><sup>L</sup> y φ<sub>i</sub><sup>V</sup> los '
                                 'coeficientes de fugacidad en el líquido y en el vapor '
                                 'incipiente, y y<sub>i</sub> la composición del vapor incipiente. '
                                 'La iteración termina cuando |Σ K<sub>i</sub> x<sub>i</sub> − 1| '
                                 '&lt; 10<sup>−9</sup>, con un máximo de 200 iteraciones. El '
                                 'resultado se almacena por composición, temperatura y ecuación de '
                                 'estado para no repetir el cálculo en barridos y mapas.',
                                 'where K<sub>i</sub> is the equilibrium ratio, '
                                 'φ<sub>i</sub><sup>L</sup> and φ<sub>i</sub><sup>V</sup> the '
                                 'fugacity coefficients in the liquid and in the incipient vapor, '
                                 'and y<sub>i</sub> the incipient-vapor composition. The iteration '
                                 'stops when |Σ K<sub>i</sub> x<sub>i</sub> − 1| &lt; '
                                 '10<sup>−9</sup>, with a maximum of 200 iterations. The result is '
                                 'cached by composition, temperature and equation of state to '
                                 'avoid repeating the calculation in sweeps and maps.'),
                                ('h3',
                                 'Ecuación de Riedel (respaldo)',
                                 'Riedel equation (fallback)'),
                                ('p',
                                 'Si la presión de burbuja no converge, por ejemplo muy cerca del '
                                 'punto crítico, se utiliza la ecuación de presión de vapor '
                                 'generalizada de tipo Riedel de la formulación de Thomson, Brobst '
                                 'y Hankinson:',
                                 'If the bubble pressure does not converge, for example very close '
                                 'to the critical point, the generalized Riedel-type vapor '
                                 'pressure equation of the Thomson, Brobst and Hankinson '
                                 'formulation is used:'),
                                ('eq', '\\log_{10} P_{Rs} = P^{(0)}_R + \\omega_m\\,P^{(1)}_R'),
                                ('eq',
                                 'P^{(0)}_R = 5.8031817\\,\\log_{10}T_r + 0.07608141\\,F \\qquad '
                                 'P^{(1)}_R = 4.86601\\,G'),
                                ('eq',
                                 'F = 35.0 - \\frac{36.0}{T_r} - 96.736\\,\\log_{10}T_r + T_r^{6} '
                                 '\\qquad G = \\log_{10}T_r + 0.03721754\\,F'),
                                ('eq', 'P_s = P_{Rs}\\,P_{cm}'),
                                ('p',
                                 'donde P<sub>Rs</sub> es la presión de saturación reducida, '
                                 'T<sub>r</sub> y ω<sub>m</sub> la temperatura pseudorreducida y '
                                 'el factor acéntrico COSTALD de la mezcla, P<sub>cm</sub> la '
                                 'presión pseudocrítica (psia) y P<sub>s</sub> la presión de '
                                 'saturación (psia). La ecuación es válida para 0 &lt; '
                                 'T<sub>r</sub> &lt; 1. Si tampoco se dispone de una presión de '
                                 'saturación válida, se conserva el volumen saturado sin '
                                 'corrección.',
                                 'where P<sub>Rs</sub> is the reduced saturation pressure, '
                                 'T<sub>r</sub> and ω<sub>m</sub> the mixture pseudo-reduced '
                                 'temperature and COSTALD acentric factor, P<sub>cm</sub> the '
                                 'pseudocritical pressure (psia) and P<sub>s</sub> the saturation '
                                 'pressure (psia). The equation is valid for 0 &lt; T<sub>r</sub> '
                                 '&lt; 1. If no valid saturation pressure is available either, the '
                                 'saturated volume is retained without correction.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, artículo 15C.',
                                 'Wilson, G.M. (1969). A modified Redlich-Kwong equation of state, '
                                 'application to general physical data calculations. <em>65th '
                                 'National AIChE Meeting</em>, Cleveland, paper 15C.'),
                                ('p',
                                 'Thomson, G.H., Brobst, K.R. y Hankinson, R.W. (1982). An '
                                 'improved correlation for densities of compressed liquids and '
                                 'liquid mixtures. <em>AIChE Journal</em>, 28(4), 671–676.',
                                 'Thomson, G.H., Brobst, K.R. and Hankinson, R.W. (1982). An '
                                 'improved correlation for densities of compressed liquids and '
                                 'liquid mixtures. <em>AIChE Journal</em>, 28(4), 671–676.')]},
                   {'titulo': ('Corrección por presión del líquido comprimido',
                               'Compressed-liquid pressure correction'),
                    'bloques': [('p',
                                 'El volumen COSTALD corresponde al líquido saturado. A presiones '
                                 'mayores que la de saturación el líquido se comprime y su volumen '
                                 'disminuye. ThermoPhase aplica la corrección de líquido '
                                 'comprimido de Chueh y Prausnitz, que es la que HYSYS asocia al '
                                 'método COSTALD para líquidos subenfriados. La corrección integra '
                                 'la compresibilidad isotérmica del líquido saturado con un '
                                 'exponente n = 9:',
                                 'The COSTALD volume corresponds to the saturated liquid. At '
                                 'pressures above the saturation pressure the liquid is compressed '
                                 'and its volume decreases. ThermoPhase applies the '
                                 'Chueh-Prausnitz compressed-liquid correction, which is the one '
                                 'HYSYS associates with the COSTALD method for subcooled liquids. '
                                 'The correction integrates the isothermal compressibility of the '
                                 'saturated liquid with an exponent n = 9:'),
                                ('eq',
                                 'V = V_s\\left[1 + 9\\,\\kappa_s\\left(P - '
                                 'P_s\\right)\\right]^{-1/9}'),
                                ('p',
                                 'donde V es el volumen molar del líquido comprimido (ft³/lbmol), '
                                 'V<sub>s</sub> el volumen saturado de COSTALD, κ<sub>s</sub> la '
                                 'compresibilidad isotérmica del líquido saturado '
                                 '(psia<sup>−1</sup>), P la presión de trabajo y P<sub>s</sub> la '
                                 'presión de saturación de la mezcla (psia).',
                                 'where V is the compressed-liquid molar volume (ft³/lbmol), '
                                 'V<sub>s</sub> the COSTALD saturated volume, κ<sub>s</sub> the '
                                 'isothermal compressibility of the saturated liquid '
                                 '(psia<sup>−1</sup>), P the working pressure and P<sub>s</sub> '
                                 'the mixture saturation pressure (psia).'),
                                ('eq',
                                 '\\frac{R\\,\\kappa_s\\,T_{cm}}{V^*_m} = \\left(1 - '
                                 '0.89\\sqrt{\\omega_m}\\right)\\exp\\left(f(T_r)\\right)'),
                                ('eq',
                                 'f(T_r) = 6.9547 - 76.2853\\,T_r + 191.3060\\,T_r^2 - '
                                 '203.5472\\,T_r^3 + 82.7631\\,T_r^4'),
                                ('p',
                                 'donde V*<sub>m</sub>, T<sub>cm</sub> y ω<sub>m</sub> son los '
                                 'parámetros COSTALD de la mezcla, que actúan como volumen '
                                 'crítico, temperatura crítica y factor acéntrico de la '
                                 'correlación. La correlación de κ<sub>s</sub> es válida para 0.4 '
                                 '≤ T<sub>r</sub> ≤ 0.98.',
                                 'where V*<sub>m</sub>, T<sub>cm</sub> and ω<sub>m</sub> are the '
                                 'COSTALD mixture parameters, which act as the critical volume, '
                                 'critical temperature and acentric factor of the correlation. The '
                                 'κ<sub>s</sub> correlation is valid for 0.4 ≤ T<sub>r</sub> ≤ '
                                 '0.98.'),
                                ('p',
                                 'Como P<sub>cm</sub> = '
                                 'Z<sub>cm</sub>·R·T<sub>cm</sub>/V*<sub>m</sub>, el cociente '
                                 'V*<sub>m</sub>/(R·T<sub>cm</sub>) es igual a '
                                 'Z<sub>cm</sub>/P<sub>cm</sub>, y la compresibilidad se evalúa '
                                 'como:',
                                 'Since P<sub>cm</sub> = '
                                 'Z<sub>cm</sub>·R·T<sub>cm</sub>/V*<sub>m</sub>, the ratio '
                                 'V*<sub>m</sub>/(R·T<sub>cm</sub>) equals '
                                 'Z<sub>cm</sub>/P<sub>cm</sub>, and the compressibility is '
                                 'evaluated as:'),
                                ('eq',
                                 '\\kappa_s = \\frac{Z_{cm}}{P_{cm}}\\left(1 - '
                                 '0.89\\sqrt{\\omega_m}\\right)\\exp\\left(f(T_r)\\right)'),
                                ('p',
                                 'donde Z<sub>cm</sub> = 0.291 − 0.080·ω<sub>m</sub> y '
                                 'P<sub>cm</sub> es la presión pseudocrítica COSTALD (psia).',
                                 'where Z<sub>cm</sub> = 0.291 − 0.080·ω<sub>m</sub> and '
                                 'P<sub>cm</sub> is the COSTALD pseudocritical pressure (psia).'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La corrección se aplica solo cuando P &gt; P<sub>s</sub>; en '
                                 'caso contrario se conserva el volumen saturado. Si el argumento '
                                 '1 + 9·κ<sub>s</sub>·(P − P<sub>s</sub>) resulta no positivo, o '
                                 'si el volumen corregido no es positivo, también se conserva el '
                                 'volumen saturado. La densidad del líquido es M/V y el factor de '
                                 'compresibilidad reportado es P·V/(R·T).',
                                 'The correction is applied only when P &gt; P<sub>s</sub>; '
                                 'otherwise the saturated volume is retained. If the argument 1 + '
                                 '9·κ<sub>s</sub>·(P − P<sub>s</sub>) is not positive, or if the '
                                 'corrected volume is not positive, the saturated volume is also '
                                 'retained. The liquid density is M/V and the reported '
                                 'compressibility factor is P·V/(R·T).'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Chueh, P.L. y Prausnitz, J.M. (1969). A generalized correlation '
                                 'for the compressibilities of normal liquids. <em>AIChE '
                                 'Journal</em>, 15(3), 471–472.',
                                 'Chueh, P.L. and Prausnitz, J.M. (1969). A generalized '
                                 'correlation for the compressibilities of normal liquids. '
                                 '<em>AIChE Journal</em>, 15(3), 471–472.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Banda de transición y régimen supercrítico',
                               'Transition band and supercritical regime'),
                    'bloques': [('p',
                                 'Las funciones de volumen reducido de COSTALD pierden validez '
                                 'cuando la temperatura pseudorreducida se aproxima a la unidad, y '
                                 'la correlación de compresibilidad de Chueh y Prausnitz es válida '
                                 'solo hasta T<sub>r</sub> = 0.98. Para obtener una densidad '
                                 'continua al pasar del líquido al fluido supercrítico, '
                                 'ThermoPhase distingue tres regímenes según T<sub>r</sub> = '
                                 'T/T<sub>cm</sub>, de manera análoga a la opción de densidad de '
                                 'líquido suavizada (Smooth Liquid Density) de HYSYS.',
                                 'The COSTALD reduced-volume functions lose validity as the '
                                 'pseudo-reduced temperature approaches unity, and the '
                                 'Chueh-Prausnitz compressibility correlation is valid only up to '
                                 'T<sub>r</sub> = 0.98. To obtain a continuous density across the '
                                 'transition from liquid to supercritical fluid, ThermoPhase '
                                 'distinguishes three regimes according to T<sub>r</sub> = '
                                 'T/T<sub>cm</sub>, analogous to the HYSYS Smooth Liquid Density '
                                 'option.'),
                                ('ul',
                                 [('T<sub>r</sub> ≤ 0.95: COSTALD con corrección de líquido '
                                   'comprimido.',
                                   'T<sub>r</sub> ≤ 0.95: COSTALD with compressed-liquid '
                                   'correction.'),
                                  ('0.95 &lt; T<sub>r</sub> &lt; 1: combinación ponderada de la '
                                   'densidad COSTALD y la densidad de la ecuación de estado.',
                                   '0.95 &lt; T<sub>r</sub> &lt; 1: weighted combination of the '
                                   'COSTALD density and the equation-of-state density.'),
                                  ('T<sub>r</sub> ≥ 1: densidad de la raíz de líquido de la '
                                   'ecuación de estado.',
                                   'T<sub>r</sub> ≥ 1: density of the equation-of-state liquid '
                                   'root.')]),
                                ('p',
                                 'En la banda de transición ambas densidades se evalúan a la '
                                 'temperatura y presión de trabajo y se combinan con un peso '
                                 'cuadrático:',
                                 'In the transition band both densities are evaluated at the '
                                 'working temperature and pressure and combined with a quadratic '
                                 'weight:'),
                                ('eq',
                                 '\\chi = \\left(\\frac{T_r - 0.95}{1 - 0.95}\\right)^2 \\qquad '
                                 '\\rho = (1 - \\chi)\\,\\rho_{COSTALD} + \\chi\\,\\rho_{EOS}'),
                                ('p',
                                 'donde χ es el peso de la ecuación de estado, ρ<sub>COSTALD</sub> '
                                 'la densidad COSTALD con corrección por presión y ρ<sub>EOS</sub> '
                                 'la densidad de la raíz de líquido de la ecuación de estado '
                                 '(lb/ft³). El peso crece de 0 en T<sub>r</sub> = 0.95 a 1 en '
                                 'T<sub>r</sub> = 1. El factor de compresibilidad reportado es '
                                 'P·M/(ρ·R·T).',
                                 'where χ is the equation-of-state weight, ρ<sub>COSTALD</sub> the '
                                 'COSTALD density with pressure correction and ρ<sub>EOS</sub> the '
                                 'density of the equation-of-state liquid root (lb/ft³). The '
                                 'weight rises from 0 at T<sub>r</sub> = 0.95 to 1 at '
                                 'T<sub>r</sub> = 1. The reported compressibility factor is '
                                 'P·M/(ρ·R·T).'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El esquema anterior es el que aplican el flash bifásico, el '
                                 'flash trifásico (fase líquida de hidrocarburos) y la pestaña de '
                                 'propiedades. En las propiedades de fase evaluadas sobre las '
                                 'curvas de la envolvente y en el mapa de densidad, la banda de '
                                 'transición se resuelve por interpolación cuadrática entre la '
                                 'densidad COSTALD evaluada a T = 0.95·T<sub>cm</sub> y la '
                                 'densidad de la ecuación de estado evaluada a T = T<sub>cm</sub>:',
                                 'The scheme above is applied by the two-phase flash, the '
                                 'three-phase flash (hydrocarbon liquid phase) and the properties '
                                 'tab. In the phase properties evaluated along the envelope curves '
                                 'and in the density map, the transition band is resolved by '
                                 'quadratic interpolation between the COSTALD density evaluated at '
                                 'T = 0.95·T<sub>cm</sub> and the equation-of-state density '
                                 'evaluated at T = T<sub>cm</sub>:'),
                                ('eq',
                                 '\\rho = \\rho_{0.95} + \\left(\\rho^{EOS}_{1.0} - '
                                 '\\rho_{0.95}\\right)\\left(\\frac{T_r - 0.95}{1 - '
                                 '0.95}\\right)^2'),
                                ('p',
                                 'donde ρ<sub>0.95</sub> es la densidad COSTALD a T<sub>r</sub> = '
                                 '0.95 y ρ<sup>EOS</sup><sub>1.0</sub> la densidad de la raíz de '
                                 'líquido de la ecuación de estado a T<sub>r</sub> = 1, ambas a la '
                                 'presión de trabajo.',
                                 'where ρ<sub>0.95</sub> is the COSTALD density at T<sub>r</sub> = '
                                 '0.95 and ρ<sup>EOS</sup><sub>1.0</sub> the density of the '
                                 'equation-of-state liquid root at T<sub>r</sub> = 1, both at the '
                                 'working pressure.'),
                                ('h3', 'Alcance del método', 'Method scope'),
                                ('p',
                                 'COSTALD alcanza su mayor exactitud para hidrocarburos con factor '
                                 'acéntrico moderado; en el intervalo habitual de gas natural y '
                                 'condensados reproduce las densidades de líquido con desviaciones '
                                 'del orden de 1 %. Para mezclas muy livianas dominadas por '
                                 'metano, con temperatura pseudorreducida próxima a la unidad, la '
                                 'exactitud disminuye y la densidad depende de la banda de '
                                 'transición.',
                                 'COSTALD is most accurate for hydrocarbons with moderate acentric '
                                 'factor; in the usual range of natural gas and condensates it '
                                 'reproduces liquid densities with deviations of the order of 1 %. '
                                 'For very light, methane-dominated mixtures with pseudo-reduced '
                                 'temperature close to unity, accuracy decreases and the density '
                                 'depends on the transition band.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.')]},
                   {'titulo': ('COSTALD en el flash trifásico y en la fase acuosa',
                               'COSTALD in the three-phase flash and in the aqueous phase'),
                    'bloques': [('p',
                                 'En el flash trifásico, el método COSTALD se aplica tanto a la '
                                 'fase líquida de hidrocarburos como a la fase acuosa. Las '
                                 'ecuaciones de mezcla y de volumen saturado son las de «Método '
                                 'COSTALD: parámetros de mezcla y volumen saturado»; lo que cambia '
                                 'es la composición sobre la que se evalúan y el tratamiento de la '
                                 'presión.',
                                 'In the three-phase flash, the COSTALD method is applied both to '
                                 'the hydrocarbon liquid phase and to the aqueous phase. The '
                                 'mixing and saturated-volume equations are those of “COSTALD '
                                 'method: mixture parameters and saturated volume”; what changes '
                                 'is the composition on which they are evaluated and the treatment '
                                 'of pressure.'),
                                ('h3', 'Fase líquida de hidrocarburos', 'Hydrocarbon liquid phase'),
                                ('p',
                                 'La composición de la fase líquida se renormaliza sobre los trece '
                                 'componentes no acuosos (N₂, CO₂ e hidrocarburos) (el agua '
                                 'disuelta, en cantidad de traza, se excluye) y se aplica el '
                                 'esquema completo: COSTALD con corrección de Chueh y Prausnitz '
                                 'para T<sub>r</sub> ≤ 0.95, combinación con la densidad de la '
                                 'ecuación de estado en la banda 0.95 &lt; T<sub>r</sub> &lt; 1 y '
                                 'densidad de la ecuación de estado para T<sub>r</sub> ≥ 1. El '
                                 'peso molecular que divide al volumen COSTALD es el de la '
                                 'composición renormalizada.',
                                 'The liquid-phase composition is renormalized over the thirteen '
                                 'non-aqueous components (N₂, CO₂ and hydrocarbons) (the dissolved '
                                 'water, present in trace amounts, is excluded) and the full '
                                 'scheme is applied: COSTALD with the Chueh-Prausnitz correction '
                                 'for T<sub>r</sub> ≤ 0.95, blending with the equation-of-state '
                                 'density in the 0.95 &lt; T<sub>r</sub> &lt; 1 band, and the '
                                 'equation-of-state density for T<sub>r</sub> ≥ 1. The molecular '
                                 'weight dividing the COSTALD volume is that of the renormalized '
                                 'composition.'),
                                ('h3', 'Fase acuosa', 'Aqueous phase'),
                                ('p',
                                 'La fase acuosa se evalúa sobre su composición completa de '
                                 'catorce componentes (agua más hidrocarburos, CO₂ y N₂ '
                                 'disueltos), de modo que los gases disueltos intervienen en la '
                                 'densidad. Para el agua se adoptan los valores por defecto de '
                                 'HYSYS: volumen característico igual al volumen crítico y factor '
                                 'acéntrico COSTALD igual al factor acéntrico SRK:',
                                 'The aqueous phase is evaluated on its full fourteen-component '
                                 'composition (water plus dissolved hydrocarbons, CO₂ and N₂), so '
                                 'that dissolved gases contribute to the density. For water, the '
                                 'HYSYS default values are adopted: characteristic volume equal to '
                                 'the critical volume, and COSTALD acentric factor equal to the '
                                 'SRK acentric factor:'),
                                ('eq',
                                 'V^*_{H_2O} = V_{c,H_2O} = 55.9\\ \\mathrm{cm^3/mol} = 0.8954\\ '
                                 '\\mathrm{ft^3/lbmol} \\qquad \\omega_{H_2O} = 0.344'),
                                ('p',
                                 'donde V*<sub>H₂O</sub> es el volumen característico COSTALD del '
                                 'agua y ω<sub>H₂O</sub> su factor acéntrico COSTALD. Las '
                                 'temperaturas críticas de la regla de mezcla son las del juego de '
                                 'parámetros de catorce componentes del flash trifásico.',
                                 'where V*<sub>H₂O</sub> is the COSTALD characteristic volume of '
                                 'water and ω<sub>H₂O</sub> its COSTALD acentric factor. The '
                                 'critical temperatures in the mixing rule are those of the '
                                 'fourteen-component parameter set of the three-phase flash.'),
                                ('p',
                                 'En la fase acuosa la densidad es M/V<sub>s</sub>, con '
                                 'V<sub>s</sub> el volumen del líquido saturado, sin corrección '
                                 'por presión ni banda de transición: el agua es poco compresible '
                                 'y su temperatura reducida es baja en el intervalo de operación. '
                                 'Para T<sub>r</sub> ≥ 1 la densidad se toma de la ecuación de '
                                 'estado. El factor de compresibilidad reportado para la fase '
                                 'acuosa en este modo es la raíz de la ecuación de estado.',
                                 'In the aqueous phase the density is M/V<sub>s</sub>, with '
                                 'V<sub>s</sub> the saturated liquid volume, without pressure '
                                 'correction or transition band: water has low compressibility and '
                                 'its reduced temperature is low over the operating range. For '
                                 'T<sub>r</sub> ≥ 1 the density is taken from the equation of '
                                 'state. The compressibility factor reported for the aqueous phase '
                                 'in this mode is the equation-of-state root.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.'),
                                ('p',
                                 'Hankinson, R.W. y Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.',
                                 'Hankinson, R.W. and Thomson, G.H. (1979). A new correlation for '
                                 'saturated densities of liquids and their mixtures. <em>AIChE '
                                 'Journal</em>, 25(4), 653–663.')]},
                   {'titulo': ('Corrección de volumen de Peneloux', 'Peneloux volume correction'),
                    'bloques': [('p',
                                 'La corrección de volumen de Peneloux (traslado de volumen) '
                                 'mejora la densidad de líquido predicha por la ecuación de estado '
                                 'cúbica sin alterar el equilibrio de fases. ThermoPhase adopta la '
                                 'formulación de PVTsim (SRK/PR con corrección de volumen), en la '
                                 'que el volumen molar se desplaza una cantidad que depende de la '
                                 'composición:',
                                 'The Peneloux volume correction (volume shift) improves the '
                                 'liquid density predicted by the cubic equation of state without '
                                 'altering phase equilibrium. ThermoPhase adopts the PVTsim '
                                 'formulation (SRK/PR with volume correction), in which the molar '
                                 'volume is shifted by a composition-dependent amount:'),
                                ('eq', 'V = \\tilde{V} - c \\qquad c = \\sum_i x_i\\,c_i'),
                                ('p',
                                 'donde V es el volumen trasladado (ft³/lbmol), Ṽ el volumen de la '
                                 'ecuación de estado, c el parámetro de traslado de la fase y '
                                 'c<sub>i</sub> el del componente i (ft³/lbmol).',
                                 'where V is the shifted volume (ft³/lbmol), Ṽ the '
                                 'equation-of-state volume, c the shift parameter of the phase and '
                                 'c<sub>i</sub> that of component i (ft³/lbmol).'),
                                ('h3', 'Parámetros de traslado', 'Shift parameters'),
                                ('p',
                                 "Se usa el término independiente de la temperatura c' de la base "
                                 "de datos de PVTsim, almacenado en forma reducida c'/R (K/atm) y "
                                 'distinto para PR y para SRK; el término dependiente de la '
                                 'temperatura no interviene. La columna PR o SRK se elige según la '
                                 'ecuación de estado activa, tanto con los parámetros de HYSYS '
                                 'como con los de PVTsim. La base incluye los valores de N₂, CO₂, '
                                 'metano a n-nonano y agua. Para un componente sin valor en la base '
                                 'se aplicaría la correlación que PVTsim documenta para componentes '
                                 'orgánicos definidos:',
                                 "The temperature-independent term c' from the PVTsim database is "
                                 "used, stored in reduced form c'/R (K/atm) and different for PR "
                                 'and SRK; the temperature-dependent term is not used. The PR or '
                                 'SRK column is selected according to the active equation of '
                                 'state, with both the HYSYS and the PVTsim parameter sets. The '
                                 'database contains values for N₂, CO₂, methane through n-nonane '
                                 'and water. For a component without a database value the correlation '
                                 'documented by PVTsim for defined organic components would be applied:'),
                                ('eq', 'Z_{RA,i} = 0.29056 - 0.08775\\,\\omega_i'),
                                ('eq',
                                 '\\mathrm{SRK:}\\quad c_i = '
                                 '0.40768\\,\\frac{R\\,T_{c,i}}{P_{c,i}}\\left(0.29441 - '
                                 'Z_{RA,i}\\right)'),
                                ('eq',
                                 '\\mathrm{PR:}\\quad c_i = '
                                 '0.50033\\,\\frac{R\\,T_{c,i}}{P_{c,i}}\\left(0.25969 - '
                                 'Z_{RA,i}\\right)'),
                                ('p',
                                 'donde Z<sub>RA,i</sub> es el factor de compresibilidad de '
                                 'Rackett del componente i, y T<sub>c,i</sub> (K), P<sub>c,i</sub> '
                                 '(atm) y ω<sub>i</sub> sus propiedades críticas y factor '
                                 'acéntrico de la base de PVTsim.',
                                 'where Z<sub>RA,i</sub> is the Rackett compressibility factor of '
                                 'component i, and T<sub>c,i</sub> (K), P<sub>c,i</sub> (atm) and '
                                 'ω<sub>i</sub> its critical properties and acentric factor from '
                                 'the PVTsim database.'),
                                ('p',
                                 'El valor reducido se convierte a unidades de campo con la '
                                 'constante de los gases expresada en ft³·atm/(lbmol·K), usando '
                                 '14.696 psia/atm como PVTsim, de modo que el término P·c/(R·T) '
                                 'coincide con el de PVTsim:',
                                 'The reduced value is converted to field units with the gas '
                                 'constant expressed in ft³·atm/(lbmol·K), using 14.696 psia/atm '
                                 'as PVTsim does, so that the term P·c/(R·T) matches that of '
                                 'PVTsim:'),
                                ('eq',
                                 "c_i = \\left(\\frac{c'}{R}\\right)_i \\frac{10.7316 \\cdot "
                                 '1.8}{14.696}'),
                                ('p',
                                 "donde (c'/R)<sub>i</sub> es el valor de la base (K/atm) y "
                                 'c<sub>i</sub> resulta en ft³/lbmol.',
                                 "where (c'/R)<sub>i</sub> is the database value (K/atm) and "
                                 'c<sub>i</sub> results in ft³/lbmol.'),
                                ('h3',
                                 'Neutralidad frente al equilibrio',
                                 'Neutrality with respect to equilibrium'),
                                ('p',
                                 'El traslado introduce en ln φ<sub>i</sub> un término '
                                 '−c<sub>i</sub>·P/(R·T) idéntico en todas las fases, que se '
                                 'cancela en K<sub>i</sub> = '
                                 'φ<sub>i</sub><sup>L</sup>/φ<sub>i</sub><sup>V</sup>. Por ello '
                                 'las composiciones, las fracciones de fase, las constantes de '
                                 'equilibrio y la envolvente no se modifican; cambian el volumen '
                                 'molar, la densidad, el factor de compresibilidad y la entalpía '
                                 'de cada fase.',
                                 'The translation introduces into ln φ<sub>i</sub> a term '
                                 '−c<sub>i</sub>·P/(R·T) that is identical in all phases and '
                                 'cancels in K<sub>i</sub> = '
                                 'φ<sub>i</sub><sup>L</sup>/φ<sub>i</sub><sup>V</sup>. Therefore '
                                 'compositions, phase fractions, equilibrium ratios and the '
                                 'envelope are unchanged; the molar volume, density, '
                                 'compressibility factor and enthalpy of each phase change.'),
                                ('h3',
                                 'Efecto sobre Z, densidad y entalpía',
                                 'Effect on Z, density and enthalpy'),
                                ('eq',
                                 'Z = \\frac{P\\,(\\tilde{V} - c)}{R\\,T} = Z_{EOS} - '
                                 '\\frac{P\\,c}{R\\,T} \\qquad \\rho = \\frac{M}{\\tilde{V} - '
                                 'c}\\,f_{\\rho}'),
                                ('p',
                                 'donde Z<sub>EOS</sub> es la raíz de la ecuación de estado de la '
                                 'fase, ρ la densidad trasladada (lb/ft³) y f<sub>ρ</sub> el '
                                 'factor de convención de unidades de PVTsim. Con un parámetro de '
                                 'traslado independiente de la temperatura la energía interna no '
                                 'cambia; la entalpía se desplaza en el producto de la presión por '
                                 'el parámetro de traslado y la entropía no se modifica:',
                                 'where Z<sub>EOS</sub> is the equation-of-state root of the '
                                 'phase, ρ the shifted density (lb/ft³) and f<sub>ρ</sub> the '
                                 'PVTsim unit-convention factor. With a temperature-independent '
                                 'shift parameter the internal energy is unchanged; the enthalpy '
                                 'is shifted by the product of pressure and shift parameter, and '
                                 'the entropy is unchanged:'),
                                ('eq', 'H = H_{EOS} - P\\,c \\qquad S = S_{EOS}'),
                                ('p',
                                 'donde H y S son la entalpía (BTU/lbmol) y la entropía '
                                 '(BTU/(lbmol·°R)) de la fase; el producto P·c (psia·ft³/lbmol) se '
                                 'convierte a BTU/lbmol con el factor 144/778.169.',
                                 'where H and S are the phase enthalpy (BTU/lbmol) and entropy '
                                 '(BTU/(lbmol·°R)); the product P·c (psia·ft³/lbmol) is converted '
                                 'to BTU/lbmol with the factor 144/778.169.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El traslado se aplica a todas las fases presentes, como en '
                                 'PVTsim: vapor, líquido de hidrocarburos y, en el flash '
                                 'trifásico, la fase acuosa, cada una con su composición completa '
                                 '(incluida el agua disuelta). En la fase vapor el efecto es '
                                 'pequeño porque el volumen molar es grande frente a c, pero no es '
                                 'nulo. Si el volumen trasladado resulta no positivo se conserva '
                                 'el volumen de la ecuación de estado.',
                                 'The translation is applied to all phases present, as in PVTsim: '
                                 'vapor, hydrocarbon liquid and, in the three-phase flash, the '
                                 'aqueous phase, each with its full composition (including '
                                 'dissolved water). In the vapor phase the effect is small because '
                                 'the molar volume is large compared with c, but it is not zero. '
                                 'If the shifted volume is not positive, the equation-of-state '
                                 'volume is retained.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.',
                                 'Péneloux, A., Rauzy, E. and Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, secciones SRK with '
                                 'Volume Correction y PR with Volume Correction. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, SRK with Volume '
                                 'Correction and PR with Volume Correction sections. Calsep A/S.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Densidad de la mezcla y fracción volumétrica de fase',
                               'Mixture density and phase volume fraction'),
                    'bloques': [('p',
                                 'Además de la densidad de cada fase, ThermoPhase reporta la '
                                 'densidad global de la corriente y la fracción volumétrica de '
                                 'cada fase. Ambas se obtienen suponiendo volúmenes aditivos entre '
                                 'fases: el volumen de la corriente es la suma de los volúmenes de '
                                 'las fases presentes, cada uno evaluado con la densidad del '
                                 'método seleccionado.',
                                 'In addition to the density of each phase, ThermoPhase reports '
                                 'the overall stream density and the volume fraction of each '
                                 'phase. Both are obtained assuming additive volumes across '
                                 'phases: the stream volume is the sum of the volumes of the '
                                 'phases present, each evaluated with the density of the selected '
                                 'method.'),
                                ('h3', 'Densidad de la mezcla', 'Mixture density'),
                                ('eq',
                                 '\\frac{1}{\\rho_{mix}} = \\sum_k \\frac{w_k}{\\rho_k} \\qquad '
                                 'w_k = \\frac{\\beta_k M_k}{\\sum_j \\beta_j M_j}'),
                                ('p',
                                 'donde ρ<sub>mix</sub> es la densidad de la corriente (lb/ft³), '
                                 'w<sub>k</sub> la fracción másica de la fase k, β<sub>k</sub> su '
                                 'fracción molar, M<sub>k</sub> su peso molecular y ρ<sub>k</sub> '
                                 'su densidad. La suma abarca vapor y líquido en el flash '
                                 'bifásico, y vapor, líquido y fase acuosa en el flash trifásico. '
                                 'Cuando existe una sola fase, la densidad de la mezcla es la de '
                                 'esa fase.',
                                 'where ρ<sub>mix</sub> is the stream density (lb/ft³), '
                                 'w<sub>k</sub> the mass fraction of phase k, β<sub>k</sub> its '
                                 'mole fraction, M<sub>k</sub> its molecular weight and '
                                 'ρ<sub>k</sub> its density. The sum covers vapor and liquid in '
                                 'the two-phase flash, and vapor, liquid and aqueous phase in the '
                                 'three-phase flash. When a single phase exists, the mixture '
                                 'density is that of the phase.'),
                                ('h3', 'Fracción volumétrica de fase', 'Phase volume fraction'),
                                ('p',
                                 'La fracción volumétrica corresponde al porcentaje volumétrico de '
                                 'fase que reporta PVTsim:',
                                 'The volume fraction corresponds to the phase volume percentage '
                                 'reported by PVTsim:'),
                                ('eq',
                                 '\\theta_k = \\frac{\\beta_k M_k / \\rho_k}{\\sum_j \\beta_j M_j '
                                 '/ \\rho_j}'),
                                ('p',
                                 'donde θ<sub>k</sub> es la fracción volumétrica de la fase k y '
                                 'β<sub>k</sub>M<sub>k</sub>/ρ<sub>k</sub> su volumen por mol de '
                                 'alimentación (ft³/lbmol). La fracción volumétrica depende del '
                                 'método de densidad elegido, porque COSTALD y Peneloux modifican '
                                 'el volumen de las fases condensadas.',
                                 'where θ<sub>k</sub> is the volume fraction of phase k and '
                                 'β<sub>k</sub>M<sub>k</sub>/ρ<sub>k</sub> its volume per mole of '
                                 'feed (ft³/lbmol). The volume fraction depends on the selected '
                                 'density method, because COSTALD and Peneloux modify the volume '
                                 'of the condensed phases.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Gravedad específica y peso molecular',
                               'Specific gravity and molecular weight'),
                    'bloques': [('p',
                                 'El peso molecular y la gravedad específica de cada fase '
                                 'completan el conjunto de propiedades volumétricas del resumen de '
                                 'resultados.',
                                 'The molecular weight and specific gravity of each phase complete '
                                 'the set of volumetric properties in the results summary.'),
                                ('h3', 'Peso molecular', 'Molecular weight'),
                                ('eq',
                                 'M_k = \\sum_i x_{i,k} M_i \\qquad M_{mix} = \\sum_i z_i M_i = '
                                 '\\sum_k \\beta_k M_k'),
                                ('p',
                                 'donde M<sub>k</sub> es el peso molecular de la fase k '
                                 '(lb/lbmol), x<sub>i,k</sub> la fracción molar del componente i '
                                 'en esa fase, z<sub>i</sub> la fracción molar global y '
                                 'M<sub>i</sub> el peso molecular del componente. Los pesos '
                                 'moleculares de los componentes son los del juego de parámetros '
                                 'activo (base de HYSYS o base de PVTsim). En el flash bifásico el '
                                 'vapor es siempre la fase de menor peso molecular (véase '
                                 '«Identificación en sistemas bifásicos»).',
                                 'where M<sub>k</sub> is the molecular weight of phase k '
                                 '(lb/lbmol), x<sub>i,k</sub> the mole fraction of component i in '
                                 'that phase, z<sub>i</sub> the overall mole fraction and '
                                 'M<sub>i</sub> the component molecular weight. Component '
                                 'molecular weights are those of the active parameter set (HYSYS '
                                 'or PVTsim database). In the two-phase flash the vapor is always '
                                 'the phase of lower molecular weight (see “Identification in '
                                 'two-phase systems”).'),
                                ('h3', 'Gravedad específica', 'Specific gravity'),
                                ('eq',
                                 'SG_{V} = \\frac{M_V}{28.9625} \\qquad SG_{L} = '
                                 '\\frac{\\rho_L}{62.4}'),
                                ('p',
                                 'donde SG<sub>V</sub> es la gravedad específica del gas referida '
                                 'al aire (peso molecular 28.9625) y SG<sub>L</sub> la gravedad '
                                 'específica de un líquido referida al agua, con ρ<sub>L</sub> en '
                                 'lb/ft³ y 62.4 lb/ft³ como densidad del agua. La gravedad '
                                 'específica de las fases líquidas y de la fase acuosa se calcula '
                                 'con la densidad del método seleccionado.',
                                 'where SG<sub>V</sub> is the gas specific gravity relative to air '
                                 '(molecular weight 28.9625) and SG<sub>L</sub> the specific '
                                 'gravity of a liquid relative to water, with ρ<sub>L</sub> in '
                                 'lb/ft³ and 62.4 lb/ft³ as the water density. The specific '
                                 'gravity of the liquid phases and of the aqueous phase is '
                                 'computed with the density of the selected method.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.')]},
                   {'titulo': ('Factores volumétricos y gas en solución',
                               'Formation volume factors and solution gas'),
                    'bloques': [('p',
                                 'El resumen de resultados del equilibrio de fases incluye los '
                                 'factores volumétricos de formación del gas (B<sub>g</sub>), del '
                                 'petróleo (B<sub>o</sub>) y del agua (B<sub>w</sub>), y la '
                                 'relación gas en solución del petróleo (R<sub>s</sub>) y del agua '
                                 '(R<sub>sw</sub>). Cada factor se reporta en la columna de su '
                                 'fase y solo cuando esa fase existe. Las condiciones estándar '
                                 'son 60 °F (519.67 °R) y 14.696 psia.',
                                 'The phase-equilibrium results summary includes the formation '
                                 'volume factors of gas (B<sub>g</sub>), oil (B<sub>o</sub>) and '
                                 'water (B<sub>w</sub>), and the solution gas-oil ratio '
                                 '(R<sub>s</sub>) and solution gas-water ratio (R<sub>sw</sub>). '
                                 'Each factor is reported in the column of its phase and only when '
                                 'that phase exists. Standard conditions are 60 °F (519.67 °R) and '
                                 '14.696 psia.'),
                                ('h3', 'Factor volumétrico del gas', 'Gas formation volume factor'),
                                ('eq',
                                 'B_g = \\frac{Z_V\\,T}{P}\\,\\frac{P_{sc}}{T_{sc}} '
                                 '\\qquad [\\mathrm{ft^3/scf}]'),
                                ('p',
                                 'donde Z<sub>V</sub> es el factor de compresibilidad de la fase '
                                 'vapor reportado (con el traslado de Peneloux si está activo), T '
                                 'y P las condiciones del flash y T<sub>sc</sub>, P<sub>sc</sub> '
                                 'las condiciones estándar. El volumen estándar del gas es el de '
                                 'gas ideal, 379.48 scf/lbmol.',
                                 'where Z<sub>V</sub> is the reported vapor compressibility '
                                 'factor (with the Peneloux shift when active), T and P the flash '
                                 'conditions and T<sub>sc</sub>, P<sub>sc</sub> the standard '
                                 'conditions. The standard gas volume is the ideal-gas volume, '
                                 '379.48 scf/lbmol.'),
                                ('h3', 'Factor volumétrico del petróleo y R<sub>s</sub>',
                                 'Oil formation volume factor and R<sub>s</sub>'),
                                ('p',
                                 'La fase líquida de hidrocarburos a (P, T) se lleva a condiciones '
                                 'estándar con un flash de una etapa (sin el agua disuelta). Por '
                                 'mol de líquido a (P, T):',
                                 'The hydrocarbon liquid phase at (P, T) is taken to standard '
                                 'conditions with a single-stage flash (dissolved water '
                                 'excluded). Per mole of liquid at (P, T):'),
                                ('eq',
                                 'V_o = \\frac{M_L}{\\rho_L} \\qquad V_{STO} = f_{HC}\\,'
                                 '\\beta_{L,sc}\\,\\frac{M_{L,sc}}{\\rho_{L,sc}}'),
                                ('eq',
                                 'B_o = \\frac{V_o}{V_{STO}} \\qquad R_s = '
                                 '\\frac{f_{HC}\\,\\beta_{V,sc}\\,379.48}{V_{STO}/5.614583}'),
                                ('p',
                                 'donde M<sub>L</sub> y ρ<sub>L</sub> son el peso molecular y la '
                                 'densidad del líquido a (P, T) con el método de densidad '
                                 'seleccionado, f<sub>HC</sub> la fracción molar de hidrocarburos '
                                 'del líquido, β<sub>L,sc</sub> y β<sub>V,sc</sub> las fracciones '
                                 'de líquido y vapor del flash a condiciones estándar y '
                                 'V<sub>STO</sub> el volumen del petróleo de tanque (ft³). '
                                 'B<sub>o</sub> resulta en bbl/STB y R<sub>s</sub> en scf/STB. '
                                 'Por encima del punto de burbuja el líquido es toda la mezcla: '
                                 'R<sub>s</sub> es constante y B<sub>o</sub> crece al bajar la '
                                 'presión por expansión del líquido. B<sub>o</sub> es máximo en el '
                                 'punto de burbuja y disminuye por debajo de él, a medida que se '
                                 'libera gas.',
                                 'where M<sub>L</sub> and ρ<sub>L</sub> are the molecular weight '
                                 'and density of the liquid at (P, T) with the selected density '
                                 'method, f<sub>HC</sub> the hydrocarbon mole fraction of the '
                                 'liquid, β<sub>L,sc</sub> and β<sub>V,sc</sub> the liquid and '
                                 'vapor fractions of the flash at standard conditions and '
                                 'V<sub>STO</sub> the stock-tank oil volume (ft³). B<sub>o</sub> '
                                 'is in bbl/STB and R<sub>s</sub> in scf/STB. Above the bubble '
                                 'point the liquid is the whole mixture: R<sub>s</sub> is constant '
                                 'and B<sub>o</sub> increases as pressure falls because the liquid '
                                 'expands. B<sub>o</sub> is maximum at the bubble point and '
                                 'decreases below it as gas is liberated.'),
                                ('h3', 'Factor volumétrico del agua y R<sub>sw</sub>',
                                 'Water formation volume factor and R<sub>sw</sub>'),
                                ('p',
                                 'La fase acuosa a (P, T) se lleva a condiciones estándar con un '
                                 'flash trifásico de su composición (Huron-Vidal). R<sub>sw</sub> '
                                 'es el gas liberado por barril de agua a condiciones estándar. '
                                 'Los volúmenes de agua se calculan con la densidad del agua pura '
                                 'de IAPWS-IF97 (región 1), porque las ecuaciones cúbicas y COSTALD '
                                 'sobrestiman la expansión térmica del agua. El volumen del gas '
                                 'disuelto no se incluye, como en las correlaciones de McCain:',
                                 'The aqueous phase at (P, T) is taken to standard conditions with '
                                 'a three-phase flash of its composition (Huron-Vidal). '
                                 'R<sub>sw</sub> is the gas liberated per barrel of water at '
                                 'standard conditions. Water volumes are computed with the '
                                 'IAPWS-IF97 (region 1) pure-water density, because cubic '
                                 'equations and COSTALD overestimate the thermal expansion of '
                                 'water. The dissolved-gas volume is not included, as in the '
                                 'McCain correlations:'),
                                ('eq',
                                 'B_w = \\frac{w_{H_2O}\\,/\\,\\rho_w(P,T)}{\\beta_{W,sc}'
                                 '\\,w_{H_2O,sc}\\,/\\,\\rho_w(P_{sc},T_{sc})} \\qquad '
                                 'R_{sw} = \\frac{\\beta_{V,sc}\\,379.48}{V_{w,sc}/5.614583}'),
                                ('p',
                                 'donde w<sub>H₂O</sub> es la fracción molar de agua de la fase '
                                 'acuosa, β<sub>W,sc</sub> y β<sub>V,sc</sub> las fracciones de '
                                 'fase acuosa y de vapor a condiciones estándar, ρ<sub>w</sub> la '
                                 'densidad IAPWS-IF97 y V<sub>w,sc</sub> el volumen del agua a '
                                 'condiciones estándar (ft³). Por debajo de 32 °F la región 1 se '
                                 'extrapola al agua líquida subenfriada, que reproduce IAPWS-95 '
                                 'hasta −22 °F. Fuera de −22 °F a 662 °F se usa la densidad del '
                                 'método seleccionado.',
                                 'where w<sub>H₂O</sub> is the water mole fraction of the aqueous '
                                 'phase, β<sub>W,sc</sub> and β<sub>V,sc</sub> the aqueous and '
                                 'vapor fractions at standard conditions, ρ<sub>w</sub> the '
                                 'IAPWS-IF97 density and V<sub>w,sc</sub> the water volume at '
                                 'standard conditions (ft³). Below 32 °F region 1 is '
                                 'extrapolated to subcooled liquid water, reproducing IAPWS-95 '
                                 'down to −22 °F. Outside −22 °F to 662 °F the density of the '
                                 'selected method is used.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'McCain, W. D. (1990). <em>The Properties of Petroleum '
                                 'Fluids</em>, 2.ª ed. PennWell.',
                                 'McCain, W. D. (1990). <em>The Properties of Petroleum '
                                 'Fluids</em>, 2nd ed. PennWell.'),
                                ('p',
                                 'Wagner, W. et al. (2000). The IAPWS Industrial Formulation 1997 '
                                 'for the Thermodynamic Properties of Water and Steam. <em>J. Eng. '
                                 'Gas Turbines Power</em>, 122, 150–182.',
                                 'Wagner, W. et al. (2000). The IAPWS Industrial Formulation 1997 '
                                 'for the Thermodynamic Properties of Water and Steam. <em>J. Eng. '
                                 'Gas Turbines Power</em>, 122, 150–182.')]}]},
 {'titulo': ('Entalpía y entropía', 'Enthalpy and entropy'),
  'subsecciones': [{'titulo': ('Esquema de cálculo', 'Calculation scheme'),
                    'bloques': [('p',
                                 'La entalpía y la entropía gobiernan los balances de energía de '
                                 'un proceso: la entalpía interviene en las cargas térmicas de '
                                 'intercambiadores y en el trabajo de compresión, y la entropía '
                                 'permite evaluar procesos de referencia como la compresión '
                                 'isentrópica. ThermoPhase calcula ambas propiedades para cada '
                                 'fase y para la corriente a partir de la composición, la '
                                 'temperatura, la presión y el factor de compresibilidad de la '
                                 'ecuación de estado.',
                                 'Enthalpy and entropy govern process energy balances: enthalpy '
                                 'enters exchanger heat duties and compression work, and entropy '
                                 'allows evaluation of reference processes such as isentropic '
                                 'compression. ThermoPhase computes both properties for each phase '
                                 'and for the stream from composition, temperature, pressure and '
                                 'the equation-of-state compressibility factor.'),
                                ('p',
                                 'El cálculo sigue el método que documenta PVTsim: cada propiedad '
                                 'se descompone en una contribución de gas ideal, que depende de '
                                 'la temperatura, la presión y la composición, y una contribución '
                                 'residual (desviación respecto al gas ideal) que se obtiene de la '
                                 'ecuación de estado activa:',
                                 'The calculation follows the method documented by PVTsim: each '
                                 'property is split into an ideal-gas contribution, which depends '
                                 'on temperature, pressure and composition, and a residual '
                                 'contribution (departure from the ideal gas) obtained from the '
                                 'active equation of state:'),
                                ('eq',
                                 'H(T,P) = \\sum_i x_i H^{\\mathrm{ig}}_i(T) + '
                                 'H^{\\mathrm{res}}(T,P)'),
                                ('eq',
                                 'S(T,P) = \\sum_i x_i S^{\\mathrm{ig}}_i(T,P) - R\\sum_i x_i \\ln '
                                 'x_i + S^{\\mathrm{res}}(T,P)'),
                                ('p',
                                 'donde H<sub>i</sub><sup>ig</sup> y S<sub>i</sub><sup>ig</sup> '
                                 'son la entalpía (BTU/lbmol) y la entropía (BTU/(lbmol·°R)) de '
                                 'gas ideal del componente puro i, x<sub>i</sub> su fracción molar '
                                 'en la fase, R la constante de los gases y H<sup>res</sup>, '
                                 'S<sup>res</sup> las contribuciones residuales de la mezcla.',
                                 'where H<sub>i</sub><sup>ig</sup> and S<sub>i</sub><sup>ig</sup> '
                                 'are the ideal-gas enthalpy (BTU/lbmol) and entropy '
                                 '(BTU/(lbmol·°R)) of pure component i, x<sub>i</sub> its mole '
                                 'fraction in the phase, R the gas constant and H<sup>res</sup>, '
                                 'S<sup>res</sup> the residual contributions of the mixture.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'El mismo esquema se aplica a las cuatro variantes de la ecuación '
                                 'de estado (PR y SRK con parámetros de HYSYS o de PVTsim). La '
                                 'constante de los gases de la parte térmica es la de PVTsim, R = '
                                 '0.08206 L·atm/(mol·K) = 8.3147295 J/(mol·K) = 1.98594 '
                                 'BTU/(lbmol·°R); las contribuciones residuales se evalúan en '
                                 'forma adimensional con R = 10.7316 psia·ft³/(lbmol·°R) y se '
                                 'multiplican por esa constante, de modo que en el resultado '
                                 'interviene una sola constante de los gases.',
                                 'The same scheme is applied to the four equation-of-state '
                                 'variants (PR and SRK with HYSYS or PVTsim parameters). The gas '
                                 'constant of the thermal part is that of PVTsim, R = 0.08206 '
                                 'L·atm/(mol·K) = 8.3147295 J/(mol·K) = 1.98594 BTU/(lbmol·°R); '
                                 'the residual contributions are evaluated in dimensionless form '
                                 'with R = 10.7316 psia·ft³/(lbmol·°R) and multiplied by that '
                                 'constant, so that a single gas constant enters the result.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Thermal '
                                 'and Volumetric Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Thermal and '
                                 'Volumetric Properties section. Calsep A/S.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Contribución de gas ideal', 'Ideal-gas contribution'),
                    'bloques': [('p',
                                 'La capacidad calorífica de gas ideal de cada componente se '
                                 'representa con un polinomio de tercer grado en la temperatura, '
                                 'que es la forma que emplea PVTsim:',
                                 'The ideal-gas heat capacity of each component is represented by '
                                 'a third-degree polynomial in temperature, the form used by '
                                 'PVTsim:'),
                                ('eq',
                                 'C^{\\mathrm{ig}}_{p,i}(T) = C_{1,i} + C_{2,i}\\,T + '
                                 'C_{3,i}\\,T^2 + C_{4,i}\\,T^3'),
                                ('p',
                                 'donde C<sub>p,i</sub><sup>ig</sup> es la capacidad calorífica de '
                                 'gas ideal (J/(mol·K)), T la temperatura (K) y C<sub>1,i</sub> a '
                                 'C<sub>4,i</sub> los coeficientes del componente i.',
                                 'where C<sub>p,i</sub><sup>ig</sup> is the ideal-gas heat '
                                 'capacity (J/(mol·K)), T the temperature (K) and C<sub>1,i</sub> '
                                 'to C<sub>4,i</sub> the coefficients of component i.'),
                                ('h3',
                                 'Coeficientes de cada juego de parámetros',
                                 'Coefficients of each parameter set'),
                                ('ul',
                                 [('Juegos de HYSYS (PR y SRK): coeficientes de Reid, Prausnitz y '
                                   'Sherwood (1977) para los trece componentes.',
                                   'HYSYS sets (PR and SRK): Reid, Prausnitz and Sherwood (1977) '
                                   'coefficients for the thirteen components.'),
                                  ('Juegos de PVTsim (PR y SRK): coeficientes '
                                   'C<sub>p</sub><sup>ig</sup>/R de la base de datos de PVTsim, '
                                   'multiplicados por R = 8.3147295 J/(mol·K).',
                                   'PVTsim sets (PR and SRK): C<sub>p</sub><sup>ig</sup>/R '
                                   'coefficients from the PVTsim database, multiplied by R = '
                                   '8.3147295 J/(mol·K).'),
                                  ('Agua: con los juegos de HYSYS, polinomio de Reid, Prausnitz y '
                                   'Sherwood (C<sub>1</sub> = 32.24, C<sub>2</sub> = '
                                   '1.924·10<sup>−3</sup>, C<sub>3</sub> = 1.055·10<sup>−5</sup>, '
                                   'C<sub>4</sub> = −3.596·10<sup>−9</sup>); con los juegos de '
                                   'PVTsim, coeficientes C<sub>p</sub><sup>ig</sup>/R de la base '
                                   'de PVTsim (3.8776448, 2.2935554·10<sup>−4</sup>, '
                                   '1.2693854·10<sup>−6</sup>, −4.3252765·10<sup>−10</sup>).',
                                   'Water: with the HYSYS sets, the Reid, Prausnitz and Sherwood '
                                   'polynomial (C<sub>1</sub> = 32.24, C<sub>2</sub> = '
                                   '1.924·10<sup>−3</sup>, C<sub>3</sub> = 1.055·10<sup>−5</sup>, '
                                   'C<sub>4</sub> = −3.596·10<sup>−9</sup>); with the PVTsim sets, '
                                   'the C<sub>p</sub><sup>ig</sup>/R coefficients from the PVTsim '
                                   'database (3.8776448, 2.2935554·10<sup>−4</sup>, '
                                   '1.2693854·10<sup>−6</sup>, −4.3252765·10<sup>−10</sup>).')]),
                                ('h3', 'Estado de referencia', 'Reference state'),
                                ('p',
                                 'Con los cuatro juegos de parámetros el estado de referencia es '
                                 'el de PVTsim: entalpía y entropía nulas para cada componente '
                                 'puro como gas ideal a T<sub>0</sub> = 273.15 K (32 °F) y '
                                 'P<sub>0</sub> = 1 atm = 14.696 psia. Las integrales del '
                                 'polinomio se evalúan analíticamente:',
                                 'With all four parameter sets the reference state is that of '
                                 'PVTsim: zero enthalpy and entropy for each pure component as an '
                                 'ideal gas at T<sub>0</sub> = 273.15 K (32 °F) and P<sub>0</sub> '
                                 '= 1 atm = 14.696 psia. The polynomial integrals are evaluated '
                                 'analytically:'),
                                ('eq',
                                 'H^{\\mathrm{ig}}_i(T) = \\int_{T_0}^{T} '
                                 'C^{\\mathrm{ig}}_{p,i}\\,dT = \\left[C_1 T + \\frac{C_2}{2}T^2 + '
                                 '\\frac{C_3}{3}T^3 + \\frac{C_4}{4}T^4\\right]_{T_0}^{T}'),
                                ('eq',
                                 'S^{\\mathrm{ig}}_i(T,P) = \\left[C_1 \\ln T + C_2 T + '
                                 '\\frac{C_3}{2}T^2 + \\frac{C_4}{3}T^3\\right]_{T_0}^{T} - '
                                 'R\\ln\\frac{P}{P_0}'),
                                ('p',
                                 'donde H<sub>i</sub><sup>ig</sup> resulta en J/mol y '
                                 'S<sub>i</sub><sup>ig</sup> en J/(mol·K); se convierten a '
                                 'BTU/lbmol y BTU/(lbmol·°R) con los factores 0.429923 y 0.238846. '
                                 'El término −R·ln(P/P<sub>0</sub>) refiere la entropía de gas '
                                 'ideal a la presión de trabajo y forma parte de la contribución '
                                 'ideal.',
                                 'where H<sub>i</sub><sup>ig</sup> results in J/mol and '
                                 'S<sub>i</sub><sup>ig</sup> in J/(mol·K); they are converted to '
                                 'BTU/lbmol and BTU/(lbmol·°R) with the factors 0.429923 and '
                                 '0.238846. The term −R·ln(P/P<sub>0</sub>) refers the ideal-gas '
                                 'entropy to the working pressure and belongs to the ideal '
                                 'contribution.'),
                                ('p',
                                 'Como el estado de referencia no incluye entalpías de formación, '
                                 'los valores absolutos de entalpía y entropía son comparables con '
                                 'los de PVTsim; frente a HYSYS, que usa otra referencia, son '
                                 'comparables las diferencias entre estados.',
                                 'Because the reference state does not include enthalpies of '
                                 'formation, absolute enthalpy and entropy values are comparable '
                                 'with those of PVTsim; relative to HYSYS, which uses a different '
                                 'reference, differences between states are comparable.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Reid, R.C., Prausnitz, J.M. y Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3.ª ed. McGraw-Hill.',
                                 'Reid, R.C., Prausnitz, J.M. and Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3rd ed. McGraw-Hill.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Thermal '
                                 'and Volumetric Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Thermal and '
                                 'Volumetric Properties section. Calsep A/S.')]},
                   {'titulo': ('Contribución residual por la ecuación de estado',
                               'Residual contribution from the equation of state'),
                    'bloques': [('p',
                                 'La contribución residual recoge el efecto de las fuerzas '
                                 'intermoleculares a la presión de trabajo. PVTsim la define a '
                                 'partir de la derivada de los coeficientes de fugacidad respecto '
                                 'a la temperatura; ThermoPhase emplea las formas cerradas '
                                 'equivalentes, válidas para PR y SRK con las constantes '
                                 'δ<sub>1</sub> y δ<sub>2</sub> de la forma general de la ecuación '
                                 'cúbica (véase «Forma general de las ecuaciones cúbicas»):',
                                 'The residual contribution accounts for intermolecular forces at '
                                 'the working pressure. PVTsim defines it through the temperature '
                                 'derivative of the fugacity coefficients; ThermoPhase uses the '
                                 'equivalent closed forms, valid for PR and SRK with the '
                                 'δ<sub>1</sub> and δ<sub>2</sub> constants of the general form of '
                                 'the cubic equation (see “General form of the cubic equations”):'),
                                ('eq',
                                 '\\frac{H^{\\mathrm{res}}}{R\\,T} = Z - 1 + '
                                 '\\frac{T\\,\\frac{da_m}{dT} - a_m}{(\\delta_1 - \\delta_2)\\,b_m '
                                 'R\\,T}\\ln\\left(\\frac{Z + \\delta_1 B}{Z + \\delta_2 '
                                 'B}\\right)'),
                                ('eq',
                                 '\\frac{S^{\\mathrm{res}}}{R} = \\ln(Z - B) + '
                                 '\\frac{\\frac{da_m}{dT}}{(\\delta_1 - \\delta_2)\\,b_m '
                                 'R}\\ln\\left(\\frac{Z + \\delta_1 B}{Z + \\delta_2 B}\\right)'),
                                ('p',
                                 'donde a<sub>m</sub> (psia·ft⁶/lbmol²) y b<sub>m</sub> '
                                 '(ft³/lbmol) son los parámetros de la mezcla, da<sub>m</sub>/dT '
                                 'su derivada respecto a la temperatura, Z el factor de '
                                 'compresibilidad de la fase y B = b<sub>m</sub>·P/(R·T) el '
                                 'covolumen adimensional. El término de presión de la entropía '
                                 'está incluido en la contribución ideal, por lo que '
                                 'S<sup>res</sup> contiene solo la no idealidad.',
                                 'where a<sub>m</sub> (psia·ft⁶/lbmol²) and b<sub>m</sub> '
                                 '(ft³/lbmol) are the mixture parameters, da<sub>m</sub>/dT its '
                                 'temperature derivative, Z the compressibility factor of the '
                                 'phase and B = b<sub>m</sub>·P/(R·T) the dimensionless covolume. '
                                 'The pressure term of the entropy is included in the ideal '
                                 'contribution, so S<sup>res</sup> contains only the '
                                 'non-ideality.'),
                                ('h3',
                                 'Derivada del parámetro atractivo',
                                 'Derivative of the attractive parameter'),
                                ('p',
                                 'Con la regla de mezcla clásica cuadrática, la derivada se '
                                 'obtiene analíticamente a partir de la función α de Soave de cada '
                                 'componente:',
                                 'With the classical quadratic mixing rule, the derivative is '
                                 "obtained analytically from each component's Soave α function:"),
                                ('eq',
                                 '\\frac{da_i}{dT} = '
                                 '-a_{c,i}\\,m_i\\,\\frac{\\sqrt{\\alpha_i}}{\\sqrt{T\\,T_{c,i}}}'),
                                ('eq',
                                 'a_m = \\sum_i\\sum_j x_i x_j a_{ij} \\qquad a_{ij} = '
                                 '\\sqrt{a_i\\,a_j}\\,(1 - k_{ij})'),
                                ('eq',
                                 '\\frac{da_m}{dT} = \\sum_i\\sum_j x_i '
                                 'x_j\\,\\frac{a_{ij}}{2}\\left(\\frac{1}{a_i}\\frac{da_i}{dT} + '
                                 '\\frac{1}{a_j}\\frac{da_j}{dT}\\right)'),
                                ('p',
                                 'donde a<sub>i</sub> = a<sub>c,i</sub>·α<sub>i</sub>(T) es el '
                                 'parámetro atractivo del componente i, a<sub>c,i</sub> su valor '
                                 'en el punto crítico, α<sub>i</sub> y m<sub>i</sub> la función α '
                                 'y su coeficiente (véase «Función α(T) y factor acéntrico») y '
                                 'k<sub>ij</sub> el coeficiente de interacción binaria. Los '
                                 'parámetros a<sub>c,i</sub>, b<sub>i</sub>, m<sub>i</sub> y '
                                 'T<sub>c,i</sub>, así como la matriz k<sub>ij</sub>, son los '
                                 'mismos que empleó el flash.',
                                 'where a<sub>i</sub> = a<sub>c,i</sub>·α<sub>i</sub>(T) is the '
                                 'attractive parameter of component i, a<sub>c,i</sub> its value '
                                 'at the critical point, α<sub>i</sub> and m<sub>i</sub> the α '
                                 'function and its coefficient (see “The α(T) function and the '
                                 'acentric factor”), and k<sub>ij</sub> the binary interaction '
                                 'coefficient. The parameters a<sub>c,i</sub>, b<sub>i</sub>, '
                                 'm<sub>i</sub>, and T<sub>c,i</sub>, as well as the '
                                 'k<sub>ij</sub> matrix, are the same ones used by the flash.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Peng, D.-Y. y Robinson, D.B. (1976). A new two-constant equation '
                                 'of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.',
                                 'Peng, D.-Y. and Robinson, D.B. (1976). A new two-constant '
                                 'equation of state. <em>Industrial &amp; Engineering Chemistry '
                                 'Fundamentals</em>, 15(1), 59–64.'),
                                ('p',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.',
                                 'Soave, G. (1972). Equilibrium constants from a modified '
                                 'Redlich-Kwong equation of state. <em>Chemical Engineering '
                                 'Science</em>, 27(6), 1197–1203.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Ensamblaje por fase y de la corriente',
                               'Phase and stream assembly'),
                    'bloques': [('p',
                                 'La entalpía y la entropía de una fase reúnen la contribución '
                                 'ideal de cada componente, el término de mezcla ideal (solo en la '
                                 'entropía) y la contribución residual evaluada con el factor de '
                                 'compresibilidad de esa fase:',
                                 'The enthalpy and entropy of a phase combine the ideal '
                                 'contribution of each component, the ideal mixing term (entropy '
                                 "only) and the residual contribution evaluated with that phase's "
                                 'compressibility factor:'),
                                ('eq',
                                 'H_k = \\sum_i x_{i,k} H^{\\mathrm{ig}}_i(T) + '
                                 'H^{\\mathrm{res}}_k + \\Delta H_{Pen,k}'),
                                ('eq',
                                 'S_k = \\sum_i x_{i,k} S^{\\mathrm{ig}}_i(T,P) - R\\sum_i '
                                 'x_{i,k}\\ln x_{i,k} + S^{\\mathrm{res}}_k'),
                                ('p',
                                 'donde H<sub>k</sub> y S<sub>k</sub> son la entalpía (BTU/lbmol) '
                                 'y la entropía (BTU/(lbmol·°R)) de la fase k, x<sub>i,k</sub> la '
                                 'fracción molar del componente i en ella y ΔH<sub>Pen,k</sub> la '
                                 'corrección de Peneloux, nula cuando la corrección no está '
                                 'activa.',
                                 'where H<sub>k</sub> and S<sub>k</sub> are the enthalpy '
                                 '(BTU/lbmol) and entropy (BTU/(lbmol·°R)) of phase k, '
                                 'x<sub>i,k</sub> the mole fraction of component i in it and '
                                 'ΔH<sub>Pen,k</sub> the Peneloux correction, which is zero when '
                                 'the correction is not active.'),
                                ('h3',
                                 'Factor de compresibilidad empleado',
                                 'Compressibility factor used'),
                                ('p',
                                 'Las contribuciones residuales se evalúan siempre con la raíz de '
                                 'la ecuación de estado de la fase (raíz de vapor para el vapor, '
                                 'raíz de líquido para el líquido), y no con el factor de '
                                 'compresibilidad reportado cuando este proviene de COSTALD o de '
                                 'la corrección de Peneloux: COSTALD es una correlación '
                                 'volumétrica sin función termodinámica asociada, y el efecto del '
                                 'traslado de Peneloux sobre la entalpía se incorpora por '
                                 'separado:',
                                 'Residual contributions are always evaluated with the '
                                 'equation-of-state root of the phase (vapor root for the vapor, '
                                 'liquid root for the liquid), not with the reported '
                                 'compressibility factor when the latter comes from COSTALD or '
                                 'from the Peneloux correction: COSTALD is a volumetric '
                                 'correlation with no associated thermodynamic function, and the '
                                 'effect of the Peneloux volume shift on enthalpy is added '
                                 'separately:'),
                                ('eq',
                                 '\\Delta H_{Pen,k} = -P\\,c_k \\qquad c_k = \\sum_i '
                                 'x_{i,k}\\,c_i'),
                                ('p',
                                 'donde c<sub>k</sub> es el parámetro de traslado de la fase '
                                 '(ft³/lbmol) y el producto P·c<sub>k</sub> se convierte a '
                                 'BTU/lbmol con el factor 144/778.169. La entropía no se modifica. '
                                 'En consecuencia, la selección entre EOS y COSTALD no altera la '
                                 'entalpía ni la entropía.',
                                 'where c<sub>k</sub> is the shift parameter of the phase '
                                 '(ft³/lbmol) and the product P·c<sub>k</sub> is converted to '
                                 'BTU/lbmol with the factor 144/778.169. Entropy is unchanged. '
                                 'Consequently, choosing between EOS and COSTALD does not alter '
                                 'enthalpy or entropy.'),
                                ('h3', 'Propiedades de la corriente', 'Stream properties'),
                                ('eq', 'H = \\sum_k \\beta_k H_k \\qquad S = \\sum_k \\beta_k S_k'),
                                ('p',
                                 'donde β<sub>k</sub> es la fracción molar de la fase k (vapor y '
                                 'líquido en el flash bifásico; vapor, líquido y fase acuosa en el '
                                 'flash trifásico). En una región monofásica la propiedad de la '
                                 'corriente es la de la única fase, evaluada con la composición '
                                 'global y la raíz correspondiente.',
                                 'where β<sub>k</sub> is the mole fraction of phase k (vapor and '
                                 'liquid in the two-phase flash; vapor, liquid and aqueous phase '
                                 'in the three-phase flash). In a single-phase region the stream '
                                 'property is that of the single phase, evaluated with the overall '
                                 'composition and the corresponding root.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Thermal '
                                 'and Volumetric Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Thermal and '
                                 'Volumetric Properties section. Calsep A/S.'),
                                ('p',
                                 'Péneloux, A., Rauzy, E. y Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.',
                                 'Péneloux, A., Rauzy, E. and Fréze, R. (1982). A consistent '
                                 'correction for Redlich-Kwong-Soave volumes. <em>Fluid Phase '
                                 'Equilibria</em>, 8(1), 7–23.')]},
                   {'titulo': ('Fase acuosa y fases con agua',
                               'Aqueous phase and water-containing phases'),
                    'bloques': [('p',
                                 'En el flash trifásico, la entalpía y la entropía de las tres '
                                 'fases (vapor, líquido de hidrocarburos y fase acuosa) se '
                                 'calculan sobre los catorce componentes de cada fase, de modo que '
                                 'el agua disuelta en las fases de hidrocarburos y los gases '
                                 'disueltos en la fase acuosa intervienen en el resultado. La '
                                 'contribución residual se evalúa con la misma regla de mezcla de '
                                 'Huron-Vidal y los mismos parámetros que empleó el flash '
                                 'trifásico, que es el procedimiento de PVTsim.',
                                 'In the three-phase flash, the enthalpy and entropy of the three '
                                 'phases (vapor, hydrocarbon liquid and aqueous phase) are '
                                 'computed over the fourteen components of each phase, so that '
                                 'water dissolved in the hydrocarbon phases and gases dissolved in '
                                 'the aqueous phase contribute to the result. The residual '
                                 'contribution is evaluated with the same Huron-Vidal mixing rule '
                                 'and the same parameters used by the three-phase flash, which is '
                                 'the PVTsim procedure.'),
                                ('h3',
                                 'Derivada numérica del parámetro atractivo',
                                 'Numerical derivative of the attractive parameter'),
                                ('p',
                                 'Con la regla de Huron-Vidal el parámetro a<sub>m</sub> depende '
                                 'de la temperatura también a través de la energía libre de '
                                 'exceso, por lo que su derivada se obtiene por diferencias '
                                 'centrales:',
                                 'With the Huron-Vidal rule the parameter a<sub>m</sub> also '
                                 'depends on temperature through the excess Gibbs energy, so its '
                                 'derivative is obtained by central differences:'),
                                ('eq',
                                 '\\frac{da_m}{dT} \\approx \\frac{a_m(T + h) - a_m(T - h)}{2\\,h} '
                                 '\\qquad h = 10^{-3}\\,T'),
                                ('p',
                                 'donde a<sub>m</sub>(T ± h) es el parámetro atractivo de la '
                                 'mezcla de catorce componentes evaluado con la regla de mezcla '
                                 'del flash a T ± h (°R). Las expresiones de H<sup>res</sup> y '
                                 'S<sup>res</sup> son las de la contribución residual, con el '
                                 'factor de compresibilidad de la raíz de la ecuación de estado '
                                 'que obtuvo el flash trifásico para cada fase.',
                                 'where a<sub>m</sub>(T ± h) is the attractive parameter of the '
                                 'fourteen-component mixture evaluated with the flash mixing rule '
                                 'at T ± h (°R). The expressions for H<sup>res</sup> and '
                                 'S<sup>res</sup> are those of the residual contribution, with the '
                                 'compressibility factor of the equation-of-state root obtained by '
                                 'the three-phase flash for each phase.'),
                                ('h3',
                                 'Contribución ideal del agua',
                                 'Ideal contribution of water'),
                                ('p',
                                 'La contribución ideal de los trece componentes no acuosos es la '
                                 'del juego de parámetros activo; la del agua se integra con su '
                                 'propio polinomio de capacidad calorífica (Reid, Prausnitz y '
                                 'Sherwood con los juegos de HYSYS; base de PVTsim con los juegos '
                                 'de PVTsim), con el mismo estado de referencia de 273.15 K y 1 '
                                 'atm. El término de mezcla ideal abarca los catorce componentes.',
                                 'The ideal contribution of the thirteen non-aqueous components is '
                                 'that of the active parameter set; that of water is integrated '
                                 'with its own heat-capacity polynomial (Reid, Prausnitz and '
                                 'Sherwood with the HYSYS sets; PVTsim database with the PVTsim '
                                 'sets), with the same 273.15 K and 1 atm reference state. The '
                                 'ideal mixing term covers all fourteen components.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Cuando la corrección de Peneloux está activa, a la entalpía de '
                                 'cada fase se suma −P·c<sub>k</sub> con el parámetro de traslado '
                                 'de su composición completa, incluido el parámetro del agua de la '
                                 'base de PVTsim. La entalpía y la entropía de la corriente son '
                                 'las sumas ponderadas por las fracciones molares de las tres '
                                 'fases.',
                                 'When the Peneloux correction is active, −P·c<sub>k</sub> is '
                                 'added to the enthalpy of each phase with the shift parameter of '
                                 'its full composition, including the water parameter from the '
                                 'PVTsim database. The stream enthalpy and entropy are the sums '
                                 'weighted by the mole fractions of the three phases.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Thermal '
                                 'and Volumetric Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Thermal and '
                                 'Volumetric Properties section. Calsep A/S.')]}]},
 {'titulo': ('Viscosidad', 'Viscosity'),
  'subsecciones': [{'titulo': ('Método de Lohrenz-Bray-Clark', 'Lohrenz-Bray-Clark method'),
                    'bloques': [('p',
                                 'La viscosidad dinámica de cada fase interviene en el '
                                 'dimensionamiento de líneas de flujo, en el cálculo de caídas de '
                                 'presión y en la simulación de procesos de transporte. '
                                 'ThermoPhase calcula la viscosidad de las fases de hidrocarburos '
                                 'por el método de Lohrenz, Bray y Clark (LBC) en la formulación '
                                 'que documenta PVTsim, que expresa la viscosidad de gas y de '
                                 'líquido con una sola correlación en la densidad reducida.',
                                 'The dynamic viscosity of each phase is required for flowline '
                                 'sizing, pressure-drop calculations and transport-process '
                                 'simulation. ThermoPhase computes the viscosity of the '
                                 'hydrocarbon phases with the Lohrenz-Bray-Clark (LBC) method in '
                                 'the formulation documented by PVTsim, which expresses gas and '
                                 'liquid viscosity with a single correlation in reduced density.'),
                                ('p',
                                 'El método descompone la viscosidad de la fase en la viscosidad '
                                 'del gas diluido a baja presión, que depende de la temperatura y '
                                 'la composición, y un término residual que depende de la densidad '
                                 'reducida:',
                                 'The method splits the phase viscosity into the dilute-gas '
                                 'viscosity at low pressure, which depends on temperature and '
                                 'composition, and a residual term that depends on the reduced '
                                 'density:'),
                                ('eq',
                                 '\\left[(\\eta - \\eta^*)\\,\\xi + 10^{-4}\\right]^{1/4} = a_1 + '
                                 'a_2\\,\\rho_r + a_3\\,\\rho_r^2 + a_4\\,\\rho_r^3 + '
                                 'a_5\\,\\rho_r^4'),
                                ('p',
                                 'donde η es la viscosidad de la fase (cP), η* la viscosidad de la '
                                 'mezcla como gas diluido (cP), ξ el parámetro reductor de '
                                 'viscosidad de la mezcla (cP<sup>−1</sup>), ρ<sub>r</sub> la '
                                 'densidad reducida y a<sub>1</sub> a a<sub>5</sub> las constantes '
                                 'del método.',
                                 'where η is the phase viscosity (cP), η* the dilute-gas viscosity '
                                 'of the mixture (cP), ξ the mixture viscosity-reducing parameter '
                                 '(cP<sup>−1</sup>), ρ<sub>r</sub> the reduced density and '
                                 'a<sub>1</sub> to a<sub>5</sub> the method constants.'),
                                ('p',
                                 'La viscosidad se calcula en cada flash para cada fase presente y '
                                 'se reporta en centipoise (cP), numéricamente igual al mPa·s. '
                                 'Solo se reporta la viscosidad por fase; no se define una '
                                 'viscosidad de la mezcla multifásica porque la viscosidad no es '
                                 'una propiedad aditiva entre fases.',
                                 'Viscosity is computed in every flash for each phase present and '
                                 'reported in centipoise (cP), numerically equal to mPa·s. Only '
                                 'phase viscosities are reported; no multiphase mixture viscosity '
                                 'is defined, because viscosity is not additive across phases.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.',
                                 'Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Transport '
                                 'Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Transport '
                                 'Properties section. Calsep A/S.')]},
                   {'titulo': ('Viscosidad de gas diluido', 'Dilute-gas viscosity'),
                    'bloques': [('p',
                                 'La viscosidad de gas diluido de cada componente se obtiene de la '
                                 'correlación de Stiel y Thodos, que distingue dos intervalos de '
                                 'temperatura reducida T<sub>r,i</sub> = T/T<sub>c,i</sub>:',
                                 'The dilute-gas viscosity of each component is obtained from the '
                                 'Stiel-Thodos correlation, which distinguishes two ranges of '
                                 'reduced temperature T<sub>r,i</sub> = T/T<sub>c,i</sub>:'),
                                ('eq',
                                 'T_{r,i} \\leq 1.5:\\quad \\eta^*_i = \\frac{35 \\times '
                                 '10^{-5}\\,T_{r,i}^{0.94}}{\\xi_i}'),
                                ('eq',
                                 'T_{r,i} > 1.5:\\quad \\eta^*_i = \\frac{17.78 \\times '
                                 '10^{-5}\\,(4.58\\,T_{r,i} - 1.67)^{5/8}}{\\xi_i}'),
                                ('eq', '\\xi_i = \\frac{T_{c,i}^{1/6}}{M_i^{1/2}\\,P_{c,i}^{2/3}}'),
                                ('p',
                                 'donde η*<sub>i</sub> es la viscosidad de gas diluido del '
                                 'componente i (cP), ξ<sub>i</sub> su parámetro reductor, '
                                 'T<sub>c,i</sub> la temperatura crítica (K), P<sub>c,i</sub> la '
                                 'presión crítica (atm) y M<sub>i</sub> el peso molecular. En el '
                                 'intervalo T<sub>r,i</sub> ≤ 1.5 ThermoPhase emplea el '
                                 'coeficiente 35·10<sup>−5</sup>, con el que se reproducen los '
                                 'resultados de PVTsim, en lugar del valor 34·10<sup>−5</sup> de '
                                 'la publicación original y de la documentación de PVTsim.',
                                 'where η*<sub>i</sub> is the dilute-gas viscosity of component i '
                                 '(cP), ξ<sub>i</sub> its reducing parameter, T<sub>c,i</sub> the '
                                 'critical temperature (K), P<sub>c,i</sub> the critical pressure '
                                 '(atm) and M<sub>i</sub> the molecular weight. In the range '
                                 'T<sub>r,i</sub> ≤ 1.5 ThermoPhase uses the coefficient '
                                 '35·10<sup>−5</sup>, which reproduces the PVTsim results, instead '
                                 'of the value 34·10<sup>−5</sup> given in the original '
                                 'publication and in the PVTsim documentation.'),
                                ('h3',
                                 'Regla de mezcla de Herning y Zipperer',
                                 'Herning-Zipperer mixing rule'),
                                ('eq',
                                 '\\eta^* = \\frac{\\sum_i x_i\\,\\eta^*_i\\,M_i^{1/2}}{\\sum_i '
                                 'x_i\\,M_i^{1/2}}'),
                                ('p',
                                 'donde η* es la viscosidad de gas diluido de la mezcla (cP) y '
                                 'x<sub>i</sub> la fracción molar del componente i en la fase; las '
                                 'sumas se extienden a los componentes presentes en la fase. La '
                                 'ponderación con la raíz del peso molecular reproduce la '
                                 'dependencia de la viscosidad del gas diluido con el peso '
                                 'molecular mejor que un promedio molar.',
                                 'where η* is the dilute-gas viscosity of the mixture (cP) and '
                                 'x<sub>i</sub> the mole fraction of component i in the phase; the '
                                 'sums extend over the components present in the phase. Weighting '
                                 'by the square root of molecular weight reproduces the '
                                 'molecular-weight dependence of dilute-gas viscosity better than '
                                 'a mole-fraction average.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Stiel, L.I. y Thodos, G. (1961). The viscosity of nonpolar gases '
                                 'at normal pressures. <em>AIChE Journal</em>, 7(4), 611–615.',
                                 'Stiel, L.I. and Thodos, G. (1961). The viscosity of nonpolar '
                                 'gases at normal pressures. <em>AIChE Journal</em>, 7(4), '
                                 '611–615.'),
                                ('p',
                                 'Herning, F. y Zipperer, L. (1936). Beitrag zur Berechnung der '
                                 'Zähigkeit technischer Gasgemische aus den Zähigkeitswerten der '
                                 'Einzelbestandteile. <em>Gas- und Wasserfach</em>, 79, 49–54 y '
                                 '69–73.',
                                 'Herning, F. and Zipperer, L. (1936). Beitrag zur Berechnung der '
                                 'Zähigkeit technischer Gasgemische aus den Zähigkeitswerten der '
                                 'Einzelbestandteile. <em>Gas- und Wasserfach</em>, 79, 49–54 and '
                                 '69–73.')]},
                   {'titulo': ('Parámetro reductor y densidad reducida',
                               'Reducing parameter and reduced density'),
                    'bloques': [('p',
                                 'El parámetro reductor de viscosidad de la mezcla tiene la misma '
                                 'forma que el de un componente puro, con propiedades '
                                 'pseudocríticas obtenidas como promedios molares:',
                                 'The mixture viscosity-reducing parameter has the same form as '
                                 'that of a pure component, with pseudocritical properties '
                                 'obtained as mole-fraction averages:'),
                                ('eq',
                                 '\\xi = \\frac{\\left(\\sum_i '
                                 'x_i\\,T_{c,i}\\right)^{1/6}}{\\left(\\sum_i '
                                 'x_i\\,M_i\\right)^{1/2}\\left(\\sum_i '
                                 'x_i\\,P_{c,i}\\right)^{2/3}}'),
                                ('p',
                                 'donde ξ es el parámetro reductor de la mezcla, con '
                                 'T<sub>c,i</sub> en K y P<sub>c,i</sub> en atm.',
                                 'where ξ is the mixture reducing parameter, with T<sub>c,i</sub> '
                                 'in K and P<sub>c,i</sub> in atm.'),
                                ('p',
                                 'La densidad reducida es el producto de la densidad molar de la '
                                 'fase por el volumen crítico de la mezcla, calculado como '
                                 'promedio molar de los volúmenes críticos:',
                                 'The reduced density is the product of the phase molar density '
                                 'and the mixture critical volume, computed as the mole-fraction '
                                 'average of the critical volumes:'),
                                ('eq',
                                 '\\rho_r = \\frac{\\rho}{\\rho_c} = \\frac{\\rho}{M}\\sum_i '
                                 'x_i\\,V_{c,i}'),
                                ('p',
                                 'donde ρ es la densidad másica de la fase, M su peso molecular, '
                                 'ρ<sub>c</sub> la densidad crítica de la mezcla y V<sub>c,i</sub> '
                                 'el volumen crítico molar del componente i. Una densidad reducida '
                                 'igual a uno corresponde al punto pseudocrítico; en la fase vapor '
                                 'a baja presión ρ<sub>r</sub> es pequeña, mientras que en la fase '
                                 'líquida alcanza valores de 2 a 3 y el término residual domina.',
                                 'where ρ is the phase mass density, M its molecular weight, '
                                 'ρ<sub>c</sub> the mixture critical density and V<sub>c,i</sub> '
                                 'the critical molar volume of component i. A reduced density of '
                                 'one corresponds to the pseudocritical point; in the vapor phase '
                                 'at low pressure ρ<sub>r</sub> is small, whereas in the liquid '
                                 'phase it reaches values of 2 to 3 and the residual term '
                                 'dominates.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La densidad reducida se evalúa en las unidades internas de '
                                 'PVTsim, con los volúmenes críticos en forma reducida '
                                 'V<sub>c</sub>/R (K/atm), de modo que la constante de los gases '
                                 'se cancela:',
                                 'The reduced density is evaluated in PVTsim internal units, with '
                                 'the critical volumes in reduced form V<sub>c</sub>/R (K/atm), so '
                                 'that the gas constant cancels:'),
                                ('eq',
                                 '\\rho_r = \\frac{P/14.696}{Z\\,T_K}\\sum_i '
                                 'x_i\\left(\\frac{V_c}{R}\\right)_i \\qquad Z = '
                                 '\\frac{P\\,M\\,f_{\\rho}}{\\rho\\,R\\,T}'),
                                ('p',
                                 'donde P está en psia, T<sub>K</sub> es la temperatura en K y Z '
                                 'el factor de compresibilidad equivalente a la densidad de la '
                                 'fase, reconstruido con el factor de convención de unidades '
                                 'f<sub>ρ</sub>.',
                                 'where P is in psia, T<sub>K</sub> is the temperature in K and Z '
                                 'the compressibility factor equivalent to the phase density, '
                                 'reconstructed with the unit-convention factor f<sub>ρ</sub>.'),
                                ('ul',
                                 [('Juegos de PVTsim: T<sub>c</sub>, P<sub>c</sub> (convertida a '
                                   'atm con 14.69595 psia/atm), M y V<sub>c</sub>/R de la base de '
                                   'datos de PVTsim, incluida el agua (V<sub>c</sub>/R = '
                                   '0.68242735 K/atm).',
                                   'PVTsim sets: T<sub>c</sub>, P<sub>c</sub> (converted to atm '
                                   'with 14.69595 psia/atm), M and V<sub>c</sub>/R from the PVTsim '
                                   'database, including water (V<sub>c</sub>/R = 0.68242735 '
                                   'K/atm).'),
                                  ('Juegos de HYSYS: T<sub>c</sub>, P<sub>c</sub> (convertida con '
                                   '14.696 psia/atm) y M del banco de HYSYS, y volúmenes críticos '
                                   'de literatura (Reid, Prausnitz y Sherwood; 55.9 cm³/mol para '
                                   'el agua) reducidos con R = 82.06 cm³·atm/(mol·K).',
                                   'HYSYS sets: T<sub>c</sub>, P<sub>c</sub> (converted with '
                                   '14.696 psia/atm) and M from the HYSYS database, and literature '
                                   'critical volumes (Reid, Prausnitz and Sherwood; 55.9 cm³/mol '
                                   'for water) reduced with R = 82.06 cm³·atm/(mol·K).')]),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.',
                                 'Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.'),
                                ('p',
                                 'Reid, R.C., Prausnitz, J.M. y Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3.ª ed. McGraw-Hill.',
                                 'Reid, R.C., Prausnitz, J.M. and Sherwood, T.K. (1977). <em>The '
                                 'Properties of Gases and Liquids</em>, 3rd ed. McGraw-Hill.')]},
                   {'titulo': ('Polinomio LBC y densidad empleada',
                               'LBC polynomial and density used'),
                    'bloques': [('p',
                                 'Despejando la viscosidad de la ecuación del método se obtiene:',
                                 'Solving the method equation for viscosity gives:'),
                                ('eq',
                                 '\\eta = \\eta^* + \\frac{\\left(a_1 + a_2\\,\\rho_r + '
                                 'a_3\\,\\rho_r^2 + a_4\\,\\rho_r^3 + a_5\\,\\rho_r^4\\right)^4 - '
                                 '10^{-4}}{\\xi}'),
                                ('eq',
                                 'a_1 = 0.10230 \\quad a_2 = 0.023364 \\quad a_3 = 0.058533 \\quad '
                                 'a_4 = -0.040758 \\quad a_5 = 0.0093324'),
                                ('p',
                                 'donde a<sub>1</sub> a a<sub>5</sub> son las constantes '
                                 'universales de Lohrenz, Bray y Clark. El término 10<sup>−4</sup> '
                                 'garantiza que para ρ<sub>r</sub> → 0 la expresión se reduzca a '
                                 'η*, en continuidad con la viscosidad de gas diluido. Si el '
                                 'numerador resulta negativo se anula y la viscosidad es la de gas '
                                 'diluido.',
                                 'where a<sub>1</sub> to a<sub>5</sub> are the universal '
                                 'Lohrenz-Bray-Clark constants. The 10<sup>−4</sup> term ensures '
                                 'that for ρ<sub>r</sub> → 0 the expression reduces to η*, in '
                                 'continuity with the dilute-gas viscosity. If the numerator turns '
                                 'out negative it is set to zero and the viscosity equals the '
                                 'dilute-gas value.'),
                                ('h3', 'Densidad empleada', 'Density used'),
                                ('p',
                                 'La densidad reducida se evalúa con la densidad de la fase que '
                                 'reporta el método de densidad seleccionado: la de la ecuación de '
                                 'estado con el método EOS, la densidad COSTALD (o la combinación '
                                 'de la banda de transición) con el método COSTALD, y la densidad '
                                 'trasladada con la corrección de Peneloux. Por ello la viscosidad '
                                 'de las fases líquidas depende del método de densidad elegido; '
                                 'con el método EOS coincide con la formulación de PVTsim, que '
                                 'evalúa LBC con la densidad de su ecuación de estado.',
                                 'The reduced density is evaluated with the phase density reported '
                                 'by the selected density method: the equation-of-state density '
                                 'with the EOS method, the COSTALD density (or the transition-band '
                                 'blend) with the COSTALD method, and the shifted density with the '
                                 'Peneloux correction. Hence the viscosity of the liquid phases '
                                 'depends on the chosen density method; with the EOS method it '
                                 'matches the PVTsim formulation, which evaluates LBC with its '
                                 'equation-of-state density.'),
                                ('p',
                                 'En el flash trifásico, la viscosidad de las fases vapor y '
                                 'líquido de hidrocarburos se calcula con la misma formulación '
                                 'sobre los catorce componentes de la fase, incluida el agua '
                                 'disuelta.',
                                 'In the three-phase flash, the viscosity of the vapor and '
                                 'hydrocarbon liquid phases is computed with the same formulation '
                                 'over the fourteen components of the phase, including dissolved '
                                 'water.'),
                                ('h3', 'Alcance del método', 'Method scope'),
                                ('p',
                                 'El método LBC utiliza únicamente propiedades críticas, pesos '
                                 'moleculares y volúmenes críticos, sin datos adicionales. Su '
                                 'exactitud típica para gases y líquidos livianos de hidrocarburos '
                                 'es del orden de 5 a 10 %; para aceites con alto contenido de '
                                 'fracciones pesadas la exactitud disminuye, ya que la viscosidad '
                                 'es muy sensible a la densidad reducida del líquido.',
                                 'The LBC method uses only critical properties, molecular weights '
                                 'and critical volumes, without additional data. Its typical '
                                 'accuracy for gases and light hydrocarbon liquids is of the order '
                                 'of 5 to 10 %; for oils with a high content of heavy fractions '
                                 'accuracy decreases, since viscosity is highly sensitive to the '
                                 'liquid reduced density.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Lohrenz, J., Bray, B.G. y Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.',
                                 'Lohrenz, J., Bray, B.G. and Clark, C.R. (1964). Calculating '
                                 'viscosities of reservoir fluids from their compositions. '
                                 '<em>Journal of Petroleum Technology</em>, 16(10), 1171–1176.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Viscosidad de la fase acuosa', 'Aqueous-phase viscosity'),
                    'bloques': [('p',
                                 'El método LBC fue desarrollado para hidrocarburos y no '
                                 'representa adecuadamente la viscosidad del agua líquida. Para la '
                                 'fase acuosa del flash trifásico, ThermoPhase emplea la '
                                 'correlación de viscosidad del agua pura que documenta PVTsim '
                                 '(Water Phase Properties), basada en Meyer et al. (1967) y '
                                 'Schmidt (1969), que divide el plano temperatura-presión en '
                                 'cuatro regiones. La correlación se evalúa con la temperatura en '
                                 'K, la presión en MN/m² y la densidad de la fase acuosa en g/cm³, '
                                 'obtenida con el método de densidad seleccionado.',
                                 'The LBC method was developed for hydrocarbons and does not '
                                 'adequately represent the viscosity of liquid water. For the '
                                 'aqueous phase of the three-phase flash, ThermoPhase uses the '
                                 'pure-water viscosity correlation documented by PVTsim (Water '
                                 'Phase Properties), based on Meyer et al. (1967) and Schmidt '
                                 '(1969), which divides the temperature-pressure plane into four '
                                 'regions. The correlation is evaluated with temperature in K, '
                                 'pressure in MN/m² and the aqueous-phase density in g/cm³, '
                                 'obtained with the selected density method.'),
                                ('h3', 'Región de agua líquida', 'Liquid-water region'),
                                ('p',
                                 'Para 273.15 K &lt; T &lt; 573.15 K y P<sub>sat</sub> &lt; P &lt; '
                                 '80 MN/m², que es la región habitual de la fase acuosa:',
                                 'For 273.15 K &lt; T &lt; 573.15 K and P<sub>sat</sub> &lt; P '
                                 '&lt; 80 MN/m², the usual region of the aqueous phase:'),
                                ('eq',
                                 '\\eta = 10^{-6}\\,a_1\\left[1 + \\left(\\frac{\\rho}{\\rho_c} - '
                                 '\\frac{P_{sat}}{P_c}\\right)a_4\\left(T_r - '
                                 'a_5\\right)\\right]10^{a_2/(T_r - a_3)}'),
                                ('p',
                                 'donde η es la viscosidad (poise, multiplicada por 100 para '
                                 'expresarla en cP), ρ la densidad de la fase (g/cm³), '
                                 'ρ<sub>c</sub> = 0.317 g/cm³, P<sub>c</sub> = 22.12 MN/m², '
                                 'T<sub>r</sub> = T/647.3 K, P<sub>sat</sub> la presión de vapor '
                                 'del agua (MN/m²) y a<sub>1</sub> = 241.4, a<sub>2</sub> = '
                                 '0.3828209486, a<sub>3</sub> = 0.2162830218, a<sub>4</sub> = '
                                 '0.1498693949, a<sub>5</sub> = 0.4711880117.',
                                 'where η is the viscosity (poise, multiplied by 100 to express it '
                                 'in cP), ρ the phase density (g/cm³), ρ<sub>c</sub> = 0.317 '
                                 'g/cm³, P<sub>c</sub> = 22.12 MN/m², T<sub>r</sub> = T/647.3 K, '
                                 'P<sub>sat</sub> the water vapor pressure (MN/m²) and '
                                 'a<sub>1</sub> = 241.4, a<sub>2</sub> = 0.3828209486, '
                                 'a<sub>3</sub> = 0.2162830218, a<sub>4</sub> = 0.1498693949, '
                                 'a<sub>5</sub> = 0.4711880117.'),
                                ('eq',
                                 '\\log_{10} P_{sat} = (D_1 - 1) + \\frac{D_2}{T} + '
                                 '\\sum_{j=3}^{7} D_j\\,T^{\\,j-2}'),
                                ('p',
                                 'donde P<sub>sat</sub> está en MN/m², T en K y D<sub>1</sub> a '
                                 'D<sub>7</sub> son las constantes del manual de PVTsim '
                                 '(D<sub>1</sub> = 2.9304370, D<sub>2</sub> = −2309.5789, '
                                 'D<sub>3</sub> = 3.4522497·10<sup>−2</sup>, D<sub>4</sub> = '
                                 '−1.3621289·10<sup>−4</sup>, D<sub>5</sub> = '
                                 '2.5878044·10<sup>−7</sup>, D<sub>6</sub> = '
                                 '−2.4709162·10<sup>−10</sup>, D<sub>7</sub> = '
                                 '9.5937646·10<sup>−14</sup>).',
                                 'where P<sub>sat</sub> is in MN/m², T in K and D<sub>1</sub> to '
                                 'D<sub>7</sub> are the PVTsim manual constants (D<sub>1</sub> = '
                                 '2.9304370, D<sub>2</sub> = −2309.5789, D<sub>3</sub> = '
                                 '3.4522497·10<sup>−2</sup>, D<sub>4</sub> = '
                                 '−1.3621289·10<sup>−4</sup>, D<sub>5</sub> = '
                                 '2.5878044·10<sup>−7</sup>, D<sub>6</sub> = '
                                 '−2.4709162·10<sup>−10</sup>, D<sub>7</sub> = '
                                 '9.5937646·10<sup>−14</sup>).'),
                                ('p',
                                 'Por debajo de 273.15 K, si la fase es líquida (ρ &gt; 0.7 '
                                 'g/cm³), se mantiene la expresión de agua líquida con presión de '
                                 'vapor nula, como agua subenfriada, y la viscosidad se limita a '
                                 '7.2551 cP.',
                                 'Below 273.15 K, if the phase is liquid (ρ &gt; 0.7 g/cm³), the '
                                 'liquid-water expression is retained with zero vapor pressure, as '
                                 'subcooled water, and the viscosity is capped at 7.2551 cP.'),
                                ('h3', 'Otras regiones', 'Other regions'),
                                ('p',
                                 'Las regiones restantes parten de la viscosidad a presión '
                                 'atmosférica η<sub>1</sub> = '
                                 '10<sup>−6</sup>[b<sub>1</sub>(T<sub>r</sub> − b<sub>2</sub>) + '
                                 'b<sub>3</sub>] poise, con b<sub>1</sub> = 263.4511, '
                                 'b<sub>2</sub> = 0.4219836243 y b<sub>3</sub> = 80.4:',
                                 'The remaining regions start from the atmospheric-pressure '
                                 'viscosity η<sub>1</sub> = '
                                 '10<sup>−6</sup>[b<sub>1</sub>(T<sub>r</sub> − b<sub>2</sub>) + '
                                 'b<sub>3</sub>] poise, with b<sub>1</sub> = 263.4511, '
                                 'b<sub>2</sub> = 0.4219836243 and b<sub>3</sub> = 80.4:'),
                                ('ul',
                                 [('Vapor subsaturado (0.1 MN/m² &lt; P &lt; P<sub>sat</sub>, '
                                   '373.15 K &lt; T &lt; 573.15 K): η = η<sub>1</sub> − '
                                   '10<sup>−5</sup>(ρ/ρ<sub>c</sub>)[c<sub>1</sub> − '
                                   'c<sub>2</sub>(T<sub>r</sub> − c<sub>3</sub>)], con '
                                   'c<sub>1</sub> = 586.1198738, c<sub>2</sub> = 1204.753943, '
                                   'c<sub>3</sub> = 0.4219836243.',
                                   'Subsaturated vapor (0.1 MN/m² &lt; P &lt; P<sub>sat</sub>, '
                                   '373.15 K &lt; T &lt; 573.15 K): η = η<sub>1</sub> − '
                                   '10<sup>−5</sup>(ρ/ρ<sub>c</sub>)[c<sub>1</sub> − '
                                   'c<sub>2</sub>(T<sub>r</sub> − c<sub>3</sub>)], with '
                                   'c<sub>1</sub> = 586.1198738, c<sub>2</sub> = 1204.753943, '
                                   'c<sub>3</sub> = 0.4219836243.'),
                                  ('Alta temperatura (0.1 &lt; P &lt; 80 MN/m², 648.15 K &lt; T '
                                   '&lt; 1073.15 K): η = η<sub>1</sub> + '
                                   '10<sup>−6</sup>[d<sub>1</sub>(ρ/ρ<sub>c</sub>)³ + '
                                   'd<sub>2</sub>(ρ/ρ<sub>c</sub>)² + '
                                   'd<sub>3</sub>(ρ/ρ<sub>c</sub>)], con d<sub>1</sub> = '
                                   '111.3564669, d<sub>2</sub> = 67.32080129, d<sub>3</sub> = '
                                   '3.205147019.',
                                   'High temperature (0.1 &lt; P &lt; 80 MN/m², 648.15 K &lt; T '
                                   '&lt; 1073.15 K): η = η<sub>1</sub> + '
                                   '10<sup>−6</sup>[d<sub>1</sub>(ρ/ρ<sub>c</sub>)³ + '
                                   'd<sub>2</sub>(ρ/ρ<sub>c</sub>)² + '
                                   'd<sub>3</sub>(ρ/ρ<sub>c</sub>)], with d<sub>1</sub> = '
                                   '111.3564669, d<sub>2</sub> = 67.32080129, d<sub>3</sub> = '
                                   '3.205147019.'),
                                  ('Resto del plano: η = η<sub>1</sub> + '
                                   '10<sup>−6</sup>·10<sup>Y</sup>/0.0192, con Y un polinomio de '
                                   'cuarto grado en X = log<sub>10</sub>(ρ/ρ<sub>c</sub>) cuyos '
                                   'coeficientes dependen de si ρ/ρ<sub>c</sub> ≤ 4/3.14.',
                                   'Rest of the plane: η = η<sub>1</sub> + '
                                   '10<sup>−6</sup>·10<sup>Y</sup>/0.0192, with Y a fourth-degree '
                                   'polynomial in X = log<sub>10</sub>(ρ/ρ<sub>c</sub>) whose '
                                   'coefficients depend on whether ρ/ρ<sub>c</sub> ≤ 4/3.14.')]),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La densidad de la fase acuosa en lb/ft³ se convierte a g/cm³ '
                                 'dividiendo por 62.42796, y la presión de psia a MN/m² '
                                 'multiplicando por 0.00689476. Si la correlación del agua no '
                                 'produce un valor positivo, la viscosidad de la fase acuosa se '
                                 'calcula por el método LBC sobre sus catorce componentes, con los '
                                 'parámetros críticos del agua del juego de parámetros activo.',
                                 'The aqueous-phase density in lb/ft³ is converted to g/cm³ by '
                                 'dividing by 62.42796, and the pressure from psia to MN/m² by '
                                 'multiplying by 0.00689476. If the water correlation does not '
                                 'yield a positive value, the aqueous-phase viscosity is computed '
                                 'with the LBC method over its fourteen components, with the water '
                                 'critical parameters of the active parameter set.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Meyer, C.A., McClintock, R.B., Silvestri, G.J. y Spencer, R.C. '
                                 '(1967). <em>ASME Steam Tables: Thermodynamic and Transport '
                                 'Properties of Steam</em>. American Society of Mechanical '
                                 'Engineers.',
                                 'Meyer, C.A., McClintock, R.B., Silvestri, G.J. and Spencer, R.C. '
                                 '(1967). <em>ASME Steam Tables: Thermodynamic and Transport '
                                 'Properties of Steam</em>. American Society of Mechanical '
                                 'Engineers.'),
                                ('p',
                                 'Schmidt, E. (1969). <em>Properties of Water and Steam in '
                                 'SI-Units</em>. Springer-Verlag.',
                                 'Schmidt, E. (1969). <em>Properties of Water and Steam in '
                                 'SI-Units</em>. Springer-Verlag.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>, sección Water '
                                 'Phase Properties. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>, Water Phase '
                                 'Properties section. Calsep A/S.')]}]},
 {'titulo': ('Propiedades del gas', 'Gas properties'),
  'subsecciones': [{'titulo': ('Poder calorífico: definiciones y bases',
                               'Heating value: definitions and bases'),
                    'bloques': [('p',
                                 'El poder calorífico de un gas es la energía liberada por la '
                                 'combustión completa de una unidad de gas con aire, con los '
                                 'productos llevados a la temperatura inicial de los reactivos. Es '
                                 'la propiedad que fija el valor comercial del gas natural y la '
                                 'que se contrasta con las especificaciones de venta y de '
                                 'transporte por gasoducto. ThermoPhase reporta el poder '
                                 'calorífico de la fase vapor, de la fase líquida de hidrocarburos '
                                 'y de la mezcla global en cada punto calculado (Equilibrio de '
                                 'fases, Puntos de saturación y Formación de hidratos).',
                                 'The heating value of a gas is the energy released by the '
                                 'complete combustion of a unit of gas with air, with the products '
                                 'brought back to the initial temperature of the reactants. It is '
                                 'the property that sets the commercial value of natural gas and '
                                 'that is checked against sales and pipeline specifications. '
                                 'ThermoPhase reports the heating value of the vapor phase, the '
                                 'hydrocarbon liquid phase, and the overall mixture at every '
                                 'calculated point (Phase Equilibrium, Saturation Points, and '
                                 'Hydrate Formation).'),
                                ('p',
                                 'Se reportan dos definiciones. El poder calorífico superior o '
                                 'bruto (HHV, <em>higher heating value</em>) supone que el agua '
                                 'formada en la combustión condensa a líquido, de modo que se '
                                 'recupera su calor latente de vaporización. El poder calorífico '
                                 'inferior o neto (LHV, <em>lower heating value</em>) supone que '
                                 'esa agua permanece como vapor. La diferencia entre ambos es el '
                                 'calor latente del agua producida.',
                                 'Two definitions are reported. The gross or higher heating value '
                                 '(HHV) assumes that the water formed by combustion condenses to '
                                 'liquid, so its latent heat of vaporization is recovered. The net '
                                 'or lower heating value (LHV) assumes that this water remains as '
                                 'vapor. The difference between the two is the latent heat of the '
                                 'water produced.'),
                                ('p',
                                 'Cada definición se expresa en dos bases: la base volumétrica, en '
                                 'BTU por pie cúbico de gas ideal a las condiciones estándar de 60 '
                                 '°F y 14.696 psia, que es la convención de las tablas GPSA y de '
                                 'HYSYS, y la base másica, en BTU por libra. La interfaz convierte '
                                 'ambos valores al sistema de unidades activo.',
                                 'Each definition is expressed on two bases: the volumetric basis, '
                                 'in BTU per cubic foot of ideal gas at the standard conditions of '
                                 '60 °F and 14.696 psia, which is the convention of the GPSA '
                                 'tables and of HYSYS, and the mass basis, in BTU per pound. The '
                                 'interface converts both values to the active unit system.'),
                                ('h3', 'Composición de cálculo', 'Calculation composition'),
                                ('p',
                                 'El poder calorífico se calcula sobre la composición de '
                                 'hidrocarburos de cada fase, con el agua excluida. Cuando la '
                                 'mezcla contiene agua, las fracciones molares de los trece '
                                 'componentes restantes (N<sub>2</sub>, CO<sub>2</sub> y '
                                 'C<sub>1</sub> a C<sub>9</sub>) se renormalizan a la unidad antes '
                                 'de aplicar la regla de mezcla, y el peso molecular de la fase se '
                                 'evalúa sobre esa misma composición renormalizada. El valor '
                                 'reportado corresponde, por tanto, a la corriente de '
                                 'hidrocarburos en base seca.',
                                 'The heating value is calculated on the hydrocarbon composition '
                                 'of each phase, with water excluded. When the mixture contains '
                                 'water, the mole fractions of the remaining thirteen components '
                                 '(N<sub>2</sub>, CO<sub>2</sub>, and C<sub>1</sub> through '
                                 'C<sub>9</sub>) are renormalized to unity before the mixing rule '
                                 'is applied, and the phase molecular weight is evaluated on the '
                                 'same renormalized composition. The reported value therefore '
                                 'corresponds to the hydrocarbon stream on a dry basis.'),
                                ('eq',
                                 '\\tilde{z}_i = \\frac{z_i}{\\sum_{j \\neq \\mathrm{H_2O}} z_j}'),
                                ('p',
                                 'donde z<sub>i</sub> es la fracción molar del componente i en la '
                                 'fase (y para el vapor, x para el líquido y la composición global '
                                 'para la mezcla), la suma excluye el agua y z̃<sub>i</sub> es la '
                                 'fracción molar en base libre de agua.',
                                 'where z<sub>i</sub> is the mole fraction of component i in the '
                                 'phase (y for the vapor, x for the liquid, and the overall '
                                 'composition for the mixture), the sum excludes water, and '
                                 'z̃<sub>i</sub> is the water-free mole fraction.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.'),
                                ('p',
                                 'Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>, '
                                 'vol. 1. Campbell Petroleum Series.',
                                 'Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>, '
                                 'vol. 1. Campbell Petroleum Series.')]},
                   {'titulo': ('Poder calorífico volumétrico', 'Volumetric heating value'),
                    'bloques': [('p',
                                 'El poder calorífico volumétrico de una fase se obtiene como el '
                                 'promedio molar de los valores caloríficos de los componentes '
                                 'puros, según el procedimiento del GPSA Engineering Data Book:',
                                 'The volumetric heating value of a phase is obtained as the molar '
                                 'average of the pure-component heating values, following the '
                                 'procedure of the GPSA Engineering Data Book:'),
                                ('eq', 'HV = \\sum_{i=1}^{N} \\tilde{z}_i \\, HV_i'),
                                ('p',
                                 'donde HV es el poder calorífico volumétrico de la fase (superior '
                                 'o inferior), en BTU/ft³ de gas ideal, HV<sub>i</sub> es el valor '
                                 'calorífico volumétrico del componente puro i en base gas ideal a '
                                 '60 °F y 14.696 psia, en BTU/ft³, y N es el número de componentes '
                                 'de hidrocarburo. La ponderación molar es exacta en base gas '
                                 'ideal porque todos los componentes ocupan el mismo volumen molar '
                                 'a las condiciones estándar.',
                                 'where HV is the volumetric heating value of the phase (higher or '
                                 'lower), in BTU/ft³ of ideal gas, HV<sub>i</sub> is the ideal-gas '
                                 'volumetric heating value of pure component i at 60 °F and 14.696 '
                                 'psia, in BTU/ft³, and N is the number of hydrocarbon components. '
                                 'Molar weighting is exact on the ideal-gas basis because all '
                                 'components occupy the same molar volume at standard conditions.'),
                                ('p',
                                 'El poder calorífico volumétrico se expresa siempre en base gas '
                                 'ideal, también para la fase líquida: el valor reportado para el '
                                 'líquido es el que tendría su composición vaporizada a gas ideal '
                                 'en condiciones estándar, de acuerdo con la convención de las '
                                 'tablas GPSA y de HYSYS.',
                                 'The volumetric heating value is always expressed on an ideal-gas '
                                 'basis, including for the liquid phase: the value reported for '
                                 'the liquid is the one its composition would have if vaporized to '
                                 'ideal gas at standard conditions, in accordance with the '
                                 'convention of the GPSA tables and HYSYS.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los valores por componente corresponden a la tabla de '
                                 'propiedades físicas GPSA-87 (valor calorífico a 60 °F, gas ideal '
                                 'a 14.696 psia). Los valores inferior / superior en BTU/ft³ son '
                                 'los siguientes:',
                                 'The component values are those of the GPSA-87 physical property '
                                 'table (heating value at 60 °F, ideal gas at 14.696 psia). The '
                                 'lower / higher values in BTU/ft³ are as follows:'),
                                ('ul',
                                 [('Metano 909.4 / 1010.0; etano 1618.7 / 1769.6; propano 2314.9 / '
                                   '2516.1.',
                                   'Methane 909.4 / 1010.0; ethane 1618.7 / 1769.6; propane 2314.9 '
                                   '/ 2516.1.'),
                                  ('Isobutano 3000.4 / 3251.9; n-butano 3010.8 / 3262.3; '
                                   'isopentano 3699.0 / 4000.9; n-pentano 3706.9 / 4008.9.',
                                   'Isobutane 3000.4 / 3251.9; n-butane 3010.8 / 3262.3; '
                                   'isopentane 3699.0 / 4000.9; n-pentane 3706.9 / 4008.9.'),
                                  ('C<sub>6</sub> (n-hexano) 4403.8 / 4755.9; C<sub>7</sub> '
                                   '(n-heptano) 5100.0 / 5502.5; C<sub>8</sub> (n-octano) 5796.1 / '
                                   '6248.9; C<sub>9</sub> (n-nonano) 6493.2 / 6996.5.',
                                   'C<sub>6</sub> (n-hexane) 4403.8 / 4755.9; C<sub>7</sub> '
                                   '(n-heptane) 5100.0 / 5502.5; C<sub>8</sub> (n-octane) 5796.1 / '
                                   '6248.9; C<sub>9</sub> (n-nonane) 6493.2 / 6996.5.'),
                                  ('N<sub>2</sub> y CO<sub>2</sub>: 0, por no ser combustibles; '
                                   'actúan como diluyentes que reducen el poder calorífico en '
                                   'proporción a su fracción molar.',
                                   'N<sub>2</sub> and CO<sub>2</sub>: 0, since they are not '
                                   'combustible; they act as diluents that reduce the heating '
                                   'value in proportion to their mole fraction.')]),
                                ('p',
                                 'Antes de aplicar la regla de mezcla, la composición se normaliza '
                                 'a suma unitaria. Si la fase no existe en el punto calculado, su '
                                 'poder calorífico no se reporta.',
                                 'Before the mixing rule is applied, the composition is normalized '
                                 'to unit sum. If the phase does not exist at the calculated '
                                 'point, its heating value is not reported.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.'),
                                ('p',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.',
                                 'AspenTech. <em>Aspen HYSYS Properties and Methods Technical '
                                 'Reference</em>. Aspen Technology, Inc.')]},
                   {'titulo': ('Poder calorífico en base másica', 'Mass-basis heating value'),
                    'bloques': [('p',
                                 'El poder calorífico másico se obtiene del volumétrico pasando '
                                 'por la base molar. Para ello se multiplica por el volumen molar '
                                 'del gas ideal a las condiciones estándar:',
                                 'The mass-basis heating value is obtained from the volumetric '
                                 'value through the molar basis. For this, it is multiplied by the '
                                 'ideal-gas molar volume at standard conditions:'),
                                ('eq',
                                 'V_{std} = \\frac{R\\,T_{std}}{P_{std}} = \\frac{10.7316 \\times '
                                 '519.67}{14.696} \\approx 379.48 \\ \\mathrm{ft^3/lbmol}'),
                                ('p',
                                 'donde R = 10.7316 psia·ft³/(lbmol·°R) es la constante universal '
                                 'de los gases, T<sub>std</sub> = 519.67 °R (60 °F) y '
                                 'P<sub>std</sub> = 14.696 psia.',
                                 'where R = 10.7316 psia·ft³/(lbmol·°R) is the universal gas '
                                 'constant, T<sub>std</sub> = 519.67 °R (60 °F), and '
                                 'P<sub>std</sub> = 14.696 psia.'),
                                ('eq', 'HV_{m} = \\frac{HV \\cdot V_{std}}{M}'),
                                ('p',
                                 'donde HV<sub>m</sub> es el poder calorífico másico, en BTU/lb, '
                                 'el producto HV·V<sub>std</sub> es el poder calorífico molar, en '
                                 'BTU/lbmol, y M es el peso molecular de la fase, en lb/lbmol.',
                                 'where HV<sub>m</sub> is the mass-basis heating value, in BTU/lb, '
                                 'the product HV·V<sub>std</sub> is the molar heating value, in '
                                 'BTU/lbmol, and M is the phase molecular weight, in lb/lbmol.'),
                                ('eq', 'M = \\sum_{i=1}^{N} \\tilde{z}_i \\, M_i'),
                                ('p',
                                 'donde M<sub>i</sub> es el peso molecular del componente i, en '
                                 'lb/lbmol. El peso molecular se evalúa sobre la composición de '
                                 'hidrocarburos libre de agua, coherente con el cálculo del poder '
                                 'calorífico volumétrico, de modo que el agua disuelta en la fase '
                                 'no diluye el valor másico.',
                                 'where M<sub>i</sub> is the molecular weight of component i, in '
                                 'lb/lbmol. The molecular weight is evaluated on the water-free '
                                 'hydrocarbon composition, consistent with the volumetric heating '
                                 'value calculation, so the water dissolved in the phase does not '
                                 'dilute the mass-basis value.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.')]},
                   {'titulo': ('Contenido de licuables (GPM C3+)', 'Liquefiable content (GPM C3+)'),
                    'bloques': [('p',
                                 'El GPM (<em>gallons per thousand cubic feet</em>) mide el '
                                 'contenido de hidrocarburos licuables de una corriente de gas: el '
                                 'volumen de líquido, en galones, que se obtendría de mil pies '
                                 'cúbicos estándar de gas si se recuperasen el propano y los '
                                 'componentes más pesados. Es un indicador de la riqueza del gas y '
                                 'del potencial de una planta de extracción de líquidos.',
                                 'GPM (gallons per thousand cubic feet) measures the liquefiable '
                                 'hydrocarbon content of a gas stream: the liquid volume, in '
                                 'gallons, that would be obtained from one thousand standard cubic '
                                 'feet of gas if propane and heavier components were recovered. It '
                                 'is an indicator of gas richness and of the potential of a '
                                 'liquids extraction plant.'),
                                ('eq',
                                 'GPM = \\frac{1000}{V_{std}} \\sum_{i \\geq C_3} \\tilde{y}_i \\, '
                                 'G_i'),
                                ('p',
                                 'donde GPM está en gal/Mscf, ỹ<sub>i</sub> es la fracción molar '
                                 'del componente i en el gas (base libre de agua), G<sub>i</sub> '
                                 'es el volumen de líquido que produce una libra-mol del '
                                 'componente, en gal/lbmol, a 60 °F y 14.696 psia, y '
                                 'V<sub>std</sub> = 379.48 ft³/lbmol.',
                                 'where GPM is in gal/Mscf, ỹ<sub>i</sub> is the mole fraction of '
                                 'component i in the gas (water-free basis), G<sub>i</sub> is the '
                                 'liquid volume yielded by one pound-mole of the component, in '
                                 'gal/lbmol, at 60 °F and 14.696 psia, and V<sub>std</sub> = '
                                 '379.48 ft³/lbmol.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los factores G<sub>i</sub> son los de la tabla GPSA-87 (columna '
                                 'gal/lbmol): propano 10.433, isobutano 12.386, n-butano 11.937, '
                                 'isopentano 13.853, n-pentano 13.712, n-hexano 15.571, n-heptano '
                                 '17.464, n-octano 19.381 y n-nonano 21.311. Metano, etano, '
                                 'N<sub>2</sub> y CO<sub>2</sub> tienen factor nulo, puesto que no '
                                 'se recuperan como líquido en el procesamiento convencional.',
                                 'The G<sub>i</sub> factors are those of the GPSA-87 table '
                                 '(gal/lbmol column): propane 10.433, isobutane 12.386, n-butane '
                                 '11.937, isopentane 13.853, n-pentane 13.712, n-hexane 15.571, '
                                 'n-heptane 17.464, n-octane 19.381, and n-nonane 21.311. Methane, '
                                 'ethane, N<sub>2</sub>, and CO<sub>2</sub> have a zero factor, '
                                 'since they are not recovered as liquid in conventional '
                                 'processing.'),
                                ('p',
                                 'El GPM se reporta para la fase gas, que es la corriente de la '
                                 'que se extraen los licuables. En las pestañas Puntos de '
                                 'saturación y Formación de hidratos, en cálculos sin agua, se '
                                 'reporta además para la mezcla global. No se reporta para la fase '
                                 'líquida.',
                                 'GPM is reported for the gas phase, which is the stream from '
                                 'which liquefiables are extracted. In the Saturation Points and '
                                 'Hydrate Formation tabs, for calculations without water, it is '
                                 'also reported for the overall mixture. It is not reported for '
                                 'the liquid phase.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.'),
                                ('p',
                                 'Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>, '
                                 'vol. 1. Campbell Petroleum Series.',
                                 'Campbell, J.M. (1992). <em>Gas Conditioning and Processing</em>, '
                                 'vol. 1. Campbell Petroleum Series.')]},
                   {'titulo': ('Contenido y capacidad de agua del gas',
                               'Gas water content and water capacity'),
                    'bloques': [('p',
                                 'El agua de la fase gas se expresa en libras de agua por millón '
                                 'de pies cúbicos estándar de gas (lb/MMscf), la unidad de la '
                                 'carta de McKetta-Wehe y del GPSA Engineering Data Book. Se '
                                 'reportan dos propiedades, ambas exclusivas de la fase vapor: el '
                                 'contenido de agua, que es el agua que el gas lleva realmente en '
                                 'las condiciones del cálculo, y la capacidad de agua, que es el '
                                 'agua que ese mismo gas tendría si estuviera saturado, es decir, '
                                 'en equilibrio con agua libre a la misma temperatura y presión.',
                                 'The water in the gas phase is expressed in pounds of water per '
                                 'million standard cubic feet of gas (lb/MMscf), the unit of the '
                                 'McKetta-Wehe chart and of the GPSA Engineering Data Book. Two '
                                 'properties are reported, both exclusive to the vapor phase: the '
                                 'water content, which is the water actually carried by the gas at '
                                 'the calculation conditions, and the water capacity, which is the '
                                 'water the same gas would hold if saturated, that is, in '
                                 'equilibrium with free water at the same temperature and '
                                 'pressure.'),
                                ('h3', 'Contenido de agua', 'Water content'),
                                ('eq',
                                 'W = y_{\\mathrm{H_2O}} \\, M_{\\mathrm{H_2O}} \\, '
                                 '\\frac{10^6}{V_{std}}'),
                                ('p',
                                 'donde W es el contenido de agua, en lb/MMscf, y<sub>H₂O</sub> es '
                                 'la fracción molar de agua en la fase vapor obtenida del flash, '
                                 'M<sub>H₂O</sub> = 18.0153 lb/lbmol es el peso molecular del agua '
                                 'y V<sub>std</sub> = 379.48 scf/lbmol es el volumen molar del gas '
                                 'ideal a 60 °F y 14.696 psia. El factor '
                                 'M<sub>H₂O</sub>·10<sup>6</sup>/V<sub>std</sub> vale '
                                 'aproximadamente 47 473 lb/MMscf por unidad de fracción molar.',
                                 'where W is the water content, in lb/MMscf, y<sub>H₂O</sub> is '
                                 'the water mole fraction in the vapor phase obtained from the '
                                 'flash, M<sub>H₂O</sub> = 18.0153 lb/lbmol is the molecular '
                                 'weight of water, and V<sub>std</sub> = 379.48 scf/lbmol is the '
                                 'ideal-gas molar volume at 60 °F and 14.696 psia. The factor '
                                 'M<sub>H₂O</sub>·10<sup>6</sup>/V<sub>std</sub> is approximately '
                                 '47,473 lb/MMscf per unit mole fraction.'),
                                ('p',
                                 'El volumen estándar es de gas ideal, como en el GPSA y en HYSYS; '
                                 'por ello no depende de la composición, que interviene solo a '
                                 'través de y<sub>H₂O</sub>. La base es la de gas húmedo: el vapor '
                                 'de agua se cuenta dentro de los pies cúbicos estándar del gas. '
                                 'En base de gas seco el valor se dividiría además por (1 − '
                                 'y<sub>H₂O</sub>), una diferencia inferior al 0.3 % en el '
                                 'intervalo usual de operación. Cuando el cálculo se realiza sin '
                                 'agua, el contenido de agua del gas es nulo.',
                                 'The standard volume is an ideal-gas volume, as in GPSA and '
                                 'HYSYS; it therefore does not depend on composition, which enters '
                                 'only through y<sub>H₂O</sub>. The basis is wet gas: the water '
                                 'vapor is counted within the standard cubic feet of gas. On a '
                                 'dry-gas basis the value would additionally be divided by (1 − '
                                 'y<sub>H₂O</sub>), a difference below 0.3 % in the usual '
                                 'operating range. When the calculation is performed without '
                                 'water, the gas water content is zero.'),
                                ('h3', 'Capacidad de agua', 'Water capacity'),
                                ('p',
                                 'La capacidad de agua se calcula mediante un segundo flash a la '
                                 'misma temperatura y presión. Se toma la composición de '
                                 'hidrocarburos de la fase vapor del flash original, se satura con '
                                 'agua añadiendo un pequeño exceso de agua libre y se resuelve el '
                                 'equilibrio trifásico vapor-líquido-acuosa con la regla de mezcla '
                                 'de Huron-Vidal. La fracción molar de agua en el vapor de ese '
                                 'segundo flash, y<sub>H₂O</sub><sup>sat</sup>, define la '
                                 'capacidad:',
                                 'The water capacity is calculated by a second flash at the same '
                                 'temperature and pressure. The hydrocarbon composition of the '
                                 'vapor phase from the original flash is taken, saturated with '
                                 'water by adding a small excess of free water, and the '
                                 'vapor-liquid-aqueous three-phase equilibrium is solved with the '
                                 'Huron-Vidal mixing rule. The water mole fraction in the vapor of '
                                 'this second flash, y<sub>H₂O</sub><sup>sat</sup>, defines the '
                                 'capacity:'),
                                ('eq',
                                 'W_{sat} = y_{\\mathrm{H_2O}}^{sat} \\, M_{\\mathrm{H_2O}} \\, '
                                 '\\frac{10^6}{V_{std}}'),
                                ('p',
                                 'donde W<sub>sat</sub> es la capacidad de agua, en lb/MMscf. La '
                                 'saturación se construye estimando primero la relación '
                                 'agua/hidrocarburo con la presión de vapor de Wilson del agua '
                                 '(tres veces P<sup>sat</sup>/P), aumentándola hasta que aparece '
                                 'fase acuosa, calculando con ese flash la cantidad de agua '
                                 'disuelta en las fases de hidrocarburo y añadiendo finalmente un '
                                 'exceso del 5 % sobre esa cantidad (ampliado por factores de tres '
                                 'si la fase acuosa no llega a formarse).',
                                 'where W<sub>sat</sub> is the water capacity, in lb/MMscf. '
                                 'Saturation is built by first estimating the water/hydrocarbon '
                                 'ratio from the Wilson vapor pressure of water (three times '
                                 'P<sup>sat</sup>/P), increasing it until an aqueous phase '
                                 'appears, computing from that flash the amount of water dissolved '
                                 'in the hydrocarbon phases, and finally adding an excess of 5 % '
                                 'over that amount (enlarged by factors of three if the aqueous '
                                 'phase does not form).'),
                                ('p',
                                 'Si el flash original ya presenta fase acuosa libre, el vapor '
                                 'está saturado y la capacidad es igual al contenido, sin segundo '
                                 'flash. Si el gas está subsaturado, la capacidad es mayor que el '
                                 'contenido; en un cálculo sin agua el contenido es cero y la '
                                 'capacidad conserva su valor positivo. Por su costo, la capacidad '
                                 'se evalúa solo cuando la propiedad está seleccionada en la tabla '
                                 'de resultados.',
                                 'If the original flash already exhibits a free aqueous phase, the '
                                 'vapor is saturated and the capacity equals the content, without '
                                 'a second flash. If the gas is undersaturated, the capacity is '
                                 'greater than the content; in a calculation without water the '
                                 'content is zero and the capacity retains its positive value. '
                                 'Owing to its cost, the capacity is evaluated only when the '
                                 'property is selected in the results table.'),
                                ('h3',
                                 'Interpretación en el diagrama de fases con agua',
                                 'Interpretation on the phase diagram with water'),
                                ('p',
                                 'En el diagrama de fases de una mezcla con agua, la línea de '
                                 'rocío de agua es el lugar geométrico de los puntos donde el '
                                 'contenido de agua del gas iguala a su capacidad. Del lado de '
                                 'menor temperatura existe agua libre y el gas está saturado '
                                 '(contenido = capacidad); del lado de mayor temperatura el gas '
                                 'está subsaturado (contenido menor que capacidad).',
                                 'On the phase diagram of a mixture with water, the water dew line '
                                 'is the locus of points where the gas water content equals its '
                                 'capacity. On the lower-temperature side free water exists and '
                                 'the gas is saturated (content = capacity); on the '
                                 'higher-temperature side the gas is undersaturated (content lower '
                                 'than capacity).'),
                                ('p',
                                 'En consecuencia, las líneas de rocío de agua calculadas para '
                                 'distintos contenidos de agua de un mismo gas son líneas de '
                                 'capacidad constante en el plano presión-temperatura. Su conjunto '
                                 'es equivalente a la carta de contenido de agua de McKetta-Wehe, '
                                 'con la diferencia de que se obtiene con la ecuación de estado '
                                 'para la composición real del gas.',
                                 'Consequently, the water dew lines calculated for different water '
                                 'contents of the same gas are lines of constant capacity in the '
                                 'pressure-temperature plane. Taken together, they are equivalent '
                                 'to the McKetta-Wehe water content chart, with the difference '
                                 'that they are obtained from the equation of state for the actual '
                                 'gas composition.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'McKetta, J.J. y Wehe, A.H. (1958). Use this chart for water '
                                 'content of natural gases. <em>Petroleum Refiner</em>, 37(8), '
                                 '153.',
                                 'McKetta, J.J. and Wehe, A.H. (1958). Use this chart for water '
                                 'content of natural gases. <em>Petroleum Refiner</em>, 37(8), '
                                 '153.'),
                                ('p',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10.ª ed. GPSA.',
                                 'Gas Processors Suppliers Association (1987). <em>Engineering '
                                 'Data Book</em>, 10th ed. GPSA.'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.')]}]},
 {'titulo': ('Formación de hidratos', 'Hydrate formation'),
  'subsecciones': [{'titulo': ('Hidratos de gas y estructuras cristalinas',
                               'Gas hydrates and crystal structures'),
                    'bloques': [('p',
                                 'Los hidratos de gas son compuestos cristalinos de inclusión '
                                 '(clatratos) en los que las moléculas de agua forman, mediante '
                                 'puentes de hidrógeno, una red de cavidades que alojan moléculas '
                                 'de gas de pequeño tamaño. Se forman cuando hidrocarburos '
                                 'livianos, nitrógeno o dióxido de carbono están en contacto con '
                                 'agua a baja temperatura y presión elevada, y pueden existir por '
                                 'encima del punto de congelación del agua. En la producción y el '
                                 'transporte de gas obstruyen tuberías, válvulas, estranguladores '
                                 'y separadores, por lo que la predicción de sus condiciones de '
                                 'formación es la base del diseño de la deshidratación y de la '
                                 'inyección de inhibidores.',
                                 'Gas hydrates are crystalline inclusion compounds (clathrates) in '
                                 'which water molecules form, through hydrogen bonds, a lattice of '
                                 'cavities that host small gas molecules. They form when light '
                                 'hydrocarbons, nitrogen, or carbon dioxide are in contact with '
                                 'water at low temperature and elevated pressure, and they can '
                                 'exist above the freezing point of water. In gas production and '
                                 'transport they plug pipelines, valves, chokes, and separators, '
                                 'so the prediction of their formation conditions is the basis for '
                                 'the design of dehydration and inhibitor injection.'),
                                ('p',
                                 'ThermoPhase calcula la temperatura de formación de hidrato a una '
                                 'presión dada o la presión de formación a una temperatura dada, y '
                                 'la curva de formación completa para trazarla sobre la envolvente '
                                 'de fases. El modelo es el de van der Waals-Platteeuw en la forma '
                                 'de Munck y colaboradores, con los parámetros y el procedimiento '
                                 'que documenta PVTsim. Se consideran tres estructuras '
                                 'cristalinas:',
                                 'ThermoPhase calculates the hydrate formation temperature at a '
                                 'given pressure or the formation pressure at a given temperature, '
                                 'and the complete formation curve for plotting on the phase '
                                 'envelope. The model is that of van der Waals-Platteeuw in the '
                                 'form of Munck et al., with the parameters and procedure '
                                 'documented by PVTsim. Three crystal structures are considered:'),
                                ('ul',
                                 [('Estructura I (sI): 46 moléculas de agua por celda unitaria, '
                                   'con 2 cavidades pequeñas y 6 grandes; ν<sub>pequeña</sub> = '
                                   '2/46 y ν<sub>grande</sub> = 6/46. Formadores: N<sub>2</sub>, '
                                   'CO<sub>2</sub> y C<sub>1</sub> en ambas cavidades; '
                                   'C<sub>2</sub> solo en la grande.',
                                   'Structure I (sI): 46 water molecules per unit cell, with 2 '
                                   'small and 6 large cavities; ν<sub>small</sub> = 2/46 and '
                                   'ν<sub>large</sub> = 6/46. Formers: N<sub>2</sub>, '
                                   'CO<sub>2</sub>, and C<sub>1</sub> in both cavities; '
                                   'C<sub>2</sub> only in the large one.'),
                                  ('Estructura II (sII): 136 moléculas de agua por celda, con 16 '
                                   'cavidades pequeñas y 8 grandes; ν<sub>pequeña</sub> = 16/136 y '
                                   'ν<sub>grande</sub> = 8/136. Formadores: N<sub>2</sub>, '
                                   'CO<sub>2</sub> y C<sub>1</sub> en ambas cavidades; '
                                   'C<sub>2</sub>, C<sub>3</sub>, iC<sub>4</sub> y nC<sub>4</sub> '
                                   'solo en la grande.',
                                   'Structure II (sII): 136 water molecules per cell, with 16 '
                                   'small and 8 large cavities; ν<sub>small</sub> = 16/136 and '
                                   'ν<sub>large</sub> = 8/136. Formers: N<sub>2</sub>, '
                                   'CO<sub>2</sub>, and C<sub>1</sub> in both cavities; '
                                   'C<sub>2</sub>, C<sub>3</sub>, iC<sub>4</sub>, and '
                                   'nC<sub>4</sub> only in the large one.'),
                                  ('Estructura H (sH): 34 moléculas de agua por celda, con 3 '
                                   'cavidades pequeñas, 2 medianas y 1 grande. Siguiendo a Madsen, '
                                   'Pedersen y Michelsen (2000), las cavidades pequeñas y medianas '
                                   'se tratan como un único tipo, ν = 5/34, ocupado por '
                                   'N<sub>2</sub> y C<sub>1</sub>; la cavidad grande, ν = 1/34, la '
                                   'ocupa el formador pesado, que entre los componentes de '
                                   'ThermoPhase es el iC<sub>5</sub>.',
                                   'Structure H (sH): 34 water molecules per cell, with 3 small, 2 '
                                   'medium, and 1 large cavity. Following Madsen, Pedersen, and '
                                   'Michelsen (2000), the small and medium cavities are treated as '
                                   'a single type, ν = 5/34, occupied by N<sub>2</sub> and '
                                   'C<sub>1</sub>; the large cavity, ν = 1/34, is occupied by the '
                                   'heavy former, which among the ThermoPhase components is '
                                   'iC<sub>5</sub>.')]),
                                ('p',
                                 'Los demás componentes (nC<sub>5</sub> y más pesados) no ocupan '
                                 'cavidades, pero intervienen en el cálculo a través de su efecto '
                                 'sobre las fugacidades de los formadores. Para cada condición se '
                                 'evalúan las tres estructuras y se toma como estable la de menor '
                                 'potencial químico del agua en el hidrato.',
                                 'The remaining components (nC<sub>5</sub> and heavier) do not '
                                 'occupy cavities, but they take part in the calculation through '
                                 'their effect on the former fugacities. For each condition the '
                                 'three structures are evaluated, and the one with the lowest '
                                 'chemical potential of water in the hydrate is taken as stable.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Sloan, E.D. y Koh, C.A. (2008). <em>Clathrate Hydrates of '
                                 'Natural Gases</em>, 3.ª ed. CRC Press.',
                                 'Sloan, E.D. and Koh, C.A. (2008). <em>Clathrate Hydrates of '
                                 'Natural Gases</em>, 3rd ed. CRC Press.'),
                                ('p',
                                 'Madsen, J., Pedersen, K.S. y Michelsen, M.L. (2000). Modeling of '
                                 'structure H hydrates using a Langmuir adsorption model. '
                                 '<em>Industrial &amp; Engineering Chemistry Research</em>, 39(4), '
                                 '1111–1114.',
                                 'Madsen, J., Pedersen, K.S. and Michelsen, M.L. (2000). Modeling '
                                 'of structure H hydrates using a Langmuir adsorption model. '
                                 '<em>Industrial &amp; Engineering Chemistry Research</em>, 39(4), '
                                 '1111–1114.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Modelo de van der Waals y Platteeuw',
                               'Van der Waals and Platteeuw model'),
                    'bloques': [('p',
                                 'El modelo de van der Waals y Platteeuw trata el hidrato como una '
                                 'solución sólida en la que las moléculas de gas se adsorben en '
                                 'las cavidades de una red de agua. La formación se describe como '
                                 'el paso del agua desde su estado puro α (agua líquida o hielo) '
                                 'al hidrato lleno H, a través de un estado hipotético β de red '
                                 'vacía. La diferencia de potencial químico del agua se descompone '
                                 'en dos contribuciones:',
                                 'The van der Waals and Platteeuw model treats the hydrate as a '
                                 'solid solution in which gas molecules are adsorbed in the '
                                 'cavities of a water lattice. Formation is described as the '
                                 'transition of water from its pure state α (liquid water or ice) '
                                 'to the filled hydrate H, through a hypothetical empty-lattice '
                                 'state β. The chemical potential difference of water is split '
                                 'into two contributions:'),
                                ('eq',
                                 '\\mu^H - \\mu^\\alpha = \\left(\\mu^H - \\mu^\\beta\\right) + '
                                 '\\left(\\mu^\\beta - \\mu^\\alpha\\right)'),
                                ('p',
                                 'donde μ<sup>H</sup>, μ<sup>β</sup> y μ<sup>α</sup> son los '
                                 'potenciales químicos del agua en el hidrato, en la red vacía y '
                                 'en el agua pura, respectivamente. El primer término representa '
                                 'la estabilización de la red por la adsorción del gas y es '
                                 'siempre negativo; el segundo es la diferencia entre la red vacía '
                                 'y el agua pura, y se obtiene de propiedades termodinámicas de '
                                 'referencia.',
                                 'where μ<sup>H</sup>, μ<sup>β</sup>, and μ<sup>α</sup> are the '
                                 'chemical potentials of water in the hydrate, in the empty '
                                 'lattice, and in pure water, respectively. The first term '
                                 'represents the lattice stabilization by gas adsorption and is '
                                 'always negative; the second is the difference between the empty '
                                 'lattice and pure water, and is obtained from reference '
                                 'thermodynamic properties.'),
                                ('p',
                                 'Cuando el agua del sistema no es pura (fase acuosa con gases '
                                 'disueltos o agua subsaturada), su potencial químico difiere del '
                                 'agua pura en RT·ln a<sub>w</sub>. El criterio de formación que '
                                 'evalúa ThermoPhase para cada estructura es:',
                                 'When the water in the system is not pure (aqueous phase with '
                                 'dissolved gases, or undersaturated water), its chemical '
                                 'potential differs from that of pure water by RT·ln '
                                 'a<sub>w</sub>. The formation criterion evaluated by ThermoPhase '
                                 'for each structure is:'),
                                ('eq',
                                 '\\frac{\\Delta\\mu_w}{RT} = \\frac{\\mu^H - \\mu^\\beta}{RT} + '
                                 '\\frac{\\mu^\\beta - \\mu^\\alpha}{RT} - \\ln a_w'),
                                ('p',
                                 'donde Δμ<sub>w</sub> es la diferencia entre el potencial químico '
                                 'del agua en el hidrato y en el sistema, a<sub>w</sub> es la '
                                 'actividad del agua referida al agua pura (líquida o hielo), R es '
                                 'la constante de los gases y T la temperatura absoluta. La curva '
                                 'de formación de hidrato es el lugar de los puntos (T, P) en que '
                                 'Δμ<sub>w</sub> = 0 para la estructura más estable; donde '
                                 'Δμ<sub>w</sub> es negativo el hidrato es estable, y donde es '
                                 'positivo el agua permanece como líquido o hielo.',
                                 'where Δμ<sub>w</sub> is the difference between the chemical '
                                 'potential of water in the hydrate and in the system, '
                                 'a<sub>w</sub> is the water activity referred to pure water '
                                 '(liquid or ice), R is the gas constant, and T is the absolute '
                                 'temperature. The hydrate formation curve is the locus of points '
                                 '(T, P) at which Δμ<sub>w</sub> = 0 for the most stable '
                                 'structure; where Δμ<sub>w</sub> is negative the hydrate is '
                                 'stable, and where it is positive water remains as liquid or '
                                 'ice.'),
                                ('eq',
                                 '\\frac{\\Delta\\mu_w}{RT} = \\min_{s \\in \\{I,\\,II,\\,H\\}} '
                                 '\\left( \\frac{\\Delta\\mu_w}{RT} \\right)_s'),
                                ('p',
                                 'donde s designa la estructura cristalina. La estructura que da '
                                 'el mínimo es la estructura estable en el punto calculado.',
                                 'where s denotes the crystal structure. The structure giving the '
                                 'minimum is the stable structure at the calculated point.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'van der Waals, J.H. y Platteeuw, J.C. (1959). Clathrate '
                                 'solutions. <em>Advances in Chemical Physics</em>, 2, 1–57.',
                                 'van der Waals, J.H. and Platteeuw, J.C. (1959). Clathrate '
                                 'solutions. <em>Advances in Chemical Physics</em>, 2, 1–57.'),
                                ('p',
                                 'Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.',
                                 'Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Término de adsorción de Langmuir', 'Langmuir adsorption term'),
                    'bloques': [('p',
                                 'La estabilización de la red por el gas atrapado se calcula con '
                                 'la teoría de adsorción de Langmuir, suponiendo que cada cavidad '
                                 'aloja como máximo una molécula y que no hay interacción entre '
                                 'moléculas de cavidades distintas:',
                                 'The lattice stabilization by the trapped gas is calculated with '
                                 'Langmuir adsorption theory, assuming that each cavity hosts at '
                                 'most one molecule and that there is no interaction between '
                                 'molecules in different cavities:'),
                                ('eq',
                                 '\\frac{\\mu^H - \\mu^\\beta}{RT} = \\sum_{i} \\nu_i \\, '
                                 '\\ln\\left(1 - \\sum_{k} Y_{ki}\\right)'),
                                ('p',
                                 'donde ν<sub>i</sub> es el número de cavidades de tipo i por '
                                 'molécula de agua e Y<sub>ki</sub> es la probabilidad de que una '
                                 'cavidad de tipo i esté ocupada por una molécula del componente '
                                 'k. La ocupación sigue la isoterma de Langmuir:',
                                 'where ν<sub>i</sub> is the number of type-i cavities per water '
                                 'molecule and Y<sub>ki</sub> is the probability that a type-i '
                                 'cavity is occupied by a molecule of component k. The occupancy '
                                 'follows the Langmuir isotherm:'),
                                ('eq', 'Y_{ki} = \\frac{C_{ki}\\,f_k}{1 + \\sum_{j} C_{ji}\\,f_j}'),
                                ('p',
                                 'donde f<sub>k</sub> es la fugacidad del componente k en las '
                                 'fases de hidrocarburo, en atm, y C<sub>ki</sub> es la constante '
                                 'de adsorción de Langmuir del componente k en la cavidad i, en '
                                 'atm<sup>−1</sup>. Al sustituir la isoterma, el término de cada '
                                 'cavidad se reduce a ν<sub>i</sub>·ln[1/(1 + Σ<sub>j</sub> '
                                 'C<sub>ji</sub> f<sub>j</sub>)], que es la forma que evalúa '
                                 'ThermoPhase.',
                                 'where f<sub>k</sub> is the fugacity of component k in the '
                                 'hydrocarbon phases, in atm, and C<sub>ki</sub> is the Langmuir '
                                 'adsorption constant of component k in cavity i, in '
                                 'atm<sup>−1</sup>. Substituting the isotherm, the term for each '
                                 'cavity reduces to ν<sub>i</sub>·ln[1/(1 + Σ<sub>j</sub> '
                                 'C<sub>ji</sub> f<sub>j</sub>)], which is the form evaluated by '
                                 'ThermoPhase.'),
                                ('p',
                                 'La dependencia de la constante de adsorción con la temperatura '
                                 'sigue la expresión de dos parámetros de Munck y colaboradores:',
                                 'The temperature dependence of the adsorption constant follows '
                                 'the two-parameter expression of Munck et al.:'),
                                ('eq',
                                 'C_{ki} = '
                                 '\\frac{A_{ki}}{T}\\,\\exp\\left(\\frac{B_{ki}}{T}\\right)'),
                                ('p',
                                 'donde T es la temperatura, en K, A<sub>ki</sub> es un parámetro '
                                 'en K/atm y B<sub>ki</sub> un parámetro en K, específicos de cada '
                                 'componente, tipo de cavidad y estructura.',
                                 'where T is the temperature, in K, A<sub>ki</sub> is a parameter '
                                 'in K/atm, and B<sub>ki</sub> is a parameter in K, specific to '
                                 'each component, cavity type, and structure.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Los parámetros A y B son los de la base de datos de PVTsim, que '
                                 'los ajusta a datos experimentales de formación de hidratos por '
                                 'separado para cada familia de ecuaciones de estado, ya que las '
                                 'fugacidades de cada ecuación difieren ligeramente. ThermoPhase '
                                 'dispone de un juego para Peng-Robinson y otro para '
                                 'Soave-Redlich-Kwong, que cubren las estructuras I, II y H. A '
                                 'modo de ejemplo, para el metano en la cavidad pequeña de la '
                                 'estructura I los parámetros (A, B) son (839.70 K/atm, −881.1 K) '
                                 'con Peng-Robinson y (0.04855 K/atm, 1594 K) con '
                                 'Soave-Redlich-Kwong, y para el iC<sub>5</sub> en la cavidad '
                                 'grande de la estructura H son (4304 K/atm, 1639 K) y (16 612 '
                                 'K/atm, 1699 K), respectivamente.',
                                 'Parameters A and B are those of the PVTsim database, which fits '
                                 'them to experimental hydrate formation data separately for each '
                                 'equation of state family, since the fugacities of each equation '
                                 'differ slightly. ThermoPhase holds one set for Peng-Robinson and '
                                 'another for Soave-Redlich-Kwong, covering structures I, II, and '
                                 'H. As an example, for methane in the small cavity of structure I '
                                 'the parameters (A, B) are (839.70 K/atm, −881.1 K) with '
                                 'Peng-Robinson and (0.04855 K/atm, 1594 K) with '
                                 'Soave-Redlich-Kwong, and for iC<sub>5</sub> in the large cavity '
                                 'of structure H they are (4304 K/atm, 1639 K) and (16,612 K/atm, '
                                 '1699 K), respectively.'),
                                ('p',
                                 'Las fugacidades internas en psia se convierten a atm (1 atm = '
                                 '14.696 psia) y la temperatura en °R se convierte a K '
                                 '(T<sub>K</sub> = T<sub>R</sub>/1.8) antes de evaluar las '
                                 'constantes de Langmuir.',
                                 'The internal fugacities in psia are converted to atm (1 atm = '
                                 '14.696 psia), and the temperature in °R is converted to K '
                                 '(T<sub>K</sub> = T<sub>R</sub>/1.8) before the Langmuir '
                                 'constants are evaluated.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.',
                                 'Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.'),
                                ('p',
                                 'Madsen, J., Pedersen, K.S. y Michelsen, M.L. (2000). Modeling of '
                                 'structure H hydrates using a Langmuir adsorption model. '
                                 '<em>Industrial &amp; Engineering Chemistry Research</em>, 39(4), '
                                 '1111–1114.',
                                 'Madsen, J., Pedersen, K.S. and Michelsen, M.L. (2000). Modeling '
                                 'of structure H hydrates using a Langmuir adsorption model. '
                                 '<em>Industrial &amp; Engineering Chemistry Research</em>, 39(4), '
                                 '1111–1114.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Término de referencia del agua', 'Water reference term'),
                    'bloques': [('p',
                                 'La diferencia de potencial químico entre la red vacía y el agua '
                                 'pura se obtiene integrando la relación de Gibbs-Helmholtz desde '
                                 'el estado de referencia T<sub>0</sub> = 273.15 K y presión nula '
                                 'hasta las condiciones del sistema:',
                                 'The chemical potential difference between the empty lattice and '
                                 'pure water is obtained by integrating the Gibbs-Helmholtz '
                                 'relation from the reference state T<sub>0</sub> = 273.15 K and '
                                 'zero pressure to the system conditions:'),
                                ('eq',
                                 '\\frac{\\mu^\\beta - \\mu^\\alpha}{RT} = '
                                 '\\frac{\\Delta\\mu^0}{R\\,T_0} - \\int_{T_0}^{T} \\frac{\\Delta '
                                 'h}{R\\,T^2}\\,dT + \\frac{\\Delta V \\, P}{R\\,\\bar{T}}'),
                                ('eq',
                                 '\\Delta h = \\Delta h^0 + \\Delta C_p \\left(T - T_0\\right)'),
                                ('p',
                                 'donde Δμ<sup>0</sup> es la diferencia de potencial químico red '
                                 'vacía - agua pura a T<sub>0</sub>, en J/mol, Δh<sup>0</sup> la '
                                 'diferencia de entalpía a T<sub>0</sub>, en J/mol, ΔC<sub>p</sub> '
                                 'la diferencia de capacidad calorífica, en J/(mol·K), ΔV la '
                                 'diferencia de volumen molar, en cm³/mol, P la presión, en Pa, y '
                                 'T̄ = (T + T<sub>0</sub>)/2 la temperatura media con que se '
                                 'aproxima el término de presión. Integrando analíticamente:',
                                 'where Δμ<sup>0</sup> is the empty lattice - pure water chemical '
                                 'potential difference at T<sub>0</sub>, in J/mol, Δh<sup>0</sup> '
                                 'the enthalpy difference at T<sub>0</sub>, in J/mol, '
                                 'ΔC<sub>p</sub> the heat capacity difference, in J/(mol·K), ΔV '
                                 'the molar volume difference, in cm³/mol, P the pressure, in Pa, '
                                 'and T̄ = (T + T<sub>0</sub>)/2 the mean temperature used to '
                                 'approximate the pressure term. Integrating analytically:'),
                                ('eq',
                                 '\\frac{\\mu^\\beta - \\mu^\\alpha}{RT} = '
                                 '\\frac{\\Delta\\mu^0}{R\\,T_0} + \\frac{\\Delta '
                                 'h^0}{R}\\left(\\frac{1}{T} - \\frac{1}{T_0}\\right) - '
                                 '\\frac{\\Delta C_p}{R}\\,\\Theta + \\frac{\\Delta V \\, '
                                 'P}{R\\,\\bar{T}}'),
                                ('eq',
                                 '\\Theta = \\ln\\frac{T}{T_0} + T_0\\left(\\frac{1}{T} - '
                                 '\\frac{1}{T_0}\\right)'),
                                ('p',
                                 'donde Θ es el término adimensional que resulta de integrar la '
                                 'contribución de ΔC<sub>p</sub>, con T y T<sub>0</sub> en K.',
                                 'where Θ is the dimensionless term resulting from integrating the '
                                 'ΔC<sub>p</sub> contribution, with T and T<sub>0</sub> in K.'),
                                ('p',
                                 'El estado de referencia α es agua líquida para T ≥ 273.15 K '
                                 '(491.67 °R) y hielo por debajo de esa temperatura. Los valores '
                                 'de Δh<sup>0</sup> y ΔV cambian según la referencia, y con hielo '
                                 'no se aplica la corrección de ΔC<sub>p</sub>, que las constantes '
                                 'publicadas definen solo para el agua líquida.',
                                 'The reference state α is liquid water for T ≥ 273.15 K (491.67 '
                                 '°R) and ice below that temperature. The values of Δh<sup>0</sup> '
                                 'and ΔV change with the reference, and with ice the '
                                 'ΔC<sub>p</sub> correction is not applied, since the published '
                                 'constants define it only for liquid water.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Se emplean las constantes de Erickson (1983) tal como las '
                                 'publica PVTsim, iguales para todas las ecuaciones de estado, con '
                                 'R = 0.08206 × 101.325 = 8.3147 J/(mol·K):',
                                 'The Erickson (1983) constants are used as published by PVTsim, '
                                 'identical for all equations of state, with R = 0.08206 × 101.325 '
                                 '= 8.3147 J/(mol·K):'),
                                ('ul',
                                 [('Estructura I: Δμ<sup>0</sup> = 1264 J/mol; Δh<sup>0</sup> = '
                                   '−4858 J/mol (líquido) y 1151 J/mol (hielo); ΔV = 4.6 cm³/mol '
                                   '(líquido) y 3.0 cm³/mol (hielo); ΔC<sub>p</sub> = −39.16 '
                                   'J/(mol·K).',
                                   'Structure I: Δμ<sup>0</sup> = 1264 J/mol; Δh<sup>0</sup> = '
                                   '−4858 J/mol (liquid) and 1151 J/mol (ice); ΔV = 4.6 cm³/mol '
                                   '(liquid) and 3.0 cm³/mol (ice); ΔC<sub>p</sub> = −39.16 '
                                   'J/(mol·K).'),
                                  ('Estructura II: Δμ<sup>0</sup> = 883 J/mol; Δh<sup>0</sup> = '
                                   '−5201 J/mol (líquido) y 808 J/mol (hielo); ΔV = 5.0 cm³/mol '
                                   '(líquido) y 3.4 cm³/mol (hielo); ΔC<sub>p</sub> = −39.16 '
                                   'J/(mol·K).',
                                   'Structure II: Δμ<sup>0</sup> = 883 J/mol; Δh<sup>0</sup> = '
                                   '−5201 J/mol (liquid) and 808 J/mol (ice); ΔV = 5.0 cm³/mol '
                                   '(liquid) and 3.4 cm³/mol (ice); ΔC<sub>p</sub> = −39.16 '
                                   'J/(mol·K).'),
                                  ('Estructura H: Δμ<sup>0</sup> = 1187.33 J/mol; Δh<sup>0</sup> = '
                                   '−5162.43 J/mol (líquido) y 846.57 J/mol (hielo); ΔV = 5.45 '
                                   'cm³/mol (líquido) y 3.85 cm³/mol (hielo); ΔC<sub>p</sub> = '
                                   '−39.16 J/(mol·K).',
                                   'Structure H: Δμ<sup>0</sup> = 1187.33 J/mol; Δh<sup>0</sup> = '
                                   '−5162.43 J/mol (liquid) and 846.57 J/mol (ice); ΔV = 5.45 '
                                   'cm³/mol (liquid) and 3.85 cm³/mol (ice); ΔC<sub>p</sub> = '
                                   '−39.16 J/(mol·K).')]),
                                ('p',
                                 'La presión interna en psia se convierte a Pa (P<sub>Pa</sub> = '
                                 'P<sub>psia</sub>/14.696 × 101 325) y ΔV a m³/mol antes de '
                                 'evaluar el término de presión.',
                                 'The internal pressure in psia is converted to Pa (P<sub>Pa</sub> '
                                 '= P<sub>psia</sub>/14.696 × 101,325) and ΔV to m³/mol before the '
                                 'pressure term is evaluated.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Erickson, D.D. (1983). <em>Development of a Natural Gas Hydrate '
                                 'Prediction Computer Program</em>. Tesis de maestría, Colorado '
                                 'School of Mines.',
                                 'Erickson, D.D. (1983). <em>Development of a Natural Gas Hydrate '
                                 'Prediction Computer Program</em>. M.Sc. thesis, Colorado School '
                                 'of Mines.'),
                                ('p',
                                 'Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.',
                                 'Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.')]},
                   {'titulo': ('Fugacidades y actividad del agua', 'Fugacities and water activity'),
                    'bloques': [('p',
                                 'El término de Langmuir requiere la fugacidad de cada formador y '
                                 'el criterio de formación requiere la actividad del agua. '
                                 'ThermoPhase obtiene ambas magnitudes de un flash trifásico sobre '
                                 'la composición total con agua, resuelto con la ecuación de '
                                 'estado activa y la regla de mezcla de Huron-Vidal, siguiendo el '
                                 'procedimiento de flash de hidratos P/T de PVTsim.',
                                 'The Langmuir term requires the fugacity of each former, and the '
                                 'formation criterion requires the water activity. ThermoPhase '
                                 'obtains both quantities from a three-phase flash on the total '
                                 'composition with water, solved with the active equation of state '
                                 'and the Huron-Vidal mixing rule, following the PVTsim P/T '
                                 'hydrate flash procedure.'),
                                ('eq',
                                 'f_k = \\frac{\\sum_{p} \\beta_p \\, x_{k,p} \\, \\phi_{k,p} \\, '
                                 'P}{\\sum_{p} \\beta_p}, \\quad p \\in \\{V,\\,L\\}'),
                                ('p',
                                 'donde f<sub>k</sub> es la fugacidad de mezcla del formador k, '
                                 'β<sub>p</sub> es la fracción molar de la fase de hidrocarburo p '
                                 '(vapor V o líquido L), x<sub>k,p</sub> es la fracción molar de k '
                                 'en esa fase, φ<sub>k,p</sub> su coeficiente de fugacidad y P la '
                                 'presión. En equilibrio las fugacidades son iguales en todas las '
                                 'fases, de modo que el promedio molar sobre las fases de '
                                 'hidrocarburo presentes es consistente cuando coexisten gas y '
                                 'líquido a lo largo de la curva.',
                                 'where f<sub>k</sub> is the mixture fugacity of former k, '
                                 'β<sub>p</sub> is the mole fraction of hydrocarbon phase p (vapor '
                                 'V or liquid L), x<sub>k,p</sub> is the mole fraction of k in '
                                 'that phase, φ<sub>k,p</sub> its fugacity coefficient, and P the '
                                 'pressure. At equilibrium the fugacities are equal in all phases, '
                                 'so the molar average over the hydrocarbon phases present is '
                                 'consistent when gas and liquid coexist along the curve.'),
                                ('p',
                                 'La fugacidad del agua en el sistema, f<sub>w</sub>, se toma de '
                                 'la fase acuosa cuando existe; en ausencia de fase acuosa (agua '
                                 'subsaturada, toda disuelta en las fases de hidrocarburo) se toma '
                                 'el promedio molar de su fugacidad sobre las fases de '
                                 'hidrocarburo, con la misma expresión anterior. La actividad del '
                                 'agua se define respecto del agua pura en el estado de referencia '
                                 'α:',
                                 'The water fugacity in the system, f<sub>w</sub>, is taken from '
                                 'the aqueous phase when it exists; in the absence of an aqueous '
                                 'phase (undersaturated water, all dissolved in the hydrocarbon '
                                 'phases) the molar average of its fugacity over the hydrocarbon '
                                 'phases is taken, with the same expression as above. The water '
                                 'activity is defined with respect to pure water in the reference '
                                 'state α:'),
                                ('eq', 'a_w = \\min\\left(\\frac{f_w}{f_{ref}},\\ 1\\right)'),
                                ('p',
                                 'donde f<sub>ref</sub> es la fugacidad del agua pura en el estado '
                                 'de referencia. Para T ≥ 273.15 K es la fugacidad del agua '
                                 'líquida pura, φ<sub>w</sub><sup>0</sup>·P, con '
                                 'φ<sub>w</sub><sup>0</sup> calculado por la ecuación de estado '
                                 'con la raíz de líquido. Por debajo de 273.15 K la referencia es '
                                 'el hielo:',
                                 'where f<sub>ref</sub> is the fugacity of pure water in the '
                                 'reference state. For T ≥ 273.15 K it is the fugacity of pure '
                                 'liquid water, φ<sub>w</sub><sup>0</sup>·P, with '
                                 'φ<sub>w</sub><sup>0</sup> calculated by the equation of state '
                                 'using the liquid root. Below 273.15 K the reference is ice:'),
                                ('eq',
                                 'f_{S}^{0} = f_{L}^{0} \\, \\exp\\left( -\\frac{\\mu^{L} - '
                                 '\\mu^{S}}{RT} \\right)'),
                                ('p',
                                 'donde f<sub>S</sub><sup>0</sup> es la fugacidad del hielo, '
                                 'f<sub>L</sub><sup>0</sup> la del agua líquida pura (subenfriada) '
                                 'por la ecuación de estado y (μ<sup>L</sup> − μ<sup>S</sup>)/RT, '
                                 'diferencia de potencial químico entre el agua líquida y el '
                                 'hielo, se obtiene como la diferencia entre los términos de '
                                 'referencia (μ<sup>β</sup> − μ<sup>α</sup>)/RT evaluados con '
                                 'hielo y con líquido, con las constantes de la estructura I.',
                                 'where f<sub>S</sub><sup>0</sup> is the fugacity of ice, '
                                 'f<sub>L</sub><sup>0</sup> that of pure (subcooled) liquid water '
                                 'from the equation of state, and (μ<sup>L</sup> − '
                                 'μ<sup>S</sup>)/RT, the chemical potential difference between '
                                 'liquid water and ice, is obtained as the difference between the '
                                 'reference terms (μ<sup>β</sup> − μ<sup>α</sup>)/RT evaluated '
                                 'with ice and with liquid, using the structure I constants.'),
                                ('p',
                                 'Con agua libre en exceso, a<sub>w</sub> es prácticamente 1 (solo '
                                 'la reducen los gases disueltos en la fase acuosa) y la curva no '
                                 'depende de la cantidad de agua. Si el agua no alcanza a formar '
                                 'fase acuosa, a<sub>w</sub> es menor que 1, el término −ln '
                                 'a<sub>w</sub> es positivo y la formación de hidrato exige mayor '
                                 'presión o menor temperatura: con poca agua la curva de hidratos '
                                 'se desplaza y depende del contenido de agua de la mezcla.',
                                 'With excess free water, a<sub>w</sub> is practically 1 (reduced '
                                 'only by the gases dissolved in the aqueous phase) and the curve '
                                 'does not depend on the amount of water. If the water does not '
                                 'form an aqueous phase, a<sub>w</sub> is less than 1, the term '
                                 '−ln a<sub>w</sub> is positive, and hydrate formation requires '
                                 'higher pressure or lower temperature: with little water the '
                                 'hydrate curve shifts and depends on the water content of the '
                                 'mixture.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'Con el agua activa en la composición, el cálculo usa la '
                                 'composición total tal como fue especificada, de modo que refleja '
                                 'el efecto de un gas subsaturado. Sin agua activa, la mezcla de '
                                 'hidrocarburos se satura internamente con agua a la temperatura y '
                                 'presión del punto: se determina el agua disuelta en las fases de '
                                 'hidrocarburo en equilibrio con una fase acuosa y se añade un '
                                 'exceso del 5 % como agua libre, el mínimo que asegura la '
                                 'presencia de la fase acuosa. Esta es la condición de gas '
                                 'saturado con agua que suponen PVTsim y HYSYS, en la que la curva '
                                 'ya no depende de la cantidad de agua. La saturación se repite en '
                                 'la solución y el punto se refina con la nueva composición.',
                                 'With water active in the composition, the calculation uses the '
                                 'total composition as specified, so it reflects the effect of an '
                                 'undersaturated gas. Without active water, the hydrocarbon '
                                 'mixture is internally saturated with water at the temperature '
                                 'and pressure of the point: the water dissolved in the '
                                 'hydrocarbon phases in equilibrium with an aqueous phase is '
                                 'determined, and a 5 % excess is added as free water, the minimum '
                                 'that ensures the presence of the aqueous phase. This is the '
                                 'water-saturated gas condition assumed by PVTsim and HYSYS, in '
                                 'which the curve no longer depends on the amount of water. '
                                 'Saturation is repeated at the solution, and the point is refined '
                                 'with the new composition.'),
                                ('p',
                                 'El modelo es compatible con las cuatro ecuaciones de estado del '
                                 'programa. Con las variantes de HYSYS se utilizan los parámetros '
                                 'de Langmuir de la contraparte de PVTsim de la misma familia '
                                 '(Peng-Robinson o Soave-Redlich-Kwong), con las fugacidades '
                                 'calculadas por la ecuación de estado de HYSYS seleccionada.',
                                 'The model is compatible with the four equations of state of the '
                                 'program. With the HYSYS variants, the Langmuir parameters of the '
                                 'PVTsim counterpart of the same family (Peng-Robinson or '
                                 'Soave-Redlich-Kwong) are used, with the fugacities calculated by '
                                 'the selected HYSYS equation of state.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. (1991). Calculation of hydrate fugacities. '
                                 '<em>Chemical Engineering Science</em>, 46(4), 1192–1193.',
                                 'Michelsen, M.L. (1991). Calculation of hydrate fugacities. '
                                 '<em>Chemical Engineering Science</em>, 46(4), 1192–1193.'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.')]},
                   {'titulo': ('Cálculo de las condiciones de formación y curva de hidratos',
                               'Calculation of formation conditions and hydrate curve'),
                    'bloques': [('p',
                                 'El punto de formación se obtiene como raíz del criterio '
                                 'Δμ<sub>w</sub>/RT = 0. Para la temperatura de formación se fija '
                                 'la presión y se resuelve la temperatura; para la presión de '
                                 'formación se fija la temperatura y se resuelve la presión. Por '
                                 'debajo de la temperatura de formación (o por encima de la '
                                 'presión de formación) el hidrato es estable.',
                                 'The formation point is obtained as the root of the criterion '
                                 'Δμ<sub>w</sub>/RT = 0. For the formation temperature the '
                                 'pressure is fixed and the temperature is solved; for the '
                                 'formation pressure the temperature is fixed and the pressure is '
                                 'solved. Below the formation temperature (or above the formation '
                                 'pressure) the hydrate is stable.'),
                                ('h3',
                                 'Implementación en ThermoPhase',
                                 'Implementation in ThermoPhase'),
                                ('p',
                                 'La resolución se realiza en dos etapas. En la primera se obtiene '
                                 'una estimación inicial con un modelo simplificado sin fase '
                                 'acuosa: fugacidades de un flash bifásico de hidrocarburos, '
                                 'a<sub>w</sub> = 1 y estructuras I y II. El criterio se evalúa '
                                 'sobre una rejilla de 48 intervalos (lineal en temperatura entre '
                                 '300 y 560 °R, o logarítmica en presión entre 10<sup>−3</sup> y '
                                 '12 000 psia), se detectan los cambios de signo y cada raíz se '
                                 'refina por bisección. La frontera de formación es la raíz de '
                                 'mayor temperatura o de menor presión, lo que resuelve también '
                                 'las curvas de forma cerrada con dos ramas propias de mezclas sin '
                                 'metano.',
                                 'The solution is carried out in two stages. In the first, an '
                                 'initial estimate is obtained with a simplified model without an '
                                 'aqueous phase: fugacities from a two-phase hydrocarbon flash, '
                                 'a<sub>w</sub> = 1, and structures I and II. The criterion is '
                                 'evaluated on a grid of 48 intervals (linear in temperature '
                                 'between 300 and 560 °R, or logarithmic in pressure between '
                                 '10<sup>−3</sup> and 12,000 psia), sign changes are detected, and '
                                 'each root is refined by bisection. The formation boundary is the '
                                 'root with the highest temperature or the lowest pressure, which '
                                 'also handles the closed-shape curves with two branches typical '
                                 'of mixtures without methane.'),
                                ('p',
                                 'En la segunda etapa se aplica el modelo completo con agua '
                                 'descrito en las secciones anteriores. Desde la estimación '
                                 'inicial se exploran valores alternadamente hacia abajo y hacia '
                                 'arriba, con pasos de 1 °R en temperatura (entre 250 y 560 °R) o '
                                 'de 0.02 en ln P (entre 10<sup>−4</sup> y 15 000 psia), hasta '
                                 'encontrar un cambio de signo del criterio; el intervalo se '
                                 'refina con el método de Brent (interpolación cuadrática inversa '
                                 'con bisección de respaldo), con tolerancia de 10<sup>−7</sup> °R '
                                 'en temperatura y de 10<sup>−12</sup> en ln P. Se retiene la raíz '
                                 'más próxima a la estimación.',
                                 'In the second stage, the complete model with water described in '
                                 'the previous sections is applied. Starting from the initial '
                                 'estimate, values are explored alternately downward and upward, '
                                 'with steps of 1 °R in temperature (between 250 and 560 °R) or '
                                 '0.02 in ln P (between 10<sup>−4</sup> and 15,000 psia), until a '
                                 'sign change of the criterion is found; the interval is refined '
                                 "with Brent's method (inverse quadratic interpolation with "
                                 'bisection fallback), with a tolerance of 10<sup>−7</sup> °R in '
                                 'temperature and 10<sup>−12</sup> in ln P. The root closest to '
                                 'the estimate is retained.'),
                                ('p',
                                 'En la solución se identifica la estructura estable y el estado '
                                 'del agua de referencia (líquido o hielo). La pestaña Formación '
                                 'de hidratos presenta la temperatura de formación en la escala '
                                 'del sistema de unidades activo y en escala absoluta, o la '
                                 'presión de formación junto con su temperatura, y en ese punto '
                                 'muestra el flash con la composición de la mezcla, del vapor, del '
                                 'líquido de hidrocarburos y de la fase acuosa, y las propiedades '
                                 'seleccionadas de cada fase. Con agua activa, las fases y '
                                 'propiedades provienen del flash trifásico de Huron-Vidal, con '
                                 'densidad de líquido por COSTALD; el poder calorífico y el GPM se '
                                 'evalúan sobre la composición de hidrocarburos libre de agua.',
                                 'At the solution, the stable structure and the state of the '
                                 'reference water (liquid or ice) are identified. The Hydrate '
                                 'Formation tab presents the formation temperature in the scale of '
                                 'the active unit system and in absolute scale, or the formation '
                                 'pressure together with its temperature, and at that point it '
                                 'shows the flash with the composition of the mixture, the vapor, '
                                 'the hydrocarbon liquid, and the aqueous phase, as well as the '
                                 'selected properties of each phase. With active water, the phases '
                                 'and properties come from the Huron-Vidal three-phase flash, with '
                                 'COSTALD liquid density; the heating value and GPM are evaluated '
                                 'on the water-free hydrocarbon composition.'),
                                ('h3', 'Curva de formación de hidratos', 'Hydrate formation curve'),
                                ('p',
                                 'La curva de formación se traza sobre la envolvente de fases. Se '
                                 'calcula en 60 presiones distribuidas geométricamente entre 5 '
                                 'psia y 1.05 veces la presión cricondenbárica de la envolvente '
                                 '(6000 psia si aún no hay envolvente), resolviendo en cada '
                                 'presión la temperatura de formación con el modelo completo y '
                                 'usando la solución anterior como estimación inicial. Se '
                                 'descartan los puntos por debajo de la temperatura mínima de la '
                                 'envolvente. Sin agua activa, la mezcla se satura con agua en '
                                 'cada punto, con una segunda saturación y resolución en la '
                                 'temperatura hallada.',
                                 'The formation curve is plotted on the phase envelope. It is '
                                 'calculated at 60 pressures geometrically distributed between 5 '
                                 'psia and 1.05 times the cricondenbar pressure of the envelope '
                                 '(6000 psia if no envelope is available yet), solving at each '
                                 'pressure the formation temperature with the complete model and '
                                 'using the previous solution as the initial estimate. Points '
                                 'below the minimum temperature of the envelope are discarded. '
                                 'Without active water, the mixture is saturated with water at '
                                 'each point, with a second saturation and solution at the '
                                 'temperature found.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Munck, J., Skjold-Jørgensen, S. y Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.',
                                 'Munck, J., Skjold-Jørgensen, S. and Rasmussen, P. (1988). '
                                 'Computations of the formation of gas hydrates. <em>Chemical '
                                 'Engineering Science</em>, 43(10), 2661–2672.'),
                                ('p',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.',
                                 'Calsep. <em>PVTsim Method Documentation</em>. Calsep A/S.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.'),
                                ('p',
                                 'Sloan, E.D. y Koh, C.A. (2008). <em>Clathrate Hydrates of '
                                 'Natural Gases</em>, 3.ª ed. CRC Press.',
                                 'Sloan, E.D. and Koh, C.A. (2008). <em>Clathrate Hydrates of '
                                 'Natural Gases</em>, 3rd ed. CRC Press.')]}]},
 {'titulo': ('Análisis de sensibilidad', 'Sensitivity analysis'),
  'subsecciones': [{'titulo': ('Descripción del análisis', 'Description of the analysis'),
                    'bloques': [('p',
                                 'La pestaña Análisis de sensibilidad calcula la variación de una '
                                 'propiedad de la mezcla con la temperatura y la presión, para la '
                                 'composición global definida en la pestaña Equilibrio de fases. '
                                 'El resultado es una familia de curvas que permite identificar '
                                 'cómo responde la propiedad a cambios de las condiciones de '
                                 'operación.',
                                 'The Sensitivity Analysis tab calculates the variation of a '
                                 'mixture property with temperature and pressure, for the overall '
                                 'composition defined in the Phase Equilibrium tab. The result is '
                                 'a family of curves that shows how the property responds to '
                                 'changes in operating conditions.'),
                                ('p',
                                 'Se especifica un intervalo de temperatura y otro de presión, '
                                 'cada uno con su valor inicial, su valor final y su número de '
                                 'puntos, distribuidos uniformemente. La variable elegida como eje '
                                 'X se barre punto a punto, y cada valor de la otra variable '
                                 'genera una curva:',
                                 'A temperature range and a pressure range are specified, each '
                                 'with its initial value, final value, and number of points, '
                                 'uniformly distributed. The variable chosen as the X axis is '
                                 'swept point by point, and each value of the other variable '
                                 'generates one curve:'),
                                ('ul',
                                 [('Eje X temperatura: cada curva es una isóbara, en la que la '
                                   'propiedad se calcula a presión constante a lo largo del '
                                   'intervalo de temperatura.',
                                   'Temperature X axis: each curve is an isobar, along which the '
                                   'property is calculated at constant pressure over the '
                                   'temperature range.'),
                                  ('Eje X presión: cada curva es una isoterma, en la que la '
                                   'propiedad se calcula a temperatura constante a lo largo del '
                                   'intervalo de presión.',
                                   'Pressure X axis: each curve is an isotherm, along which the '
                                   'property is calculated at constant temperature over the '
                                   'pressure range.')]),
                                ('p',
                                 'La temperatura se especifica en escala absoluta (°R o K según el '
                                 'sistema de unidades) y la presión en las unidades activas. La '
                                 'variable del eje X admite como mínimo dos puntos y la familia de '
                                 'curvas se limita a doce. Los puntos en los que la propiedad no '
                                 'existe, porque la fase correspondiente está ausente o el cálculo '
                                 'no converge, se dejan en blanco, de modo que la curva se '
                                 'interrumpe en las fronteras de fase.',
                                 'Temperature is specified on an absolute scale (°R or K depending '
                                 'on the unit system) and pressure in the active units. The X-axis '
                                 'variable requires at least two points, and the family of curves '
                                 'is limited to twelve. Points at which the property does not '
                                 'exist, because the corresponding phase is absent or the '
                                 'calculation does not converge, are left blank, so the curve is '
                                 'interrupted at phase boundaries.')]},
                   {'titulo': ('Motor de cálculo', 'Calculation engine'),
                    'bloques': [('p',
                                 'Cada punto del barrido se calcula con el mismo motor que la '
                                 'pestaña Equilibrio de fases, con la ecuación de estado, los '
                                 'coeficientes de interacción binaria (en los cálculos sin agua) y '
                                 'el método de densidad de líquido seleccionados en ella (COSTALD, '
                                 'raíz de la ecuación de estado o traslado de volumen de '
                                 'Peneloux). Los valores de un punto del barrido coinciden, por '
                                 'tanto, con los de un flash individual a las mismas condiciones.',
                                 'Each point of the sweep is calculated with the same engine as '
                                 'the Phase Equilibrium tab, with the equation of state, the '
                                 'binary interaction coefficients (in the water-free '
                                 'calculations), and the liquid density method selected there '
                                 '(COSTALD, equation of state root, or Peneloux volume shift). The '
                                 'values at a point of the sweep therefore coincide with those of '
                                 'an individual flash at the same conditions.'),
                                ('h3', 'Mezcla sin agua', 'Mixture without water'),
                                ('p',
                                 'Cuando el agua no está activa, la composición se reduce a los '
                                 'trece componentes de hidrocarburo renormalizados y se resuelve '
                                 'un flash bifásico vapor-líquido. La entalpía y la entropía '
                                 'molares de la corriente se calculan con los métodos del capítulo '
                                 '«Entalpía y entropía», y la densidad de la mezcla por aditividad '
                                 'de volúmenes de las fases (véase «Densidad de la mezcla y '
                                 'fracción volumétrica de fase»).',
                                 'When water is not active, the composition is reduced to the '
                                 'thirteen renormalized hydrocarbon components and a vapor-liquid '
                                 'two-phase flash is solved. The molar enthalpy and entropy of the '
                                 'stream are computed with the methods of the “Enthalpy and '
                                 'entropy” chapter, and the mixture density by additivity of the '
                                 'phase volumes (see “Mixture density and phase volume '
                                 'fraction”).'),
                                ('h3', 'Mezcla con agua', 'Mixture with water'),
                                ('p',
                                 'Cuando el agua está activa y su fracción en la mezcla es '
                                 'positiva, cada punto se resuelve con el flash trifásico con la '
                                 'regla de mezcla de Huron-Vidal, seguido de la identificación de '
                                 'las fases de hidrocarburo y del cálculo de propiedades por fase. '
                                 'La entalpía y la entropía de la corriente son los promedios '
                                 'ponderados por las fracciones molares de las fases presentes, y '
                                 'la densidad de la mezcla se obtiene por aditividad de volúmenes '
                                 'sobre las tres fases.',
                                 'When water is active and its fraction in the mixture is '
                                 'positive, each point is solved with the three-phase flash using '
                                 'the Huron-Vidal mixing rule, followed by the identification of '
                                 'the hydrocarbon phases and the calculation of properties per '
                                 'phase. The stream enthalpy and entropy are the averages weighted '
                                 'by the mole fractions of the phases present, and the mixture '
                                 'density is obtained by volume additivity over the three phases.'),
                                ('h3', 'Referencias', 'References'),
                                ('p',
                                 'Michelsen, M.L. y Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2.ª ed. '
                                 'Tie-Line Publications.',
                                 'Michelsen, M.L. and Mollerup, J.M. (2007). <em>Thermodynamic '
                                 'Models: Fundamentals and Computational Aspects</em>, 2nd ed. '
                                 'Tie-Line Publications.'),
                                ('p',
                                 'Huron, M.-J. y Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.',
                                 'Huron, M.-J. and Vidal, J. (1979). New mixing rules in simple '
                                 'equations of state for representing vapour-liquid equilibria of '
                                 'strongly non-ideal mixtures. <em>Fluid Phase Equilibria</em>, '
                                 '3(4), 255–271.'),
                                ('p',
                                 'Pedersen, K.S., Christensen, P.L. y Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2.ª ed. '
                                 'CRC Press.',
                                 'Pedersen, K.S., Christensen, P.L. and Shaikh, J.A. (2015). '
                                 '<em>Phase Behavior of Petroleum Reservoir Fluids</em>, 2nd ed. '
                                 'CRC Press.')]},
                   {'titulo': ('Propiedades disponibles', 'Available properties'),
                    'bloques': [('p',
                                 'El desplegable de propiedades ofrece las siguientes magnitudes, '
                                 'convertidas al sistema de unidades activo:',
                                 'The property drop-down list offers the following quantities, '
                                 'converted to the active unit system:'),
                                ('ul',
                                 [('Factor de compresibilidad del vapor y del líquido.',
                                   'Compressibility factor of the vapor and of the liquid.'),
                                  ('Densidad másica de la mezcla, del líquido y del vapor.',
                                   'Mass density of the mixture, the liquid, and the vapor.'),
                                  ('Fracción molar de vapor y de líquido.',
                                   'Vapor and liquid mole fraction.'),
                                  ('Gravedad específica, peso molecular y viscosidad del líquido y '
                                   'del vapor.',
                                   'Specific gravity, molecular weight, and viscosity of the '
                                   'liquid and of the vapor.'),
                                  ('Entalpía molar y entropía molar de la mezcla.',
                                   'Molar enthalpy and molar entropy of the mixture.'),
                                  ('Capacidad de agua del gas, en lb/MMscf, calculada por el '
                                   'segundo flash con el gas saturado de agua; está disponible '
                                   'también sin agua en la mezcla.',
                                   'Gas water capacity, in lb/MMscf, calculated by the second '
                                   'flash with the water-saturated gas; it is also available '
                                   'without water in the mixture.'),
                                  ('Factores volumétricos B<sub>g</sub> y B<sub>o</sub> y gas en '
                                   'solución R<sub>s</sub> (véase «Factores volumétricos y gas en '
                                   'solución»).',
                                   'Formation volume factors B<sub>g</sub> and B<sub>o</sub> and '
                                   'solution gas R<sub>s</sub> (see “Formation volume factors and '
                                   'solution gas”).')]),
                                ('p',
                                 'Las siguientes propiedades solo aplican cuando el agua está '
                                 'activa, y únicamente entonces aparecen en el desplegable:',
                                 'The following properties apply only when water is active, and '
                                 'only then do they appear in the drop-down list:'),
                                ('ul',
                                 [('Factor de compresibilidad, densidad másica, gravedad '
                                   'específica, peso molecular y viscosidad de la fase acuosa.',
                                   'Compressibility factor, mass density, specific gravity, '
                                   'molecular weight, and viscosity of the aqueous phase.'),
                                  ('Fracción molar de la fase acuosa.',
                                   'Mole fraction of the aqueous phase.'),
                                  ('Fracción molar de agua en el vapor y en el líquido de '
                                   'hidrocarburos.',
                                   'Water mole fraction in the vapor and in the hydrocarbon '
                                   'liquid.'),
                                  ('Contenido de agua del gas, en lb/MMscf.',
                                   'Gas water content, in lb/MMscf.'),
                                  ('Factor volumétrico B<sub>w</sub> y gas en solución '
                                   'R<sub>sw</sub> de la fase acuosa.',
                                   'Formation volume factor B<sub>w</sub> and solution gas '
                                   'R<sub>sw</sub> of the aqueous phase.')]),
                                ('p',
                                 'El contenido y la capacidad de agua siguen las definiciones de '
                                 '«Contenido y capacidad de agua del gas»: con fase acuosa '
                                 'presente, la capacidad es igual al contenido; sin ella, la '
                                 'capacidad se obtiene por el flash del gas saturado. El segundo '
                                 'flash se ejecuta solo cuando la propiedad graficada es la '
                                 'capacidad de agua.',
                                 'The water content and capacity follow the definitions of “Gas '
                                 'water content and water capacity”: with an aqueous phase '
                                 'present, the capacity equals the content; without it, the '
                                 'capacity is obtained from the flash of the saturated gas. The '
                                 'second flash is executed only when the plotted property is the '
                                 'water capacity.')]}]}]
