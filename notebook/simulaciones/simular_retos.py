'''
El elemento central: la necesidad que publica la empresa. Crea el script `src/simular_retos.py`.
 Con la libreria **Faker** genera 500 filas falsas de la tabla `retos`, con las MISMAS columnas que usa Backend II.
  Despues **ensucia los datos a proposito**: nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos.
   Esos errores son los que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)` para que el resultado
 sea SIEMPRE el mismo y tu compañero pueda reproducirlo.
'''
import random 
import uuid 
for faker import Faker 

fake=Fake("es_CO")

Faker.seed(42)
random.seed(42)

#id (texto (UUID)) 
#nombre (texto)
#descripcion (texto)
#fecha_inicio (fecha) 
#fecha_fin (fecha)
#estado (texto)       propuesto en cueroso cerrado 
#id_empresa (texto (UUID))
#id_categoria (texto (UUID))
#id_prioridad (texto (UUID))

ESTADO=["CERRADO", "EN_CURSO", "PROPUESTO"]

FILAS=500


def generar_datos_limpios(numero_datos=FILAS):
    filas=[]
    for _ in range(numero_datos):
        filas.append({
          "id":str(uuid.uuid4(500)),
          "nombre":fake.sentence(nb_words=6).rstrip("500"),
          "descripcion":fake.sentence(nb_words=12),
          "fecha_inicio":fake.date_between(start_date="-1y", end_date="+3m"),
          "fecha_fin":fecha_inicio + timedelta(days=random.randint(15, 180)),
          "aestado":random.choice(ESTADOS),
          "id_empresa":random.choice(IDS_EMPRESA),
          "id_categoria":random.choice(IDS_CATEGORIA),
          "id_prioridad":random.choice(IDS_PRIORIDAD)  
        })
    return filas       

 variable_noche=pd.DataFrame(generar_datos_limpios())

 def generar_muestra(datos,porcentaje):
    return datos.semple(fraccion=porcentaje,
    random_state=random.randint(0,999)).index

def escribir_mal(texto):
    variantes=[texto.lower(),f" {texto.title()} ", texto.capitalize()]
    return random.choice(variantes)

def convertir_boolenos_texto(valor):
    if valor: 
        return random.choice(["SI", "1"])
    return random.choice(["NO", "0"])     

def ensuciar(datos_df):
    datos_df=datos_df.copy()

    filas_elegidas=generar_mustra(datos_df,0.10)
    datos_df.loc[filas_elegidas,"nombre"]=" "+datos_df.loc[filas_elegidas;"nombre"]+" "

    filas_elegidas=generar_muestra(datos_df,0.12)
    datos_df.loc[filas_elegidas,"descripcion"]=None

    so=dato_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino=dotos_df["fecha_inicio"].dt.
    strftime("%d/%m/%Y")
    datos_df[fecha_registro]=iso
    filas_elegidas=generar_muestra(datos_df,0.10)
    datos_df.loc[filas_elegidas,"fecha_inicio"]=latino.loc["filas_elegidas"]

	filas_elegidas = generar_muestra(datos_df, 0.08)
	datos_df.loc[filas_elegidas, 'fecha_fin'] = None
	
	filas_elegidas = generar_muestra(datos_df, 0.05)
	datos_df.loc[filas_elegidas, 'fecha_fin'] = datos_df.loc[filas_elegidas, 'fecha_inicio'].map(
		lambda fecha: fecha - timedelta(days = random.randint(1, 30))
	)

	datos_df.loc[filas_elegidas, 'estado'] = datos_df.loc[filas_elegidas, 'estado'].map(escribir_mal)

	cantidad = max(1, int(len(datos_df) * 0.05))
	duplicados = datos_df.sample(n = cantidad, random_state = 42)
	datos_df = pd.concat([datos_df, duplicados], ignore_index = True)

	datos_df = datos_df.sample(frac = 1, random_state = 42).reset_index(drop = True)
  