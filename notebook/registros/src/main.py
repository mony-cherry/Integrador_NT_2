import os

from notebook.simulacion.simular_registros import generar_registros
from notebook.exportacion.exportar_registros import exportar
from notebook.consulta.consultas_registros import main as ejecutar_consultas
from notebook.graficas.reporte_registros import main as generar_graficas
from notebook.limpieza.limpiar_registros import (
    RUTA_SALIDA,
    guardar_datos,
    guardar_otros_formatos,
    imprimir_diagnostico,
    leer_datos,
    limpiar,
)

# Ruta del CSV sucio que genera la exportación
RUTA_SUCIO = os.path.join("data", "crudo", "registros_sucio.csv")


def main():
    """Ejecuta el flujo completo del proyecto de registros."""

    # 1. Simulación: genera los datos ya ensuciados
    print("=== 1. Simulación ===")
    df = generar_registros()
    print(df.shape)
    print(df.isna().sum())

    # 2. Exportación: guarda CSV, XLSX y JSON en data/crudo
    print("\n=== 2. Exportación ===")
    exportar(df)

    # 3. Limpieza: lee el CSV sucio, lo limpia y guarda data/limpio
    print("\n=== 3. Limpieza ===")
    df_sucio = leer_datos(RUTA_SUCIO)
    filas_iniciales = len(df_sucio)
    imprimir_diagnostico(df_sucio, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df_limpio = limpiar(df_sucio)

    imprimir_diagnostico(df_limpio, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print("\nFilas eliminadas:", filas_iniciales - len(df_limpio))
    guardar_datos(df_limpio, RUTA_SALIDA)
    print("Archivo limpio guardado en:", RUTA_SALIDA)
    guardar_otros_formatos(df_limpio, RUTA_SALIDA)

    # 4. Consultas: lee data/limpio/registros_limpio.csv y guarda los 5 resultados
    print("\n=== 4. Consultas ===")
    ejecutar_consultas()

    # 5. Gráficas: lee data/limpio/registros_limpio.csv, guarda los PNG en reportes/
    print("\n=== 5. Gráficas ===")
    generar_graficas()


if __name__ == "__main__":
    main()