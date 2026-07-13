# ThermoPhase

Aplicación de escritorio (PyQt6) para el cálculo de equilibrio de fases de mezclas
de hidrocarburos mediante las ecuaciones de estado **Peng-Robinson (PR)** y
**Soave-Redlich-Kwong (SRK)**.

Módulos:
- Flash bifásico (equilibrio de fases)
- Envolventes de fase (Ziervogel-Poling y Michelsen), isocalidades y mapa de densidad
- Puntos de saturación (burbuja y rocío)
- Propiedades termodinámicas (entalpía y entropía) — actualmente solo PR
- Guardado/carga de simulaciones (`.tpsim`) y exportación de reportes en PDF

## Ejecutar en local

```bash
pip install -r requirements.txt
python main.py
```

## Archivos del proyecto

| Archivo                    | Rol                                                    |
|----------------------------|--------------------------------------------------------|
| `main.py`                  | **Punto de entrada** — ejecuta este archivo            |
| **Motor termodinámico**    |                                                        |
| `eos.py`                   | Ecuaciones de estado PR y SRK; cálculo flash           |
| `envolvente.py`            | Envolvente de fases por Ziervogel-Poling               |
| `envolvente_michelsen.py`  | Envolvente por continuación pseudo-arclength           |
| `entalpia_entropia.py`     | Entalpía y entropía molar (H, S)                       |
| `mapa_densidad.py`         | Mapa de densidad dentro de la envolvente               |
| **Interfaz gráfica**       |                                                        |
| `ventana_principal.py`     | Ventana, menús, pestañas Equilibrio y Parámetros       |
| `pestana_envolvente.py`    | Pestaña Envolvente de fases                            |
| `pestana_saturacion.py`    | Pestaña Puntos de saturación                           |
| `pestana_propiedades.py`   | Pestaña Propiedades termodinámicas                     |
| `dialogos.py`              | Ventanas emergentes (info / advertencia / error)       |
| **Entrada y salida**       |                                                        |
| `simulacion.py`            | Guardar y cargar archivos `.tpsim`                     |
| `reporte_pdf.py`           | Exportar reporte PDF del cálculo flash                 |
| `asociar_extension.py`     | Asociar `.tpsim` con el programa (Windows Registry)    |
| `rutas.py`                 | Localiza los recursos (funciona también dentro del .exe)|
| **Recursos**               |                                                        |
| `splash.png`               | Pantalla de carga                                      |
| `thermophase.ico`          | Ícono de la aplicación                                 |

## Convenciones internas

| Concepto               | Unidad / valor                          |
|------------------------|-----------------------------------------|
| Temperatura            | grados Rankine (°R)                     |
| Presión                | psia                                    |
| Constante de los gases | `R_GAS = 10.7316` psi·ft³/(lb-mol·°R)   |
| Conversión °R ↔ °F     | `459.67`                                |
| Componentes            | 13 fijos: N₂, CO₂, C1…C9                |
| Orden de las tuplas    | siempre `(P, T)`                        |

## Compilar el ejecutable de Windows

El workflow `.github/workflows/build.yml` compila el `.exe` automáticamente en cada
push a `main` y lo sube como artefacto descargable (pestaña **Actions**). Al crear
un tag `v*` (por ejemplo `v2.0`) publica además una *release* con el ejecutable.
