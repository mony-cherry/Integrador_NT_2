"""Consultas HU Q01 sobre la tabla prioridades (proyecto integrador).

Lee data/limpio/prioridades_limpio.csv (el archivo LIMPIO), resuelve cinco
consultas (cada una en su funcion), imprime el titulo y el resultado de cada
una y guarda data/limpio/prioridades_consulta_N.csv.

Uso (desde cualquier carpeta):
    python src/notebook/consulta/consultas_prioridades.py
"""
import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: micodigo/src/notebook/consulta/consultas_prioridades.py
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "limpio" / "prioridades_limpio.csv"
CARPETA_SALIDA = RAIZ / "data" / "limpio"


def cargar_datos(ruta):
    """Lee el CSV limpio y devuelve un DataFrame (falla con mensaje claro si no existe)."""
    if not Path(ruta).is_file():
        sys.exit(f"Error: no se encontro el archivo '{ruta}'.")
    df = pd.read_csv(ruta)
    columnas = {"id", "nombre", "nivel", "dias_max_respuesta"}
    faltan = columnas - set(df.columns)
    if faltan:
        sys.exit(f"Error: faltan las columnas {sorted(faltan)} en '{ruta}'.")
    return df


def mostrar(titulo, resultado, carpeta, numero):
    """Imprime el titulo y el resultado de una consulta y la guarda en prioridades_consulta_N.csv."""
    print(f"\nConsulta {numero}: {titulo}")
    print(resultado.to_string(index=False))
    resultado.to_csv(carpeta / f"prioridades_consulta_{numero}.csv", index=False)


def consulta_1(df):
    """Consulta 1: prioridades ordenadas de la mas urgente (nivel 1) a la menos urgente."""
    ordenadas = df.sort_values("nivel", kind="stable")
    return ordenadas


def consulta_2(df):
    """Consulta 2: solo las prioridades urgentes (nivel 1 y 2)."""
    urgentes = df[df["nivel"] <= 2]
    return urgentes


def consulta_3(df):
    """Consulta 3: cuantas veces aparece cada nombre (permite detectar variantes escritas distinto)."""
    conteo = df["nombre"].value_counts()
    return conteo.rename_axis("nombre").reset_index(name="veces")


def consulta_4(df):
    """Consulta 4 (GROUPBY): cuantas filas hay por nivel."""
    por_nivel = df.groupby("nivel")["id"].count()
    return por_nivel.rename("filas").reset_index()


def consulta_5(df):
    """Consulta 5 (GROUPBY): dias de respuesta minimo, promedio y maximo por prioridad."""
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    return resumen.reset_index()


def consultar(ruta_entrada=RUTA_ENTRADA, carpeta_salida=CARPETA_SALIDA):
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    df = cargar_datos(ruta_entrada)

    consultas = [
        ("Prioridades ordenadas de la mas urgente a la menos urgente", consulta_1),
        ("Solo las prioridades urgentes (nivel 1 y 2)", consulta_2),
        ("Cuantas veces aparece cada nombre (detecta variantes)", consulta_3),
        ("Cuantas filas hay por nivel", consulta_4),
        ("Dias de respuesta minimo, promedio y maximo por prioridad", consulta_5),
    ]
    for numero, (titulo, funcion) in enumerate(consultas, start=1):
        mostrar(titulo, funcion(df), carpeta, numero)


if __name__ == "__main__":
    consultar()