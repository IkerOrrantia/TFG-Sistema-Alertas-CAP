import paho.mqtt.client as mqtt
import json
import ssl
import random
import os
import sys

# ==========================================
# 1. CARGAR CREDENCIALES DESDE EL CONFIG.JSON
# ==========================================
# Buscamos el config.json en la carpeta raíz (un nivel por encima de 'backend')
ruta_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))

try:
    with open(ruta_config, 'r') as f:
        credenciales = json.load(f)
except FileNotFoundError:
    # Por si acaso lo estás ejecutando directamente desde la raíz
    try:
        with open('config.json', 'r') as f:
            credenciales = json.load(f)
    except FileNotFoundError:
        print("❌ ERROR CRÍTICO: No se encuentra el archivo config.json.")
        print("Asegúrate de que existe en la carpeta raíz del proyecto.")
        sys.exit(1)

BROKER = credenciales["BROKER"]
PORT = 8883 # Forzamos el puerto nativo MQTT (no el web 8884)
USUARIO = credenciales["USUARIO"]
PASSWORD = credenciales["PASSWORD"]
TOPIC = credenciales["TOPIC"]

# ==========================================
# 2. CONEXIÓN MQTT
# ==========================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("\n✅ Conectado al servidor de alertas (HiveMQ) con éxito.")
    else:
        print(f"❌ Error al conectar, código: {rc}")

client = mqtt.Client(client_id=f"Generador_TFG_{random.randint(1000,9999)}")
client.username_pw_set(USUARIO, PASSWORD)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.on_connect = on_connect

print("Iniciando conexión segura...")
client.connect(BROKER, PORT, 60)
client.loop_start()

# ==========================================
# 3. DICCIONARIO DE ALERTAS (MULTI-IDIOMA)
# ==========================================
def generar_alerta(opcion):
    alertas = {
        "1": { # ZONA SEGURA (Minor)
            "val": str(random.randint(18, 22)), "unit": "°C",
            "es": ["ZONA SEGURA", "Todos los parámetros se encuentran dentro de la normalidad. No hay riesgo inminente.", "Minor", "Sistema Automatizado"],
            "en": ["SAFE ZONE", "All parameters are within normal ranges. No imminent risk.", "Minor", "Automated System"],
            "eu": ["EREMU SEGURUA", "Parametro guztiak normaltasunaren barruan daude. Ez dago berehalako arriskurik.", "Minor", "Sistema Automatizatua"],
            "pt": ["ZONA SEGURA", "Todos os parâmetros estão dentro da normalidade. Nenhum risco iminente.", "Minor", "Sistema Automatizado"]
        },
        "2": { # CALIDAD DEL AIRE (Moderate)
            "val": str(random.randint(150, 190)), "unit": "AQI",
            "es": ["ALERTA TOXICOLÓGICA", "Calidad del aire perjudicial. Se recomienda el uso de mascarilla FPP2 y cerrar ventanas.", "Moderate", "Estación Meteorológica"],
            "en": ["TOXIC ALERT", "Unhealthy air quality. FPP2 mask usage and closing windows recommended.", "Moderate", "Weather Station"],
            "eu": ["ALERTA TOXIKOLOGIKOA", "Airearen kalitate kaltegarria. FPP2 maskara erabiltzea eta leihoak ixtea gomendatzen da.", "Moderate", "Estazio Meteorologikoa"],
            "pt": ["ALERTA TOXICOLÓGICO", "Qualidade do ar prejudicial. Recomenda-se o uso de máscara FPP2 e fechar janelas.", "Moderate", "Estação Meteorológica"]
        },
        "3": { # TEMPORAL / INUNDACIÓN (Moderate)
            "val": str(random.randint(80, 120)), "unit": "mm/h",
            "es": ["ALERTA POR LLUVIAS", "Precipitaciones intensas. Peligro de inundación en plantas bajas y garajes.", "Moderate", "AEMET"],
            "en": ["HEAVY RAIN WARNING", "Intense rainfall. Flooding danger in ground floors and garages.", "Moderate", "AEMET"],
            "eu": ["EURI ALERTA", "Prezipitazio handiak. Beheko solairuetan eta garajeetan uholde arriskua.", "Moderate", "Euskalmet"],
            "pt": ["ALERTA DE CHUVA", "Precipitações intensas. Perigo de inundação no térreo e garagens.", "Moderate", "IPMA"]
        },
        "4": { # INCENDIO (Extreme)
            "val": str(random.randint(250, 450)), "unit": "°C",
            "es": ["FUEGO INDUSTRIAL", "Incendio detectado en el sector norte. Evacúe el edificio inmediatamente usando las escaleras.", "Extreme", "Sensor Térmico T-42"],
            "en": ["INDUSTRIAL FIRE", "Fire detected in the north sector. Evacuate the building immediately using the stairs.", "Extreme", "Thermal Sensor T-42"],
            "eu": ["SUTE INDUSTRIALA", "Sutea detektatu da iparraldeko sektorean. Ebakuatu eraikina berehala eskailerak erabiliz.", "Extreme", "Sentsore Termikoa T-42"],
            "pt": ["FOGO INDUSTRIAL", "Incêndio detectado no setor norte. Evacue o edifício imediatamente usando as escadas.", "Extreme", "Sensor Térmico T-42"]
        },
        "5": { # INTRUSIÓN (Severe)
            "val": "1", "unit": "BREACH",
            "es": ["INTRUSIÓN DETECTADA", "Brecha de seguridad en el perímetro sur. Personal de seguridad en camino. Manténgase a salvo.", "Severe", "Alarma Perimetral"],
            "en": ["INTRUSION DETECTED", "Security breach in the south perimeter. Security personnel en route. Stay safe.", "Severe", "Perimeter Alarm"],
            "eu": ["INTRUSIOA DETEKTATUTA", "Segurtasun haustura hegoaldeko perimetroan. Segurtasun langileak bidean. Mantendu seguru.", "Severe", "Perimetroko Alarma"],
            "pt": ["INTRUSÃO DETECTADA", "Violação de segurança no perímetro sul. Equipe de segurança a caminho. Mantenha-se seguro.", "Severe", "Alarme Perimetral"]
        },
        "6": { # FUGA QUÍMICA (Extreme)
            "val": str(random.randint(400, 600)), "unit": "PPM",
            "es": ["FUGA DE GAS AMONIACO", "Niveles letales detectados. Evacuación obligatoria. Siga las rutas de escape iluminadas.", "Extreme", "Sensor de Gases C-09"],
            "en": ["AMMONIA GAS LEAK", "Lethal levels detected. Mandatory evacuation. Follow the illuminated escape routes.", "Extreme", "Gas Sensor C-09"],
            "eu": ["AMONIAKO GAS ISURIA", "Maila hilgarriak detektatu dira. Nahitaezko ebakuazioa. Jarraitu argiztatutako ihesbideak.", "Extreme", "Gas Sentsorea C-09"],
            "pt": ["VAZAMENTO DE GÁS AMÔNIA", "Níveis letais detectados. Evacuação obrigatória. Siga as rotas de fuga iluminadas.", "Extreme", "Sensor de Gás C-09"]
        }
    }

    if opcion not in alertas:
        return None

    data = alertas[opcion]
    info_list = []
    
    # Construimos el formato CAP para cada idioma
    for lang in ["es", "en", "eu", "pt"]:
        info_list.append({
            "language": lang,
            "headline": data[lang][0],
            "description": data[lang][1],
            "severity": data[lang][2],
            "senderName": data[lang][3],
            "parameter": [{"value": data["val"]}, {"value": data["unit"]}]
        })

    return {"alert": {"info": info_list}}

# ==========================================
# 4. BUCLE DE CONTROL MANUAL (MENÚ)
# ==========================================
print("\n" + "="*50)
print(" 🎛️ PANEL DE SIMULACIÓN DE EMERGENCIAS (TFG)")
print("="*50)

while True:
    print("\nOpciones de disparo:")
    print(" [1] 🟢 Estado Seguro (Normalidad)")
    print(" [2] 🟠 Calidad del Aire (Moderada)")
    print(" [3] 🟠 Lluvias / Inundación (Moderada)")
    print(" [4] 🔴 Incendio Industrial (Extremo)")
    print(" [5] 🔴 Intrusión de Seguridad (Severo)")
    print(" [6] 🔴 Fuga Química de Gas (Extremo)")
    print(" [0] Salir del simulador")
    
    seleccion = input("\nElige una opción (0-6) y pulsa Enter: ")
    
    if seleccion == "0":
        print("Cerrando simulador...")
        break
        
    payload = generar_alerta(seleccion)
    
    if payload:
        mensaje_json = json.dumps(payload)
        client.publish(TOPIC, mensaje_json)
        print(f"📡 ¡Alerta enviada correctamente al Tótem!")
    else:
        print("⚠️ Opción no válida. Por favor, elige un número del 0 al 6.")

client.loop_stop()
client.disconnect()