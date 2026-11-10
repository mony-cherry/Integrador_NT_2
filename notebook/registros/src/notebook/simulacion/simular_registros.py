import random
import uuid
import pandas as pd
from faker import Faker

# 1. Constantes: los valores que sirven de selector
ESTADOS = ["INSCRITO", "EN PROCESO", "FINALIZADO"]
IDS_USUARIO = [str(uuid.uuid4()) for _ in range(500)]
IDS_RETO = [str(uuid.uuid4()) for _ in range(100)]
FILAS = 800

# 2. Faker en español de Colombia y semillas fijas (datos reproducibles)
fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)


def generar_datos_limpios(n):
    """Genera n filas limpias de la tabla registros."""
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO),
        })
    return pd.DataFrame(filas)


def generar_muestra(datos, porcentaje):
    """Devuelve los índices de una muestra aleatoria del porcentaje indicado."""
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def escribir_mal_estado(texto):
    """Devuelve el estado con una variante mal escrita."""
    variantes = [texto.lower(), texto.upper(), f" {texto.capitalize()} "]
    return random.choice(variantes)


def ensuciar(datos_df):
    """Ensucia el DataFrame limpio según los criterios de la HU F01."""
    datos_df = datos_df.copy()

    # fecha_registro: dos formatos mezclados (40% en formato latino)
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    datos_df["fecha_registro"] = iso
    filas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas, "fecha_registro"] = latino.loc[filas]

    # observacion: 20% nulos
    filas = generar_muestra(datos_df, 0.20)
    datos_df.loc[filas, "observacion"] = None

    # estado: 20% mal escrito
    filas = generar_muestra(datos_df, 0.20)
    datos_df.loc[filas, "estado"] = datos_df.loc[filas, "estado"].map(escribir_mal_estado)

    # 10% con el par id_usuario + id_reto repetido (copiado de otra fila)
    filas = generar_muestra(datos_df, 0.10)
    resto = list(datos_df.index.difference(filas))
    fuentes = random.choices(resto, k=len(filas))
    datos_df.loc[filas, "id_usuario"] = datos_df.loc[fuentes, "id_usuario"].values
    datos_df.loc[filas, "id_reto"] = datos_df.loc[fuentes, "id_reto"].values

    # 5% de filas repetidas tal cual (duplicados exactos)
    duplicadas = datos_df.sample(frac=0.05, random_state=random.randint(0, 999))
    datos_df = pd.concat([datos_df, duplicadas], ignore_index=True)

    return datos_df


def generar_registros(n=FILAS):
    """Genera los registros ya ensuciados y devuelve el DataFrame."""
    df = ensuciar(generar_datos_limpios(n))
    return df


if __name__ == "__main__":
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())