import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import PyPDF2
from PIL import Image as Image, ImageOps as ImagOps
import glob
from gtts import gTTS
import os
import time
from streamlit_lottie import st_lottie
import json
import paho.mqtt.client as mqtt
import pytz

# Configuración MQTT actualizada
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_SENSOR_TOPIC = "sensor_data"  # Cambiado para coincidir con Wokwi
MQTT_CONTROL_TOPIC = "Eden"        # Topic para comandos

# Variables de estado para los datos del sensor
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def on_message(client, userdata, message):
    """Callback para mensajes MQTT"""
    try:
        payload = json.loads(message.payload.decode())
        st.session_state.sensor_data = payload
    except Exception as e:
        st.error(f"Error al procesar mensaje: {e}")

def get_mqtt_message():
    """Función mejorada para obtener mensajes MQTT"""
    try:
        client = mqtt.Client()
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_SENSOR_TOPIC)
        
        # Esperar por datos
        client.loop_start()
        time.sleep(2)  # Dar tiempo para recibir datos
        client.loop_stop()
        client.disconnect()
        
        return st.session_state.sensor_data
    except Exception as e:
        st.error(f"Error de conexión MQTT: {e}")
        return None

def send_mqtt_message(message):
    """Función para enviar comandos MQTT"""
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_CONTROL_TOPIC, message)
        client.disconnect()
        return True
    except Exception as e:
        st.error(f"Error al enviar comando MQTT: {e}")
        return False

# ... (mantener el resto de las funciones auxiliares igual)

# En la sección de la interfaz donde muestras los datos del sensor:
with col1:
    st.subheader("Datos del Sensor")
    if st.button("Obtener Lectura"):
        with st.spinner('Obteniendo datos del sensor...'):
            sensor_data = get_mqtt_message()
            
            if sensor_data and isinstance(sensor_data, dict):
                st.success("Datos recibidos correctamente")
                if 'Temp' in sensor_data:
                    st.metric("Temperatura", f"{sensor_data['Temp']:.1f}°C")
                if 'Hum' in sensor_data:
                    st.metric("Humedad", f"{sensor_data['Hum']:.1f}%")
            else:
                st.warning("No se recibieron datos del sensor. Verifica la conexión.")

# Para debugging (opcional)
if st.checkbox("Mostrar datos raw del sensor"):
    st.write("Datos raw:", st.session_state.sensor_data)
