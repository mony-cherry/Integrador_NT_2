"""Reporte gráfico de la tabla retos (HU G01 de Kaizen).

Ejecutar desde la raíz del proyecto:
    python src/notebook/graficar/graficar_retos.py

Lee data/limpio/retos_limpio.csv, crea tres gráficas con matplotlib, las guarda en la
carpeta reportes/ e imprime la ruta de cada una y las conclusiones.
"""

import os
import sys

import matplotlib

# Backend sin ventana: el script guarda las imágenes y nunca se queda esperando.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Archivo limpio que se grafica.
RUTA_LIMPIO = os.path.join("data", "limpio", "retos_limpio.csv")

# Carpeta donde se guardan las gráficas.
CARPETA_REPORTES = "reportes"

# Rutas de las tres gráficas.
RUTA_GRAFICA_1 = os.path.join(CARPETA_REPORTES, "retos_grafica_1.png")
RUTA_GRAFICA_2 = os.path.join(CARPETA_REPORTES, "retos_grafica_2.png")
RUTA_GRAFICA_3 = os.path.join(CARPETA_REPORTES, "retos_grafica_3.png")

# Color único para las tres gráficas (una sola serie en cada una).
COLOR = "#2a6fb0"

# Nombres de los meses para escribir las conclusiones.
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Posibles razones por las que los retos se concentran en un mes.
RAZONES_MES = {
    1: "es el arranque del año, cuando se hacen propósitos y empieza el primer semestre",
    2: "coincide con el inicio de clases y del primer semestre",
    7: "coincide con el inicio del segundo semestre",
    8: "coincide con el inicio del segundo semestre",
    9: "es el regreso a las actividades después de las vacaciones de mitad de año",
    12: "es el cierre del año, cuando se plantean metas para el siguiente",
}

# Razón por defecto cuando el mes no tiene una explicación típica.
RAZON_GENERICA = (
    "puede coincidir con una campaña, un periodo académico o una temporada propia del proyecto"
)


def leer_datos(ruta=RUTA_LIMPIO):
    """Lee retos_limpio.csv y deja las fechas y la duración listas para graficar."""
    df = pd.read_csv(ruta)

    faltan = [c for c in ["estado", "fecha_inicio", "fecha_fin"] if c not in df.columns]
    if faltan:
        print(f"Error: al archivo le faltan las columnas {faltan}")
        sys.exit(1)

    # Las fechas del archivo limpio vienen en formato AAAA-MM-DD.
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")

    # Si el archivo no trae la duración, se calcula con las fechas.
    if "duracion_dias" not in df.columns:
        df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")

    return df


def grafica_estados(df):
    """Gráfica 1 (barras): cantidad de retos por estado."""
    conteo = df["estado"].value_counts()

    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar", color=COLOR, rot=0)
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado del reto")
    plt.ylabel("Cantidad de retos")
    plt.grid(axis="y", alpha=0.3)
    plt.gca().set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_1, dpi=120)
    plt.close()
    print(f"Gráfica 1 guardada en: {RUTA_GRAFICA_1}")


def contar_por_mes(df):
    """Cuenta los retos que empiezan en cada mes, incluyendo los meses con cero."""
    por_mes = df["fecha_inicio"].dt.to_period("M").value_counts().sort_index()
    todos_los_meses = pd.period_range(por_mes.index.min(), por_mes.index.max(), freq="M")
    return por_mes.reindex(todos_los_meses, fill_value=0)


def grafica_meses(df):
    """Gráfica 2 (línea): retos que empiezan cada mes."""
    por_mes = contar_por_mes(df)
    # Para graficar, el eje x usa texto AAAA-MM.
    por_mes.index = por_mes.index.strftime("%Y-%m")

    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o", color=COLOR, rot=45)
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio")
    plt.ylabel("Cantidad de retos")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_2, dpi=120)
    plt.close()
    print(f"Gráfica 2 guardada en: {RUTA_GRAFICA_2}")


def grafica_duracion(df):
    """Gráfica 3 (histograma): cómo se reparte la duración de los retos.

    Solo entran los retos con fechas coherentes (duración mayor o igual a 0);
    los que tienen el fin antes que el inicio se reportan aparte.
    """
    validos = df[df["duracion_dias"] >= 0]

    plt.figure(figsize=(8, 5))
    validos["duracion_dias"].plot(kind="hist", bins=20, color=COLOR, edgecolor="white")
    plt.title("Distribución de la duración de los retos")
    plt.xlabel("Duración (días)")
    plt.ylabel("Cantidad de retos")
    plt.grid(axis="y", alpha=0.3)
    plt.gca().set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICA_3, dpi=120)
    plt.close()
    print(f"Gráfica 3 guardada en: {RUTA_GRAFICA_3}")


def conclusion_mes(df):
    """Devuelve el texto sobre el mes donde se concentran los retos y por qué."""
    por_mes = contar_por_mes(df)
    periodo = por_mes.idxmax()
    cantidad = int(por_mes.max())
    porcentaje = cantidad / por_mes.sum() * 100
    nombre = MESES[periodo.month - 1]
    razon = RAZONES_MES.get(periodo.month, RAZON_GENERICA)
    return (
        f"1) Los retos se concentran en {nombre} de {periodo.year}: {cantidad} de "
        f"{int(por_mes.sum())} ({porcentaje:.1f}%) empiezan ese mes. Puede ser porque {razon}. "
        "Los datos solos no lo confirman; conviene validarlo con el equipo."
    )


def conclusion_duracion(df):
    """Devuelve las líneas con la duración promedio de un reto según su estado."""
    validos = df[df["duracion_dias"] >= 0]
    promedios = validos.groupby("estado")["duracion_dias"].mean().sort_values(ascending=False)
    lineas = ["2) Duración promedio de un reto según su estado (solo fechas coherentes):"]
    for estado, promedio in promedios.items():
        lineas.append(f"   - {estado}: {promedio:.1f} días")
    lineas.append(f"   En general, la mitad de los retos dura {validos['duracion_dias'].median():.0f} días o menos.")
    return "\n".join(lineas)


def conclusion_incoherentes(df):
    """Devuelve el texto con cuántos retos tienen la fecha de fin antes que la de inicio."""
    incoherentes = int((df["duracion_dias"] < 0).sum())
    return (
        f"3) Retos con la fecha de fin antes que la de inicio: {incoherentes} de {len(df)}. "
        "Dato para el back: hay que validar que fecha_fin no sea menor que fecha_inicio al guardar un reto."
    )


def imprimir_conclusiones(df):
    """Imprime las conclusiones que piden los criterios de la HU G01."""
    print("\nCONCLUSIONES")
    print("=" * 60)
    print(conclusion_mes(df))
    print(conclusion_duracion(df))
    print(conclusion_incoherentes(df))


def graficar():
    """Lee el CSV limpio, crea las tres gráficas e imprime las conclusiones."""
    df = leer_datos()

    # La carpeta se crea sola si no existe.
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    grafica_estados(df)
    grafica_meses(df)
    grafica_duracion(df)

    imprimir_conclusiones(df)


if __name__ == "__main__":
    graficar()