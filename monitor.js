import fs from 'fs';
import mqtt from 'mqtt';
import credenciales from './config.json' with { type: 'json' };

const LOG_FILE = 'totem_incidencias.log';

// Función para escribir en el archivo con fecha y hora
function logEvent(type, message) {
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
    const logLine = `[${timestamp}] [${type}] ${message}\n`;
    
    // Escribe en la consola y en el archivo de texto
    console.log(logLine.trim());
    fs.appendFileSync(LOG_FILE, logLine, 'utf8');
}

logEvent('SISTEMA', 'Tótem encendido. Iniciando servicios de monitorización...');

// Configuración de conexión al Broker
const brokerUrl = `mqtts://${credenciales.BROKER}:8883`;
const options = {
    clientId: `Vigilante_${Math.random().toString(16).substring(2, 8)}`,
    username: credenciales.USUARIO,
    password: credenciales.PASSWORD,
    clean: true,
    connectTimeout: 5000,
    reconnectPeriod: 5000 // Intenta reconectar cada 5 segundos si se cae el Wi-Fi
};

// Conectar a HiveMQ
const client = mqtt.connect(brokerUrl, options);

client.on('connect', () => {
    logEvent('RED', 'Conexión Wi-Fi/Red estable. Conectado a HiveMQ.');
    client.subscribe(credenciales.TOPIC, (err) => {
        if (!err) logEvent('MQTT', `Suscrito al canal de alertas: ${credenciales.TOPIC}`);
    });
});

client.on('offline', () => {
    logEvent('ALERTA-RED', 'Pérdida de conexión a internet o caída del Broker MQTT.');
});

client.on('reconnect', () => {
    logEvent('RED', 'Intentando reconectar a la red...');
});

client.on('message', (topic, message) => {
    try {
        const payload = JSON.parse(message.toString());
        const info = payload.alert.info[0];
        logEvent('EMERGENCIA', `Alerta recibida: ${info.headline} (Severidad: ${info.severity})`);
    } catch (e) {
        logEvent('ERROR', 'Mensaje recibido con formato incorrecto.');
    }
});

// Capturar cierre del programa (ej. alguien apaga la máquina)
process.on('SIGINT', () => {
    logEvent('SISTEMA', 'Apagado manual del sistema detectado.');
    process.exit();
});