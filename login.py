"""
ThermoPhase — ventana de ingreso de usuario.

Se muestra después del splash (cuando el programa ya terminó de cargar) y antes
de abrir la ventana principal.  Por ahora no valida nada: el botón «Ingresar»
cierra el diálogo y deja entrar al programa; cerrar la ventana sale de él.
La verificación en línea de usuario/licencia se conectará aquí más adelante.
"""
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QCheckBox, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QColor, QFont, QIcon
from PyQt6.QtCore import Qt

from rutas import ruta_recurso

_F = 'Arial Narrow'
_NAR = '#E2571E'
_NAR_HOVER = '#C94A15'


class DialogoLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ThermoPhase")
        ico = ruta_recurso('thermophase.ico')
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint
                            | Qt.WindowType.WindowCloseButtonHint)
        self.setObjectName('fondo')
        self.setFixedSize(460, 420)
        self.setStyleSheet("QDialog#fondo{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
                           "stop:0 #F4F4F4,stop:1 #E2E2E2);}")

        v = QVBoxLayout(self)
        v.setContentsMargins(40, 34, 40, 34)

        card = QFrame()
        card.setObjectName('card')
        # Mismo degradado vertical que el fondo del splash (blanco → gris claro)
        card.setStyleSheet("QFrame#card{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
                           "stop:0 #FFFFFF,stop:1 #E9E9E9);"
                           "border:1px solid #D6D6D6;border-radius:10px;}")
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(28)
        sh.setOffset(0, 6)
        sh.setColor(QColor(0, 0, 0, 45))
        card.setGraphicsEffect(sh)

        c = QVBoxLayout(card)
        c.setContentsMargins(34, 34, 34, 30)
        c.setSpacing(0)

        marca = QLabel()
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marca.setStyleSheet('background:transparent;border:none;')
        ruta_marca = ruta_recurso('marca.png')
        pm = QPixmap(ruta_marca) if os.path.exists(ruta_marca) else QPixmap()
        if not pm.isNull():
            dpr = self.devicePixelRatioF() or 1.0
            pm = pm.scaledToWidth(int(250 * dpr), Qt.TransformationMode.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            marca.setPixmap(pm)
        else:
            marca.setText("ThermoPhase")
            marca.setStyleSheet(f'font-family:"{_F}";font-size:26pt;color:#303030;'
                                'background:transparent;border:none;')
        c.addWidget(marca)
        c.addSpacing(30)

        self.ed_usuario = self._campo(c, "USUARIO")
        self.ed_clave = self._campo(c, "CONTRASEÑA", clave=True)

        fila = QHBoxLayout()
        self.ck_recordar = QCheckBox("Recordarme en este equipo")
        self.ck_recordar.setStyleSheet(
            f'QCheckBox{{font-family:"{_F}";font-size:10pt;color:#555;border:none;background:transparent;}}'
            'QCheckBox::indicator{width:14px;height:14px;border:1px solid #BBB;border-radius:3px;background:#FFF;}'
            f'QCheckBox::indicator:checked{{background:{_NAR};border:1px solid {_NAR};}}')
        fila.addWidget(self.ck_recordar)
        fila.addStretch()
        c.addLayout(fila)
        c.addSpacing(18)

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
        c.addWidget(self.btn_ingresar)

        v.addWidget(card)
        self.ed_usuario.setFocus()

    def _campo(self, lay, titulo, clave=False):
        l = QLabel(titulo)
        l.setStyleSheet(f'font-family:"{_F}";font-size:9pt;color:#7A7A7A;border:none;'
                        'background:transparent;letter-spacing:0.5px;')
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
        lay.addSpacing(4)
        lay.addWidget(e)
        lay.addSpacing(14)
        return e


def pedir_ingreso(parent=None):
    """Muestra el diálogo de ingreso.  Devuelve True si el usuario pulsó
    «Ingresar» y False si cerró la ventana."""
    dlg = DialogoLogin(parent)
    try:
        scr = dlg.screen().availableGeometry()
        dlg.move(scr.x() + (scr.width() - dlg.width())//2,
                 scr.y() + (scr.height() - dlg.height())//2)
    except Exception:
        pass
    return dlg.exec() == QDialog.DialogCode.Accepted
