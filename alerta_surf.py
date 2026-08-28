"""
🌊 SURFLINE CASTELLÓN v2.0 AI - Motor de Física y Alertas
Calcula la altura efectiva real de ola en las 11 playas de Castellón,
aplica el efecto sombra del Cabo de Oropesa, evalúa vientos terrales (offshore),
genera preavisos con 2 días de antelación y envía alertas personalizadas por Telegram y WhatsApp.
"""

import math
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# ============================================================
# 📍 BASE DE DATOS GEOMORFOLÓGICA DE SPOTS (11 PLAYAS)
# ============================================================
SPOT_CONFIG = {
    'Planetario':     {'lat': 39.980, 'lon': 0.030, 'azimut': 26,  'thetaCrit': 45, 'sBase': 0.15, 'offshoreMin': 275, 'offshoreMax': 315, 'tipo': 'Principal'},
    'Gurugú':         {'lat': 39.990, 'lon': 0.040, 'azimut': 26,  'thetaCrit': 45, 'sBase': 0.15, 'offshoreMin': 275, 'offshoreMax': 315, 'tipo': 'Principal'},
    'Pirámides':      {'lat': 40.050, 'lon': 0.070, 'azimut': 38,  'thetaCrit': 50, 'sBase': 0.10, 'offshoreMin': 285, 'offshoreMax': 330, 'tipo': 'Principal'},
    'El Palaciet':    {'lat': 40.056, 'lon': 0.076, 'azimut': 45,  'thetaCrit': 55, 'sBase': 0.10, 'offshoreMin': 290, 'offshoreMax': 340, 'tipo': 'Principal'},
    'Voramar':        {'lat': 40.060, 'lon': 0.080, 'azimut': 54,  'thetaCrit': 65, 'sBase': 0.05, 'offshoreMin': 300, 'offshoreMax': 350, 'tipo': 'Principal'},
    'La Renegà':      {'lat': 40.030, 'lon': 0.090, 'azimut': 172, 'thetaCrit': 10, 'sBase': 0.90, 'offshoreMin': 230, 'offshoreMax': 290, 'tipo': 'Secundario'},
    'Morro de Gos':   {'lat': 40.098, 'lon': 0.147, 'azimut': 60,  'thetaCrit': 65, 'sBase': 0.05, 'offshoreMin': 300, 'offshoreMax': 350, 'tipo': 'Principal'},
    'Burriana':       {'lat': 39.880, 'lon':-0.050, 'azimut': 26,  'thetaCrit': 45, 'sBase': 0.20, 'offshoreMin': 275, 'offshoreMax': 315, 'tipo': 'Secundario'},
    'Nules':          {'lat': 39.850, 'lon': 0.080, 'azimut': 26,  'thetaCrit': 40, 'sBase': 0.25, 'offshoreMin': 275, 'offshoreMax': 315, 'tipo': 'Secundario'},
    'Almenara':       {'lat': 39.750, 'lon': 0.050, 'azimut': 26,  'thetaCrit': 35, 'sBase': 0.30, 'offshoreMin': 275, 'offshoreMax': 315, 'tipo': 'Secundario'},
    'Peñíscola Norte':{'lat': 40.370, 'lon': 0.400, 'azimut': 10,  'thetaCrit': 10, 'sBase': 0.80, 'offshoreMin': 260, 'offshoreMax': 300, 'tipo': 'Principal'},
    'Vinaròs':        {'lat': 40.470, 'lon': 0.480, 'azimut': 10,  'thetaCrit': 10, 'sBase': 0.85, 'offshoreMin': 260, 'offshoreMax': 300, 'tipo': 'Secundario'}
}

# ============================================================
# 🔐 CONFIGURACIÓN Y CREDENCIALES (Variables de Entorno o Fallback)
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8650554341:AAF2DNZZcI5MkK2GDgrqC6hrAh6zhL1lFO4')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID', '-1003885396809')
ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '+34687688854')
ADMIN_CALLMEBOT_KEY = os.environ.get('ADMIN_CALLMEBOT_KEY', '7360308')

# Lista de surfistas suscritos (se sincroniza con Supabase / configuración local)
USUARIOS_DEFECTO = [
    {
        'nombre': 'Jordi (Admin)',
        'telefono': '+34687688854',
        'callmebot_key': ADMIN_CALLMEBOT_KEY,
        'telegram_id': TELEGRAM_CHANNEL_ID,
        'playas': ['Voramar', 'Planetario', 'El Palaciet', 'Gurugú', 'Peñíscola Norte'],
        'preaviso_2_dias': True,
        'activo': True
    }
]

# ============================================================
# 🌊 MOTOR DE FÍSICA COSTERA DE CASTELLÓN
# ============================================================
def calcular_fisica(spot_nombre, h, periodo, dir_swell):
    """
    Calcula la altura efectiva de ola en la orilla aplicando:
    1. Sombra logística del Cabo de Oropesa.
    2. Modulador Sommerfeld (refracción de periodos largos para doblar el cabo).
    3. Exposición coseno con la perpendicular de la playa.
    """
    h = float(h or 0)
    periodo = float(periodo or 0)
    dir_swell = float(dir_swell or 0)
    if h <= 0:
        return 0.0

    cfg = SPOT_CONFIG.get(spot_nombre, SPOT_CONFIG['Planetario'])

    # 1. Sigmoide logística de bloqueo geográfico (Cabo Oropesa)
    k = 0.15
    sf = cfg['sBase'] + (1.0 - cfg['sBase']) / (1.0 + math.exp(-k * (dir_swell - cfg['thetaCrit'])))

    # 2. Modulador Sommerfeld de periodo (ondas largas refractan más)
    amplificador = 1.0
    if dir_swell < 75:
        ganancia = (periodo / 4.0) ** 2
        ganancia = min(max(ganancia, 1.0), 2.5)
        factor_sombra = 1.0 - sf
        amplificador = 1.0 + ((ganancia - 1.0) * factor_sombra)

    # 3. Exposición Coseno
    normal_costa = cfg['azimut'] + 90
    exposicion = abs(math.cos(math.radians(dir_swell - normal_costa)))
    exposicion = max(exposicion, 0.05)

    heff = h * sf * amplificador * exposicion
    return round(heff, 2)


def calcular_calidad(h, p, ws, wd, spot_nombre, presion=1013, visib=24000):
    """
    Calcula la calidad de 0 a 5 estrellas para el Mediterráneo.
    """
    h = float(h or 0)
    p = float(p or 0)
    ws = float(ws or 0) # nudos
    wd = float(wd or 0) # grados

    if h < 0.20:
        return 0
    if h < 0.35:
        return 1

    s = 2.0
    if h >= 0.50: s += 1.0
    if h >= 0.90: s += 1.0

    if p >= 5.0: s += 0.5
    if p >= 7.0: s += 0.5

    energia = h * h * p
    if energia >= 4.0: s += 0.5
    if energia >= 12.0: s += 0.5

    # Viento Offshore específico por playa
    cfg = SPOT_CONFIG.get(spot_nombre, SPOT_CONFIG['Planetario'])
    if cfg['offshoreMin'] < cfg['offshoreMax']:
        is_offshore = (wd >= cfg['offshoreMin'] and wd <= cfg['offshoreMax'])
    else:
        is_offshore = (wd >= cfg['offshoreMin'] or wd <= cfg['offshoreMax'])

    if is_offshore and ws < 15:
        s += 1.0
        if ws < 8: s += 0.5  # Glassy bonus
    elif not is_offshore and ws > 18:
        s -= 1.0
        if ws > 28: s -= 1.0

    if presion < 1008: s += 0.5
    if visib < 2000: s -= 0.5

    return min(max(int(round(s)), 0), 5)


def escala_humana(h):
    """Convierte altura en metros a escala humana surfista."""
    if h < 0.35: return "Plato (<30cm)"
    if h < 0.55: return "Rodilla (Knee high)"
    if h < 0.85: return "Cintura (Waist high)"
    if h < 1.25: return "Pecho a Hombro (Chest high)"
    if h < 1.75: return "Cabeza (Head high)"
    return "Por encima de la cabeza (Overhead 🤙)"


def badge_calidad(estrellas):
    """Devuelve el badge visual de Surfline."""
    if estrellas >= 5: return "🟣 EPIC", "⭐⭐⭐⭐⭐"
    if estrellas == 4: return "🟢 GOOD", "⭐⭐⭐⭐"
    if estrellas == 3: return "🟡 FAIR TO GOOD", "⭐⭐⭐"
    if estrellas == 2: return "🟠 POOR TO FAIR", "⭐⭐"
    return "⚪ FLAT", "⭐"


# ============================================================
# 🛰️ CONSULTA A OPEN-METEO (4 DÍAS DE PREVISIÓN)
# ============================================================
def fetch_open_meteo(lat, lon):
    try:
        marine_url = (
            f"https://marine-api.open-meteo.com/v1/marine?"
            f"latitude={lat}&longitude={lon}&hourly=wave_height,wave_period,wave_direction,swell_wave_height,swell_wave_period,swell_wave_direction,sea_surface_temperature"
            f"&timezone=Europe/Madrid&forecast_days=4"
        )
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=wind_speed_10m,wind_gusts_10m,wind_direction_10m,pressure_msl,visibility"
            f"&timezone=Europe/Madrid&forecast_days=4"
        )

        req_m = urllib.request.Request(marine_url, headers={'User-Agent': 'SurflineCastellon/2.0'})
        req_w = urllib.request.Request(weather_url, headers={'User-Agent': 'SurflineCastellon/2.0'})

        with urllib.request.urlopen(req_m, timeout=10) as resp_m:
            data_m = json.loads(resp_m.read().decode('utf-8')).get('hourly', {})
        with urllib.request.urlopen(req_w, timeout=10) as resp_w:
            data_w = json.loads(resp_w.read().decode('utf-8')).get('hourly', {})

        return {'marine': data_m, 'weather': data_w}
    except Exception as e:
        print(f"⚠️ Error consultando Open-Meteo ({lat}, {lon}): {e}")
        return None


# ============================================================
# 📲 ENVÍO DE NOTIFICACIONES TELEGRAM Y WHATSAPP
# ============================================================
def enviar_telegram(chat_id, texto, botones=None):
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': texto,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    if botones:
        payload['reply_markup'] = {'inline_keyboard': botones}

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=8)
        print(f"✅ Telegram enviado a {chat_id}")
    except Exception as e:
        print(f"❌ Error Telegram ({chat_id}): {e}")


def enviar_whatsapp(telefono, apikey, texto):
    if not telefono or not apikey:
        return
    try:
        texto_enc = urllib.parse.quote(texto)
        url = f"https://api.callmebot.com/whatsapp.php?phone={telefono}&text={texto_enc}&apikey={apikey}"
        req = urllib.request.Request(url, headers={'User-Agent': 'SurflineCastellon/2.0'})
        urllib.request.urlopen(req, timeout=10)
        print(f"✅ WhatsApp enviado a {telefono}")
    except Exception as e:
        print(f"❌ Error WhatsApp ({telefono}): {e}")


# ============================================================
# 🚀 MOTOR PRINCIPAL: ANÁLISIS DE OLAS Y ALERTAS
# ============================================================
def ejecutar_analisis_diario():
    print("🌊 Iniciando análisis de oleaje para Castellón...")
    ahora = datetime.now()
    hoy_str = ahora.strftime('%Y-%m-%d')
    fecha_2d = (ahora + timedelta(days=2)).strftime('%Y-%m-%d')

    mejores_hoy = []
    mejores_2d = []

    for spot_nombre, cfg in SPOT_CONFIG.items():
        data = fetch_open_meteo(cfg['lat'], cfg['lon'])
        if not data or not data['marine'].get('time'):
            continue

        times = data['marine']['time']
        whs = data['marine']['wave_height']
        wps = data['marine']['wave_period']
        wdirs = data['marine']['wave_direction']
        sw_hs = data['marine'].get('swell_wave_height', whs)
        sw_ps = data['marine'].get('swell_wave_period', wps)
        sw_dirs = data['marine'].get('swell_wave_direction', wdirs)

        wspeeds = [w * 0.54 for w in data['weather']['wind_speed_10m']] # km/h a nudos
        wdirs_w = data['weather']['wind_direction_10m']
        pressures = data['weather']['pressure_msl']

        mejor_spot_hoy = {'est': 0, 'h': 0, 'spot': spot_nombre}
        mejor_spot_2d = {'est': 0, 'h': 0, 'spot': spot_nombre}

        for i, t_str in enumerate(times):
            fecha_dia = t_str.split('T')[0]
            hora = int(t_str.split('T')[1].split(':')[0])

            if hora < 7 or hora > 20:
                continue

            h_base = sw_hs[i] if (sw_hs[i] and sw_hs[i] > 0.15) else whs[i]
            p_base = sw_ps[i] if (sw_ps[i] and sw_ps[i] > 4.0) else wps[i]
            dir_base = sw_dirs[i] if (sw_dirs[i] is not None) else wdirs[i]

            heff = calcular_fisica(spot_nombre, h_base, p_base, dir_base)
            stars = calcular_calidad(heff, p_base, wspeeds[i], wdirs_w[i], spot_nombre, pressures[i])

            registro = {
                'spot': spot_nombre,
                'fecha': fecha_dia,
                'hora': hora,
                'heff': heff,
                'periodo': p_base,
                'estrellas': stars,
                'viento_kt': round(wspeeds[i], 1),
                'viento_dir': wdirs_w[i],
                'direccion_ola': dir_base
            }

            if fecha_dia == hoy_str and stars > mejor_spot_hoy['est']:
                mejor_spot_hoy = registro
            if fecha_dia == fecha_2d and stars > mejor_spot_2d['est']:
                mejor_spot_2d = registro

        if mejor_spot_hoy['est'] >= 3:
            mejores_hoy.append(mejor_spot_hoy)
        if mejor_spot_2d['est'] >= 3:
            mejores_2d.append(mejor_spot_2d)

    # ─── GENERAR Y ENVIAR REPORTES PERSONALIZADOS ───
    for u in USUARIOS_DEFECTO:
        if not u.get('activo'): continue

        playas_user = u['playas']
        alertas_user_hoy = [m for m in mejores_hoy if m['spot'] in playas_user]
        alertas_user_2d = [m for m in mejores_2d if m['spot'] in playas_user]

        # 1. Alerta Preaviso 2 Días
        if u.get('preaviso_2_dias') and alertas_user_2d:
            msg = f"🚨 <b>SURFLINE CASTELLÓN · PREAVISO 48H ({fecha_2d})</b>\n\n"
            msg += "Se detecta marejada para tus playas favoritas:\n\n"
            for a in alertas_user_2d:
                badge, stars_str = badge_calidad(a['estrellas'])
                humano = escala_humana(a['heff'])
                msg += f"📍 <b>{a['spot'].upper()}</b> — <i>Pico a las {a['hora']}:00h</i>\n"
                msg += f"{badge} {stars_str}\n"
                msg += f"🌊 <b>{a['heff']}m</b> ({humano}) · <b>{a['periodo']}s</b>\n"
                msg += f"💨 <b>{a['viento_kt']}kt</b> (Dir {int(a['viento_dir'])}°)\n\n"

            msg += "📱 <i>Ver cámaras y mapas en vivo en la Web</i> 🤙"

            botones_tg = [
                [{'text': '🏄 Abrir Web', 'url': 'https://mralcachofino-cyber.github.io/surfline-castellon/'}],
                [{'text': '📹 Ver Webcams', 'callback_data': 'btn_cams'}]
            ]
            enviar_telegram(u['telegram_id'], msg, botones_tg)
            if u.get('callmebot_key'):
                enviar_whatsapp(u['telefono'], u['callmebot_key'], msg.replace('<b>','*').replace('</b>','*').replace('<i>','_').replace('</i>','_'))

        # 2. Parte de Hoy (si hay olas destacadas)
        if alertas_user_hoy:
            msg_hoy = f"🌊 <b>PARTE DE HOY ({hoy_str})</b>\n\n"
            for a in alertas_user_hoy:
                badge, stars_str = badge_calidad(a['estrellas'])
                msg_hoy += f"📍 <b>{a['spot'].upper()}</b> — {a['hora']}:00h | {badge}\n"
                msg_hoy += f"🌊 <b>{a['heff']}m</b> {a['periodo']}s · 💨 <b>{a['viento_kt']}kt</b>\n\n"
            msg_hoy += "🤙 <i>¡Buen baño! Recuerda votar tu sesión al salir.</i>"
            enviar_telegram(u['telegram_id'], msg_hoy)

    print("✅ Análisis diario finalizado.")


if __name__ == '__main__':
    ejecutar_analisis_diario()
