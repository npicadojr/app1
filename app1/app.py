# main.py
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
from functions import generate_answer, send_message
import logging

load_dotenv()
app = Flask(__name__)
TOKEN = os.getenv('TOKEN')
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN') # Load verify token from .env

# Configure logging
logging.basicConfig(level=logging.INFO)

def handle_post_request(request):
    try:
        value = data['entry'][0]['changes'][0].get('value', {})
        if 'messages' not in value:
            return jsonify({"status": "success", "message": "No hay mensajes nuevos"}), 200

        sender_number = value['messages'][0]['from']
        received_message = value['messages'][0].get('text', {}).get('body', '')

        response_message = generate_answer(received_message)
        send_message(sender_number, response_message)
        return jsonify({"status": "success"}), 200

    except KeyError as e:
        logging.error(f"KeyError processing WhatsApp data: {e}")
        return jsonify({"status": "error", "message": f"Error processing data: Missing key {e}"}), 400
    except IndexError as e:
        logging.error(f"IndexError processing WhatsApp data: {e}")
        return jsonify({"status": "error", "message": f"Error processing data: Invalid index {e}"}), 400
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True) # Log the exception traceback
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_get_request(request):
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    else:
        logging.warning("Webhook verification failed with incorrect token.")
        return "Error de autentificacion.", 403
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        return handle_get_request(request)
    elif request.method == "POST":
        try:
            data = request.get_json()
            logging.info(f"Received webhook data: {data}")

            if not is_valid_whatsapp_data(data):
                logging.error("Invalid incoming WhatsApp data structure.")
                return jsonify({"status": "error", "message": "Datos inválidos"}), 400

            return handle_post_request(request)
        except Exception as e:
            logging.error(f"Error parsing incoming JSON: {e}")
            return jsonify({"status": "error", "message": "Error al parsear el JSON."}), 400
    return None


def is_valid_whatsapp_data(data):
    return (
        isinstance(data, dict) and
        'entry' in data and isinstance(data['entry'], list) and len(data['entry']) > 0 and
        'changes' in data['entry'][0] and isinstance(data['entry'][0]['changes'], list) and len(data['entry'][0]['changes']) > 0 and
        'value' in data['entry'][0]['changes'][0]
    )

if __name__ == "__main__":
    if not TOKEN or not WHATSAPP_NUMBER or not VERIFY_TOKEN:
        logging.error("ERROR: Asegúrate de configurar TOKEN, WHATSAPP_NUMBER y VERIFY_TOKEN en el archivo .env")
        exit()
