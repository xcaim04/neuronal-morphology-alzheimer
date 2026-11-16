"""Descarga el dataset sana vs Alzheimer desde NeuroMorpho.org y escribe dataset/manifest.csv.

Fuente: archivo "Booker" (PMID 41651661, doi 10.1523/ENEURO.0099-23.2025): neuronas piramidales
de CA1 de raton, APP/PS1 transgenico vs controles C57BL/6J del mismo estudio y protocolo.
Seleccion:
  - solo reconstrucciones "_Merged" (arbol dendritico completo); las "_AP"/"_BAS" son solo
    apical o solo basal y no son comparables morfometricamente.
  - solo edades 6 y 12 meses: a 1 mes el APP/PS1 aun no tiene patologia amiloide.
  - se descartan los SWC que morphio no abre.
Uso (desde la raiz del repo): uv run python scripts/descargar_dataset.py
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request

import morphio  # ya es dependencia del pipeline; valida cada SWC descargado

API = "https://neuromorpho.org/api/neuron/select"
SWC_URL = "https://neuromorpho.org/dableFiles/{arch}/CNG%20version/{name}.CNG.swc"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ARCHIVE = "Booker"
EDADES = {"6.0", "12.0"}  # meses
GRUPOS = {"Control": ("sana", "sanas"), "APP/PS1 transgenic": ("alzheimer", "enfermas")}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")
COLS = ["archivo", "grupo", "neuron_name", "archivo_neuromorpho", "especie", "cepa", "region",
        "tipo_celular", "edad", "condicion", "url"]


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={**HEADERS, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def neuronas():
    d = json.loads(get(API + "?size=500", json.dumps({"archive": [ARCHIVE]}).encode()))
    assert d["page"]["totalPages"] == 1, "paginar: el archivo tiene >500 neuronas"
    return d["_embedded"]["neuronResources"]


def main():
    filas = []
    sel = [n for n in neuronas()
           if n["neuron_name"].lower().endswith("_merged")
           and n["min_age"] in EDADES and n["age_scale"] == "Month"
           and n["species"] == "mouse"
           and len(n["experiment_condition"]) == 1 and n["experiment_condition"][0] in GRUPOS]
    for n in sorted(sel, key=lambda n: n["neuron_name"]):
        grupo, carpeta = GRUPOS[n["experiment_condition"][0]]
        nombre = n["neuron_name"]
        url = SWC_URL.format(arch=n["archive"].lower(), name=urllib.parse.quote(nombre))
        archivo = f"{nombre}.CNG.swc"
        destino = os.path.join(ROOT, carpeta, archivo)
        if not os.path.exists(destino):
            datos = get(url)
            if datos.lstrip()[:1] in (b"<", b"{"):  # pagina de error HTML/JSON en vez de SWC
                print("descartado (no es SWC):", nombre)
                continue
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "wb") as f:
                f.write(datos)
            time.sleep(1)  # ser amable con el servidor
        try:
            morphio.Morphology(destino)
        except Exception as e:  # lo que no abre morphio no lo puede leer el pipeline
            print("descartado (morphio):", nombre, str(e).splitlines()[3:4])
            os.remove(destino)
            continue
        edad = n["min_age"] if n["min_age"] == n["max_age"] else f"{n['min_age']}-{n['max_age']}"
        filas.append({"archivo": f"{carpeta}/{archivo}", "grupo": grupo, "neuron_name": nombre,
                      "archivo_neuromorpho": n["archive"], "especie": n["species"] or "",
                      "cepa": n["strain"] or "", "region": "/".join(n["brain_region"] or []),
                      "tipo_celular": "/".join(n["cell_type"] or []),
                      "edad": f"{edad} {n['age_scale']}", "condicion": "|".join(n["experiment_condition"]),
                      "url": url})
    with open(os.path.join(ROOT, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)
    print({g: sum(r["grupo"] == g for r in filas) for g in ("sana", "alzheimer")})


if __name__ == "__main__":
    main()
