"""
splash.py — Pantalla de carga de ThermoPhase.

La imagen de fondo (splash.png, a 3× de su tamaño en pantalla) contiene el
logotipo, los textos fijos y una envolvente de fases REAL calculada con
ThermoPhase (petróleo volátil, Peng-Robinson, con líneas de calidad 25, 50
y 75 % y el punto crítico).  La barra de progreso y el mensaje de estado se
dibujan aquí y se animan con el avance real del arranque:

    sp = SplashScreen(); sp.show()
    sp.progreso(0.30, "Cargando bibliotecas gráficas…")
    ...
    sp.terminar(minimo=2.0)        # completa la barra y cierra

Este módulo solo depende de PyQt6, para poder mostrarse antes de importar el
resto del programa (numpy, matplotlib y los modelos termodinámicos).
"""
import os
import time

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (QPixmap, QPainter, QColor, QFont, QFontDatabase,
                         QLinearGradient, QPainterPath)
from PyQt6.QtWidgets import QWidget, QApplication

from rutas import ruta_recurso

ANCHO, ALTO = 784, 420                  # tamaño lógico (px)
# geometría de la barra (px lógicos) — coincide con splash.png
BARRA_X, BARRA_Y, BARRA_W, BARRA_H = 54.9, 336.0, 674.2, 4.0
TEXTO_Y = BARRA_Y + 12.0
NARANJA = QColor(210, 60, 15)
NARANJA_CLARO = QColor(236, 95, 36)
GRIS_BARRA = QColor(222, 222, 222)
GRIS_TEXTO = QColor(110, 110, 110)


def _fuente_estado():
    """Inter (incluida con el programa) o, si no carga, Segoe UI/Arial."""
    fam = None
    ttf = ruta_recurso('Inter-Regular.ttf')
    if os.path.exists(ttf):
        fid = QFontDatabase.addApplicationFont(ttf)
        if fid >= 0:
            fams = QFontDatabase.applicationFontFamilies(fid)
            fam = fams[0] if fams else None
    f = QFont(fam or 'Segoe UI')
    f.setPixelSize(12)
    return f


class SplashScreen(QWidget):
    """Pantalla de carga con barra de progreso animada."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen |
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._img = None
        self._valor = 0.0            # valor mostrado (animado)
        self._objetivo = 0.0         # avance real
        self._texto = "Iniciando ThermoPhase…"
        self._t0 = time.time()
        self._fase = 0.0             # brillo que recorre la barra
        self._fuente = _fuente_estado()

        ancho, alto = ANCHO, ALTO
        ruta = ruta_recurso('splash.png')
        if os.path.exists(ruta):
            img = QPixmap(ruta)
            if not img.isNull():
                # se reescala UNA vez, con filtro suave, a los píxeles físicos
                # de la pantalla (escalado de Windows 100 %, 125 %, 150 %…)
                try:
                    dpr = max(float(QApplication.primaryScreen().devicePixelRatio()), 1.0)
                except Exception:
                    dpr = 1.0
                self._img = img.scaled(int(round(ancho*dpr)), int(round(alto*dpr)),
                                       Qt.AspectRatioMode.IgnoreAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self._img.setDevicePixelRatio(dpr)
        self.setFixedSize(ancho, alto)
        g = QApplication.primaryScreen().availableGeometry()
        self.move(g.x() + (g.width() - ancho)//2, g.y() + (g.height() - alto)//2)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)        # ~60 fps

    # ── API ──────────────────────────────────────────────────────────────
    def progreso(self, frac, texto=None, animar_ms=180):
        """Fija el avance real (0–1) y el mensaje.  Anima la barra durante
        `animar_ms` procesando eventos, para que se vea moverse aunque el
        paso siguiente bloquee el hilo principal."""
        self._objetivo = max(self._objetivo, min(1.0, float(frac)))
        if texto:
            self._texto = texto
        fin = time.time() + animar_ms/1000.0
        while time.time() < fin:
            QApplication.processEvents()
            time.sleep(0.008)
        self.repaint()
        QApplication.processEvents()

    def terminar(self, minimo=2.0, texto="Listo"):
        """Completa la barra y espera a que la animación llegue al final y a
        que el splash haya estado visible al menos `minimo` segundos."""
        self._objetivo = 1.0
        self._texto = texto
        while (self._valor < 0.999 or time.time() - self._t0 < minimo):
            QApplication.processEvents()
            time.sleep(0.008)
        self._timer.stop()
        self.close()

    # ── animación ────────────────────────────────────────────────────────
    def _tick(self):
        d = self._objetivo - self._valor
        if d > 0:
            # acercamiento suave con velocidad mínima
            self._valor = min(self._objetivo, self._valor + max(d*0.12, 0.004))
        self._fase = (self._fase + 0.012) % 1.4
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._img is not None:
            p.drawPixmap(0, 0, self._img)
        else:
            p.fillRect(self.rect(), QColor(250, 250, 250))
            f = QFont('Segoe UI'); f.setPixelSize(56); f.setBold(True)
            p.setFont(f); p.setPen(QColor(20, 20, 20))
            p.drawText(QRectF(0, 0, ANCHO, ALTO*0.75),
                       Qt.AlignmentFlag.AlignCenter, "ThermoPhase")
        # barra: fondo
        r = QRectF(BARRA_X, BARRA_Y, BARRA_W, BARRA_H)
        rad = BARRA_H/2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(GRIS_BARRA)
        p.drawRoundedRect(r, rad, rad)
        # barra: avance con degradado
        w = BARRA_W*self._valor
        if w > 0.5:
            rv = QRectF(BARRA_X, BARRA_Y, max(w, BARRA_H), BARRA_H)
            g = QLinearGradient(BARRA_X, 0, BARRA_X + BARRA_W, 0)
            g.setColorAt(0.0, NARANJA)
            g.setColorAt(1.0, NARANJA_CLARO)
            p.setBrush(g)
            p.drawRoundedRect(rv, rad, rad)
            # brillo que recorre la parte llena
            camino = QPainterPath(); camino.addRoundedRect(rv, rad, rad)
            p.save(); p.setClipPath(camino)
            cx = BARRA_X + (self._fase - 0.2)*w
            gb = QLinearGradient(cx - 60, 0, cx + 60, 0)
            gb.setColorAt(0.0, QColor(255, 255, 255, 0))
            gb.setColorAt(0.5, QColor(255, 255, 255, 110))
            gb.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.setBrush(gb)
            p.drawRect(QRectF(cx - 60, BARRA_Y, 120, BARRA_H))
            p.restore()
        # mensaje de estado
        p.setFont(self._fuente)
        p.setPen(GRIS_TEXTO)
        p.drawText(QRectF(BARRA_X, TEXTO_Y, BARRA_W*0.62, 18),
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
                   self._texto)
        p.end()
