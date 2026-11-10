"""Limpieza de la tabla retos (HU L01 de Kaizen).

Uso:
    python scripts/limpiar_retos.py retos_sucio.csv

Lee el CSV sucio, imprime el diagnostico, corrige los errores que piden los
criterios, imprime el diagnostico otra vez y guarda el resultado en
data/limpio/retos_limpio.csv.
"""

import os
import sys

import pandas as pd

# Ruta donde se guarda el archivo limpio (segun los criterios de la HU L01).
RUTA_SALIDA = os.path.join("data", "limpio", "retos_limpio.csv")

# Columnas que no pueden quedar con nulos despues de limpiar.
# "descripcion" no va aqui porque se rellena con "Sin descripcion".
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "estado", "fecha_inicio", "fecha_fin"]


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnostico: shape, info, nulos por columna y duplicados."""
    print(f"\n{'=' * 60}\n{titulo}\n{'=' * 60}")
    print(f"df.shape: {df.shape}")
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\ndf.duplicated().sum(): {df.duplicated().sum()}")


def vaciar_textos_en_blanco(df):
    """Quita espacios sobrantes en los textos y vuelve nulos los vacios."""
    for columna in df.columns:
        if pd.api.types.is_string_dtype(df[columna]) or df[columna].dtype == object:
            df[columna] = df[columna].str.strip().replace("", pd.NA)
    return df


def convertir_fecha(serie):
    """Convierte una columna de texto a datetime aunque venga en dos formatos.

    Las fechas ISO (AAAA-MM-DD) se leen tal cual, porque con dayfirst=True
    pandas invertiria dia y mes. El resto (por ejemplo DD/MM/AAAA) se lee con
    format="mixed" y dayfirst=True, como piden los criterios. Lo que no se
    pueda interpretar queda como NaT.
    """
    texto = serie.astype("string").str.strip()
    es_iso = texto.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)
    fechas_iso = pd.to_datetime(texto.where(es_iso), format="ISO8601", errors="coerce")
    fechas_otras = pd.to_datetime(
        texto.where(~es_iso), format="mixed", dayfirst=True, errors="coerce"
    )
    return fechas_iso.fillna(fechas_otras)


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime."""
    for columna in ["fecha_inicio", "fecha_fin"]:
        df[columna] = convertir_fecha(df[columna])
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios sobrantes, en mayusculas y con guion bajo."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def rellenar_descripciones(df):
    """Rellena las descripciones vacias con 'Sin descripcion'."""
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def marcar_fechas_incoherentes(df):
    """Crea duracion_dias y fecha_valida y reporta cuantas fechas son incoherentes.

    Una fecha es incoherente cuando fecha_fin es anterior a fecha_inicio.
    """
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    df["fecha_valida"] = df["duracion_dias"] >= 0
    incoherentes = int((df["duracion_dias"] < 0).sum())
    print(f"\nFechas incoherentes (fin antes que inicio): {incoherentes}")
    return df


def eliminar_nulos_obligatorios(df):
    """Elimina las filas con nulos en columnas obligatorias y reporta cuantas."""
    obligatorias = [c for c in COLUMNAS_OBLIGATORIAS if c in df.columns]
    con_nulos = int(df[obligatorias].isna().any(axis=1).sum())
    print(f"Filas eliminadas por nulos en columnas obligatorias: {con_nulos}")
    df = df.dropna(subset=obligatorias).copy()
    # Sin nulos, la duracion ya se puede guardar como entero.
    df["duracion_dias"] = df["duracion_dias"].astype(int)
    return df


def limpiar(df):
    """Aplica todas las correcciones de la HU L01 y devuelve el DataFrame limpio."""
    df = df.drop_duplicates()  # duplicados exactos
    df = vaciar_textos_en_blanco(df)  # espacios y vacios -> nulos reales
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripciones(df)
    df = marcar_fechas_incoherentes(df)
    df = eliminar_nulos_obligatorios(df)

    # Al unificar el estado pueden aparecer duplicados exactos nuevos.
    antes = len(df)
    df = df.drop_duplicates()
    print(f"Duplicados exactos nuevos tras unificar: {antes - len(df)}")
    return df.reset_index(drop=True)


def main():
    """Lee el CSV sucio, limpia, imprime el diagnostico y guarda el limpio."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/limpiar_retos.py retos_sucio.csv")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])
    filas_antes = len(df)
    nulos_antes = df.isna().sum()

    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")
    df = limpiar(df)
    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

    # Nulos corregidos por columna (solo las columnas que ya existian).
    nulos_despues = df.isna().sum().reindex(nulos_antes.index, fill_value=0)
    print("\nNulos antes / despues / corregidos por columna:")
    print(
        pd.DataFrame(
            {
                "antes": nulos_antes,
                "despues": nulos_despues,
                "corregidos": nulos_antes - nulos_despues,
            }
        )
    )

    print(f"\nFilas antes: {filas_antes} | despues: {len(df)}")
    print(f"Filas eliminadas: {filas_antes - len(df)}")

    # Comprobacion final de los criterios.
    obligatorias = [c for c in COLUMNAS_OBLIGATORIAS if c in df.columns]
    assert df[obligatorias].isna().sum().sum() == 0, "Quedan nulos obligatorios"
    assert df.duplicated().sum() == 0, "Quedan duplicados exactos"

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"\nArchivo limpio guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()