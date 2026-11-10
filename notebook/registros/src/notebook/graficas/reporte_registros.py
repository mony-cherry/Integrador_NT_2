"""Reporte gráfico de la HU G01 sobre la tabla registros (archivo LIMPIO).

Uso:
    python scripts/reporte_registros.py registros_limpio.csv

Lee registros_limpio.csv, crea tres gráficas con matplotlib, las guarda en
la carpeta reportes/ (dpi=120) e imprime la ruta de cada una y las
conclusiones al final.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

# Ruta por defecto si no se pasa argumento
RUTA_POR_DEFECTO = os.path.join("data", "limpio", "registros_limpio.csv")
CARPETA_SALIDA = "reportes"


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


def guardar_grafica(nombre_archivo):
    """Ajusta el diseño, guarda la figura activa en reportes/ y la cierra."""
    plt.tight_layout()
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1_por_estado(df):
    """Gráfica 1 (barras): cuántas participaciones hay por estado."""
    conteo = df["estado"].value_counts()
    conteo.plot(kind="bar", figsize=(8, 5), color="#4C78A8")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=30, ha="right")
    ruta = guardar_grafica("registros_grafica_1.png")
    return ruta, conteo


def grafica_2_por_mes(df):
    """Gráfica 2 (línea): cuántas participaciones hubo cada mes."""
    por_mes = df.groupby("mes")["id"].count()
    por_mes.plot(kind="line", marker="o", figsize=(8, 5), color="#F58518")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=45, ha="right")
    plt.grid(alpha=0.3)
    ruta = guardar_grafica("registros_grafica_2.png")
    return ruta, por_mes


def grafica_3_top_retos(df):
    """Gráfica 3 (barras horizontales): los 10 retos con más participantes."""
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    top_retos.plot(kind="barh", figsize=(8, 5), color="#54A24B")
    plt.title("Los 10 retos con más participantes")
    plt.xlabel("Número de participantes")
    plt.ylabel("Id del reto")
    plt.gca().invert_yaxis()  # El reto con más participantes queda arriba
    ruta = guardar_grafica("registros_grafica_3.png")
    return ruta, top_retos


def contar_duplicados(df):
    """Cuenta las inscripciones repetidas: mismo usuario en el mismo reto."""
    return int(df.duplicated(subset=["id_usuario", "id_reto"], keep="first").sum())


def escribir_conclusiones(conteo, por_mes, top_retos, duplicados):
    """Arma el texto de las conclusiones a partir de los resultados."""
    lineas = []

    # Reto más popular (si hay empate se avisa)
    maximo = int(top_retos.max())
    lideres = [str(r) for r in top_retos[top_retos == maximo].index]
    if len(lideres) == 1:
        lineas.append(
            f"1. El reto más popular es el {lideres[0]}, con {maximo} participantes."
        )
    else:
        lineas.append(
            f"1. Los retos más populares son {', '.join(lideres)} (empatados), "
            f"con {maximo} participantes cada uno."
        )

    # Mes con más inscripciones
    maximo_mes = int(por_mes.max())
    meses = [str(m) for m in por_mes[por_mes == maximo_mes].index]
    lineas.append(
        f"2. El mes con más inscripciones fue {', '.join(meses)}, "
        f"con {maximo_mes} participaciones."
    )

    # Inscripciones duplicadas y por qué el back responde 409
    lineas.append(
        f"3. Se encontraron {duplicados} inscripciones duplicadas (mismo usuario "
        "en el mismo reto)."
    )
    lineas.append(
        "   El back debe bloquearlas con 409 Conflict: la pareja (id_usuario, "
        "id_reto) tiene que ser única, y un segundo intento choca con una "
        "inscripción que ya existe. Así se evita contar dos veces al mismo "
        "participante en los reportes."
    )

    # Estado más frecuente (apoya la gráfica 1)
    lineas.append(
        f"4. El estado más frecuente es {conteo.idxmax()}, con {int(conteo.max())} "
        f"de {int(conteo.sum())} participaciones."
    )
    return lineas


def main():
    """Lee el archivo, crea las gráficas e imprime rutas y conclusiones."""
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    df = cargar_datos(ruta_csv)

    # La carpeta se crea sola
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    ruta1, conteo = grafica_1_por_estado(df)
    ruta2, por_mes = grafica_2_por_mes(df)
    ruta3, top_retos = grafica_3_top_retos(df)

    print("Gráficas guardadas:")
    for ruta in (ruta1, ruta2, ruta3):
        print(f"  {ruta}")

    print("\nConclusiones:")
    for linea in escribir_conclusiones(conteo, por_mes, top_retos, contar_duplicados(df)):
        print(linea)


if __name__ == "__main__":
    main()