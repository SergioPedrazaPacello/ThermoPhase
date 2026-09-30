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
#  Contenido: se construye desde documentacion_contenido (español); la
#  traducción al inglés la aplica documentacion_i18n por bloque.
# ═════════════════════════════════════════════════════════════════════


def _bloque_html(b):
    tipo = b[0]
    if tipo == 'p':
        return f"<p>{b[1]}</p>"
    if tipo == 'h3':
        return f"<h3>{b[1]}</h3>"
    if tipo == 'eq':
        return _eq(b[1])
    if tipo == 'ul':
        return "<ul>" + "".join(f"<li>{es}</li>" for es, _en in b[1]) + "</ul>"
    return ""


def _construir_secciones():
    import documentacion_contenido as _dc
    secciones = []
    for ci, cap in enumerate(_dc.CAPITULOS, start=1):
        subs = []
        for si, sub in enumerate(cap['subsecciones'], start=1):
            titulo = f"{ci}.{si} {sub['titulo'][0]}"
            cuerpo = "\n".join(_bloque_html(b) for b in sub['bloques'])
            subs.append((titulo, f"<h2>{titulo}</h2>\n{cuerpo}"))
        secciones.append((f"{ci}. {cap['titulo'][0]}", subs))
    return secciones


SECCIONES = _construir_secciones()
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

        # Sincroniza los títulos del árbol con el idioma activo desde el
        # arranque (el árbol se construye en español; si el idioma es inglés
        # hay que traducirlo ya, sin esperar a un cambio manual de idioma).
        self.retraducir()

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
        import documentacion_i18n as _doc_i18n
        lang = _i18n.get_idioma()
        vis = getattr(self, '_arbol_visible', True)
        self.lbl_contenido.setText(_i18n.t("Contenido"))
        self.btn_ocultar.setText(_i18n.t("Ocultar") if vis else _i18n.t("Mostrar"))
        self.btn_atras.setText(_i18n.t("Atrás"))
        self.btn_adelante.setText(_i18n.t("Adelante"))
        def _tt(titulo):
            # Traduce el título del árbol: primero el diccionario general de
            # idioma, luego el de la documentación (por texto sin número).
            t = _i18n.t(titulo)
            if t == titulo:
                t = _doc_i18n.traducir_titulo_rapido(titulo, lang)
            return t
        for si, (sec_titulo, subs) in enumerate(SECCIONES):
            top = self._tops[si]
            top.setText(0, _tt(_sin_num(sec_titulo)))
            for ci, (sub_titulo, _h) in enumerate(subs):
                top.child(ci).setText(0, _tt(_sin_num(sub_titulo)))
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
        # Traducir el contenido al idioma activo (los bloques sin traducción
        # quedan en español).
        import idioma as _i18n
        import documentacion_i18n as _doc_i18n
        html = _doc_i18n.traducir_html(html, _i18n.get_idioma())
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
