from time import sleep

import paho.mqtt.client as mqtt
import json
import ssl
import random
import os
import sys
import datetime
import uuid

# 1. CARGAR CREDENCIALES DESDE EL CONFIG.JSON
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

# 2. CONEXIÓN MQTT
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
# 3. DICCIONARIO DE ALERTAS (MULTI-IDIOMA - 4 ESTADOS)
# ==========================================
def generar_alerta(opcion):
    alertas = {
        "1": { # ZONA SEGURA (Minor)
            "es": ["ESTADO SEGURO", "Todos los parámetros se encuentran dentro de la normalidad. No hay riesgo inminente.", "Minor", "Sistema Automatizado"],
            "en": ["SAFE STATE", "All parameters are within normal limits. No imminent risk.", "Minor", "Automated System"],
            "eu": ["GUNE SEGURUA", "Parametro guztiak normaltasunaren barruan daude. Ez dago berehalako arriskurik.", "Minor", "Sistema Automatizatua"],
            "pt": ["ESTADO SEGURO", "Todos os parâmetros estão dentro da normalidade. Nenhum risco iminente.", "Minor", "Sistema Automatizado"]
        },
        "2": { # INCENDIO (Extreme)
            "es": ["ALERTA DE INCENDIO", "Fuego detectado en las instalaciones. Evacue el edificio inmediatamente usando las escaleras.", "Extreme", "Sensor Térmico T-42"],
            "en": ["FIRE ALERT", "Fire detected on premises. Evacuate the building immediately using the stairs.", "Extreme", "Thermal Sensor T-42"],
            "eu": ["SUTE ALERTA", "Sutea aurkitu da. Eraikina hustu berehala eskailerak erabiliz.", "Extreme", "Sentsore Termikoa T-42"],
            "pt": ["ALERTA DE INCÊNDIO", "Fogo detetado nas instalações. Evacue o edifício imediatamente usando as escadas.", "Extreme", "Sensor Térmico T-42"]
        },
        "3": { # TERREMOTO (Severe)
            "es": ["ALERTA DE TERREMOTO", "Actividad sísmica detectada. Aléjese de las ventanas y busque refugio bajo una estructura sólida.", "Severe", "Instituto Sismológico"],
            "en": ["EARTHQUAKE ALERT", "Seismic activity detected. Move away from windows and take cover under a sturdy desk or table.", "Severe", "Seismological Institute"],
            "eu": ["LURRIKARA ALERTA", "Jarduera sismikoa detektatu da. Urrrundu leihoetatik eta babestu mahai baten azpian.", "Severe", "Institutu Sismologikoa"],
            "pt": ["ALERTA DE SISMO", "Atividade sísmica detetada. Afaste-se das janelas e procure abrigo debaixo de uma mesa sólida.", "Severe", "Instituto Sismológico"]
        },
        "4": { # CALIDAD DEL AIRE (Moderate)
            "es": ["MALA CALIDAD DEL AIRE", "Niveles críticos de contaminación exterior. Cierre puertas y ventanas y evite salir.", "Moderate", "Estación Meteorológica"],
            "en": ["POOR AIR QUALITY", "Critical levels of outdoor pollution. Close doors and windows and avoid going outside.", "Moderate", "Weather Station"],
            "eu": ["AIREAREN KALITATE TXARRA", "Kutsadura maila kritikoa. Itxi ateak eta leihoak eta saihestu kalera irtetea.", "Moderate", "Estazio Meteorologikoa"],
            "pt": ["MÁ QUALIDADE DO AR", "Níveis críticos de poluição exterior. Feche portas e janelas e evite sair.", "Moderate", "Estação Meteorológica"]
        }
    }

    if opcion not in alertas:
        return None

    data = alertas[opcion]
    info_list = []
    
    # TIMESTAMP CAP ESTÁNDAR
    ahora = datetime.datetime.now(datetime.UTC).isoformat()
    
    # Nivel de severidad para el tipo de mensaje
    severidad_base = data["es"][2]

    # Construimos el formato para cada idioma SIN datos inventados (parameter)
    for lang in ["es", "en", "eu", "pt"]:
        info_list.append({
            "language": lang,
            "headline": data[lang][0],
            "description": data[lang][1],
            "severity": data[lang][2],
            "senderName": data[lang][3]
        })

    # Empaquetamos bajo el estándar CAP
    return {
        "alert": {
            "identifier": str(uuid.uuid4()),
            "sender": "retime-python-backend@deusto.es",
            "sent": ahora,
            "status": "Actual",
            "msgType": "Alert" if severidad_base != "Minor" else "Update",
            "scope": "Public",
            "info": info_list
        }
    }

# MODO EDUCATIVO (SIMULACRO AUTOMÁTICO)
def ejecutar_modo_educativo():
    print("\n" + "="*50)
    print(" 🎓 INICIANDO MODO EDUCATIVO (DEMO)")
    print("="*50)
    print("El sistema emitirá una alerta diferente cada 30 segundos.")
    print("Presiona Ctrl+C en la terminal para abortar y volver a estado seguro.\n")

    # Lista de tuplas: ("opcion_menu", tiempo_espera_segundos)
    escenarios = [
        ("2", 30), # Incendio: 30 segundos
        ("3", 30), # Terremoto: 30 segundos
        ("4", 36)  # Calidad del aire: 36 segundos (6 segundos extra)
    ]

    try:
        for opcion, tiempo_espera in escenarios:
            payload = generar_alerta(opcion)
            headline = payload['alert']['info'][0]['headline']
            print(f">>> Simulando catástrofe: {headline} (Esperando {tiempo_espera}s)...")
            
            mensaje_json = json.dumps(payload, ensure_ascii=False)
            client.publish(TOPIC, mensaje_json)
            
            sleep(tiempo_espera) # El tiempo ahora es dinámico para cada iteración

        print("\n>>> Ciclo educativo finalizado. Restaurando sistema a Modo Seguro (IDLE)...")
        payload_seguro = generar_alerta("1")
        client.publish(TOPIC, json.dumps(payload_seguro, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n\n[!] Modo Educativo interrumpido por el administrador.")
        print(">>> Forzando sistema a Modo Seguro (IDLE)...")
        payload_seguro = generar_alerta("1")
        client.publish(TOPIC, json.dumps(payload_seguro, ensure_ascii=False))
        
    print("="*50 + "\n")

# INICIALIZACIÓN AUTOMÁTICA: ESTADO SEGURO (IDLE)
sleep(2) # Pequeña pausa para asegurar que la conexión MQTT se ha estabilizado
print("\n>>> Sincronizando tótems: Enviando Estado Seguro (IDLE) inicial...")
payload_inicial = generar_alerta("1")
if payload_inicial:
    mensaje_json = json.dumps(payload_inicial, ensure_ascii=False)
    client.publish(TOPIC, mensaje_json, retain=True)
    print("📡 [✓] Estado Seguro inicial inyectado y retenido en el broker.")

# ==========================================
# 4. BUCLE DE CONTROL MANUAL (MENÚ)
# ==========================================
sleep(1)
print("\n" + "="*50)
print(" 🎛️" + "\t" + "PANEL DE SIMULACIÓN DE EMERGENCIAS")
print("="*50)

while True:
    print("\nOpciones de disparo:")
    print(" [1] 🟢 Estado Seguro (Normalidad)")
    print(" [2] 🔴 Alerta de Incendio (Extremo)")
    print(" [3] 🟠 Alerta de Terremoto (Severo)")
    print(" [4] 🟣 Mala Calidad del Aire (Moderada)")
    print(" [5] 🎓 Modo Educativo (Ciclo de Alertas)")
    print(" [0] Salir del simulador")
    
    seleccion = input("\nElige una opción (0-4) y pulsa Enter: ")
    
    if seleccion == "0":
        print("Cerrando simulador...")
        break
    elif seleccion == "5":
        ejecutar_modo_educativo()
        continue
        
    payload = generar_alerta(seleccion)
    
    if payload:
        mensaje_json = json.dumps(payload, ensure_ascii=False)
        client.publish(TOPIC, mensaje_json)
        print(f"📡 ¡Alerta '{payload['alert']['info'][0]['headline']}' enviada correctamente al Tótem!")
    else:
        print("⚠️ Opción no válida. Por favor, elige un número del 0 al 4.")

client.loop_stop()
client.disconnect()