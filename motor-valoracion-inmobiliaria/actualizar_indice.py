"""Importa niveles de oferta verificados por ciudad/distrito desde un CSV.

CSV esperado: ciudad,distrito,eur_m2,fecha,fuente,url
No mezcla un índice trimestral autonómico con niveles mensuales de distrito.
"""
import argparse
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def update(csv_path):
    rows=list(csv.DictReader(csv_path.open(encoding='utf-8-sig',newline='')))
    if not rows:raise ValueError('CSV vacío')
    required={'ciudad','distrito','eur_m2','fecha','fuente','url'}
    if not required.issubset(rows[0]):raise ValueError(f'Faltan columnas: {required-set(rows[0])}')
    dates={r['fecha'].strip() for r in rows}
    if len(dates)!=1:raise ValueError('Todas las ciudades/distritos deben corresponder a una sola fecha')
    current={'fecha':dates.pop(),'fuente':'Niveles de oferta documentados en indice_fuentes.csv',
             'nota':'Proyección ilustrativa; no validada contra anuncios recientes',
             'ciudades':{}}
    for row in rows:
        city, district = row['ciudad'].strip(),row['distrito'].strip()
        if city not in {'Madrid','Barcelona','Valencia'}:raise ValueError(city)
        if not row['fuente'].strip() or not row['url'].strip():raise ValueError(f'Sin fuente en {city}/{district}')
        value=float(row['eur_m2'])
        if not 300<=value<=50000:raise ValueError(f'€/m² improbable en {city}/{district}: {value}')
        zone=current['ciudades'].setdefault(city,{})
        if district in zone:raise ValueError(f'Zona duplicada: {city}/{district}')
        zone[district]=value
    for city,zone in current['ciudades'].items():
        if '_ciudad' not in zone:
            raise ValueError(f'Falta la fila de la ciudad completa (_ciudad): {city}')
    # Solo incorporar escenarios nuevos; fuente CSV conservada junto a índice.
    (ROOT/'indice.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'indice_fuentes.csv').write_bytes(csv_path.read_bytes())
    print('indice.json e indice_fuentes.csv actualizados; recuerda que sus estimaciones NO están validadas')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path,help='CSV con fuentes y niveles por zona')
    update(parser.parse_args().csv)
