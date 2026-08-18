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
    "&Copiar": "&Copy", "&Pegar": "&Paste", "&Navegador": "&Navigator",
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
    "Disponibles": "Available",
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
    "Factor acentrico": "Acentric factor",
    "Peso Molecular (lb/lb-mol)": "Molecular Weight (lb/lb-mol)",

    # Botones / dialogos comunes
    "Aceptar": "OK", "Exportar CSV": "Export CSV",
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
    "Fraccion Molar": "Mole Fraction", "Fracción Molar": "Mole Fraction",
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
    "Curva de Rocio": "Dew Curve", "vapor": "vapour", "Punto": "Point",
    "Punto crítico": "Critical point", "Punto critico": "Critical point",
    # Diálogos emergentes (títulos y mensajes)
    "ThermoPhase — Advertencia": "ThermoPhase — Warning",
    "ThermoPhase — Error": "ThermoPhase — Error",
    "Advertencia": "Warning", "Error": "Error",
    "La suma de fracciones debe ser 1.0": "The sum of fractions must be 1.0",
    "La suma de las fracciones debe ser 1.0": "The sum of fractions must be 1.0",
    "No se pudo abrir el archivo:": "Could not open the file:",
    "No se pudo guardar el archivo:": "Could not save the file:",
    "¿Desea guardar los cambios?": "Do you want to save the changes?",
    "Cambios sin guardar": "Unsaved changes",
    "Archivo guardado correctamente.": "File saved successfully.",
    # Acerca de ThermoPhase
    "ThermoPhase 1.0\n\n"
    "Software de equilibrio de fases y propiedades termodinamicas "
    "para mezclas de hidrocarburos (13 componentes).\n"
    "Ecuaciones de estado: Peng-Robinson y Soave-Redlich-Kwong.":
        "ThermoPhase 1.0\n\n"
        "Phase equilibrium and thermodynamic properties software "
        "for hydrocarbon mixtures (13 components).\n"
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
