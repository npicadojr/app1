# functions.py
from dotenv import load_dotenv
import os
import logging
import requests
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# Configuración
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.getenv("GITHUB_TOKEN")
TOKEN = os.getenv('TOKEN')
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')

def send_message(number_to, message):
    try:
        url = f"https://graph.facebook.com/v12.0/{WHATSAPP_NUMBER}/messages"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": number_to,
            "text": {"body": message}
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            logging.info(f"Mensaje enviado a {number_to}")
            return True
        else:
            logging.warning(f"Fallo al enviar mensaje: {response.status_code} - {response.text}")
 # Raise an exception for non-success status codes
            response.raise_for_status()
    except Exception as e:
        logging.exception("Excepción al enviar mensaje:")
        return False

def generate_answer(question):
    try:
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )
        response = client.complete(
            messages=[
 # Consider making the system message configurable
 SystemMessage("You are a helpful assistant."),
                UserMessage(f"Q: {question}\nA:")
            ],
            temperature=1.0,
            top_p=1.0,
 model=model
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        logging.exception("Error al generar respuesta:")
        return None # Return None to indicate failure