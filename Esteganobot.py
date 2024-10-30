import telebot
from stegano import lsb
from PIL import Image
import os
import tempfile

TOKEN = '6618116796:AAHtlTN6RxPc1rIdGcoJyL6uuYlhfB_qjB4'
bot = telebot.TeleBot(TOKEN)

welcome_message = (
    "¡Hola! Soy un bot de esteganografía. Puedes ocultar mensajes en imágenes o revelar mensajes ocultos en imágenes.\n"
    "Elige una opción:\n"
    "1. Ocultar mensaje en imagen\n"
    "2. Revelar mensaje oculto en imagen\n"
    "Escribe '1' para ocultar un mensaje o '2' para revelar un mensaje."
)

estado = None
mensaje_a_ocultar = None

@bot.message_handler(commands=['start'])
def start(message):
    global estado, mensaje_a_ocultar
    estado = None
    mensaje_a_ocultar = None
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global estado, mensaje_a_ocultar
    text = message.text.strip()

    if text == '1':
        estado = 'ocultar'
        bot.reply_to(message, "Por favor, envía el mensaje que deseas ocultar en la imagen.")
    elif text == '2':
        estado = 'revelar'
        bot.reply_to(message, "Por favor, envía la imagen que contiene el mensaje oculto.")
    elif estado == 'ocultar' and mensaje_a_ocultar is None:
        mensaje_a_ocultar = text
        bot.reply_to(message, "Mensaje recibido. Ahora, envía la imagen en la que deseas ocultarlo.")
    else:
        bot.reply_to(message, "Opción no válida. Por favor, selecciona 1 o 2.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global estado, mensaje_a_ocultar

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
        temp_image.write(downloaded_file)
        ruta_imagen = temp_image.name

    if estado == 'ocultar' and mensaje_a_ocultar:
        ruta_codificada = ocultar_mensaje(ruta_imagen, mensaje_a_ocultar)
        if ruta_codificada:
            with open(ruta_codificada, 'rb') as img:
                bot.send_photo(message.chat.id, img, caption="Aquí está tu imagen con el mensaje oculto.")
            os.remove(ruta_codificada)
        else:
            bot.reply_to(message, "Error al ocultar el mensaje.")
        mensaje_a_ocultar = None
        estado = None

    elif estado == 'revelar':
        mensaje_revelado = revelar_mensaje(ruta_imagen)
        if mensaje_revelado:
            bot.reply_to(message, f"Mensaje revelado: {mensaje_revelado}")
        else:
            bot.reply_to(message, "No se encontró ningún mensaje oculto en esta imagen.")
        estado = None

    os.remove(ruta_imagen)

def ocultar_mensaje(ruta_imagen, mensaje):
    try:
        ruta_codificada = ruta_imagen.replace(".png", "_codificada.png")
        lsb.hide(ruta_imagen, mensaje).save(ruta_codificada)
        return ruta_codificada
    except Exception as e:
        print(f"Error al ocultar mensaje: {e}")
        return None

def revelar_mensaje(ruta_imagen):
    try:
        mensaje_revelado = lsb.reveal(ruta_imagen)
        return mensaje_revelado
    except Exception as e:
        print(f"Error al revelar mensaje: {e}")
        return None

bot.polling()
