import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

fake = Faker("es_CO")

Faker.seed(42)
random.seed(42)

ESTADOS = ["CERRADO", "EN_CURSO", "PROPUESTO"]
IDS_EMPRESA = [str(uuid.UUID(int=random.getrandbits(128), version=4))]
IDS_CATEGORIA = [str(uuid.UUID(int=random.getrandbits(128), version=4))]
IDS_PRIORIDAD = [str(uuid.UUID(int=random.getrandbits(128), version=4))]

FILAS = 500


def generar_datos_limpios(numero_datos=FILAS):
    filas = []
    for _ in range(numero_datos):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id": str(uuid.UUID(int=random.getrandbits(128), version=4)),
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
    disponibles = [
        indice for indice in datos.index
        if excluir is None or indice not in excluir
    ]
    cantidad = round(len(datos) * porcentaje)
    return random.sample(disponibles, min(cantidad, len(disponibles)))


def escribir_mal(texto):
    variantes = [texto.lower(), f" {texto.title()} ", texto.upper()]
    return random.choice(variantes)


def ensuciar(datos_df):
    datos_df = datos_df.copy()

    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "nombre"] = datos_df.loc[filas, "nombre"].map(
        lambda nombre: f" {nombre} "
    )

    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "nombre"] = datos_df.loc[filas, "nombre"].map(escribir_mal)

    filas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas, "descripcion"] = None

    fechas_inicio = pd.to_datetime(datos_df["fecha_inicio"])
    latino = fechas_inicio.dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = fechas_inicio.dt.strftime("%Y-%m-%d")
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "fecha_inicio"] = latino.loc[filas]

    nulos_fin = generar_muestra(datos_df, 0.08)
    datos_df.loc[nulos_fin, "fecha_fin"] = None

    fechas_fin_invalidas = generar_muestra(
        datos_df, 0.05, excluir=nulos_fin
    )
    datos_df.loc[fechas_fin_invalidas, "fecha_fin"] = [
        fechas_inicio.loc[indice] - timedelta(days=random.randint(1, 30))
        for indice in fechas_fin_invalidas
    ]

    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "estado"] = datos_df.loc[filas, "estado"].map(escribir_mal)

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


def generar_retos(n=FILAS):
    datos_df = pd.DataFrame(generar_datos_limpios(n))
    return ensuciar(datos_df)


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
