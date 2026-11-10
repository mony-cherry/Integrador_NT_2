#rutina para convertir una lista de diccionarios en multiples funtes de informacion
import json
from pathlib import Path

#1 configuracion (cambiarsegun su tabla)
NOMBRE_ENTIDAD="empresas"
CARPETA_PROYECTO=Path(__file__).resolve().parents[2]
CARPETA_CRUDOS=CARPETA_PROYECTO/"datos"/"crudos"
CARPETA_LIMPIOS=CARPETA_PROYECTO/"datos"/"limpios"
CARPETA_REPORTES=CARPETA_PROYECTO/"datos"/"reportes"

#funciones genericas para elvaorar los archivos

#2.1 CREAR LA CARPETA SI NO EXITE
def preparar_carpeta(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta

#2.2 EXPORTAR A CSV
def exportar_a_csv(datos_df,carpeta, nombre_archivo):
    ruta=preparar_carpeta(carpeta)/f"{nombre_archivo}.csv"
    datos_df.to_csv(ruta, index=False,sep=";",encoding="utf-8-sig")
    return ruta

#2.3 EXPORTAR A JSON
def exportar_a_json(datos_df,carpeta, nombre_archivo):
    ruta=preparar_carpeta(carpeta)/f"{nombre_archivo}.json"
    datos_df.to_json(ruta, orient="records",date_format="iso",indent=2)
    return ruta

#2.4 EXPORTAR A EXCEL
def exportar_a_excel(datos_df,carpeta, nombre_archivo):
    ruta=preparar_carpeta(carpeta)/f"{nombre_archivo}.xlsx"
    datos_df.to_excel(ruta, index=False, engine="openpyxl")
    return ruta

#3 genero los archivos en mi proyecto
def exportar_usuarios_crudos(datos_sucios_df):
    return[
        exportar_a_csv(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudos"),
        exportar_a_json(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudos"),
        exportar_a_excel(datos_sucios_df, CARPETA_CRUDOS, f"{NOMBRE_ENTIDAD}_crudos")
    ]