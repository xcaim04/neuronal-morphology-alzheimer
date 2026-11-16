import pandas as pd

from main import limitaciones


def _grupo(archivo):
    return pd.DataFrame({"archivo": [archivo]})


def _manifest(region_alz):
    filas = [
        {"archivo": "sanas/a.swc", "especie": "raton", "cepa": "C57BL/6J", "region": "hipocampo",
         "tipo_celular": "granular", "edad": "6m", "condicion": "control"},
        {"archivo": "enfermas/b.swc", "especie": "raton", "cepa": "APP/PS1", "region": region_alz,
         "tipo_celular": "granular", "edad": "6m", "condicion": "alzheimer"},
    ]
    return pd.DataFrame(filas)


def test_reporta_campos_distintos_salvo_cepa_y_condicion():
    texto = "\n".join(limitaciones(_grupo("a.swc"), _grupo("b.swc"), _manifest("corteza")))
    assert "difieren en region" in texto
    assert "difieren en cepa" not in texto
    assert "difieren en condicion" not in texto


def test_grupos_comparables_salvo_genotipo():
    texto = "\n".join(limitaciones(_grupo("a.swc"), _grupo("b.swc"), _manifest("hipocampo")))
    assert "difieren" not in texto
    assert "coinciden en especie, region, tipo_celular, edad" in texto


def test_sin_manifest():
    texto = "\n".join(limitaciones(_grupo("a.swc"), _grupo("b.swc"), None))
    assert "No hay metadatos de procedencia" in texto
