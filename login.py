"""
ThermoPhase — ventana de ingreso de usuario.

Se muestra después del splash (cuando el programa ya terminó de cargar) y antes
de abrir la ventana principal.  Es un recuadro flotante sin marco de ventana
(igual que el splash): se arrastra con el ratón y se cierra con la «×» o Esc.

Por ahora no valida nada: el botón «Ingresar» cierra el diálogo y deja entrar
al programa; cerrarlo sale de él.  La verificación en línea de usuario/licencia
se conectará aquí más adelante.
"""
import os
import base64
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QCheckBox, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QByteArray

from rutas import ruta_recurso

_F = 'Arial Narrow'
_NAR = '#E2571E'
_NAR_HOVER = '#C94A15'
_SOMBRA = 24          # margen transparente alrededor del recuadro para la sombra


def _pixmap_marca():
    try:
        from logo_marca import PNG_B64
        pm = QPixmap()
        pm.loadFromData(QByteArray(base64.b64decode(PNG_B64)), 'PNG')
        return pm
    except Exception:
        return QPixmap()


class DialogoLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ThermoPhase")
        ico = ruta_recurso('thermophase.ico')
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
        # Sin marco ni barra de título; ventana propia (aparece en la barra de tareas)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._arrastre = None

        v = QVBoxLayout(self)
        v.setContentsMargins(_SOMBRA, _SOMBRA - 6, _SOMBRA, _SOMBRA + 6)

        card = QFrame()
        card.setObjectName('card')
        # Mismo degradado vertical que el fondo del splash (blanco → gris claro)
        card.setStyleSheet("QFrame#card{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
                           "stop:0 #FFFFFF,stop:1 #E6E6E6);"
                           "border:1px solid #CFCFCF;border-radius:10px;}")
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(24)
        sh.setOffset(0, 5)
        sh.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(sh)

        c = QVBoxLayout(card)
        c.setContentsMargins(34, 8, 10, 26)
        c.setSpacing(0)

        # Botón de cierre propio (no hay barra de título)
        sup = QHBoxLayout()
        sup.addStretch()
        b_x = QPushButton("✕")
        b_x.setFixedSize(26, 26)
        b_x.setCursor(Qt.CursorShape.PointingHandCursor)
        b_x.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b_x.setToolTip("Salir")
        b_x.setStyleSheet('QPushButton{background:transparent;border:none;border-radius:13px;'
                          'color:#8A8A8A;font-size:11pt;}'
                          'QPushButton:hover{background:#E4E4E4;color:#303030;}')
        b_x.clicked.connect(self.reject)
        sup.addWidget(b_x)
        c.addLayout(sup)

        cuerpo = QVBoxLayout()
        cuerpo.setContentsMargins(0, 0, 22, 0)
        cuerpo.setSpacing(0)
        c.addLayout(cuerpo)

        marca = QLabel()
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marca.setStyleSheet('background:transparent;border:none;')
        pm = _pixmap_marca()
        if not pm.isNull():
            dpr = self.devicePixelRatioF() or 1.0
            pm = pm.scaledToWidth(int(250 * dpr), Qt.TransformationMode.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            marca.setPixmap(pm)
        else:
            marca.setText("ThermoPhase")
            marca.setStyleSheet(f'font-family:"{_F}";font-size:26pt;color:#303030;'
                                'background:transparent;border:none;')
        cuerpo.addWidget(marca)
        cuerpo.addSpacing(22)

        self.ed_usuario = self._campo(cuerpo, "Usuario")
        self.ed_clave = self._campo(cuerpo, "Contraseña", clave=True)

        fila = QHBoxLayout()
        self.ck_recordar = QCheckBox("Recordarme en este equipo")
        self.ck_recordar.setStyleSheet(
            f'QCheckBox{{font-family:"{_F}";font-size:10pt;color:#555;border:none;background:transparent;}}'
            'QCheckBox::indicator{width:14px;height:14px;border:1px solid #BBB;border-radius:3px;background:#FFF;}'
            f'QCheckBox::indicator:checked{{background:{_NAR};border:1px solid {_NAR};}}')
        fila.addWidget(self.ck_recordar)
        fila.addStretch()
        cuerpo.addLayout(fila)
        cuerpo.addSpacing(12)

        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setFixedHeight(38)
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.setDefault(True)
        self.btn_ingresar.setStyleSheet(
            f'QPushButton{{background:{_NAR};color:#FFFFFF;border:none;border-radius:6px;'
            f'font-family:"{_F}";font-size:12pt;font-weight:bold;}}'
            f'QPushButton:hover{{background:{_NAR_HOVER};}}'
            f'QPushButton:pressed{{background:#B0410F;}}')
        self.btn_ingresar.clicked.connect(self.accept)
        cuerpo.addWidget(self.btn_ingresar)

        v.addWidget(card)
        self.setFixedWidth(380 + 2*_SOMBRA)
        self.setFixedHeight(self.sizeHint().height())
        self.ed_usuario.setFocus()

    def _campo(self, lay, titulo, clave=False):
        l = QLabel(titulo)
        l.setStyleSheet(f'font-family:"{_F}";font-size:10pt;color:#555;border:none;'
                        'background:transparent;')
        e = QLineEdit()
        e.setFixedHeight(34)
        e.setStyleSheet(
            f'QLineEdit{{font-family:"{_F}";font-size:12pt;color:#202020;background:#F7F7F7;'
            'border:1px solid #DDDDDD;border-radius:6px;padding:0 10px;'
            'lineedit-password-character:8226;}'
            f'QLineEdit:focus{{border:1px solid {_NAR};background:#FFFFFF;}}')
        if clave:
            e.setEchoMode(QLineEdit.EchoMode.Password)
            f = e.font()
            f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
            e.setFont(f)
        lay.addWidget(l)
        lay.addSpacing(3)
        lay.addWidget(e)
        lay.addSpacing(10)
        return e

    # ── arrastre con el ratón (no hay barra de título) ───────────────────
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._arrastre = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()
            ev.accept()

    def mouseMoveEvent(self, ev):
        if self._arrastre is not None and ev.buttons() & Qt.MouseButton.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._arrastre)
            ev.accept()

    def mouseReleaseEvent(self, ev):
        self._arrastre = None


def pedir_ingreso(parent=None):
    """Muestra el diálogo de ingreso.  Devuelve True si el usuario pulsó
    «Ingresar» y False si lo cerró (× o Esc)."""
    dlg = DialogoLogin(parent)
    try:
        scr = dlg.screen().availableGeometry()
        dlg.move(scr.x() + (scr.width() - dlg.width())//2,
                 scr.y() + (scr.height() - dlg.height())//2)
    except Exception:
        pass
    dlg.raise_()
    dlg.activateWindow()
    return dlg.exec() == QDialog.DialogCode.Accepted
