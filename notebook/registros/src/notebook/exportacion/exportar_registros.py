import os
from notebook.simulacion.simular_registros import generar_registros

CARPETA = os.path.join("data", "crudo")


def exportar(df):
    """Guarda el DataFrame en CSV, Excel y JSON dentro de data/crudo."""
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "registros_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "registros_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "registros_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    exportar(generar_registros())