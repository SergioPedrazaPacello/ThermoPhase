"""
graficos_menu.py — Menú de clic derecho común a todos los gráficos.

`instalar(canvas)` da al canvas un menú con «Mostrar líneas de cuadrícula»,
«Guardar imagen...» y «Copiar imagen».  Las ventanas que ya tienen su propio
menú agregan solo la opción de cuadrícula con `accion_cuadricula(menu, canvas)`.

La cuadrícula se quita en el momento de dibujar (envoltura de canvas.draw), de
modo que se respeta aunque el código de cada pestaña vuelva a llamar
ax.grid(True, ...) al redibujar.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QApplication, QFileDialog

import idioma as _i18n


def _preparar(canvas):
    if getattr(canvas, '_tp_grid_ok', False):
        return
    canvas._tp_grid_ok = True
    canvas._tp_sin_grilla = False
    original = canvas.draw

    def draw(*a, **k):
        if canvas._tp_sin_grilla:
            for ax in canvas.figure.axes:
                try:
                    if getattr(ax, 'name', '') == '3d':
                        ax.grid(False)
                    else:
                        ax.grid(False, which='both')
                except Exception:
                    pass
        return original(*a, **k)
    canvas.draw = draw


def cuadricula_visible(canvas):
    return not getattr(canvas, '_tp_sin_grilla', False)


def set_cuadricula(canvas, visible):
    _preparar(canvas)
    canvas._tp_sin_grilla = not visible
    if visible:
        for ax in canvas.figure.axes:
            try:
                ax.grid(True)
            except Exception:
                pass
    # Si el dueño sabe redibujar desde cero (con su estilo de cuadrícula), se usa.
    redib = getattr(canvas, '_tp_redibujar', None)
    if visible and callable(redib):
        try:
            redib(); return
        except Exception:
            pass
    canvas.draw_idle()


def accion_cuadricula(menu, canvas):
    """Agrega la opción al menú; devuelve la acción (ya conectada)."""
    _preparar(canvas)
    a = menu.addAction(_i18n.t("Mostrar líneas de cuadrícula"))
    a.setCheckable(True); a.setChecked(cuadricula_visible(canvas))
    a.toggled.connect(lambda v: set_cuadricula(canvas, v))
    return a


def _guardar(canvas):
    ruta, _f = QFileDialog.getSaveFileName(canvas, _i18n.t("Guardar imagen..."),
                                           "grafico.png", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
    if ruta:
        try:
            canvas.figure.savefig(ruta, dpi=200, facecolor=canvas.figure.get_facecolor())
        except Exception:
            pass


def instalar(canvas, redibujar=None):
    """Menú de clic derecho estándar.  `redibujar`: función que vuelve a
    dibujar el gráfico con su estilo (se usa al reactivar la cuadrícula)."""
    _preparar(canvas)
    if redibujar is not None:
        canvas._tp_redibujar = redibujar
    canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def menu(pos):
        m = QMenu(canvas)
        accion_cuadricula(m, canvas)
        m.addSeparator()
        a_g = m.addAction(_i18n.t("Guardar imagen..."))
        a_c = m.addAction(_i18n.t("Copiar imagen"))
        r = m.exec(canvas.mapToGlobal(pos))
        if r is a_g:
            _guardar(canvas)
        elif r is a_c:
            QApplication.clipboard().setPixmap(canvas.grab())
    canvas.customContextMenuRequested.connect(menu)
