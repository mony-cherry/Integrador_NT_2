"""Limpia la tabla empresas del proyecto integrador (HU L01 de Kaizen).

Uso:
    python src/limpiar_empresas.py data/crudo/empresas_sucio.csv

Lee el CSV sucio, imprime el diagnóstico, corrige los errores que piden los
criterios, imprime el diagnóstico otra vez y guarda empresas_limpio en los
tres formatos: CSV, Excel y JSON.
"""

import os
import sys

import pandas as pd

# Carpeta y nombres de los archivos limpios (los tres formatos).
CARPETA_SALIDA = os.path.join("data", "limpio")
RUTA_SALIDA = os.path.join(CARPETA_SALIDA, "empresas_limpio.csv")
RUTA_XLSX = os.path.join(CARPETA_SALIDA, "empresas_limpio.xlsx")
RUTA_JSON = os.path.join(CARPETA_SALIDA, "empresas_limpio.json")

# Columnas que debe traer el CSV.
COLUMNAS_ESPERADAS = ["nombre", "sector", "nit", "telefono", "activa", "contacto", "correo"]

# Columnas obligatorias: después de limpiar no puede quedar ningún nulo en ellas.
# "contacto" no está aquí porque se rellena con "Sin contacto".
COLUMNAS_OBLIGATORIAS = ["nombre", "sector", "nit", "activa"]


def leer_datos(ruta):
    """Lee el CSV sucio con pandas. Todo entra como texto para no perder ceros
    iniciales en el NIT ni en el teléfono, y 'activa' llega como "True"/"False"."""
    if not os.path.isfile(ruta):
        sys.exit(f"Error: no existe el archivo '{ruta}'.")
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: faltan las columnas {faltantes} en '{ruta}'.")
    return df


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico: shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print(f"df.shape: {df.shape}")
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\ndf.duplicated().sum(): {df.duplicated().sum()}")


def quitar_duplicados(df):
    """Quita las filas duplicadas exactas."""
    return df.drop_duplicates()


def limpiar_nombre(df):
    """Quita los espacios sobrantes del nombre."""
    df["nombre"] = df["nombre"].str.strip()
    return df


def unificar_sector(df):
    """Unifica el sector: sin espacios sobrantes y con formato Título
    ('LOGISTICA' y ' logistica ' quedan como 'Logistica')."""
    df["sector"] = df["sector"].str.strip().str.title()
    return df


def limpiar_nit(df):
    """Deja el NIT en un solo formato: sin puntos ni guiones."""
    df["nit"] = df["nit"].str.strip().str.replace(r"[.\-]", "", regex=True)
    return df


def limpiar_telefono(df):
    """Deja el teléfono solo con dígitos."""
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    return df


def convertir_activa(df):
    """Convierte 'activa' de texto a booleano. Los valores que no se
    reconocen quedan como nulo (y se tratan más adelante)."""
    df["activa"] = (
        df["activa"].astype(str).str.strip().str.upper()
        .map({"TRUE": True, "SI": True, "1": True,
              "FALSE": False, "NO": False, "0": False})
    )
    return df


def rellenar_contacto(df):
    """Rellena los contactos vacíos con 'Sin contacto'."""
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    return df


def marcar_correos(df):
    """Crea la columna correo_valido: True si el correo contiene '@'."""
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    return df


def quitar_nulos_obligatorios(df):
    """Elimina las filas con nulos en las columnas obligatorias y deja
    'activa' como booleano de verdad (bool, no object)."""
    df = df.dropna(subset=COLUMNAS_OBLIGATORIAS).copy()
    df["activa"] = df["activa"].astype(bool)
    return df


def limpiar(df):
    """Aplica todas las correcciones en orden y devuelve el DataFrame limpio."""
    df = quitar_duplicados(df)
    df = limpiar_nombre(df)
    df = unificar_sector(df)
    df = limpiar_nit(df)
    df = limpiar_telefono(df)
    df = convertir_activa(df)
    df = rellenar_contacto(df)
    df = marcar_correos(df)
    # Al normalizar pueden aparecer duplicados nuevos que antes no eran exactos.
    df = quitar_duplicados(df)
    df = quitar_nulos_obligatorios(df)
    return df


def guardar(df, ruta):
    """Guarda el resultado en los tres formatos (CSV, Excel y JSON),
    creando la carpeta si falta. 'ruta' es la del CSV."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    df.to_excel(RUTA_XLSX, index=False, sheet_name="empresas")
    df.to_json(RUTA_JSON, orient="records", force_ascii=False, indent=2)


def main():
    """Punto de entrada: lee, diagnostica, limpia, diagnostica y guarda."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "crudo", "empresas_sucio.csv")

    df = leer_datos(ruta_entrada)
    filas_antes = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_antes - len(df)} "
          f"(de {filas_antes} quedan {len(df)})")

    guardar(df, RUTA_SALIDA)
    for ruta in (RUTA_SALIDA, RUTA_XLSX, RUTA_JSON):
        print(f"Archivo limpio guardado en: {ruta} -> {df.shape}")


if __name__ == "__main__":
    main()