import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

import secrets # Archivo secrets.py con token, credenciales y IDs


# Token de acceso al bot de telegram
TELEGRAM_TOKEN = secrets.TELEGRAM_TOKEN

# Credenciales de la Cuenta de Servicio de Google Sheets
CREDENCIALES_GOOGLE_SHEETS = secrets.CREDENCIALES_GOOGLE_SHEETS

# ID de la planilla de Google Sheets
ID_GOOGLE_SHEETS = secrets.ID_GOOGLE_SHEETS

# Inicializar el cliente de Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# IDs Usuarios autorizados
USUARIOS_AUTORIZADOS = secrets.USUARIOS_AUTORIZADOS

# Funcion para manejar el comando /start
def iniciar(update, context):
    id_usuario = update.message.from_user.id
    if id_usuario in USUARIOS_AUTORIZADOS:
        context.bot.send_message(chat_id=update.effective_chat.id, text='¡Hola! Podés cargar tus gastos en el siguiente formato y orden: $0000.00, Categoría, Descripción (opcional)')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No estás autorizado para interactuar con este bot.')

# Función para manejar los mensajes con gastos
def manejar_gasto(update, context):
    id_usuario = update.message.from_user.id
    if id_usuario in USUARIOS_AUTORIZADOS:
        texto_gasto = update.message.text
        partes_gasto = texto_gasto.split(' ')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No estás autorizado para interactuar con este bot.')

            
    if len(partes_gasto) >= 2:
        parte_monto = partes_gasto[0]
        if parte_monto[0] == '$':
            try:
                monto = float(parte_monto[1:].replace(',', '.'))  # Reemplaza ',' por '.' y convierte a float
                categoria = partes_gasto[1]
                descripcion = ' '.join(partes_gasto[2:]) if len(partes_gasto) > 2 else ''
                autor = update.message.from_user.username  # Obtener el nombre de usuario de Telegram
                
                # Guardar los datos en la hoja de cálculo
                credenciales = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIALES_GOOGLE_SHEETS)
                cliente = gspread.authorize(credenciales)
                hoja_calculo = cliente.open_by_key(ID_GOOGLE_SHEETS).sheet1
                zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
                fecha_hora = datetime.now(tz=zona_horaria)
                fecha_hora_str = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
                fila_gasto = [fecha_hora_str, monto, categoria, descripcion, autor]
                hoja_calculo.append_row(fila_gasto)

                context.bot.send_message(chat_id=update.effective_chat.id, text='Gasto registrado correctamente.')
            except ValueError:
                context.bot.send_message(chat_id=update.effective_chat.id, text='El monto del gasto no tiene un formato válido. Asegúrate de ingresar un número decimal con el formato correcto: $0000.00')
        
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='El gasto no ha sido ingresado correctamente. Inténtalo nuevamente. Recuerda ingresar los datos en este orden y de la siguiente manera: $0000.00, Categoría, Descripción (opcional).')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='El gasto no ha sido ingresado correctamente. Inténtalo nuevamente. Recuerda ingresar los datos en este orden y de la siguiente manera: $0000.00, Categoría, Descripción (opcional).')


# Configurar el Updater con el token del bot de Telegram
actualizador = Updater(token=TELEGRAM_TOKEN, use_context=True)

# Obtener el despachador del Updater
despachador = actualizador.dispatcher

# Manejador para el comando /start
manejador_inicio = CommandHandler('start', iniciar)
despachador.add_handler(manejador_inicio)

# Manejador para los mensajes con gastos
manejador_gastos = MessageHandler(Filters.text & (~Filters.command), manejar_gasto)
despachador.add_handler(manejador_gastos)

# Iniciar el bot
actualizador.start_polling()
