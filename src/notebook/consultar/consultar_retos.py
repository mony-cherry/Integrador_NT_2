"""Consultas de la HU Q01 sobre la tabla retos (archivo LIMPIO).

Lee data/limpio/retos_limpio.csv, responde las cinco consultas en orden y
guarda cada resultado como retos_consulta_N en CSV, XLSX y JSON dentro de
data/limpio.

Ejecutar desde la raíz del proyecto:
    python src/notebook/consultar/consultar_retos.py
"""
import os

import pandas as pd

RUTA_LIMPIO = os.path.join("data", "limpio", "retos_limpio.csv")
CARPETA_SALIDA = os.path.join("data", "limpio")


def cargar_retos(ruta=RUTA_LIMPIO):
    """Lee retos_limpio.csv y convierte fecha_inicio a fecha."""
    df = pd.read_csv(ruta)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    return df


def guardar(resultado, numero):
    """Guarda el resultado de la consulta N en CSV, XLSX y JSON."""
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    base = os.path.join(CARPETA_SALIDA, f"retos_consulta_{numero}")
    resultado.to_csv(f"{base}.csv", index=False, encoding="utf-8")
    resultado.to_excel(f"{base}.xlsx", index=False, sheet_name="consulta")
    resultado.to_json(
        f"{base}.json", orient="records", force_ascii=False, indent=2, date_format="iso"
    )


def consulta_1(df):
    """Consulta 1: ¿qué retos están en curso?"""
    print("\n=== Consulta 1: ¿Qué retos están en curso? ===")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(en_curso.to_string(index=False))
    guardar(en_curso, 1)
    return en_curso


def consulta_2(df):
    """Consulta 2: ¿cuáles son los 10 retos más largos?"""
    print("\n=== Consulta 2: ¿Cuáles son los 10 retos más largos? ===")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos.to_string(index=False))
    guardar(largos, 2)
    return largos


def consulta_3(df):
    """Consulta 3: ¿cuántos retos hay por estado?"""
    print("\n=== Consulta 3: ¿Cuántos retos hay por estado? ===")
    conteo = df["estado"].value_counts().rename_axis("estado").reset_index(name="cantidad")
    print(conteo.to_string(index=False))
    guardar(conteo, 3)
    return conteo


def consulta_4(df):
    """Consulta 4 (groupby): duración promedio, mínima y máxima por estado."""
    print("\n=== Consulta 4: ¿Cuál es la duración promedio, mínima y máxima por estado? ===")
    resumen = (
        df.groupby("estado")["duracion_dias"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
        .reset_index()
    )
    print(resumen.to_string(index=False))
    guardar(resumen, 4)
    return resumen


def consulta_5(df):
    """Consulta 5 (groupby): ¿cuántos retos empiezan cada mes?"""
    print("\n=== Consulta 5: ¿Cuántos retos empiezan cada mes? ===")
    por_mes = (
        df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"]
        .count()
        .rename("cantidad")
        .reset_index()
    )
    por_mes["fecha_inicio"] = por_mes["fecha_inicio"].astype(str)
    por_mes = por_mes.rename(columns={"fecha_inicio": "mes"})
    print(por_mes.to_string(index=False))
    guardar(por_mes, 5)
    return por_mes


def consultar():
    """Carga el CSV limpio y ejecuta las cinco consultas en orden."""
    df = cargar_retos()
    for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5):
        consulta(df)
    print(f"\nListo: guardé retos_consulta_1 ... retos_consulta_5 (csv, xlsx, json) en {CARPETA_SALIDA}")


if __name__ == "__main__":
    consultar()