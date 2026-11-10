"""Consultas de la HU Q01 sobre la tabla empresas.

Uso:
    python src/consultas_empresas.py data/limpio/empresas_limpio.csv

Lee el archivo LIMPIO, resuelve cinco consultas con pandas (dos usan groupby),
imprime el titulo y el resultado de cada una en orden y guarda cada resultado
como CSV en la misma carpeta del archivo de entrada.
"""

import sys
from pathlib import Path

import pandas as pd

SECTOR_CONSULTA_2 = "Logistica"  # sector que se filtra en la consulta 2
RUTA_ENTRADA = Path("data") / "limpio" / "empresas_limpio.csv"  # por defecto


def cargar_datos(ruta):
    """Lee empresas_limpio.csv y deja la columna 'activa' como booleana."""
    df = pd.read_csv(ruta)
    if df["activa"].dtype == object:
        # Por si el CSV trae "True"/"False" como texto
        df["activa"] = df["activa"].astype(str).str.strip().str.lower() == "true"
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de la consulta N como empresas_consulta_N.csv."""
    # el indice (id, sector...) pasa a ser una columna para no perderlo
    tabla = resultado.reset_index()
    tabla.columns = [str(c) for c in tabla.columns]  # 'activa' trae False/True
    base = carpeta / f"empresas_consulta_{numero}"
    tabla.to_csv(base.with_suffix(".csv"), index=False, encoding="utf-8")
    return base.with_suffix(".csv")


def consulta_1_activas(df):
    """Consulta 1: empresas activas (filtro simple)."""
    print("\nConsulta 1 - ¿Qué empresas están activas?")
    activas = df[df["activa"] == True]  # noqa: E712
    print(activas.to_string(index=False))
    return activas.set_index("id")


def consulta_2_sector(df):
    """Consulta 2: empresas de un sector, ordenadas por nombre."""
    print(f"\nConsulta 2 - ¿Qué empresas son del sector {SECTOR_CONSULTA_2}, ordenadas por nombre?")
    logistica = df[df["sector"] == SECTOR_CONSULTA_2].sort_values("nombre")
    print(logistica.to_string(index=False))
    return logistica.set_index("id")


def consulta_3_conteo(df):
    """Consulta 3: cuántas empresas hay por sector (conteo rápido con value_counts)."""
    print("\nConsulta 3 - ¿Cuántas empresas hay por sector? (conteo rápido)")
    conteo = df["sector"].value_counts()
    conteo.name = "empresas"
    print(conteo.to_string())
    return conteo


def consulta_4_por_sector(df):
    """Consulta 4 (groupby): empresas por sector, de mayor a menor."""
    print("\nConsulta 4 - ¿Cuántas empresas hay por sector, de mayor a menor? (groupby)")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    por_sector.name = "empresas"
    print(por_sector.to_string())
    return por_sector


def consulta_5_activas_inactivas(df):
    """Consulta 5 (groupby doble): activas e inactivas por sector."""
    print("\nConsulta 5 - ¿Cuántas empresas activas e inactivas hay por sector? (groupby doble)")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    return tabla


def main():
    """Ejecuta las cinco consultas en orden y guarda cada resultado."""
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_ENTRADA
    if not ruta.is_file():
        sys.exit(f"Error: no existe el archivo '{ruta}'.")
    df = cargar_datos(ruta)
    print(f"Archivo leído: {ruta} ({len(df)} empresas)")

    consultas = [
        consulta_1_activas,
        consulta_2_sector,
        consulta_3_conteo,
        consulta_4_por_sector,
        consulta_5_activas_inactivas,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        guardar(resultado, ruta.parent, numero)

    print(f"\nListo: se guardaron empresas_consulta_1 a empresas_consulta_5 (.csv) en {ruta.parent}")


if __name__ == "__main__":
    main()