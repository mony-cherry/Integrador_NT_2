"""Reporte HU G01: graficas de la tabla prioridades (proyecto integrador).

Lee los resultados de las consultas (data/limpio/prioridades_consulta_N.csv),
crea tres graficas con matplotlib, las guarda en reportes/ (dpi=120) e imprime
la ruta de cada una y las conclusiones.

    Grafica 1 (barras): cuantas filas hay por nivel          <- consulta 4
    Grafica 2 (barras): dias promedio de respuesta por nombre <- consulta 5
    Grafica 3 (torta):  reparto de las prioridades            <- consulta 3
    Conclusiones: usan ademas la consulta 1 (tabla completa por nivel).

Uso (desde cualquier carpeta):
    python src/notebook/graficas/reporte_prioridades.py
"""
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script guarda las imagenes y no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

# Raiz del proyecto: micodigo/src/notebook/graficas/reporte_prioridades.py
RAIZ = Path(__file__).resolve().parents[3]
CARPETA_DATOS = RAIZ / "data" / "limpio"
CARPETA_REPORTES = RAIZ / "reportes"
PRIORIDADES_REALES = 5  # el catalogo real tiene 5 prioridades
NIVEL_MIN, NIVEL_MAX = 1, 5  # rango valido de 'nivel'


def cargar_consulta(numero, columnas):
    """Lee prioridades_consulta_N.csv (termina con un mensaje claro si algo falla)."""
    ruta = CARPETA_DATOS / f"prioridades_consulta_{numero}.csv"
    if not ruta.is_file():
        sys.exit(f"Error: no se encontro el archivo '{ruta}'.")
    df = pd.read_csv(ruta)
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        sys.exit(f"Error: faltan las columnas {faltan} en '{ruta}'.")
    return df


def grafica_1(por_nivel, carpeta):
    """Grafica 1 (barras): cuantas filas hay por nivel. Devuelve la ruta guardada."""
    por_nivel = por_nivel.set_index("nivel")["filas"]
    ax = por_nivel.plot(kind="bar", figsize=(8, 5), color="#4C78A8", rot=0)
    ax.bar_label(ax.containers[0])  # escribe el valor encima de cada barra
    plt.title("Filas por nivel de prioridad")
    plt.xlabel("Nivel")
    plt.ylabel("Cantidad de filas")
    plt.tight_layout()
    ruta = os.path.join(carpeta, "prioridades_grafica_1.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_2(resumen, carpeta):
    """Grafica 2 (barras): dias promedio de respuesta por prioridad. Devuelve la ruta guardada."""
    resumen = resumen.set_index("nombre")
    ax = resumen["mean"].plot(kind="bar", figsize=(8, 5), color="#F58518", rot=0)
    ax.bar_label(ax.containers[0])
    plt.title("Días promedio de respuesta por prioridad")
    plt.xlabel("Prioridad")
    plt.ylabel("Días promedio de respuesta")
    plt.tight_layout()
    ruta = os.path.join(carpeta, "prioridades_grafica_2.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_3(conteo, carpeta):
    """Grafica 3 (torta): reparto de las prioridades. Devuelve la ruta guardada."""
    conteo = conteo.set_index("nombre")["veces"]
    conteo.plot(kind="pie", autopct="%1.1f%%", figsize=(7, 7))
    plt.title("Reparto de las prioridades")
    plt.xlabel("Prioridad")
    plt.ylabel("Porcentaje de filas")
    plt.tight_layout()
    ruta = os.path.join(carpeta, "prioridades_grafica_3.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def conclusion_cuantas(conteo):
    """Conclusion 1: cuantas prioridades REALES quedaron al final (deberian ser 5)."""
    nombres = sorted(conteo["nombre"].dropna().unique())
    n = len(nombres)
    print(f"1. Prioridades reales: quedaron {n} ({', '.join(nombres)}).")
    if n == PRIORIDADES_REALES:
        print(f"   OK: coincide con las {PRIORIDADES_REALES} esperadas; la limpieza unifico las variantes.")
    else:
        print(f"   ATENCION: se esperaban {PRIORIDADES_REALES}. Revisa variantes de escritura "
              "(mayusculas, espacios) o nombres que no pertenecen al catalogo.")


def conclusion_relacion(tabla):
    """Conclusion 2: relacion entre el nivel y los dias maximos de respuesta."""
    print("\n2. Relación entre nivel y días máximos de respuesta:")
    por_nivel = tabla.groupby("nivel")["dias_max_respuesta"].agg(["min", "max"])
    for nivel, fila in por_nivel.iterrows():
        print(f"   - Nivel {nivel:g}: de {fila['min']:g} a {fila['max']:g} días.")
    corr = tabla["nivel"].corr(tabla["dias_max_respuesta"])
    if pd.isna(corr):
        print("   No se puede medir la relación (hay un solo nivel o los días no varían).")
        return
    fuerza = "fuerte" if abs(corr) >= 0.8 else "moderada" if abs(corr) >= 0.4 else "débil"
    sentido = "más" if corr > 0 else "menos"
    print(f"   Relación {fuerza} (correlación = {corr:.2f}): a mayor nivel, {sentido} días de plazo máximo.")
    if (tabla.groupby("nivel")["dias_max_respuesta"].nunique() <= 1).all():
        print("   Cada nivel tiene un único plazo: los días dependen solo del nivel.")


def conclusion_validacion(por_nivel):
    """Conclusion 3: por que el back debe validar que 'nivel' este entre 1 y 5."""
    fuera = int(por_nivel.loc[~por_nivel["nivel"].between(NIVEL_MIN, NIVEL_MAX), "filas"].sum())
    print(f"\n3. Por qué el back debe validar que nivel esté entre {NIVEL_MIN} y {NIVEL_MAX}:")
    print("   - El plazo de respuesta sale del nivel: un nivel inválido deja un plazo erróneo o inexistente.")
    print("   - Las consultas filtran y agrupan por nivel (ej. nivel <= 2): un 0, un 9 o un vacío "
          "falsea los resultados o queda fuera.")
    print("   - El front se puede saltar (otro cliente, Postman): el back es la última barrera "
          "antes de la base de datos y debe rechazar el dato con un error 400/422.")
    print(f"   En este archivo hay {fuera} fila(s) con nivel fuera de {NIVEL_MIN}-{NIVEL_MAX}.")


def reportar():
    """Crea las tres graficas en reportes/ e imprime rutas y conclusiones."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # tildes bien en consolas de Windows

    tabla = cargar_consulta(1, ["nombre", "nivel", "dias_max_respuesta"])
    conteo = cargar_consulta(3, ["nombre", "veces"])
    por_nivel = cargar_consulta(4, ["nivel", "filas"])
    resumen = cargar_consulta(5, ["nombre", "mean"])

    carpeta = str(CARPETA_REPORTES)
    os.makedirs(carpeta, exist_ok=True)  # la carpeta se crea sola

    print("===== GRAFICAS GUARDADAS =====")
    print(grafica_1(por_nivel, carpeta))
    print(grafica_2(resumen, carpeta))
    print(grafica_3(conteo, carpeta))

    print("\n===== CONCLUSIONES =====")
    conclusion_cuantas(conteo)
    conclusion_relacion(tabla)
    conclusion_validacion(por_nivel)


if __name__ == "__main__":
    reportar()