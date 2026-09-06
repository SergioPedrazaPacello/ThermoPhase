"""
edicion.py — Copiar / Pegar / Deshacer / Rehacer para ThermoPhase, con el
comportamiento habitual de Windows (Ctrl+C, Ctrl+V, Ctrl+Z, Ctrl+Y).

Reglas:
- Si el foco esta en un campo de texto (QLineEdit, incluido el editor de una
  celda o el de un spinbox), se usa el copiar/pegar/deshacer/rehacer NATIVO
  de ese campo (no se rompe el comportamiento normal).
- Si el foco esta en una TABLA (celdas seleccionadas, sin estar editando):
    * Copiar: copia la seleccion (una o varias celdas) al portapapeles como
      texto separado por tabuladores/saltos (compatible con Excel). Funciona
      tambien en tablas de solo lectura, para copiar resultados.
    * Pegar: escribe desde la celda activa, SOLO en celdas editables.
    * Deshacer/Rehacer: revierten/repiten la ultima escritura del usuario en
      una celda editable (historial global entre tablas).
"""
from PyQt6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QLineEdit, QMenu, QMenuBar
)
from PyQt6.QtCore import Qt


class GestorEdicion:
    def __init__(self):
        self._tablas = []          # tablas registradas (para deshacer/rehacer)
        self._shadow = {}          # id(tabla) -> {(r,c): texto_actual}
        self._undo = []            # [(tabla, r, c, viejo, nuevo), ...]
        self._redo = []
        self._silencio = False
        self._ultimo = None        # ultimo widget relevante enfocado
        app = QApplication.instance()
        if app is not None:
            app.focusChanged.connect(self._on_focus)

    # ── Seguimiento de foco ──────────────────────────────────
    def _on_focus(self, old, new):
        if new is None or isinstance(new, (QMenu, QMenuBar)):
            return
        if isinstance(new, QLineEdit) or self._tabla_desde(new) is not None:
            self._ultimo = new

    @staticmethod
    def _tabla_desde(w):
        while w is not None:
            if isinstance(w, QTableWidget):
                return w
            w = w.parent()
        return None

    def _relevante(self):
        w = QApplication.focusWidget()
        if isinstance(w, QLineEdit) or self._tabla_desde(w) is not None:
            return w
        return self._ultimo

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
            self._undo.append((tabla, r, c, viejo, nuevo))
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

    # ── Copiar ───────────────────────────────────────────────
    def copiar(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.copy()
            return
        tabla = self._tabla_desde(w)
        if tabla is None:
            return
        items = tabla.selectedItems()
        if not items:
            r, c = tabla.currentRow(), tabla.currentColumn()
            it = tabla.item(r, c) if (r >= 0 and c >= 0) else None
            QApplication.clipboard().setText(it.text() if it else '')
            return
        rs = [it.row() for it in items]
        cs = [it.column() for it in items]
        r0, r1, c0, c1 = min(rs), max(rs), min(cs), max(cs)
        sel = {(it.row(), it.column()): it.text() for it in items}
        filas = ['\t'.join(sel.get((r, c), '') for c in range(c0, c1 + 1))
                 for r in range(r0, r1 + 1)]
        QApplication.clipboard().setText('\n'.join(filas))

    # ── Pegar ────────────────────────────────────────────────
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
        if len(filas) > 1 and filas[-1] == '':
            filas = filas[:-1]
        r0 = max(tabla.currentRow(), 0)
        c0 = max(tabla.currentColumn(), 0)
        for dr, fila in enumerate(filas):
            for dc, val in enumerate(fila.split('\t')):
                r, c = r0 + dr, c0 + dc
                if r >= tabla.rowCount() or c >= tabla.columnCount():
                    continue
                it = tabla.item(r, c)
                if it is None:
                    it = QTableWidgetItem()
                    tabla.setItem(r, c, it)
                if not self._editable(it):
                    continue
                it.setText(val)     # dispara itemChanged -> queda en historial

    # ── Deshacer / Rehacer ───────────────────────────────────
    def deshacer(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.undo()
            return
        if not self._undo:
            return
        tabla, r, c, viejo, nuevo = self._undo.pop()
        self._set(tabla, r, c, viejo)
        self._redo.append((tabla, r, c, viejo, nuevo))
        try:
            tabla.setCurrentCell(r, c)
        except Exception:
            pass

    def rehacer(self):
        w = self._relevante()
        if isinstance(w, QLineEdit):
            w.redo()
            return
        if not self._redo:
            return
        tabla, r, c, viejo, nuevo = self._redo.pop()
        self._set(tabla, r, c, nuevo)
        self._undo.append((tabla, r, c, viejo, nuevo))
        try:
            tabla.setCurrentCell(r, c)
        except Exception:
            pass
