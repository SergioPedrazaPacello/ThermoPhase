"""
idioma.py — Traduccion de la interfaz de ThermoPhase (Espanol / Ingles).

Estrategia: se guarda el idioma activo y un diccionario ES->EN. La funcion
`retraducir(widget)` recorre TODO el arbol de widgets (menus, etiquetas,
botones, combos, tablas, titulos de ventana) y cambia el texto segun el
idioma. La primera vez guarda el texto original en espanol como propiedad
dinamica del widget, de modo que volver a espanol lo restaura intacto.
"""

from PyQt6.QtWidgets import (
    QLabel, QPushButton, QCheckBox, QRadioButton, QToolButton, QGroupBox,
    QComboBox, QTableWidget, QTreeWidget, QMenuBar, QMenu, QAbstractButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

_IDIOMA = 'ES'          # 'ES' o 'EN'


def get_idioma():
    return _IDIOMA


def set_idioma(lang):
    global _IDIOMA
    _IDIOMA = 'EN' if str(lang).upper() == 'EN' else 'ES'


# ── Diccionario ES -> EN ─────────────────────────────────────────────
TRAD = {
    "Ocultar": "Hide", "Mostrar": "Show", "Atrás": "Back", "Adelante": "Forward",
    "Contenido": "Contents",
    # Menus (con & de mnemonico)
    "&Archivo": "&File", "&Editar": "&Edit", "&Ver": "&View",
    "&Herramientas": "&Tools", "&Exportar": "E&xport", "Ve&ntana": "&Window",
    "A&yuda": "&Help", "&Idioma": "&Language",
    "&Nuevo": "&New", "&Abrir...": "&Open...", "&Guardar": "&Save",
    "Guardar &como...": "Save &As...",
    "&Imprimir / Exportar a PDF...": "&Print / Export to PDF...",
    "&Salir": "&Exit", "&Deshacer": "&Undo", "&Rehacer": "&Redo",
    "&Copiar": "&Copy", "&Pegar": "&Paste", "Cortar": "Cut", "Borrar": "Delete",
    "Factor volumetrico Bg [ft3/scf]": "Formation volume factor Bg [ft3/scf]",
    "Factor volumetrico Bo [bbl/STB]": "Formation volume factor Bo [bbl/STB]",
    "Factor volumetrico Bw [bbl/STB]": "Formation volume factor Bw [bbl/STB]",
    "Gas en solucion Rs [scf/STB]": "Solution gas Rs [scf/STB]",
    "Factor volumétrico del gas Bg [ft3/scf]": "Gas formation volume factor Bg [ft3/scf]",
    "Factor volumétrico del petróleo Bo [bbl/STB]": "Oil formation volume factor Bo [bbl/STB]",
    "Factor volumétrico del agua Bw [bbl/STB]": "Water formation volume factor Bw [bbl/STB]",
    "Gas en solución en el petróleo Rs [scf/STB]": "Solution gas-oil ratio Rs [scf/STB]",
    "Gas en solución en el agua Rsw [scf/STB]": "Solution gas-water ratio Rsw [scf/STB]",
    "Escala del gráfico:": "Chart scale:", "Lineal": "Linear",
    "Semilog (eje Y logarítmico)": "Semi-log (log Y axis)",
    "Semilog (eje X logarítmico)": "Semi-log (log X axis)",
    "Logarítmica (ambos ejes)": "Log-log (both axes)",
    "Copiar": "Copy", "Pegar": "Paste", "Deshacer": "Undo", "Rehacer": "Redo", "&Navegador": "&Navigator",
    "Barra de &herramientas": "&Toolbar",
    "&Asociar archivos .tpsim con este programa":
        "&Associate .tpsim files with this program",
    "&Quitar asociacion de archivos .tpsim":
        "&Remove .tpsim file association",
    "Exportar resultados a &PDF...": "Export results to &PDF...",
    "&Cascada": "&Cascade", "&Mosaico": "&Tile", "Cerrar &todas": "Close &all",
    "&Acerca de ThermoPhase...": "&About ThermoPhase...",
    "&Documentación técnica": "&Technical Documentation",
    "Documentación técnica": "Technical Documentation",
    "Espanol": "Spanish", "Español": "Spanish", "Ingles": "English",
    "Inglés": "English",

    # Barra de selectores / navegador
    "Ecuación de estado:": "Equation of state:", "Densidad:": "Density:",
    "Corrección de volumen:": "Volume correction:", "Ninguna": "None",
    "Método envolvente:": "Envelope method:", "Navegador": "Navigator",
    "Cálculos": "Calculations", "Datos": "Data",

    # Arbol de calculos / datos
    "Equilibrio de fases": "Phase equilibrium",
    "Envolvente de fases": "Phase envelope",
    "Puntos de saturación": "Saturation points",
    "Propiedades termodinámicas": "Thermodynamic properties",
    "ThermoPhase — Análisis de Sensibilidad": "ThermoPhase — Sensitivity Analysis",
    "Desde:": "From:",
    "Hasta:": "To:",
    "Calcular": "Calculate",
    "(cargando)": "(loading)",
    "Gráficos": "Graphics",
    "&Gráficos": "&Graphics",
    "Activar cursor": "Enable cursor",
    "Mostrar iconos": "Show icons",
    "Análisis de sensibilidad": "Sensitivity analysis",
    "Análisis de Sensibilidad": "Sensitivity Analysis",
    "Sensibilidad": "Sensitivity",
    "Propiedad:": "Property:",
    "Variable del eje X:": "X-axis variable:",
    "N° puntos:": "No. of points:",
    "Factor de compresibilidad (vapor)": "Compressibility factor (vapor)",
    "Factor de compresibilidad (líquido)": "Compressibility factor (liquid)",
    "Densidad másica (mezcla)": "Mass density (mixture)",
    "Densidad másica (líquido)": "Mass density (liquid)",
    "Densidad másica (vapor)": "Mass density (vapor)",
    "Fracción de vapor (molar)": "Vapor fraction (molar)",
    "Gravedad específica (líquido)": "Specific gravity (liquid)",
    "Gravedad específica (vapor)": "Specific gravity (vapor)",
    "Peso molecular (líquido)": "Molecular weight (liquid)",
    "Peso molecular (vapor)": "Molecular weight (vapor)",
    "Viscosidad (líquido)": "Viscosity (liquid)",
    "Viscosidad (vapor)": "Viscosity (vapor)",
    "Entalpía molar (mezcla)": "Molar enthalpy (mixture)",
    "Entropía molar (mezcla)": "Molar entropy (mixture)",
    "Demasiadas curvas (>12). Reduzca el N° de puntos de la variable que NO está en el eje X.":
        "Too many curves (>12). Reduce the number of points of the variable NOT on the X-axis.",
    "Ingrese rangos positivos de T y P.": "Enter positive T and P ranges.",
    "Complete los campos de temperatura y presión (desde, hasta y N° puntos).":
        "Fill in the temperature and pressure fields (from, to and No. of points).",
    "Ingrese rangos positivos y N° de puntos válidos (T≥2, P≥1).":
        "Enter positive ranges and valid point counts (T≥2, P≥1).",
    "Error en el cálculo:": "Calculation error:",
    "Parámetros de la ecuación de estado": "Equation of state parameters",
    "Componentes": "Components", "Fluidos": "Fluids",
    "Equilibrio": "Equilibrium", "Envolvente": "Envelope",
    "Saturación": "Saturation", "Propiedades": "Properties",
    "Parametros": "Parameters", "Saturacion": "Saturation",
    "Fluido": "Fluid",

    # Titulos de ventana
    "ThermoPhase — Equilibrio de Fases": "ThermoPhase — Phase Equilibrium",
    "ThermoPhase — Envolvente de Fases": "ThermoPhase — Phase Envelope",
    "ThermoPhase — Puntos de Saturación": "ThermoPhase — Saturation Points",
    "ThermoPhase — Formación de Hidratos": "ThermoPhase — Hydrate Formation",
    "ThermoPhase — Propiedades Termodinamicas (Entalpia / Entropia)":
        "ThermoPhase — Thermodynamic Properties (Enthalpy / Entropy)",
    "ThermoPhase — Fluidos": "ThermoPhase — Fluids",

    # Equilibrio
    "Presión (psia):": "Pressure (psia):", "Temperatura (°R):": "Temperature (°R):",
    "Temperatura (°F):": "Temperature (°F):", "Equivalente (°R):": "Equivalent (°R):",
        "Propiedades...": "Properties...",
    "Propiedades a mostrar": "Properties to show",
    "Seleccione las propiedades a mostrar:": "Select the properties to show:",
    "Seleccione las 6 propiedades a mostrar en el resumen:":
        "Select the 6 properties to show in the summary:",
    "Seleccione las propiedades a mostrar en el resumen:":
        "Select the properties to show in the summary:",
    "Disponibles": "Available",
    "Seleccionados": "Selected",
    "Seleccionados: ": "Selected: ",
    "Seleccione los componentes del fluido:": "Select the fluid components:",
    "ThermoPhase — Componentes del fluido": "ThermoPhase — Fluid components",
    "Componentes del fluido": "Fluid components",
    "Identificación": "Identification",
    "Nombre": "Name",
    "Símbolo": "Symbol",
    "Punto de ebullición normal": "Normal boiling point",
    "Volumen crítico": "Critical volume",
    "Propiedades en conjunto": "General properties",
    "Propiedades recopiladas de HYSYS": "Properties collected from HYSYS",
    "Propiedades recopiladas de PVTsim": "Properties collected from PVTsim",
    "Volumen característico V* (COSTALD)": "Characteristic volume V* (COSTALD)",
    "Propiedades críticas (HYSYS)": "Critical properties (HYSYS)",
    "Temperatura crítica": "Critical temperature",
    "Presión crítica": "Critical pressure",
    "Factor acéntrico (PR)": "Acentric factor (PR)",
    "Factor acéntrico (SRK)": "Acentric factor (SRK)",
    "Propiedades críticas (PVTsim)": "Critical properties (PVTsim)",
    "Factor acéntrico": "Acentric factor",
    "Densidad de líquido (COSTALD)": "Liquid density (COSTALD)",
    "Volumen característico V*": "Characteristic volume V*",
    "Seleccionadas": "Selected",
    "Seleccionadas: ": "Selected: ",
    "Agregar": "Add",
    "Viscosidad": "Viscosity",
    "Realizar Calculo": "Run Calculation", "Fraccion masica": "Mass fraction",
    "Fraccion molar": "Mole fraction", "Normalizar": "Normalize",
    "Densidad": "Density", "Ecuacion:": "Equation:",
    "Resumen de los calculos:": "Calculation summary:",
    "Composicion de las fases:": "Phase composition:",
    "Composicion de las fases en equilibrio:": "Equilibrium phase composition:",
    "Mezcla": "Mixture", "Fase Vapor": "Vapour Phase", "Fase Liquida": "Liquid Phase",
    "Fase vapor": "Vapour phase", "Fase liquida": "Liquid phase",
    "Composicion General": "Overall Composition", "Corriente global": "Overall stream",
    "Fase fraccion [molar]:": "Phase fraction [molar]:",
    "Fase fraccion [masica]:": "Phase fraction [mass]:",
    "Fase fraccion [molar]": "Phase fraction [molar]",
    "Fase fraccion [masica]": "Phase fraction [mass]",
    "Fase fraccion [volumetrica]": "Phase fraction [volume]",
    "Fase fraccion [volumetrica]:": "Phase fraction [volume]:",
    "Fase Acuosa": "Aqueous Phase",
    "Gravedad especifica:": "Specific gravity:", "Gravedad especifica": "Specific gravity",
    "Densidad masica [lb/ft3]:": "Mass density [lb/ft3]:",
    "Factor de compresibilidad:": "Compressibility factor:",
    "Factor de compresibilidad": "Compressibility factor",
    "Peso molecular:": "Molecular weight:", "Peso molecular": "Molecular weight",
    "Sumatorias:": "Totals:", "Componente": "Component",
    "Calculando...": "Calculating...",

    # Envolvente / saturacion
    "Calcular Envolvente": "Calculate Envelope",
    "Calcular Isocalidad": "Calculate Quality Line",
    "Líneas de isocalidad:": "Quality lines:", "Puntos especiales:": "Special points:",
    "Marcar punto:": "Mark point:", "Colocar": "Place", "Quitar": "Remove",
    "Mostrar mapa de densidad": "Show density map",
    "Calcular punto de saturacion": "Calculate saturation point",
    "No se encontro punto de saturacion": "No saturation point found",
    "Propiedades del punto de saturacion:": "Saturation point properties:",
    "Fraccion molar de fase:": "Phase mole fraction:",
    "Datos de entrada:": "Input data:", "Resultado:": "Result:",
    "Resultados:": "Results:", "Condiones de calculo:": "Calculation conditions:",
    "Calcular propiedades": "Calculate properties", "Calcular:": "Calculate:",
    "Metodo:": "Method:", "Propiedad": "Property",

    # Fluidos
    "Fluidos guardados": "Saved fluids",
    "Composicion del fluido (fraccion molar)": "Fluid composition (mole fraction)",
    "Composicion del fluido (fraccion o porcentaje molar)": "Fluid composition (mole fraction or percent)",
    "Capturar actual": "Capture current",
    "Cargar en composicion principal": "Load into main composition",
    "Renombrar": "Rename", "Eliminar": "Delete", "Renombrar fluido": "Rename fluid",
    "Nombre:": "Name:", "Nuevo": "New",

    # Parametros
    "Propiedades criticas y factor acentrico":
        "Critical properties and acentric factor",
    "Coeficientes de interaccion binaria": "Binary interaction coefficients",
    "Fuente de los coeficientes de iteracion binaria:":
        "Source of the binary interaction coefficients:",
    "Restaurar valores originales": "Restore original values",
    "Temperatura Critica (°R)": "Critical Temperature (°R)",
    "Presion Critica (psi)": "Critical Pressure (psi)",
    "Temperatura Critica": "Critical Temperature",
    "Presion Critica": "Critical Pressure",
    "Factor acentrico": "Acentric factor",
    "Peso Molecular (lb/lb-mol)": "Molecular Weight (lb/lb-mol)",

    # Botones / dialogos comunes
    "Aceptar": "OK", "Cancelar": "Cancel", "Exportar CSV": "Export CSV",
    "Coeficientes restaurados.": "Coefficients restored.",
    "Operacion completada.": "Operation completed.",
    "Convergencia exitosa.": "Convergence successful.",
    "Guardado": "Saved", "Listo": "Ready",
    "Selecciona un fluido primero.": "Select a fluid first.",
    "Ingrese la presion y la temperatura.": "Enter the pressure and temperature.",
    "Ingrese un valor de presion o temperatura.":
        "Enter a pressure or temperature value.",
    "Ingrese valores numéricos válidos de presión y temperatura.":
        "Enter valid numeric pressure and temperature values.",
    "Asociacion registrada correctamente.": "Association registered successfully.",
    "Asociacion eliminada correctamente.": "Association removed successfully.",
    "Asociacion eliminada.": "Association removed.",

    # Componentes (nombres, para el arbol y tablas)
    "Nitrógeno [N₂]:": "Nitrogen [N₂]:", "Dióxido de carbono [CO₂]:": "Carbon dioxide [CO₂]:",
    "Metano [C1]:": "Methane [C1]:", "Etano [C2]:": "Ethane [C2]:",
    "Propano [C3]:": "Propane [C3]:", "Isobutano (2-metilpropano) [iC4]:":
        "Isobutane (2-methylpropane) [iC4]:", "n-Butano [nC4]:": "n-Butane [nC4]:",
    "Isopentano (2-metilbutano) [iC5]:": "Isopentane (2-methylbutane) [iC5]:",
    "n-Pentano [nC5]:": "n-Pentane [nC5]:", "Hexano [C6]:": "Hexane [C6]:",
    "Heptano [C7]:": "Heptane [C7]:", "Octano [C8]:": "Octane [C8]:",
    "Nonano [C9]:": "Nonane [C9]:",
    "Nitrógeno [N₂]": "Nitrogen [N₂]", "Dióxido de carbono [CO₂]": "Carbon dioxide [CO₂]",
    "Metano [C1]": "Methane [C1]", "Etano [C2]": "Ethane [C2]",
    "Propano [C3]": "Propane [C3]", "Isobutano (2-metilpropano) [iC4]":
        "Isobutane (2-methylpropane) [iC4]", "n-Butano [nC4]": "n-Butane [nC4]",
    "Isopentano (2-metilbutano) [iC5]": "Isopentane (2-methylbutane) [iC5]",
    "n-Pentano [nC5]": "n-Pentane [nC5]", "Hexano [C6]": "Hexane [C6]",
    "Heptano [C7]": "Heptane [C7]", "Octano [C8]": "Octane [C8]",
    "Nonano [C9]": "Nonane [C9]",
    "Contenido de agua [lb/MMscf]": "Water content [lb/MMscf]",
    "Capacidad de agua [lb/MMscf]": "Water capacity [lb/MMscf]",
    "Contenido de agua del gas [lb/MMscf]": "Gas water content [lb/MMscf]",
    "Capacidad de agua del gas [lb/MMscf]": "Gas water capacity [lb/MMscf]",
    "n-Hexano [nC6]:": "n-Hexane [nC6]:", "n-Hexano [nC6]": "n-Hexane [nC6]",
    "n-Heptano [nC7]:": "n-Heptane [nC7]:", "n-Heptano [nC7]": "n-Heptane [nC7]",
    "n-Octano [nC8]:": "n-Octane [nC8]:", "n-Octano [nC8]": "n-Octane [nC8]",
    "n-Nonano [nC9]:": "n-Nonane [nC9]:", "n-Nonano [nC9]": "n-Nonane [nC9]",

    # ── Ampliacion: cadenas que faltaban al traducir ────────────────────
    "Presion (psi):": "Pressure (psi):",
    "Presion (psia):": "Pressure (psia):",
    "Presión (psi):": "Pressure (psi):",
    "Temperatura (°R):": "Temperature (°R):",
    "Temperatura (°F):": "Temperature (°F):",
    "Cricondentérmica (°F):": "Cricondentherm (°F):",
    "Cricondenbárica (psi):": "Cricondenbar (psi):",
    "Cricondentermica (°F):": "Cricondentherm (°F):",
    "Cricondenbarica (psi):": "Cricondenbar (psi):",
    "Cricondentérmica": "Cricondentherm",
    "Cricondenbárica": "Cricondenbar",
    "T crítica": "Critical T",
    "P crítica": "Critical P",
    "HHV masico [BTU/lb]": "HHV mass [BTU/lb]",
    "LHV masico [BTU/lb]": "LHV mass [BTU/lb]",
    "HHV volumetrico [BTU/pie3]": "HHV volumetric [BTU/ft3]",
    "LHV volumetrico [BTU/pie3]": "LHV volumetric [BTU/ft3]",
    "GPM C3+ [gal/1000pie3]": "GPM C3+ [gal/1000ft3]",
    "Mostrar cricondentérmica y cricondenbárica":
        "Show cricondentherm and cricondenbar",
    "Mostrar punto crítico": "Show critical point",
    "Línea de isocalidad N°1:": "Quality line No.1:",
    "Línea de isocalidad N°2:": "Quality line No.2:",
    "Línea de isocalidad N°3:": "Quality line No.3:",
    "Línea de isocalidad N°4:": "Quality line No.4:",
    "Línea de isocalidad N°5:": "Quality line No.5:",
    "Temperatura de rocio (°F):": "Dew temperature (°F):",
    "Temperatura de rocío (°F):": "Dew temperature (°F):",
    "Temperatura de burbuja (°F):": "Bubble temperature (°F):",
    "Entalpia molar [Btu/lbmol]:": "Molar enthalpy [Btu/lbmol]:",
    "Entropia molar [Btu/lbmol-F]:": "Molar entropy [Btu/lbmol-F]:",
    "Entalpía molar [Btu/lbmol]:": "Molar enthalpy [Btu/lbmol]:",
    "Entropía molar [Btu/lbmol-F]:": "Molar entropy [Btu/lbmol-F]:",
    "Abrir calculo del fluido seleccionado (ventana independiente):":
        "Open calculation for the selected fluid (separate window):",
    "Abrir cálculo del fluido seleccionado (ventana independiente):":
        "Open calculation for the selected fluid (separate window):",
    "Parámetros EOS": "EOS Parameters", "Parametros EOS": "EOS Parameters",
    "Fraccion Molar": "Mole Fraction", "Fraccion o porcentaje": "Fraction or percent",
    "Composicion en fraccion molar (suma 1) o en porcentaje molar (suma 100)": "Composition as mole fraction (sum 1) or mole percent (sum 100)", "Fracción Molar": "Mole Fraction",
    "Fraccion Masica": "Mass Fraction", "Fracción Másica": "Mass Fraction",
    "Densidad masica [lb/ft3]": "Mass density [lb/ft3]",
    "Densidad masica [lb/ft3]:": "Mass density [lb/ft3]:",
    "Densidad másica [lb/ft3]": "Mass density [lb/ft3]",
    "Densidad másica [lb/ft3]:": "Mass density [lb/ft3]:",
    "Fase fraccion [molar]:": "Phase fraction [molar]:",
    "Fase fraccion [masica]:": "Phase fraction [mass]:",
    "Fase fracción [molar]:": "Phase fraction [molar]:",
    "Fase fracción [másica]:": "Phase fraction [mass]:",
    "Gravedad especifica": "Specific gravity",
    "Gravedad especifica:": "Specific gravity:",
    "Gravedad específica": "Specific gravity",
    "Gravedad específica:": "Specific gravity:",
    "Marcar punto:": "Mark point:",
    "Presion Critica (psi)": "Critical Pressure (psi)",
    "Presión Crítica (psi)": "Critical Pressure (psi)",
    "Presion de Burbuja": "Bubble Pressure", "Presión de Burbuja": "Bubble Pressure",
    "Presion de Rocío": "Dew Pressure", "Presión de Rocío": "Dew Pressure",
    "Temperatura Critica (°R)": "Critical Temperature (°R)",
    "Peso Molecular (lb/lb-mol)": "Molecular Weight (lb/lb-mol)",
    "Peso Molecular": "Molecular Weight",
    "Punto de burbuja": "Bubble point", "Punto de rocío": "Dew point",
    "Punto de rocio": "Dew point",
    "Presión": "Pressure", "Temperatura": "Temperature",
    "Cargando...": "Loading...", "(cargando)": "(loading)",
    "Peng-Robinson EOS": "Peng-Robinson EOS",
    "Temperatura de Rocío": "Dew Temperature",
    "Temperatura de Rocio": "Dew Temperature",
    "Temperatura de Burbuja": "Bubble Temperature",
    "% vapor": "% vapour", "% Vapor": "% Vapour",
    "Fase Vapor": "Vapour Phase", "Fase Líquida": "Liquid Phase",
    "Fase Liquida": "Liquid Phase", "Propiedad": "Property",
    "Valor": "Value", "Unidad": "Unit", "Unidades": "Units",
    "Cantidad": "Amount", "Total": "Total",
    # Etiquetas de gráficos (matplotlib)
    "Temperatura (°F)": "Temperature (°F)", "Presión (psia)": "Pressure (psia)",
    "Presion (psia)": "Pressure (psia)", "Temperatura (°R)": "Temperature (°R)",
    "Curva de Burbuja": "Bubble Curve", "Curva de Rocío": "Dew Curve",
    "Curva de Hidratos": "Hydrate Curve", "Hidratos": "Hydrates",
    "Curva de Rocio": "Dew Curve", "vapor": "vapour", "Punto": "Point",
    "Punto crítico": "Critical point", "Punto critico": "Critical point",
    "Curva de saturación": "Saturation curve",
    "Curva de saturacion": "Saturation curve",
    "Factor de compresibilidad (acuosa)": "Compressibility factor (aqueous)",
    "Densidad másica (acuosa)": "Mass density (aqueous)",
    "Fracción de líquido (molar)": "Liquid fraction (molar)",
    "Fracción acuosa (molar)": "Aqueous fraction (molar)",
    "Gravedad específica (acuosa)": "Specific gravity (aqueous)",
    "Peso molecular (acuosa)": "Molecular weight (aqueous)",
    "Viscosidad (acuosa)": "Viscosity (aqueous)",
    "Agua en el vapor (fracción molar)": "Water in vapor (mole fraction)",
    "Agua en el líquido (fracción molar)": "Water in liquid (mole fraction)",
    "La propiedad seleccionada requiere agua en la mezcla.":
        "The selected property requires water in the mixture.",
    "Propiedades generales": "General properties",
    "Formador de hidrato (estructuras)": "Hydrate former (structures)",
    "Anfitrión (red del hidrato)": "Host (hydrate lattice)",
    "Parámetros de HYSYS (EOS PR y SRK de HYSYS)": "HYSYS parameters (HYSYS PR and SRK EOS)",
    "Parámetros de PVTsim (EOS PR y SRK de PVTsim)": "PVTsim parameters (PVTsim PR and SRK EOS)",
    "Volumen crítico (viscosidad LBC)": "Critical volume (LBC viscosity)",
    "Traslado de volumen de Peneloux (PR)": "Peneloux volume shift (PR)",
    "Traslado de volumen de Peneloux (SRK)": "Peneloux volume shift (SRK)",
    "Cp de gas ideal a 60 °F": "Ideal-gas Cp at 60 °F",
    "Factor acéntrico": "Acentric factor",
    "Agua [H₂O]": "Water [H₂O]",
    "Agua [H₂O]:": "Water [H₂O]:",
    "La mezcla no contiene hidrocarburos.":
        "The mixture contains no hydrocarbons.",
    "Curvas de Isocalidad no disponibles para mezclas con agua.":
        "Quality lines are not available for mixtures with water.",
    "Mapa de densidad no disponible para mezclas con agua.":
        "Density map is not available for mixtures with water.",
    "Rocío HC (2-HC)": "HC dew (2-HC)",
    "Límite 3 fases HC (3-HC)": "HC 3-phase boundary (3-HC)",
    "Línea trifásica V-L-Aq": "V-L-Aq three-phase line",
    "Aparición de agua (3-Aq)": "Water appearance (3-Aq)",
    "Rocío de agua (2-Aq)": "Water dew (2-Aq)",
    "Las curvas de isocalidad no están disponibles en "
    "componentes puros.":
        "Quality lines are not available for pure components.",
    "El mapa de densidad no está disponible en componentes "
    "puros (la saturación es una única curva, sin área "
    "bifásica).":
        "The density map is not available for pure components "
        "(saturation is a single curve, with no two-phase area).",
    # Diálogos emergentes (títulos y mensajes)
    "ThermoPhase — Advertencia": "ThermoPhase — Warning",
    "ThermoPhase — Error": "ThermoPhase — Error",
    "Advertencia": "Warning", "Error": "Error",
    "La suma de fracciones debe ser 1.0": "The sum of fractions must be 1.0",
    "La composicion debe sumar 1 (fraccion molar) o 100 (porcentaje molar)": "The composition must add up to 1 (mole fraction) or 100 (mole percent)",
    "La suma de las fracciones debe ser 1.0": "The sum of fractions must be 1.0",
    "No se pudo abrir el archivo:": "Could not open the file:",
    "No se pudo guardar el archivo:": "Could not save the file:",
    "¿Desea guardar los cambios?": "Do you want to save the changes?",
    "Cambios sin guardar": "Unsaved changes",
    "Archivo guardado correctamente.": "File saved successfully.",
    # Acerca de ThermoPhase
    "ThermoPhase 1.0\n\n"
    "Software de equilibrio de fases y propiedades termodinamicas "
    "para mezclas de hidrocarburos.\n"
    "Ecuaciones de estado: Peng-Robinson y Soave-Redlich-Kwong.":
        "ThermoPhase 1.0\n\n"
        "Phase equilibrium and thermodynamic properties software "
        "for hydrocarbon mixtures.\n"
        "Equations of state: Peng-Robinson and Soave-Redlich-Kwong.",
    # Reportes PDF (mensaje, titulo de dialogo, nombre por defecto)
    "PDF exportado correctamente:": "PDF exported successfully:",
    "Exportar resultados a PDF": "Export results to PDF",
    "Todos los archivos (*.*)": "All files (*.*)",
    "reporte": "report", "Generando PDF...": "Generating PDF...",
    # Saturacion
    "Equivalente (°R / psi):": "Equivalent (°R / psi):",
    "Equivalente (°R):": "Equivalent (°R):",
    "Equivalente (psi):": "Equivalent (psi):",
    "Convergencia exitosa.": "Convergence successful.",
    "Temperatura de rocio (°F):": "Dew temperature (°F):",
    # Entalpia/Entropia: mensajes de modo y dialogos
    "Sistema en fase vapor unica.": "Single vapour phase system.",
    "Sistema en fase liquida unica.": "Single liquid phase system.",
    "Sistema bifasico vapor-liquido.": "Two-phase vapour-liquid system.",
    "Sistema en region supercritica.": "Supercritical region system.",
    "Ingrese Temperatura y Presion positivas.":
        "Enter positive Temperature and Pressure.",
    "Composicion vacia. Ingrese la composicion en la "
    "pestaña de Equilibrio de fases.":
        "Empty composition. Enter the composition in the "
        "Phase Equilibrium tab.",
    "Fraccion molar de fase:": "Phase mole fraction:",
    "Fase vapor": "Vapour phase", "Fase liquida": "Liquid phase",
    # Nombres por defecto de fluidos / cromatografias
    "Cromatografia": "Chromatography", "Cromatografía": "Chromatography",
    # Ventanas emergentes restantes
    "Fluido «%s» cargado en la composicion principal.":
        "Fluid «%s» loaded into the main composition.",
    "No hay resultados del calculo flash para exportar.\n"
    "Ejecute el calculo en la pestaña de Equilibrio de fases.":
        "No flash calculation results to export.\n"
        "Run the calculation in the Phase Equilibrium tab.",
    "No hay resultados del calculo flash para exportar":
        "No flash calculation results to export",
    "Valor inválido en Línea de isocalidad N°%d.":
        "Invalid value in Quality line No.%d.",
    "La calidad N°%d debe estar entre 0 y 100 (%%).":
        "Quality No.%d must be between 0 and 100 (%%).",
    "Ingrese al menos un valor de % de vapor en las celdas.":
        "Enter at least one % vapour value in the cells.",
    "CSV guardado:": "CSV saved:", "Operacion completada.": "Operation completed.",
    "No se pudo completar la operacion:": "Could not complete the operation:",
    "ThermoPhase": "ThermoPhase", "Guardado": "Saved",
    "ThermoPhase — Información": "ThermoPhase — Information",
    "ThermoPhase — Informacion": "ThermoPhase — Information",
    # Reporte PDF (contenido)
    "Reporte de Simulacion - ThermoPhase": "Simulation Report - ThermoPhase",
    "Condiones de calculo:": "Calculation conditions:",
    "Condiciones de calculo:": "Calculation conditions:",
    "Modelo de calculo ocupado:": "Calculation model used:",
    "Ecuacion de estado ocupada:": "Equation of state used:",
    "Metodo de calculo de densidad:": "Density calculation method:",
    "Composicion General": "Overall Composition",
    "Composicion de las fases:": "Phase composition:",
    "Resumen de los calculos:": "Calculation summary:",
    "Presion": "Pressure", "Temperatura": "Temperature",
    "Densidad masica": "Mass density", "Entalpia molar": "Molar enthalpy",
    "Entropia molar": "Molar entropy", "Sistema de unidades:": "Unit system:", "Equivalente": "Equivalent",
    "Temperatura de Hidrato": "Hydrate Temperature", "Presion de Hidrato": "Hydrate Pressure",
    "Formación de hidratos": "Hydrate Formation", "Formación de Hidratos": "Hydrate Formation",
    "Estructura": "Structure",
    "Calcular formacion de hidrato": "Calculate hydrate formation",
    "Agregar curva de formacion de hidrato": "Add hydrate formation curve",
    "Quitar curva de formacion de hidrato": "Remove hydrate formation curve",
    "Datos de entrada:": "Input data:",
    "Composicion de las fases en equilibrio:": "Equilibrium phase composition:",
    "Propiedades del punto de hidrato:": "Hydrate point properties:",
    "No se encontró punto de formación de hidrato en el rango.":
        "No hydrate formation point found in range.",
    "Poder calorífico y GPM": "Heating Value and GPM",
    "Poder calorífico y riqueza del gas": "Heating value and gas richness",
    "Cálculo del poder calorífico volumétrico": "Calculation of the volumetric heating value",
    "Conversión a base másica": "Conversion to a mass basis",
    "Contenido de licuables (GPM)": "Liquefiable content (GPM)",
    "Formación de hidratos": "Hydrate Formation",
    "Formación de hidratos de gas": "Gas hydrate formation",
    "El modelo de van der Waals y Platteeuw": "The van der Waals and Platteeuw model",
    "Término de adsorción de Langmuir": "Langmuir adsorption term",
    "Término de referencia del agua": "Water reference term",
    "Fugacidad de mezcla y flujo de cálculo": "Mixture fugacity and calculation flow",
    "Generado": "Generated",
    "Página": "Page",
    "Simulador termodinámico": "Thermodynamic simulator",
    "Tipo de calculo": "Calculation type",
    "Propiedades del punto:": "Point properties:",
    "Comparar envolventes": "Compare envelopes",
    "Comparación de envolventes": "Envelope comparison",
    "ThermoPhase — Comparación de envolventes": "ThermoPhase — Envelope Comparison",
    "Composición principal": "Main composition",
    "Seleccione los fluidos cuyas envolventes se compararán:": "Select the fluids whose envelopes will be compared:",
    "Fluidos disponibles": "Available fluids",
    "Fluidos a graficar": "Fluids to plot",
    "Graficar": "Plot",
    "Sin composición:": "No composition:",
    "La composición no suma 1 (fracción molar) ni 100 (porcentaje molar):": "Composition does not add up to 1 (mole fraction) or 100 (mole percent):",
    "Ninguno de los fluidos seleccionados tiene una composición válida; no se puede graficar.": "None of the selected fluids has a valid composition; nothing can be plotted.",
    "Los siguientes fluidos no se graficarán:": "The following fluids will not be plotted:",
    "Resaltar fluido:": "Highlight fluid:",
    "Ninguno": "None",
    "No se pudo trazar la envolvente de:": "The envelope could not be traced for:",
    "Fluido:": "Fluid:",
    "Calculando:": "Calculating:",
    "Seleccionar fluidos": "Select fluids",
    "Comparar envolventes": "Compare envelopes",
    "Recorrido de presión y temperatura": "Pressure and temperature path",
    "Recorrido": "Path",
    "Puntos del recorrido, en el orden en que se recorren:": "Path points, in the order they are followed:",
    "Agregar punto": "Add point",
    "Quitar punto": "Remove point",
    "Cada punto debe tener presión y temperatura numéricas.": "Each point must have numeric pressure and temperature.",
    "La presión y la temperatura absoluta deben ser mayores que cero.": "Pressure and absolute temperature must be greater than zero.",
    "Mostrar curva de hidratos": "Show hydrate curve",
    "Flash múltiple": "Multiple flash",
    "&Flash múltiple": "&Multiple flash",
    "ThermoPhase — Flash múltiple": "ThermoPhase — Multiple flash",
    "Nuevo cálculo": "New calculation",
    "Guardar CSV": "Save CSV",
    "No convergió el cálculo en las corridas:": "The calculation did not converge in runs:",
    "Condiciones de cada corrida:": "Conditions of each run:",
    "Propiedades a mostrar:": "Properties to display:",
    "Ingrese al menos un punto de presión y temperatura.": "Enter at least one pressure and temperature point.",
    "Seleccione al menos una propiedad.": "Select at least one property.",
    "El fluido seleccionado no tiene composición.": "The selected fluid has no composition.",
    "Condiciones:": "Conditions:",
    "Composición:": "Composition:",
    "Composición": "Composition",
    "ThermoPhase — Ingreso de datos": "ThermoPhase — Data input",
    "Mostrar marcadores": "Show markers",
    "Mostrar valores en algunos puntos": "Show values at some points",
    "Puntos de saturación e hidratos (a la presión o temperatura de la corrida)": "Saturation and hydrate points (at the run pressure or temperature)",
    "Temperatura de rocío": "Dew temperature",
    "Temperatura de burbuja": "Bubble temperature",
    "Temperatura de hidrato": "Hydrate temperature",
    "Presión de rocío": "Dew pressure",
    "Presión de burbuja": "Bubble pressure",
    "Presión de hidrato": "Hydrate pressure",
    "Margen de hidrato": "Hydrate margin",
    "&Cálculos": "&Calculations",
    "Contenido de agua de saturación": "Saturation water content",
    "ThermoPhase — Contenido de agua de saturación": "ThermoPhase — Saturation water content",
    "Estado de la corriente:": "Stream state:",
    "Agua de saturación [porcentaje molar]:": "Saturation water [mole percent]:",
    "Agua ingresada [porcentaje molar]:": "Entered water [mole percent]:",
    "Diferencia [porcentaje molar]:": "Difference [mole percent]:",
    "Contenido de agua del gas saturado [lb/MMscf]:": "Water content of saturated gas [lb/MMscf]:",
    "Fases de hidrocarburo:": "Hydrocarbon phases:",
    "Composición de la corriente:": "Stream composition:",
    "Composición de entrada": "Input composition",
    "Composición saturada": "Saturated composition",
    "Cargar en el fluido": "Load into the fluid",
    "Cargar en la composición principal": "Load into the main composition",
    "Guardar como fluido nuevo": "Save as new fluid",
    "Calcular contenido de agua": "Calculate water content",
    "Cargar en la composición actual": "Load into the current composition",
    "Tipo de flash:": "Flash type:",
    "Presión y temperatura": "Pressure and temperature",
    "Presión y entalpía": "Pressure and enthalpy",
    "Presión y entropía": "Pressure and entropy",
    "Ingrese la presion y la entropia.": "Enter the pressure and the entropy.",
    "Ingrese la presion y la entalpia.": "Enter the pressure and the enthalpy.",
    "Presión y fracción de vapor": "Pressure and vapour fraction",
    "Temperatura y fracción de vapor": "Temperature and vapour fraction",
    "Fraccion de vapor (molar):": "Vapour fraction (molar):",
    "Ingrese la presion y la fraccion de vapor.": "Enter the pressure and the vapour fraction.",
    "Ingrese la temperatura y la fraccion de vapor.": "Enter the temperature and the vapour fraction.",
    "La fraccion de vapor debe estar entre 0 y 1.": "The vapour fraction must be between 0 and 1.",
    "La fracción de vapor debe estar entre 0 y 1.": "The vapour fraction must be between 0 and 1.",
    "No hay punto de burbuja a esta presión.": "There is no bubble point at this pressure.",
    "No hay punto de rocío a esta presión.": "There is no dew point at this pressure.",
    "No existe esa fracción de vapor a esta presión.": "That vapour fraction does not exist at this pressure.",
    "No hay punto de burbuja a esta temperatura.": "There is no bubble point at this temperature.",
    "No hay punto de rocío a esta temperatura.": "There is no dew point at this temperature.",
    "No existe esa fracción de vapor a esta temperatura.": "That vapour fraction does not exist at this temperature.",
    "No se encontró la temperatura de rocío a esta presión.": "No dew point temperature was found at this pressure.",
    "No se encontró la temperatura de burbuja a esta presión.": "No bubble point temperature was found at this pressure.",
    "No se encontró la presión de rocío a esta temperatura.": "No dew point pressure was found at this temperature.",
    "No se encontró la presión de burbuja a esta temperatura.": "No bubble point pressure was found at this temperature.",
    "No se obtuvo resultado con estos datos.": "No result was obtained with these data.",
    "Sin agua": "Without water",
    "Saturada": "Saturated",
    "Subsaturada": "Undersaturated",
    "Con agua libre": "With free water",
    "Vapor y líquido": "Vapour and liquid",
    "Vapor": "Vapour",
    "Líquido": "Liquid",
    "Agua libre en exceso [porcentaje molar]:": "Excess free water [mole percent]:",
    "Agua faltante [porcentaje molar]:": "Missing water [mole percent]:",
    "No se pudo saturar la corriente con agua a estas condiciones.": "The stream could not be saturated with water at these conditions.",
    "La composición saturada se cargó en la composición principal.": "The saturated composition was loaded into the main composition.",
    "La composición saturada se cargó en el fluido": "The saturated composition was loaded into the fluid",
    "saturado con agua": "water saturated",
    "Se creó el fluido": "Fluid created:",
}

# EN -> ES (inverso) para poder detectar y revertir.
_TRAD_INV = {v: k for k, v in TRAD.items()}


def t(s):
    """Traduce s al idioma activo (desde el original en espanol)."""
    if _IDIOMA == 'EN':
        return TRAD.get(s, s)
    return s


def _traducir_texto(es):
    """Dado el texto ORIGINAL en espanol, devuelve el que corresponde."""
    return TRAD.get(es, es) if _IDIOMA == 'EN' else es


def _orig_es(w, actual):
    """Obtiene/almacena el texto original en espanol de un widget."""
    prev = w.property("_i18n_es")
    if prev is None or prev == "":
        # Si el texto actual esta en ingles (por un cambio previo), busca su ES.
        es = _TRAD_INV.get(actual, actual)
        w.setProperty("_i18n_es", es)
        return es
    return prev


def retraducir(widget):
    """Recorre el arbol de `widget` y aplica el idioma activo a todo texto."""
    if widget is None:
        return
    # Menus
    if isinstance(widget, QMenuBar):
        for act in widget.actions():
            _tr_action(act)
    # Botones y etiquetas
    for w in widget.findChildren(QLabel):
        es = _orig_es(w, w.text()); w.setText(_traducir_texto(es))
    for w in widget.findChildren(QAbstractButton):
        txt = w.text()
        if txt:
            es = _orig_es(w, txt); w.setText(_traducir_texto(es))
    for w in widget.findChildren(QGroupBox):
        es = _orig_es(w, w.title()); w.setTitle(_traducir_texto(es))
    # Placeholders de campos de texto
    from PyQt6.QtWidgets import QLineEdit, QTabWidget
    for w in widget.findChildren(QLineEdit):
        ph = w.placeholderText()
        if ph:
            prev = w.property("_i18n_es_ph")
            es = prev if prev else _TRAD_INV.get(ph, ph)
            if not prev:
                w.setProperty("_i18n_es_ph", es)
            w.setPlaceholderText(_traducir_texto(es))
    # Pestañas (QTabWidget)
    for w in widget.findChildren(QTabWidget):
        for i in range(w.count()):
            t = w.tabText(i)
            key = f"_i18n_es_tab_{i}"
            prev = w.property(key)
            es = prev if prev else _TRAD_INV.get(t, t)
            if not prev:
                w.setProperty(key, es)
            w.setTabText(i, _traducir_texto(es))
    for w in widget.findChildren(QComboBox):
        for i in range(w.count()):
            it = w.itemText(i)
            key = f"_i18n_es_{i}"
            prev = w.property(key)
            es = prev if prev else _TRAD_INV.get(it, it)
            if not prev:
                w.setProperty(key, es)
            w.setItemText(i, _traducir_texto(es))
    # Menus contextuales / barra
    mb = widget.findChild(QMenuBar)
    if mb is not None:
        for act in mb.actions():
            _tr_action(act)
    # Tablas (cabeceras y celdas de etiqueta que esten en el diccionario)
    for tb in widget.findChildren(QTableWidget):
        # Cabeceras horizontales y verticales
        for cab in ('h', 'v'):
            cnt = tb.columnCount() if cab == 'h' else tb.rowCount()
            for k in range(cnt):
                it = (tb.horizontalHeaderItem(k) if cab == 'h'
                      else tb.verticalHeaderItem(k))
                if it is None:
                    continue
                txt = it.text()
                es = it.data(Qt.ItemDataRole.UserRole + 99)
                if es is None:
                    es = _TRAD_INV.get(txt, txt)
                    it.setData(Qt.ItemDataRole.UserRole + 99, es)
                it.setText(_traducir_texto(es))
        for r in range(tb.rowCount()):
            for c in range(tb.columnCount()):
                it = tb.item(r, c)
                if it is None:
                    continue
                txt = it.text()
                es = it.data(Qt.ItemDataRole.UserRole + 99)
                if es is None:
                    es = _TRAD_INV.get(txt, txt)
                    if es in TRAD or es in _TRAD_INV.values():
                        it.setData(Qt.ItemDataRole.UserRole + 99, es)
                if es in TRAD:
                    it.setText(_traducir_texto(es))
    # Arboles (QTreeWidget) — items de primer y segundo nivel
    for tr in widget.findChildren(QTreeWidget):
        def _walk(item):
            txt = item.text(0)
            es = item.data(0, Qt.ItemDataRole.UserRole + 99)
            if es is None:
                es = _TRAD_INV.get(txt, txt)
                item.setData(0, Qt.ItemDataRole.UserRole + 99, es)
            item.setText(0, _traducir_texto(es))
            for k in range(item.childCount()):
                _walk(item.child(k))
        for i in range(tr.topLevelItemCount()):
            _walk(tr.topLevelItem(i))


def _tr_action(act):
    if act.isSeparator():
        return
    es = act.property("_i18n_es")
    if es is None:
        es = _TRAD_INV.get(act.text(), act.text())
        act.setProperty("_i18n_es", es)
    act.setText(_traducir_texto(es))
    sub = act.menu()
    if sub is not None:
        for a in sub.actions():
            _tr_action(a)
