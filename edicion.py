"""
edicion.py — Copiar / Pegar / Cortar / Borrar / Deshacer / Rehacer para
ThermoPhase, con el comportamiento habitual de Windows y Excel (Ctrl+C,
Ctrl+V, Ctrl+X, Supr, Ctrl+Z, Ctrl+Y).

Reglas:
- Si el foco está en un campo de texto (QLineEdit, incluido el editor de una
  celda o el de un spinbox), se usa el comportamiento NATIVO de ese campo.
- Si el foco está en una TABLA (celdas seleccionadas, sin estar editando):
    * Copiar: copia la selección (una o varias celdas, filas visibles) al
      portapapeles como texto separado por tabuladores y saltos de línea,
      compatible con Excel.  Los números se copian con el separador decimal
      del sistema (coma en una configuración regional en español), de modo
      que Excel los reconoce como números.  Funciona también en tablas de
      solo lectura (resultados).
    * Pegar: escribe un bloque copiado de Excel desde la celda superior
      izquierda de la selección, saltando las filas ocultas (componentes
      inactivos) y escribiendo solo en celdas editables.  Si se copió un
      único valor y hay varias celdas seleccionadas, se rellenan todas.
      Los números se normalizan al punto decimal (se acepta punto o coma,
      separador de miles y el signo %).
    * Cortar / Supr: copia y/o borra las celdas editables seleccionadas.
    * Deshacer/Rehacer: revierten/repiten la última acción del usuario sobre
      celdas editables; un pegado o borrado de varias celdas es UNA acción.
- Clic derecho sobre una tabla: menú con las mismas acciones.
"""
import re

from PyQt6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QLineEdit, QMenu, QMenuBar,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QObject, QEvent, QLocale
from PyQt6.QtGui import QKeySequence

from numeros import normalizar_texto

_RE_NUM = re.compile(r'^[-+]?\d+(\.\d+)?([eE][-+]?\d+)?$')


def _t(s):
    try:
        import idioma
        return idioma.t(s)
    except Exception:
        return s


class GestorEdicion(QObject):
    def __init__(self):
        super().__init__()
        self._tablas = []          # tablas registradas (para deshacer/rehacer)
        self._shadow = {}          # id(tabla) -> {(r,c): texto_actual}
        self._undo = []            # [[(tabla, r, c, viejo, nuevo), ...], ...]
        self._redo = []
        self._silencio = False
        self._lote = None          # acumulador de un pegado/borrado múltiple
        self._ultimo = None        # último widget relevante enfocado
        app = QApplication.instance()
        if app is not None:
            app.focusChanged.connect(self._on_focus)
            app.installEventFilter(self)

    # ── Seguimiento de foco ──────────────────────────────────
    def _on_focus(self, old, new):
        if new is None or isinstance(new, (QMenu, QMenuBar)):
            return
        if isinstance(new, QLineEdit):
            self._ultimo = new
            return
        tabla = self._tabla_desde(new)
        if tabla is not None:
            self._ultimo = new
            self.registrar(tabla)

    @staticmethod
    def _tabla_desde(w):
        while w is not None:
            if isinstance(w, QTableWidget):
                return w
            w = w.parent() if hasattr(w, 'parent') else None
        return None

    def _relevante(self):
        w = QApplication.focusWidget()
        if isinstance(w, QLineEdit) or self._tabla_desde(w) is not None:
            return w
        return self._ultimo

    # ── Atajos de teclado y menú contextual sobre tablas ─────
    _SECUENCIAS = (
        (QKeySequence.StandardKey.Copy, 'copiar'),
        (QKeySequence.StandardKey.Paste, 'pegar'),
        (QKeySequence.StandardKey.Cut, 'cortar'),
        (QKeySequence.StandardKey.Undo, 'deshacer'),
        (QKeySequence.StandardKey.Redo, 'rehacer'),
        (QKeySequence.StandardKey.Delete, 'borrar'),
    )

    def _accion_de(self, ev):
        for seq, nombre in self._SECUENCIAS:
            if ev.matches(seq):
                return nombre
        if ev.key() == Qt.Key.Key_Y and ev.modifiers() == Qt.KeyboardModifier.ControlModifier:
            return 'rehacer'
        if ev.key() == Qt.Key.Key_Backspace and ev.modifiers() == Qt.KeyboardModifier.NoModifier:
            return 'borrar'
        return None

    def eventFilter(self, obj, ev):
        try:
            tipo = ev.type()
            if tipo in (QEvent.Type.ShortcutOverride, QEvent.Type.KeyPress) \
                    and isinstance(obj, QTableWidget) \
                    and obj.state() != QAbstractItemView.State.EditingState:
                accion = self._accion_de(ev)
                if accion is not None:
                    if tipo == QEvent.Type.ShortcutOverride:
                        ev.accept()          # la tabla recibe la tecla
                        return False
                    self.registrar(obj)
                    self._ultimo = obj
                    getattr(self, accion)()
                    return True
            elif tipo == QEvent.Type.ContextMenu:
                tabla = self._tabla_desde(obj)
                if tabla is not None and obj is tabla.viewport():
                    self._menu_contextual(tabla, ev.globalPos())
                    return True
        except Exception:
            pass
        return False

    def _menu_contextual(self, tabla, pos):
        self.registrar(tabla)
        self._ultimo = tabla
        tabla.setFocus()
        editable = any(self._editable(it) for it in tabla.selectedItems()) or \
            self._editable(tabla.item(tabla.currentRow(), tabla.currentColumn())
                           if tabla.currentRow() >= 0 else None)
        m = QMenu(tabla)
        for txt, fn, ok in ((_t("Deshacer"), self.deshacer, bool(self._undo)),
                            (_t("Rehacer"), self.rehacer, bool(self._redo)),
                            (None, None, None),
                            (_t("Cortar"), self.cortar, editable),
                            (_t("Copiar"), self.copiar, True),
                            (_t("Pegar"), self.pegar, editable),
                            (_t("Borrar"), self.borrar, editable)):
            if txt is None:
                m.addSeparator(); continue
            a = m.addAction(txt); a.triggered.connect(fn); a.setEnabled(ok)
        m.exec(pos)

    # ── Registro de tablas editables ─────────────────────────
    def registrar(self, tabla):
        if tabla is None or tabla in self._tablas:
            return
        self._tablas.append(tabla)
        sh = {}
        for r in range(tabla.rowCount()):
            for c in range(tabla.columnCount()):
                it = tabla.item(r, c)
                sh[(r, c)] = it.text() if it is not None else ''
        self._shadow[id(tabla)] = sh
        tabla.itemChanged.connect(lambda it, t=tabla: self._on_changed(t, it))
        # El programa a veces reescribe celdas con las señales bloqueadas
        # (normalizar, cargar un fluido...): se resincroniza la celda activa
        # para que el "valor anterior" de una edición sea el que se ve.
        tabla.currentCellChanged.connect(
            lambda r, c, _pr, _pc, t=tabla: self._sync(t, [(r, c)]))
        try:
            tabla.destroyed.connect(lambda *_a, t=tabla: self._olvidar(t))
        except Exception:
            pass

    def _olvidar(self, tabla):
        if tabla in self._tablas:
            self._tablas.remove(tabla)
        self._shadow.pop(id(tabla), None)
        self._undo = [[op for op in l if op[0] is not tabla] for l in self._undo]
        self._redo = [[op for op in l if op[0] is not tabla] for l in self._redo]
        self._undo = [l for l in self._undo if l]
        self._redo = [l for l in self._redo if l]

    def _sync(self, tabla, celdas):
        sh = self._shadow.get(id(tabla))
        if sh is None:
            return
        for r, c in celdas:
            it = tabla.item(r, c) if (r >= 0 and c >= 0) else None
            if it is not None:
                sh[(r, c)] = it.text()

    @staticmethod
    def _editable(item):
        return (item is not None
                and bool(item.flags() & Qt.ItemFlag.ItemIsEditable))

    def _on_changed(self, tabla, item):
        sh = self._shadow.get(id(tabla))
        if sh is None:
            return
        r, c = item.row(), item.column()
        nuevo = item.text()
        if self._silencio:
            sh[(r, c)] = nuevo
            return
        viejo = sh.get((r, c), '')
        if viejo == nuevo:
            return
        if self._editable(item):
            op = (tabla, r, c, viejo, nuevo)
            if self._lote is not None:
                self._lote.append(op)
            else:
                self._undo.append([op])
            self._redo.clear()
        sh[(r, c)] = nuevo

    def _set(self, tabla, r, c, val):
        self._silencio = True
        try:
            it = tabla.item(r, c)
            if it is None:
                it = QTableWidgetItem()
                tabla.setItem(r, c, it)
            it.setText(val)
        finally:
            self._silencio = False
        sh = self._shadow.get(id(tabla))
        if sh is not None:
            sh[(r, c)] = val

    # ── Utilidades de selección ──────────────────────────────
    @staticmethod
    def _filas_visibles(tabla, desde):
        return [r for r in range(desde, tabla.rowCount()) if not tabla.isRowHidden(r)]

    @staticmethod
    def _cols_visibles(tabla, desde):
        return [c for c in range(desde, tabla.columnCount()) if not tabla.isColumnHidden(c)]

    def _seleccion(self, tabla):
        """Celdas seleccionadas (visibles) como {(r, c): item}; si no hay
        selección, la celda activa."""
        sel = {}
        for rg in tabla.selectedRanges():
            for r in range(rg.topRow(), rg.bottomRow() + 1):
                if tabla.isRowHidden(r):
                    continue
                for c in range(rg.leftColumn(), rg.rightColumn() + 1):
                    if tabla.isColumnHidden(c):
                        continue
                    sel[(r, c)] = tabla.item(r, c)
        if not sel:
            r, c = tabla.currentRow(), tabla.currentColumn()
            if r >= 0 and c >= 0:
                sel[(r, c)] = tabla.item(r, c)
        return sel

    # ── Copiar / Cortar / Borrar ─────────────────────────────
    @staticmethod
    def _texto_para_excel(txt):
        t = txt.strip()
        if _RE_NUM.match(t):
            dp = QLocale.system().decimalPoint()
            if dp and dp != '.':
                return t.replace('.', dp)
        return txt

    def copiar(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.copy()
            return
        tabla = self._tabla_desde(w)
        if tabla is None:
            return
        sel = self._seleccion(tabla)
        if not sel:
            return
        filas = sorted({r for r, _ in sel}); cols = sorted({c for _, c in sel})
        lineas = []
        for r in filas:
            vals = []
            for c in cols:
                it = sel.get((r, c), None) if (r, c) in sel else None
                vals.append(self._texto_para_excel(it.text()) if it is not None else '')
            lineas.append('\t'.join(vals))
        QApplication.clipboard().setText('\r\n'.join(lineas))

    def borrar(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.del_() if w.hasSelectedText() else None
            return
        tabla = self._tabla_desde(w)
        if tabla is None:
            return
        self.registrar(tabla)
        sel = self._seleccion(tabla)
        self._sync(tabla, list(sel.keys()))
        self._lote = []
        try:
            for (r, c), it in sel.items():
                if self._editable(it) and it.text() != '':
                    it.setText('')
        finally:
            lote, self._lote = self._lote, None
        if lote:
            self._undo.append(lote); self._redo.clear()

    def cortar(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.cut()
            return
        self.copiar()
        self.borrar()

    # ── Pegar ────────────────────────────────────────────────
    @staticmethod
    def _valor_pegado(val):
        v = val.strip()
        n = normalizar_texto(v)
        try:
            float(n)
            return n
        except ValueError:
            return v

    def pegar(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.paste()
            return
        tabla = self._tabla_desde(w)
        if tabla is None:
            return
        txt = QApplication.clipboard().text()
        if txt == '':
            return
        filas = txt.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        while len(filas) > 1 and filas[-1] == '':
            filas = filas[:-1]
        bloque = [f.split('\t') for f in filas]
        self.registrar(tabla)
        sel = self._seleccion(tabla)
        if not sel:
            return
        self._sync(tabla, [(r, c) for r in range(tabla.rowCount())
                           for c in range(tabla.columnCount())])
        self._lote = []
        try:
            if len(bloque) == 1 and len(bloque[0]) == 1 and len(sel) > 1:
                # un único valor sobre varias celdas → rellenar la selección
                val = self._valor_pegado(bloque[0][0])
                for (r, c), it in sel.items():
                    if self._editable(it):
                        it.setText(val)
            else:
                r0 = min(r for r, _ in sel); c0 = min(c for _, c in sel)
                rows = self._filas_visibles(tabla, r0)
                cols = self._cols_visibles(tabla, c0)
                for dr, fila in enumerate(bloque):
                    if dr >= len(rows):
                        break
                    for dc, val in enumerate(fila):
                        if dc >= len(cols):
                            break
                        r, c = rows[dr], cols[dc]
                        it = tabla.item(r, c)
                        if not self._editable(it):
                            continue
                        it.setText(self._valor_pegado(val))
                tabla.clearSelection()
                tabla.setCurrentCell(r0, c0)
        finally:
            lote, self._lote = self._lote, None
        if lote:
            self._undo.append(lote); self._redo.clear()

    # ── Deshacer / Rehacer ───────────────────────────────────
    def deshacer(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.undo()
            return
        if not self._undo:
            return
        lote = self._undo.pop()
        for tabla, r, c, viejo, nuevo in reversed(lote):
            self._set(tabla, r, c, viejo)
        self._redo.append(lote)
        self._refrescar(lote)

    def rehacer(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.redo()
            return
        if not self._redo:
            return
        lote = self._redo.pop()
        for tabla, r, c, viejo, nuevo in lote:
            self._set(tabla, r, c, nuevo)
        self._undo.append(lote)
        self._refrescar(lote)

    @staticmethod
    def _refrescar(lote):
        """Tras deshacer/rehacer enfoca la primera celda afectada (las tablas
        ya recibieron itemChanged al reescribirse el texto)."""
        tabla, r, c = lote[0][0], lote[0][1], lote[0][2]
        try:
            tabla.setCurrentCell(r, c)
        except Exception:
            pass
