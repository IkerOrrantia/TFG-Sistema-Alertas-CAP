import paho.mqtt.client as mqtt
import json
import time
import random
import uuid
import ssl
from datetime import datetime

# ==========================================
# CONFIGURACIÓN HIVEMQ CLOUD (Cámbialo aquí)
# ==========================================
BROKER = "8c5f6d94879849ce994d70618deed882.s1.eu.hivemq.cloud" 
PORT = 8883                                
USUARIO = "Iker_tfg"                
PASSWORD = "P3nS@C4L2mxJZrH"            
TOPIC = "totem/alertas"


# --- LISTA DE POSIBLES ESCENARIOS ---
ESCENARIOS = [
    {
        "type": "Fire",
        "severity": "Severe",
        "headline": "ALARMA DE INCENDIO",
        "desc": "Detectores de humo activados en Planta 2.",
        "instruction": "EVACUACIÓN INMEDIATA. No use ascensor.",
        "param_name": "temperature",
        "param_val": lambda: str(random.randint(60, 120)), 
        "param_unit": "°C"
    },
    {
        "type": "Environment",
        "severity": "Moderate",
        "headline": "Calidad Aire Baja",
        "desc": "Niveles de CO2 superiores a lo recomendado.",
        "instruction": "Ventilación forzada activada. Abra ventanas.",
        "param_name": "reading",
        "param_val": lambda: str(random.randint(1000, 1600)), 
        "param_unit": "ppm"
    },
    {
        "type": "Safety",
        "severity": "Minor",
        "headline": "Sistema Normal",
        "desc": "Parámetros ambientales dentro de rango.",
        "instruction": "Operación estándar.",
        "param_name": "reading",
        "param_val": lambda: str(random.randint(400, 800)), 
        "param_unit": "ppm"
    },
    {
        "type": "Met",
        "severity": "Severe",
        "headline": "ALERTA INUNDACIÓN",
        "desc": "Lluvias torrenciales. Riesgo en planta baja.",
        "instruction": "Busque zonas altas. Evite sótano.",
        "param_name": "waterLevel",
        "param_val": lambda: str(random.randint(10, 50)),
        "param_unit": "mm"
    },
    {
        "type": "Security",
        "severity": "Severe",
        "headline": "INTRUSIÓN DETECTADA",
        "desc": "Acceso no autorizado en puerta trasera.",
        "instruction": "Personal de seguridad en camino.",
        "param_name": "zone",
        "param_val": lambda: "Zona Norte",
        "param_unit": "Loc"
    }
]

def generar_alerta_cap():
    escenario = random.choice(ESCENARIOS)
    valor_actual = escenario["param_val"]()
    ahora = datetime.now().isoformat()
    
    alerta = {
        "alert": {
            "identifier": f"ES-ALERT-{str(uuid.uuid4())[:8]}",
            "sender": "totem-backend",
            "sent": ahora,
            "status": "Actual",
            "msgType": "Alert",
            "scope": "Public",
            "info": [{
                "language": "es-ES",
                "category": [escenario["type"]],
                "event": escenario["headline"],
                "urgency": "Immediate",
                "severity": escenario["severity"],
                "certainty": "Observed",
                "headline": escenario["headline"],
                "description": escenario["desc"],
                "instruction": escenario["instruction"],
                "parameter": [
                    {"valueName": escenario["param_name"], "value": valor_actual},
                    {"valueName": "unit", "value": escenario["param_unit"]}
                ]
            }]
        }
    }
    return alerta

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Generador_Backend_TFG")
    
    # Añadimos las credenciales y el certificado TLS
    client.username_pw_set(USUARIO, PASSWORD)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    
    try:
        print(f"Conectando a {BROKER}...")
        client.connect(BROKER, PORT, 60)
        print("✅ Generador de MULTI-ALERTAS conectado a HiveMQ Cloud.")
        
        while True:
            payload = generar_alerta_cap()
            mensaje_json = json.dumps(payload, ensure_ascii=False)
            client.publish(TOPIC, mensaje_json)
            
            info = payload['alert']['info'][0]
            print(f"📡 Enviado: {info['headline']} ({info['severity']})")
            
            time.sleep(5)

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()