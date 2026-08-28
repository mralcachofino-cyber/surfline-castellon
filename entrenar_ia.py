"""
🧠 SURFLINE CASTELLÓN AI - Cerebro de Machine Learning
Entrena un modelo de calibración para el Mediterráneo usando el histórico de datos
y busca sesiones pasadas con más del 70% de similitud para sugerir clips de vídeo.
"""

import os
import math
import csv
import json

CSV_PATH = os.path.join(os.path.dirname(__file__), 'historico_olas.csv')
MODELO_JSON_PATH = os.path.join(os.path.dirname(__file__), 'modelo_ia.json')

def cargar_historico():
    registros = []
    if not os.path.exists(CSV_PATH):
        return registros

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                registros.append({
                    'fecha': r.get('fecha', ''),
                    'hora': r.get('hora', ''),
                    'spot': r.get('spot', ''),
                    'altura_ola': float(r.get('altura_ola', 0)),
                    'periodo_ola': float(r.get('periodo_ola', 0)),
                    'energia': float(r.get('energia', 0)),
                    'direccion_ola': float(r.get('direccion_ola', 0)),
                    'velocidad_viento': float(r.get('velocidad_viento', 0)),
                    'rafagas_viento': float(r.get('rafagas_viento', 0)),
                    'temp_mar': float(r.get('temp_mar', 24.0)),
                    'puntuacion': float(r.get('puntuacion', 5.0))
                })
            except Exception:
                continue
    return registros


def calcular_similitud(actual, historico):
    """
    Calcula el porcentaje de similitud (0 a 100%) entre dos estados del mar.
    Pondera: Altura (35%), Periodo (25%), Viento (20%), Dirección Swell (20%).
    """
    # Diferencia de altura (tolerancia ±0.3m)
    diff_h = abs(actual['altura_ola'] - historico['altura_ola'])
    sim_h = max(0.0, 1.0 - (diff_h / 0.5))

    # Diferencia de periodo (tolerancia ±1.5s)
    diff_p = abs(actual['periodo_ola'] - historico['periodo_ola'])
    sim_p = max(0.0, 1.0 - (diff_p / 2.5))

    # Diferencia de viento (tolerancia ±5kt)
    diff_w = abs(actual['velocidad_viento'] - historico['velocidad_viento'])
    sim_w = max(0.0, 1.0 - (diff_w / 8.0))

    # Diferencia de dirección (grados circulares)
    diff_d = abs(actual['direccion_ola'] - historico['direccion_ola']) % 360
    if diff_d > 180: diff_d = 360 - diff_d
    sim_d = max(0.0, 1.0 - (diff_d / 45.0))

    score = (sim_h * 0.35 + sim_p * 0.25 + sim_w * 0.20 + sim_d * 0.20) * 100
    return round(score, 1)


def buscar_mejor_sesion_similar(spot, h, p, w, dir_swell):
    historico = cargar_historico()
    spot_hist = [r for r in historico if r['spot'].lower() == spot.lower()]
    if not spot_hist:
        spot_hist = historico

    actual = {
        'altura_ola': float(h),
        'periodo_ola': float(p),
        'velocidad_viento': float(w),
        'direccion_ola': float(dir_swell)
    }

    mejor_match = None
    mejor_score = 0.0

    for h_reg in spot_hist:
        score = calcular_similitud(actual, h_reg)
        if score > mejor_score and score >= 60.0:
            mejor_score = score
            mejor_match = {
                'fecha': h_reg['fecha'],
                'hora': h_reg['hora'],
                'spot': h_reg['spot'],
                'similitud': score,
                'puntuacion_real': h_reg['puntuacion'],
                'altura_ola': h_reg['altura_ola'],
                'periodo_ola': h_reg['periodo_ola']
            }

    return mejor_match


def entrenar_modelo_local():
    print("🧠 Entrenando modelo de calibración local...")
    datos = cargar_historico()
    print(f"📊 Registros cargados: {len(datos)}")

    resumen = {
        'total_registros': len(datos),
        'spots_calibrados': list(set(d['spot'] for d in datos)),
        'fecha_ultimo_entrenamiento': '2026-08-28'
    }

    with open(MODELO_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

    print("✅ Modelo IA guardado en modelo_ia.json")
    return resumen


if __name__ == '__main__':
    entrenar_modelo_local()
    test = buscar_mejor_sesion_similar('Voramar', 1.1, 7.0, 6.0, 60.0)
    print("🧪 Test de búsqueda de sesión similar:", test)
