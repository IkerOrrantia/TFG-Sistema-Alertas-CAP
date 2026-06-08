/* =========================================================================
   MÓDULO: EL VIGILANTE (Node.js)
   Descripción: Monitorización de salud de red y telemetría de alertas.
   ========================================================================= */
import fs from 'fs';
import mqtt from 'mqtt';
import credenciales from './config.json' with { type: 'json' };

const LOG_FILE = 'totem_incidencias.log';

 //  SISTEMA DE LOGGING Y TELEMETRÍA
function logEvent(type, message) {
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
    const logLine = `[${timestamp}] [${type}] ${message}\n`;
    
    // 1. Escribe en la consola y en el archivo de texto local (Cold Storage)
    console.log(logLine.trim());
    fs.appendFileSync(LOG_FILE, logLine, 'utf8');

    // 2. Envía la telemetría a la nube (Hot Storage)
    if (typeof client !== 'undefined' && client && client.connected) {
        const telemetriaData = JSON.stringify({
            dispositivo: "Totem-Gipuzkoa",
            timestamp: timestamp,
            tipo: type,
            mensaje: message
        });
        client.publish('totem/telemetria', telemetriaData);
    }
}


 //  CLIENTE MQTT (CONEXIÓN Y ESTADOS)

const brokerUrl = `mqtts://${credenciales.BROKER}:8883`;
const options = {
    clientId: `Vigilante_${Math.random().toString(16).substring(2, 8)}`,
    username: credenciales.USUARIO,
    password: credenciales.PASSWORD,
    clean: true,
    connectTimeout: 5000,
    reconnectPeriod: 5000
};
const client = mqtt.connect(brokerUrl, options);

logEvent('SISTEMA', 'Tótem encendido. Iniciando servicios de monitorización...');

// Evento: Conexión establecida
client.on('connect', () => {
    logEvent('RED', 'Conexión Wi-Fi/Red estable. Conectado a HiveMQ.');
    client.subscribe(credenciales.TOPIC, (err) => {
        if (!err) logEvent('MQTT', `Suscrito al canal de alertas: ${credenciales.TOPIC}`);
    });
});

// Evento: Pérdida de red
client.on('offline', () => {
    logEvent('RED', 'Pérdida de conexión Wi-Fi/Red. Intentando reconectar...');
});

// Evento: Errores internos
client.on('error', (err) => {
    logEvent('ERROR', `Fallo en el cliente MQTT: ${err.message}`);
});


//   RECEPCIÓN DE ALERTAS (CAP v1.2) 
client.on('message', (topic, message) => {
    try {
        const payload = JSON.parse(message.toString());
        
        // Extraemos los datos críticos del estándar CAP
        const headline = payload.alert?.info[0]?.headline || "Alerta Desconocida";
        const severity = payload.alert?.info[0]?.severity || "Unknown";
        
        if(severity === "Minor") {
            logEvent('SISTEMA', `Retorno a la normalidad: ${headline}`);
        } else {
            logEvent('ALERTA', `[${severity}] Desplegando emergencia: ${headline}`);
        }

    } catch (error) {
        logEvent('ERROR', `Imposible parsear la trama MQTT entrante: ${error.message}`);
    }
});