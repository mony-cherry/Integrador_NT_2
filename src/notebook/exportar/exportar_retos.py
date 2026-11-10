import os
import sys

# Importa la función sin copiar el código de generación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simular_retos import generar_retos

CARPETA = "data/crudo"


def exportar():
    df = generar_retos()

    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "retos_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "retos_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "retos_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="retos")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(ruta, df.shape)


if __name__ == "__main__":
    exportar()