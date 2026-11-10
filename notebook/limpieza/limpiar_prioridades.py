"""Limpia la tabla prioridades del proyecto integrador (HU L01 de Kaizen).

Lee data/crudo/prioridades_sucio.csv, imprime el diagnostico, corrige los
errores, imprime el diagnostico otra vez y guarda en data/limpio/:
    - prioridades_limpio.csv    (tabla limpia)
    - prioridades_catalogo.csv  (catalogo real: un registro por nombre)

Uso (desde cualquier carpeta):
    python src/notebook/limpieza/limpiar_prioridades.py
"""

import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: micodigo/src/notebook/limpieza/limpiar_prioridades.py
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "crudo" / "prioridades_sucio.csv"
CARPETA_SALIDA = RAIZ / "data" / "limpio"

# Nivel que le corresponde a cada nombre (ya unificado con capitalize()).
# Coincide con NIVELES de simular_prioridades.py.
NIVELES = {
    "Urgente": 5,
    "Alta": 4,
    "Media": 3,
    "Baja": 2,
    "Minima": 1,
}

# Columnas obligatorias (no pueden quedar con nulos).
COLUMNAS_OBLIGATORIAS = ["nombre", "nivel", "dias_max_respuesta"]

# Un plazo mayor a este valor (en dias) se considera absurdo.
MAX_DIAS_VALIDO = 60


def leer_datos(ruta):
    """Lee el CSV sucio con pandas y revisa que esten las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS_OBLIGATORIAS if c not in df.columns]
    if faltan:
        sys.exit(f"ERROR: faltan las columnas {faltan} en {ruta}")
    return df


def diagnostico(df, titulo):
    """Imprime el diagnostico: shape, info, nulos por columna y duplicados."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Elimina las filas que son duplicados exactos."""
    return df.drop_duplicates()


def unificar_nombre(df):
    """Quita espacios sobrantes y unifica mayusculas/minusculas en 'nombre'."""
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    return df


def convertir_nivel(df):
    """Convierte 'nivel' a numero y rellena los vacios usando el nombre."""
    # Se normaliza el texto para que "Tres " tambien cuente; los nulos quedan
    # como "nan" y luego pasan a NaN con to_numeric.
    df["nivel"] = df["nivel"].astype(str).str.strip().str.lower()
    df["nivel"] = df["nivel"].replace(
        {"cinco": 5, "cuatro": 4, "tres": 3, "dos": 2, "uno": 1}
    )
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    # El nivel que quedo vacio se toma del catalogo, segun el nombre.
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES))
    return df


def limpiar_dias(df):
    """Convierte 'dias_max_respuesta' a numero, anula los absurdos y rellena con la mediana."""
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    # Valor absurdo (> 60 dias) pasa a nulo.
    df.loc[df["dias_max_respuesta"] > MAX_DIAS_VALIDO, "dias_max_respuesta"] = None
    # Todos los nulos (originales y absurdos) se rellenan con la mediana.
    mediana = df["dias_max_respuesta"].median()
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(mediana)
    print(f"\nMediana usada para rellenar dias_max_respuesta: {mediana}")
    return df


def ajustar_tipos(df):
    """Pasa 'nivel' y los dias a int cuando ya no hay nulos y son enteros."""
    if df["nivel"].notna().all():
        df["nivel"] = df["nivel"].astype(int)
    dias = df["dias_max_respuesta"]
    if dias.notna().all() and (dias % 1 == 0).all():
        df["dias_max_respuesta"] = dias.astype(int)
    return df


def sacar_catalogo(df):
    """Devuelve el catalogo real: la primera fila de cada nombre."""
    return df.drop_duplicates(subset=["nombre"])


def verificar(df):
    """Comprueba que no quedan nulos en columnas obligatorias ni duplicados exactos."""
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("\n===== VERIFICACION =====")
    print(f"nulos en columnas obligatorias: {nulos}  ->", "OK" if nulos == 0 else "FALLA")
    print(f"duplicados exactos: {duplicados}  ->", "OK" if duplicados == 0 else "FALLA")
    return nulos == 0 and duplicados == 0


def limpiar(ruta_entrada=RUTA_ENTRADA, carpeta_salida=CARPETA_SALIDA):
    """Ejecuta todo el flujo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    ruta_entrada = Path(ruta_entrada)
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    df = leer_datos(ruta_entrada)
    filas_antes = len(df)
    diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados(df)
    df = unificar_nombre(df)
    df = convertir_nivel(df)
    df = limpiar_dias(df)
    df = ajustar_tipos(df)

    diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_antes - len(df)} (de {filas_antes} a {len(df)})")

    catalogo = sacar_catalogo(df)
    if len(catalogo) != 5:
        print(f"AVISO: el catalogo tiene {len(catalogo)} filas y se esperaban 5.")

    ruta_limpio = carpeta_salida / "prioridades_limpio.csv"
    ruta_catalogo = carpeta_salida / "prioridades_catalogo.csv"
    df.to_csv(ruta_limpio, index=False, encoding="utf-8")
    catalogo.to_csv(ruta_catalogo, index=False, encoding="utf-8")
    print(f"\nGuardado: {ruta_limpio}")
    print(f"Guardado: {ruta_catalogo} ({len(catalogo)} filas)")

    if not verificar(df):
        sys.exit(1)
    return df


if __name__ == "__main__":
    limpiar()