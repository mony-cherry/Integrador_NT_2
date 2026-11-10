"""Flujo completo de la tabla retos: simular -> exportar -> limpiar -> consultar -> graficar.

Ejecutar desde la raíz del proyecto:
    python src/notebook/main.py
"""
import os
import random
import uuid
from datetime import timedelta

import matplotlib

# Backend sin ventana: el script guarda las imágenes y nunca se queda esperando.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from faker import Faker  # noqa: E402

# ----------------------------------------------------------------------------
# 1. SIMULACIÓN (HU F01)
# ----------------------------------------------------------------------------
fake = Faker("es_CO")

# Semilla fija para que los datos sean reproducibles
Faker.seed(42)
random.seed(42)

ESTADOS = ["CERRADO", "EN_CURSO", "PROPUESTO"]
# Listas fijas con varios valores para poder agrupar después
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(4)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]


def generar_datos_limpios(numero_datos=500):
    filas = []
    for _ in range(numero_datos):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return filas


def generar_muestra(datos, porcentaje, excluir=None):
    excluir = set(excluir) if excluir is not None else set()
    disponibles = [indice for indice in datos.index if indice not in excluir]
    cantidad = round(len(datos) * porcentaje)
    return random.sample(disponibles, min(cantidad, len(disponibles)))


def escribir_estado_mal(estado):
    # Variantes de la HU: 'en_curso', 'EN CURSO', ' Cerrado '
    variantes = [
        estado.lower(),
        estado.replace("_", " "),
        f" {estado.capitalize()} ",
    ]
    return random.choice(variantes)


def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # nombre: 10% con espacios sobrantes
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "nombre"] = datos_df.loc[filas, "nombre"].map(
        lambda nombre: f" {nombre} "
    )

    # descripcion: 12% nulos
    filas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas, "descripcion"] = None

    # fecha_inicio: formatos mezclados "2026-03-02" y "02/03/2026"
    fechas_inicio = pd.to_datetime(datos_df["fecha_inicio"])
    latino = fechas_inicio.dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = fechas_inicio.dt.strftime("%Y-%m-%d")
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "fecha_inicio"] = latino.loc[filas]

    # fecha_fin: 8% nulos y 5% anterior a fecha_inicio
    nulos_fin = generar_muestra(datos_df, 0.08)
    datos_df.loc[nulos_fin, "fecha_fin"] = None

    fechas_fin_invalidas = generar_muestra(datos_df, 0.05, excluir=nulos_fin)
    datos_df.loc[fechas_fin_invalidas, "fecha_fin"] = [
        (fechas_inicio.loc[indice] - timedelta(days=random.randint(1, 30))).date()
        for indice in fechas_fin_invalidas
    ]

    # estado: variantes mal escritas
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "estado"] = datos_df.loc[filas, "estado"].map(
        escribir_estado_mal
    )

    # 5% de filas duplicadas tal cual
    cantidad_duplicados = round(len(datos_df) * 0.05)
    if cantidad_duplicados:
        duplicados = datos_df.sample(
            n=cantidad_duplicados,
            random_state=random.randint(0, 999),
        )
        datos_df = pd.concat([datos_df, duplicados], ignore_index=True)

    return datos_df.sample(
        frac=1,
        random_state=random.randint(0, 999),
    ).reset_index(drop=True)


def generar_retos(n=500):
    datos_df = pd.DataFrame(generar_datos_limpios(n))
    df = ensuciar(datos_df)
    return df


# ----------------------------------------------------------------------------
# 2. EXPORTACIÓN (HU X01)
# ----------------------------------------------------------------------------
CARPETA_CRUDO = os.path.join("data", "crudo")
RUTA_SUCIO = os.path.join(CARPETA_CRUDO, "retos_sucio.csv")


def exportar(df):
    """Guarda el DataFrame sucio en CSV, XLSX y JSON dentro de data/crudo."""
    os.makedirs(CARPETA_CRUDO, exist_ok=True)

    ruta_csv = RUTA_SUCIO
    ruta_xlsx = os.path.join(CARPETA_CRUDO, "retos_sucio.xlsx")
    ruta_json = os.path.join(CARPETA_CRUDO, "retos_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="retos")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(ruta, df.shape)


# ----------------------------------------------------------------------------
# 3. LIMPIEZA (HU L01)
# ----------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------
# 4. CONSULTAS (HU Q01)
# ----------------------------------------------------------------------------
CARPETA_CONSULTAS = os.path.dirname(RUTA_SALIDA)


def cargar_retos(ruta=RUTA_SALIDA):
    """Lee retos_limpio.csv y convierte fecha_inicio a fecha."""
    df = pd.read_csv(ruta)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    return df


def guardar(resultado, numero):
    """Guarda el resultado de la consulta N en CSV, XLSX y JSON."""
    os.makedirs(CARPETA_CONSULTAS, exist_ok=True)
    base = os.path.join(CARPETA_CONSULTAS, f"retos_consulta_{numero}")
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
    print(
        "\nListo: guardé retos_consulta_1 ... retos_consulta_5 "
        f"(csv, xlsx, json) en {CARPETA_CONSULTAS}"
    )


# ----------------------------------------------------------------------------
# 5. GRÁFICAS Y CONCLUSIONES (HU G01)
# ----------------------------------------------------------------------------
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


def leer_datos(ruta=RUTA_SALIDA):
    """Lee retos_limpio.csv y deja las fechas y la duración listas para graficar."""
    df = pd.read_csv(ruta)

    faltan = [c for c in ["estado", "fecha_inicio", "fecha_fin"] if c not in df.columns]
    if faltan:
        print(f"Error: al archivo le faltan las columnas {faltan}")
        raise SystemExit(1)

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


# ----------------------------------------------------------------------------
# FLUJO PRINCIPAL
# ----------------------------------------------------------------------------
def main():
    # 1. Simular los datos sucios
    print("== Simulación ==")
    df_sucio = generar_retos()
    print(df_sucio.shape)

    # 2. Exportarlos a CSV, XLSX y JSON
    print("\n== Exportación ==")
    exportar(df_sucio)

    # 3. Leer el CSV sucio, limpiar y guardar el limpio
    print("\n== Limpieza ==")
    df = pd.read_csv(RUTA_SUCIO)
    filas_antes = len(df)
    nulos_antes = df.isna().sum()

    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")
    df = limpiar(df)
    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

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

    obligatorias = [c for c in COLUMNAS_OBLIGATORIAS if c in df.columns]
    assert df[obligatorias].isna().sum().sum() == 0, "Quedan nulos obligatorios"
    assert df.duplicated().sum() == 0, "Quedan duplicados exactos"

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"\nArchivo limpio guardado en: {RUTA_SALIDA}")

    # 4. Responder las cinco consultas con el archivo limpio
    print("\n== Consultas ==")
    consultar()

    # 5. Crear las gráficas y mostrar las conclusiones
    print("\n== Gráficas ==")
    graficar()


if __name__ == "__main__":
    main()