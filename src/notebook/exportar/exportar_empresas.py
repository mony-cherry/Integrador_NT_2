'''
Exporta la tabla `empresas` simulada a tres formatos: CSV, Excel y JSON.
Importa `generar_empresas` de simular_empresas.py (no copia el codigo de generacion).
Ejecutar desde la raiz del proyecto: python src/notebook/exportar/exportar_empresas.py
'''
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.notebook.simular.simular_empresas import generar_empresas

CARPETA = "data/crudo"


def exportar():
    # 1. generar los datos sucios con la funcion del otro script
    df = generar_empresas()

    # 2. crear la carpeta si no existe
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = f"{CARPETA}/empresas_sucio.csv"
    ruta_xlsx = f"{CARPETA}/empresas_sucio.xlsx"
    ruta_json = f"{CARPETA}/empresas_sucio.json"

    # 3. exportar a los tres formatos
    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    # 4. mostrar la ruta y el tamaño de cada archivo generado
    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    exportar()