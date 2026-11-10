import os
import sys
from pathlib import Path

# main.py esta en notebook/main.py, dentro de la raiz del repo (Integrador_NT_2/).
CARPETA_NOTEBOOK = Path(__file__).resolve().parent
RAIZ_PROYECTO = CARPETA_NOTEBOOK.parent

# Agrega al path todas las subcarpetas de notebook/ para importar los scripts
# por nombre, sin importar si la carpeta esta en singular o plural.
for carpeta in sorted(CARPETA_NOTEBOOK.iterdir()):
    if carpeta.is_dir() and not carpeta.name.startswith((".", "__")):
        sys.path.insert(0, str(carpeta))

# Todo se ejecuta desde la raiz para que los archivos salgan en Integrador_NT_2/data/.
os.chdir(RAIZ_PROYECTO)

import consultas_prioridades  # noqa: E402
import exportar_prioridades  # noqa: E402
import limpiar_prioridades  # noqa: E402
import reporte_prioridades  # noqa: E402
import simular_prioridades  # noqa: E402


def main():
    # 1. Simulacion: vista previa de los datos sucios (HU F01).
    print("== Simulacion ==")
    df = simular_prioridades.generar_prioridades()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    # 2. Exportacion: CSV, XLSX y JSON en data/crudo (HU X01).
    print("\n== Exportacion ==")
    exportar_prioridades.exportar()

    # 3. Limpieza: data/crudo -> data/limpio (HU L01).
    print("\n== Limpieza ==")
    limpiar_prioridades.limpiar()

    # 4. Consultas: cinco preguntas sobre data/limpio (HU Q01).
    print("\n== Consultas ==")
    consultas_prioridades.consultar()

    # 5. Graficas y conclusiones en reportes/ (HU G01).
    print("\n== Graficas ==")
    reporte_prioridades.reportar()


if __name__ == "__main__":
    main()