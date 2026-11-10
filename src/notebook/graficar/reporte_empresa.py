"""
reporte_empresas.py - HU G01: gráficas y conclusiones de la tabla empresas.

Uso:
    python src/notebook/graficar/reporte_empresa.py data/limpio/empresas_limpio.csv

Lee el CSV limpio, crea tres gráficas con matplotlib en la carpeta reportes/
(barras por sector, torta activas vs inactivas, barras apiladas por sector y
estado) e imprime las conclusiones.
"""

import os
import re
import sys

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Archivo de entrada por defecto (el LIMPIO)
RUTA_ENTRADA = os.path.join("data", "limpio", "empresas_limpio.csv")

# Carpeta de salida y colores (paleta categórica validada: azul y naranja)
CARPETA = "reportes"
DPI = 120
COLOR_ACTIVA = "#2a78d6"
COLOR_INACTIVA = "#eb6834"
FONDO = "#fcfcfb"

# Un correo es válido si tiene texto@dominio.extensión, sin espacios ni doble @
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def leer_datos(ruta):
    """Lee empresas_limpio.csv y deja la columna 'activa' como Activa/Inactiva."""
    if not os.path.exists(ruta):
        print(f"No encuentro el archivo: {ruta}")
        sys.exit(1)
    df = pd.read_csv(ruta)
    for columna in ("sector", "activa"):
        if columna not in df.columns:
            print(f"Falta la columna '{columna}' en {ruta}")
            sys.exit(1)
    df["activa"] = df["activa"].apply(normalizar_activa)
    return df


def normalizar_activa(valor):
    """Convierte True/False, 1/0, si/no o activa/inactiva en 'Activa'/'Inactiva'."""
    texto = str(valor).strip().lower()
    if texto in ("true", "1", "si", "sí", "activa", "activo", "s", "yes"):
        return "Activa"
    return "Inactiva"


def preparar_figura():
    """Crea una figura nueva con el fondo de la paleta."""
    plt.figure(figsize=(8, 5), facecolor=FONDO)
    plt.gca().set_facecolor(FONDO)


def guardar(ruta):
    """Ajusta el diseño, guarda la imagen con dpi=120, la cierra e imprime la ruta."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=DPI)
    plt.close()
    print(f"Gráfica guardada: {ruta}")


def grafica_1_por_sector(df, ruta):
    """Gráfica 1 - Barras: cantidad de empresas por sector."""
    por_sector = df["sector"].value_counts()
    preparar_figura()
    por_sector.plot(kind="bar", color=COLOR_ACTIVA, width=0.6)
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=30, ha="right")
    guardar(ruta)
    return por_sector


def grafica_2_activas(df, ruta):
    """Gráfica 2 - Torta: empresas activas vs inactivas."""
    conteo = df["activa"].value_counts()
    colores = [COLOR_ACTIVA if estado == "Activa" else COLOR_INACTIVA for estado in conteo.index]
    preparar_figura()
    conteo.plot(kind="pie", autopct="%1.1f%%", colors=colores, startangle=90,
                wedgeprops={"edgecolor": FONDO, "linewidth": 2})
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Proporción de empresas", labelpad=45)  # separado para no tapar 'Activa'
    guardar(ruta)
    return conteo


def grafica_3_apiladas(df, ruta):
    """Gráfica 3 - Barras apiladas: activas e inactivas por sector."""
    tabla = pd.crosstab(df["sector"], df["activa"])
    for estado in ("Activa", "Inactiva"):  # por si falta alguno de los dos
        if estado not in tabla.columns:
            tabla[estado] = 0
    tabla = tabla[["Activa", "Inactiva"]]
    preparar_figura()
    tabla.plot(kind="bar", stacked=True, color=[COLOR_ACTIVA, COLOR_INACTIVA],
               width=0.6, ax=plt.gca(), edgecolor=FONDO, linewidth=2)
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=30, ha="right")
    plt.legend(title="Estado")
    guardar(ruta)
    return tabla


def contar_correos_invalidos(df):
    """Cuenta los correos vacíos o que no cumplen el formato texto@dominio.ext."""
    columna = "correo" if "correo" in df.columns else ("email" if "email" in df.columns else None)
    if columna is None:
        return None
    return (~df[columna].fillna("").astype(str).str.fullmatch(PATRON_CORREO)).sum()


def main():
    """Genera y guarda las tres gráficas del reporte."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA
    df = leer_datos(ruta_entrada)
    os.makedirs(CARPETA, exist_ok=True)

    grafica_1_por_sector(df, os.path.join(CARPETA, "empresas_grafica_1.png"))
    grafica_2_activas(df, os.path.join(CARPETA, "empresas_grafica_2.png"))
    grafica_3_apiladas(df, os.path.join(CARPETA, "empresas_grafica_3.png"))
    correos_invalidos = contar_correos_invalidos(df)
    if correos_invalidos is not None:
        print(f"Correos inválidos: {correos_invalidos}")


if __name__ == "__main__":
    main()