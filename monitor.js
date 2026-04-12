import fs from 'fs';
import mqtt from 'mqtt';
import credenciales from './config.json' with { type: 'json' };

const LOG_FILE = 'totem_incidencias.log';

// ==============================================
// 1. FUNCIONES
// ==============================================
function logEvent(type, message) {
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
    const logLine = `[${timestamp}] [${type}] ${message}\n`;
    
    // Escribe en la consola y en el archivo de texto local
    console.log(logLine.trim());
    fs.appendFileSync(LOG_FILE, logLine, 'utf8');

    // Envía la telemetría a la nube (si el cliente está conectado)
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

// ==============================================
// 2. PRIMERO CREAMOS EL CLIENTE MQTT
// ==============================================
const brokerUrl = `mqtts://${credenciales.BROKER}:8883`;
const options = {
    clientId: `Vigilante_${Math.random().toString(16).substring(2, 8)}`,
    username: credenciales.USUARIO,
    password: credenciales.PASSWORD,
    clean: true,
    connectTimeout: 5000,
    reconnectPeriod: 5000
};

// ¡AQUÍ NACE LA VARIABLE CLIENT!
const client = mqtt.connect(brokerUrl, options);

// ==============================================
// 3. AHORA SÍ, EMPEZAMOS A REGISTRAR EVENTOS
// ==============================================
// Como 'client' ya existe arriba, esta línea ya no dará error
logEvent('SISTEMA', 'Tótem encendido. Iniciando servicios de monitorización...');

client.on('connect', () => {
    logEvent('RED', 'Conexión Wi-Fi/Red estable. Conectado a HiveMQ.');
    client.subscribe(credenciales.TOPIC, (err) => {
        if (!err) logEvent('MQTT', `Suscrito al canal de alertas: ${credenciales.TOPIC}`);
    });
});

client.on('offline', () => {
    logEvent('RED', 'Pérdida de conexión Wi-Fi/Red. Intentando reconectar...');
});

client.on('error', (err) => {
    logEvent('ERROR', `Fallo en el cliente MQTT: ${err.message}`);
});