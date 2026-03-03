import paho.mqtt.client as mqtt
import json
import time
import random
import uuid
from datetime import datetime

# CONFIGURACIÓN
BROKER = "51.49.204.68"
PORT = 1883
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
        "param_val": lambda: str(random.randint(60, 120)), # Temperatura alta
        "param_unit": "°C"
    },
    {
        "type": "Environment",
        "severity": "Moderate",
        "headline": "Calidad Aire Baja",
        "desc": "Niveles de CO2 superiores a lo recomendado.",
        "instruction": "Ventilación forzada activada. Abra ventanas.",
        "param_name": "reading",
        "param_val": lambda: str(random.randint(1000, 1600)), # CO2 Medio
        "param_unit": "ppm"
    },
    {
        "type": "Safety",
        "severity": "Minor",
        "headline": "Sistema Normal",
        "desc": "Parámetros ambientales dentro de rango.",
        "instruction": "Operación estándar.",
        "param_name": "reading",
        "param_val": lambda: str(random.randint(400, 800)), # CO2 Bajo
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
    # 1. Elegir un desastre aleatorio
    escenario = random.choice(ESCENARIOS)
    
    # 2. Generar valor dinámico (ej. la temperatura cambia cada vez)
    valor_actual = escenario["param_val"]()

    ahora = datetime.now().isoformat()
    
    # 3. Construir JSON CAP
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
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Generador_Multievento")
    
    try:
        print(f"Conectando a {BROKER}...")
        client.connect(BROKER, PORT, 60)
        print("✅ Generador de MULTI-ALERTAS listo.")
        
        while True:
            payload = generar_alerta_cap()
            mensaje_json = json.dumps(payload, ensure_ascii=False)
            client.publish(TOPIC, mensaje_json)
            
            # Log bonito
            info = payload['alert']['info'][0]
            print(f"📡 Enviado: {info['headline']} ({info['severity']})")
            
            time.sleep(5) # Una alerta nueva cada 5 segundos

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()