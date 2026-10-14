'''
Organizacion que registra o propone retos. Crea el script `src/simular_empresas.py`. 
Con la libreria **Faker** genera 300 filas falsas de la tabla `empresas`, 
con las MISMAS columnas que usa Backend II. Despues **ensucia los datos a proposito**:
nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos.
Esos errores son los que vas a arreglar en la etapa de limpieza, 
asi que tienen que quedar bien puestos.
Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)`
para que el resultado sea SIEMPRE el mismo y tu compañero pueda reproducirlo.
'''
import random
import uuid
import pandas as pd
from faker import Faker

#1. configurar el faker a la region que necesito
fake=Faker("es_CO")

#2. Sembrar semillas para tener coherencia en los datos
#simulados
Faker.seed(42)
random.seed(42)

#id (texto (UUID)),
#nombre (texto), 
#nit (texto),
#sector (texto),
#contacto (texto), 
#correo (texto),
#telefono (texto),
#activa (booleano).

SECTORES=["LOGISTICA","TECNOLOGIA","SALUD","ALIMENTOS"]


def generar_muestra(df, porcentaje):
    cantidad=round(len(df)*porcentaje)
    return random.sample(list(df.index),cantidad)


def generar_empresas(n=300):
    filas=[]
    for _ in range(n):
        filas.append({
            "id":str(uuid.uuid4()),
            "nombre":fake.company(),
            "nit":fake.numerify("#########-#"),
            "sector":random.choice(SECTORES),
            "contacto":fake.name(),
            "correo":fake.company_email(),
            "telefono":fake.numerify("3#########"),
            "activa":random.choice([True,False]),
        })

    df=pd.DataFrame(filas)

    filas_elegidas=generar_muestra(df,0.10)
    df.loc[filas_elegidas,"nombre"]=" "+df.loc[filas_elegidas,"nombre"]+" "

    filas_elegidas=generar_muestra(df,0.15)
    df.loc[filas_elegidas,"nombre"]=df.loc[filas_elegidas,"nombre"].str.upper()

    nit_digitos=df["nit"].str.replace("-","",regex=False)
    df["nit"]=nit_digitos
    filas_con_puntos=generar_muestra(df,0.50)
    df.loc[filas_con_puntos,"nit"]=df.loc[filas_con_puntos,"nit"].map(
        lambda nit: f"{nit[:3]}.{nit[3:6]}.{nit[6:9]}-{nit[9]}"
    )

    filas_elegidas=generar_muestra(df,0.10)
    variantes_sector={
        "LOGISTICA":["Logistica","LOGISTICA"," logistica "],
        "TECNOLOGIA":["Tecnologia","TECNOLOGIA"," tecnologia "],
        "SALUD":["Salud","SALUD"," salud "],
        "ALIMENTOS":["Alimentos","ALIMENTOS"," alimentos "],
    }
    df.loc[filas_elegidas,"sector"]=df.loc[filas_elegidas,"sector"].map(
        lambda sector: random.choice(variantes_sector[sector])
    )

    filas_elegidas=generar_muestra(df,0.08)
    df.loc[filas_elegidas,"contacto"]=None

    filas_elegidas=generar_muestra(df,0.06)
    df.loc[filas_elegidas,"correo"]=df.loc[filas_elegidas,"correo"].str.replace("@","",regex=False)

    indices_telefono=list(df.index)
    random.shuffle(indices_telefono)
    formatos_telefono=[
        lambda telefono: telefono,
        lambda telefono: f"{telefono[:3]} {telefono[3:6]} {telefono[6:]}",
        lambda telefono: f"+57 {telefono[:3]}-{telefono[3:6]}-{telefono[6:]}",
    ]
    for posicion, indice in enumerate(indices_telefono):
        formato=formatos_telefono[posicion % len(formatos_telefono)]
        df.loc[indice,"telefono"]=formato(df.loc[indice,"telefono"])

    df["activa"]=df["activa"].astype(object)
    filas_elegidas=generar_muestra(df,0.10)
    df.loc[filas_elegidas,"activa"]=df.loc[filas_elegidas,"activa"].map(
        lambda activa: random.choice(["SI","1"]) if activa else random.choice(["No","0"])
    )

    cantidad_nit_repetidos=round(n*0.03)
    filas_nit_repetido=random.sample(list(df.index),cantidad_nit_repetidos)
    filas_donantes=[]
    for fila in filas_nit_repetido:
        tiene_puntos="." in df.loc[fila,"nit"]
        candidatos=[
            indice for indice in df.index
            if indice not in filas_nit_repetido
            and indice not in filas_donantes
            and ("." in df.loc[indice,"nit"])==tiene_puntos
        ]
        donante=random.choice(candidatos)
        filas_donantes.append(donante)
        df.loc[fila,"nit"]=df.loc[donante,"nit"]

    cantidad_duplicados=round(n*0.05)
    duplicados=df.sample(n=cantidad_duplicados,random_state=random.randint(0,999))
    df=pd.concat([df,duplicados],ignore_index=True)
    return df


if __name__ == "__main__":
    df=generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())