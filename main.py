'''
Ejecuta todo el proyecto integrador en orden:
simular -> exportar -> limpiar -> consultar -> graficar.

Uso (desde la raiz del proyecto o desde cualquier lugar):
    python main.py              # corre todas las etapas
    python main.py limpiar      # corre solo una etapa
    python main.py exportar limpiar   # corre varias, en el orden dado
'''
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
NOTEBOOK = RAIZ / "src" / "notebook"

# clave -> (nombre de la etapa, script, archivos que debe dejar la etapa)
ETAPAS = {
    "simular": (
        "Simular empresas",
        NOTEBOOK / "simular" / "simular_empresas.py",
        [],
    ),
    "exportar": (
        "Exportar empresas",
        NOTEBOOK / "exportar" / "exportar_empresas.py",
        [
            RAIZ / "data" / "crudo" / "empresas_sucio.csv",
            RAIZ / "data" / "crudo" / "empresas_sucio.xlsx",
            RAIZ / "data" / "crudo" / "empresas_sucio.json",
        ],
    ),
    "limpiar": (
        "Limpiar empresas",
        NOTEBOOK / "limpiar" / "limpiar_empresas.py",
        [
            RAIZ / "data" / "limpio" / "empresas_limpio.csv",
            RAIZ / "data" / "limpio" / "empresas_limpio.xlsx",
            RAIZ / "data" / "limpio" / "empresas_limpio.json",
        ],
    ),
    "consultar": (
        "Consultar empresas",
        NOTEBOOK / "consultar" / "consultas_empresas.py",
        [
            RAIZ / "data" / "limpio" / f"empresas_consulta_{n}.csv"
            for n in range(1, 6)
        ],
    ),
    "graficar": (
        "Graficar empresas",
        NOTEBOOK / "graficar" / "reporte_empresa.py",
        [RAIZ / "reportes" / f"empresas_grafica_{n}.png" for n in range(1, 4)],
    ),
}


def correr_etapa(clave):
    nombre, script, salidas = ETAPAS[clave]

    if not script.exists():
        print(f"[OMITIDA] {nombre}: no existe {script.relative_to(RAIZ)}")
        return True

    print(f"\n=== {nombre} ===")

    # exportar_empresas.py importa simular_empresas.py, que vive en otra carpeta
    entorno = os.environ.copy()
    entorno["PYTHONPATH"] = os.pathsep.join(
        [str(NOTEBOOK / "simular"), entorno.get("PYTHONPATH", "")]
    )

    # cwd=RAIZ para que las rutas relativas (data/crudo, data/limpio) queden en la raiz
    resultado = subprocess.run(
        [sys.executable, str(script)], cwd=RAIZ, env=entorno
    )
    if resultado.returncode != 0:
        print(f"[ERROR] {nombre} fallo (codigo {resultado.returncode})")
        return False

    # comprobar que la etapa dejo los archivos que prometia
    faltantes = [s for s in salidas if not s.exists()]
    if faltantes:
        for s in faltantes:
            print(f"[ERROR] {nombre}: no se genero {s.relative_to(RAIZ)}")
        return False
    for s in salidas:
        print(f"[OK] {s.relative_to(RAIZ)} ({s.stat().st_size} bytes)")
    return True


def main():
    # sin argumentos corre todo; con argumentos, solo las etapas pedidas
    claves = sys.argv[1:] or list(ETAPAS)

    desconocidas = [c for c in claves if c not in ETAPAS]
    if desconocidas:
        sys.exit(
            f"Etapa(s) desconocida(s): {desconocidas}. "
            f"Opciones: {', '.join(ETAPAS)}"
        )

    for clave in claves:
        if not correr_etapa(clave):
            print("\nPipeline detenido por un error.")
            sys.exit(1)
    print("\nPipeline terminado sin errores.")


if __name__ == "__main__":
    main()