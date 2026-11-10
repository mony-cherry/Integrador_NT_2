"""Consultas de la HU Q01 sobre la tabla registros (archivo LIMPIO).

Uso:
    python scripts/consultas_registros.py registros_limpio.csv

Resuelve cinco consultas con pandas, cada una en su propia función, imprime
el título y el resultado de cada una (en orden) y guarda el resultado de la
consulta N en registros_consulta_N.csv, en la misma carpeta del archivo leído
(p. ej. data/limpio/registros_consulta_1.csv).
"""

import os
import sys

import pandas as pd

# Ruta por defecto si no se pasa argumento
RUTA_POR_DEFECTO = os.path.join("data", "limpio", "registros_limpio.csv")


def cargar_datos(ruta):
    """Lee el CSV limpio y se asegura de que exista la columna 'mes'."""
    if not os.path.exists(ruta):
        sys.exit(f"Error: no se encontró el archivo '{ruta}'.")
    df = pd.read_csv(ruta)

    # Si el archivo no trae 'mes', se deriva de la primera columna de fecha
    if "mes" not in df.columns:
        columnas_fecha = [c for c in df.columns if "fecha" in c.lower()]
        if not columnas_fecha:
            sys.exit("Error: el archivo no tiene columna 'mes' ni columna de fecha.")
        fechas = pd.to_datetime(df[columnas_fecha[0]], errors="coerce")
        df["mes"] = fechas.dt.to_period("M").astype(str)

    faltan = [c for c in ["id", "id_usuario", "id_reto", "estado"] if c not in df.columns]
    if faltan:
        sys.exit(f"Error: faltan columnas obligatorias: {faltan}")
    return df


def guardar_resultado(resultado, numero, carpeta):
    """Guarda el resultado de la consulta N como registros_consulta_N.csv."""
    ruta = os.path.join(carpeta, f"registros_consulta_{numero}.csv")
    # Series (value_counts / groupby) -> DataFrame para que el CSV tenga encabezados
    if isinstance(resultado, pd.Series):
        resultado = resultado.reset_index()
    resultado.to_csv(ruta, index=False)
    return ruta


def mostrar(titulo, resultado, ruta_guardado):
    """Imprime el título de la consulta, su resultado y dónde se guardó."""
    print(f"\n=== {titulo} ===")
    print(resultado.to_string() if len(resultado) else "(sin resultados)")
    print(f"-> guardado en {ruta_guardado}")


def consulta_1_finalizados(df):
    """Consulta 1: participaciones cuyo estado es FINALIZADO."""
    return df[df["estado"] == "FINALIZADO"]


def consulta_2_repetidos(df):
    """Consulta 2: mismo usuario inscrito más de una vez en el mismo reto."""
    return df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]


def consulta_3_conteo_por_estado(df):
    """Consulta 3: cuántas participaciones hay por cada estado."""
    return df["estado"].value_counts()


def consulta_4_top_retos(df):
    """Consulta 4 (GROUPBY): los 10 retos con más participantes."""
    return df.groupby("id_reto")["id"].count().nlargest(10)


def consulta_5_por_mes(df):
    """Consulta 5 (GROUPBY): cuántas participaciones hubo cada mes."""
    return df.groupby("mes")["id"].count()


def main():
    """Carga el CSV, ejecuta las cinco consultas en orden y guarda los resultados."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    df = cargar_datos(ruta)
    carpeta = os.path.dirname(os.path.abspath(ruta))

    consultas = [
        ("Consulta 1: ¿Qué participaciones ya están finalizadas?", consulta_1_finalizados),
        ("Consulta 2: ¿Qué participaciones están repetidas (mismo usuario en el mismo reto)?", consulta_2_repetidos),
        ("Consulta 3: ¿Cuántas participaciones hay por estado?", consulta_3_conteo_por_estado),
        ("Consulta 4: ¿Cuáles son los 10 retos con más participantes?", consulta_4_top_retos),
        ("Consulta 5: ¿Cuántas participaciones hubo cada mes?", consulta_5_por_mes),
    ]

    for numero, (titulo, funcion) in enumerate(consultas, start=1):
        resultado = funcion(df)
        ruta_csv = guardar_resultado(resultado, numero, carpeta)
        mostrar(titulo, resultado, ruta_csv)


if __name__ == "__main__":
    main()