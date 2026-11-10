import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

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


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())