"""Limpia la tabla registros (HU L01) del proyecto integrador.

Uso:
    python scripts/limpiar_registros.py registros_sucio.csv

Lee el CSV sucio, imprime el diagnóstico, corrige los errores que piden los
criterios, imprime el diagnóstico otra vez y guarda el resultado en
data/limpio/registros_limpio.csv.
"""

import sys
from pathlib import Path

import pandas as pd

# Ruta de salida del archivo limpio (según los criterios de la HU L01).
RUTA_SALIDA = Path("data") / "limpio" / "registros_limpio.csv"

# Columnas que no pueden quedar con nulos después de limpiar.
# "observacion" no está aquí porque se rellena con "Sin observacion".
COLUMNAS_OBLIGATORIAS = ["id_usuario", "id_reto", "fecha_registro", "estado"]


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico del DataFrame: shape, info, nulos y duplicados."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def leer_datos(ruta):
    """Lee el CSV sucio con pd.read_csv() y devuelve el DataFrame."""
    return pd.read_csv(ruta)


def quitar_duplicados_exactos(df):
    """Quita las filas que son duplicados exactos de otra fila."""
    return df.drop_duplicates()


def convertir_fecha(df):
    """Convierte fecha_registro a datetime aunque venga en dos formatos.

    Primero se leen las fechas ISO (AAAA-MM-DD), porque con dayfirst=True pandas
    las voltea (2026-03-07 pasaría a ser 2026-07-03). Las demás (DD/MM/AAAA) se
    leen con format="mixed" y dayfirst=True. Lo que no se pueda convertir queda
    como NaT (errors="coerce").
    """
    iso = pd.to_datetime(df["fecha_registro"], format="ISO8601", errors="coerce")
    resto = pd.to_datetime(
        df["fecha_registro"], format="mixed", dayfirst=True, errors="coerce"
    )
    df["fecha_registro"] = iso.fillna(resto)
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios en los bordes, en mayúsculas y con guion bajo.

    Cualquier grupo de espacios dentro del texto se vuelve un solo guion bajo.
    """
    df["estado"] = (
        df["estado"].str.strip().str.upper().str.replace(r"\s+", "_", regex=True)
    )
    return df


def rellenar_observaciones(df):
    """Rellena las observaciones vacías con "Sin observacion"."""
    df["observacion"] = df["observacion"].fillna("Sin observacion")
    return df


def quitar_participaciones_repetidas(df):
    """Detecta e imprime las participaciones repetidas (mismo usuario y reto).

    Deja solo la primera participación de cada par id_usuario + id_reto.
    """
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print("\nFilas con participación repetida (usuario + reto):", len(repetidos))
    return df.drop_duplicates(subset=["id_usuario", "id_reto"], keep="first")


def quitar_nulos_obligatorios(df):
    """Elimina las filas con nulos en las columnas obligatorias.

    Así, después de limpiar no queda ningún nulo en esas columnas.
    """
    antes = len(df)
    df = df.dropna(subset=COLUMNAS_OBLIGATORIAS)
    print("Filas eliminadas por nulos en columnas obligatorias:", antes - len(df))
    return df


def crear_columna_mes(df):
    """Crea la columna mes (año-mes) para agrupar después."""
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    return df


def limpiar(df):
    """Aplica todos los pasos de limpieza en orden y devuelve el DataFrame limpio."""
    df = quitar_duplicados_exactos(df)
    df = convertir_fecha(df)
    df = unificar_estado(df)
    df = rellenar_observaciones(df)
    df = quitar_nulos_obligatorios(df)
    df = quitar_participaciones_repetidas(df)
    df = crear_columna_mes(df)
    return df


def guardar_datos(df, ruta):
    """Guarda el DataFrame limpio en CSV (UTF-8, sin índice), creando la carpeta."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")


def guardar_otros_formatos(df, ruta_csv):
    """Guarda también el DataFrame limpio en Excel y JSON, junto al CSV.

    La columna mes (Period) se pasa a texto para que Excel y JSON la acepten.
    """
    df = df.copy()
    df["mes"] = df["mes"].astype(str)
    ruta_xlsx = ruta_csv.with_suffix(".xlsx")
    ruta_json = ruta_csv.with_suffix(".json")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2,
               date_format="iso")
    print("Archivo limpio guardado en:", ruta_xlsx)
    print("Archivo limpio guardado en:", ruta_json)


def main():
    """Lee el CSV, lo limpia, imprime el antes y el después y guarda el resultado."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/limpiar_registros.py registros_sucio.csv")
        sys.exit(1)

    ruta_entrada = Path(sys.argv[1])
    if not ruta_entrada.exists():
        print(f"No encuentro el archivo: {ruta_entrada}")
        sys.exit(1)

    df = leer_datos(ruta_entrada)
    filas_iniciales = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print("\nFilas eliminadas:", filas_iniciales - len(df))

    guardar_datos(df, RUTA_SALIDA)
    print("Archivo limpio guardado en:", RUTA_SALIDA)
    guardar_otros_formatos(df, RUTA_SALIDA)


if __name__ == "__main__":
    main()