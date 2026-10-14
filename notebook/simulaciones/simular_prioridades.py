import random
import uuid

import pandas as pd
from faker import Faker

# 1. Configurar Faker a la region que se necesita.
fake = Faker("es_CO")

# 2. Sembrar semillas: el resultado es SIEMPRE el mismo y el companero lo reproduce.
Faker.seed(42)
random.seed(42)

# 3. Constantes (selectores).
# Solo hay 5 prioridades reales: nombre -> nivel.
# NOTA: ajusta nombres y valores a los que use tu Backend II.
NIVELES = {
    "urgente": 5,
    "alta": 4,
    "media": 3,
    "baja": 2,
    "minima": 1,
}

# nivel -> dias maximos de respuesta (columna extra, solo para el analisis).
DIAS = {
    5: 1,
    4: 2,
    3: 5,
    2: 10,
    1: 15,
}

# Para ensuciar `nivel` con la palabra en vez del numero.
NIVEL_EN_PALABRA = {5: "cinco", 4: "cuatro", 3: "tres", 2: "dos", 1: "uno"}

# 4. Tamano del dataset.
FILAS = 200


# 5. Generar los N datos LIMPIOS.
def generar_datos_limpios(numero_datos=FILAS):
    filas = []
    for _ in range(numero_datos):
        nombre = random.choice(list(NIVELES.keys()))
        nivel = NIVELES[nombre]
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "nivel": nivel,
            "dias_max_respuesta": DIAS[nivel],
        })
    return filas


# ---------------------------------------------------------------------------
# Ensuciar los datos
# ---------------------------------------------------------------------------

# 1. Elegir al azar un porcentaje de filas (sin repetir las ya usadas).
def generar_muestra(datos, porcentaje, excluir=None):
    disponibles = [i for i in datos.index if excluir is None or i not in excluir]
    cantidad = round(len(datos) * porcentaje)
    return random.sample(disponibles, cantidad)


# 2. Escribir mal un texto: 'ALTA', ' alta ' o 'Alta'.
def escribir_mal(texto):
    variantes = [texto.upper(), f" {texto.lower()} ", texto.title()]
    return random.choice(variantes)


# 3. Ensuciar todo el DataFrame.
def ensuciar(datos_df):
    datos_df = datos_df.copy()
    # object para poder mezclar int, str y None en la misma columna
    datos_df["nivel"] = datos_df["nivel"].astype(object)
    datos_df["dias_max_respuesta"] = datos_df["dias_max_respuesta"].astype(object)

    # nombre: variantes de escritura en ~40% de las filas
    filas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas, "nombre"] = datos_df.loc[filas, "nombre"].map(escribir_mal)

    # nivel: 7% None, 20% como texto ('3'), 20% como palabra ('tres')
    nulos = generar_muestra(datos_df, 0.07)
    como_texto = generar_muestra(datos_df, 0.20, excluir=nulos)
    como_palabra = generar_muestra(datos_df, 0.20, excluir=nulos + como_texto)
    datos_df.loc[como_texto, "nivel"] = datos_df.loc[como_texto, "nivel"].map(str)
    datos_df.loc[como_palabra, "nivel"] = datos_df.loc[como_palabra, "nivel"].map(NIVEL_EN_PALABRA)
    datos_df.loc[nulos, "nivel"] = None

    # dias_max_respuesta: 5% None, 3% valor absurdo (999)
    nulos = generar_muestra(datos_df, 0.05)
    absurdos = generar_muestra(datos_df, 0.03, excluir=nulos)
    datos_df.loc[nulos, "dias_max_respuesta"] = None
    datos_df.loc[absurdos, "dias_max_respuesta"] = 999

    # duplicados exactos: 8% de las filas se sobrescriben con copias de otras.
    # Va al final para que la copia sea identica (tal cual) a la fila original.
    # Asi el DataFrame sigue teniendo 200 filas.
    posiciones = list(range(len(datos_df)))
    random.shuffle(posiciones)
    k = round(len(datos_df) * 0.08)
    origen, destino = posiciones[:k], posiciones[k:2 * k]
    datos_df.iloc[destino, :] = datos_df.iloc[origen, :].to_numpy()

    return datos_df


# 4. Funcion principal: importable desde el script de exportacion.
def generar_prioridades(n=200):
    df = pd.DataFrame(generar_datos_limpios(n))
    df = ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_prioridades()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())