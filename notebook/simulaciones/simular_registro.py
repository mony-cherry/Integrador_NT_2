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

#3. Identifico los datos que debo simular
#id (texto (UUID)) 
#fecha_registro (fecha y hora)
#observacion (texto)
#estado (texto)
#id_usuario (texto (UUID))
#id_reto (texto (UUID))


#4. Identifico los datos o el dato que sea un selector
ESTADOS = ["INSCRITO", "EN PROCESO", "FINALIZADO"]
IDS_USUARIO = [str(uuid.uuid4())]
IDS_RETO = [str(uuid.uuid4())]

#5. Defino mi DATASET
FILAS=800

#6. Construyo una funcion para generar los N datos pedidos (LIMPIOS)
def generar_datos_limpios(numero_datos=FILAS):
    filas=[]
    for _ in range(numero_datos):
        
        filas.append({
            "id":str(uuid.uuid4()),
            "fecha_registro":fake.date_time_between(start_date="-2y", end_date="now"),
            "observacion":fake.sentence(nb_words=10),
            "estado":random.choice(ESTADOS),
            "id_usuario":random.choice(IDS_USUARIO),
            "id_reto":random.choice(IDS_RETO)
        })  
    return filas

generar_datos_limpios()
variable_noche=pd.DataFrame(generar_datos_limpios())

#Ensuciar datos

def generar_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje,
        random_state=random.randint(0, 999)).index

def escribir_mal_estado(texto):
    variantes = [texto.lower(), texto.upper(), f" {texto.capitalize()} "]
    return random.choice(variantes)

def ensuciar(datos_df):
    datos_df = datos_df.copy()

    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    datos_df["fecha_registro"] = iso
    filas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas, "fecha_registro"] = latino.loc[filas]

    #observacion 20% none
    filas = generar_muestra(datos_df, 0.20)
    datos_df.loc[filas, "observacion"] = None

    #estado 20% mal escrito
    filas = generar_muestra(datos_df, 0.20)
    datos_df.loc[filas, "estado"] = datos_df.loc[filas, "estado"].map(escribir_mal_estado)

    #5% filas repetidas
    duplicadas = datos_df.sample(frac=0.05, random_state=random.randint(0, 999))
    datos_df = pd.concat([datos_df, duplicadas], ignore_index=True)

    return datos_df