import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

import secrets  # Archivo secrets.py con token, credenciales y IDs

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

# Categorías de gasto
CATEGORIAS_GASTOS = [
    'AUTOS', 'BEBÉS', 'CASA/OBRA', 'COMBUSTIBLE', 'COMIDA', 'DELIVERY', 'IMPUESTOS',
    'PRÉSTAMOS', 'RESTAURANT', 'ROPA/CALZADO', 'SALUD', 'SEGUROS', 'SERVICIOS',
    'SUPERMERCADO', 'TARJETAS', 'VARIOS/OTROS', 'VIAJES'
]

# Formas de pago
FORMAS_PAGO = ['EFECTIVO', 'DÉBITO/TRANSFERENCIA', 'CRÉDITO']

# Funcion para manejar el comando /start
def iniciar(update, context):
    id_usuario = update.message.from_user.id
    if id_usuario in USUARIOS_AUTORIZADOS:
        context.bot.send_message(chat_id=update.effective_chat.id, text='¡Hola! Ingresa el monto del gasto en el siguiente formato: $0000.00')
        context.user_data['fase'] = 'monto'
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No estás autorizado para interactuar con este bot.')

# Función para manejar los mensajes de texto
def manejar_mensaje(update, context):
    id_usuario = update.message.from_user.id
    if id_usuario in USUARIOS_AUTORIZADOS:
        fase = context.user_data.get('fase', 'monto')

        if fase == 'monto':
            manejar_monto(update, context)
        elif fase == 'descripcion':
            manejar_descripcion(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='No estás autorizado para interactuar con este bot.')

# Función para manejar el ingreso del monto
def manejar_monto(update, context):
    texto_gasto = update.message.text
    parte_monto = texto_gasto.strip()

    if parte_monto[0] == '$':
        try:
            monto = float(parte_monto[1:].replace(',', '.'))  # Reemplaza ',' por '.' y convierte a float
            context.user_data['monto'] = monto
            context.user_data['fase'] = 'forma_pago'
            context.user_data['monto_message_id'] = update.message.message_id  # Guardar el ID del mensaje del monto
            mostrar_formas_pago(update, context)
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text='El monto del gasto no tiene un formato válido. Asegúrate de ingresar un número decimal con el formato correcto: $0000.00')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='El gasto no ha sido ingresado correctamente. Inténtalo nuevamente. Recuerda ingresar los datos en este orden y de la siguiente manera: $0000.00')

# Función para mostrar las formas de pago
def mostrar_formas_pago(update, context):
    teclado_formas_pago = [
        [InlineKeyboardButton(forma, callback_data=forma)] for forma in FORMAS_PAGO
    ]
    reply_markup = InlineKeyboardMarkup(teclado_formas_pago)
    update.message.reply_text('Selecciona la forma de pago:', reply_markup=reply_markup)

# Función para manejar la selección de formas de pago
def seleccionar_forma_pago(update, context):
    query = update.callback_query
    forma_pago = query.data
    context.user_data['forma_pago'] = forma_pago
    context.user_data['fase'] = 'categoria'
    query.delete_message()
    mostrar_categorias(update, context)

# Función para mostrar las categorías
def mostrar_categorias(update, context):
    teclado_categorias = [
        [InlineKeyboardButton(categoria, callback_data=categoria)] for categoria in CATEGORIAS_GASTOS
    ]
    reply_markup = InlineKeyboardMarkup(teclado_categorias)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Selecciona la categoría del gasto:', reply_markup=reply_markup)

# Función para manejar la selección de categorías
def seleccionar_categoria(update, context):
    query = update.callback_query
    categoria = query.data
    context.user_data['categoria'] = categoria
    context.user_data['fase'] = 'descripcion'
    query.delete_message()
    context.user_data['descripcion_message'] = context.bot.send_message(chat_id=update.effective_chat.id, text='Por favor, ingresa la descripción del gasto (opcional):')

# Función para manejar la descripción del gasto
def manejar_descripcion(update, context):
    descripcion = update.message.text
    context.user_data['descripcion'] = descripcion
    context.user_data['descripcion_message_id'] = update.message.message_id  # Guardar el ID del mensaje de la descripción
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['descripcion_message'].message_id)  # Eliminar el mensaje de solicitud de descripción
    guardar_gasto(update, context)

# Función para guardar el gasto en Google Sheets
def guardar_gasto(update, context):
    descripcion = context.user_data.get('descripcion', '')
    monto = context.user_data.get('monto', '')
    categoria = context.user_data.get('categoria', '')
    forma_pago = context.user_data.get('forma_pago', '')
    autor = update.message.from_user.username  # Obtener el nombre de usuario de Telegram

    # Guardar los datos en la hoja de cálculo
    try:
        credenciales = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIALES_GOOGLE_SHEETS)
        cliente = gspread.authorize(credenciales)
        hoja_calculo = cliente.open_by_key(ID_GOOGLE_SHEETS).sheet1
        zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_hora = datetime.now(tz=zona_horaria)
        fecha_hora_str = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fila_gasto = [fecha_hora_str, monto, forma_pago, categoria, descripcion, autor]
        hoja_calculo.append_row(fila_gasto)

        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Gasto registrado correctamente.\n\nDetalles del gasto:\nMonto: ${monto}\nForma de Pago: {forma_pago}\nCategoría: {categoria}\nDescripción: {descripcion}')
        
        # Eliminar mensajes de monto y descripción
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['monto_message_id'])
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['descripcion_message_id'])
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error al registrar el gasto: {e}')

    context.user_data['fase'] = 'monto'  # Resetear la fase a 'monto' para el próximo gasto

# Configurar el Updater con el token del bot de Telegram
actualizador = Updater(token=TELEGRAM_TOKEN, use_context=True)

# Obtener el despachador del Updater
despachador = actualizador.dispatcher

# Manejador para el comando /start
manejador_inicio = CommandHandler('start', iniciar)
despachador.add_handler(manejador_inicio)

# Manejador para los mensajes de texto
manejador_mensaje = MessageHandler(Filters.text & (~Filters.command), manejar_mensaje)
despachador.add_handler(manejador_mensaje)

# Manejador para la selección de formas de pago
manejador_callback_forma_pago = CallbackQueryHandler(seleccionar_forma_pago, pattern='^(' + '|'.join(FORMAS_PAGO) + ')$')
despachador.add_handler(manejador_callback_forma_pago)

# Manejador para la selección de categorías
manejador_callback_categoria = CallbackQueryHandler(seleccionar_categoria, pattern='^(' + '|'.join(CATEGORIAS_GASTOS) + ')$')
despachador.add_handler(manejador_callback_categoria)

# Iniciar el bot
actualizador.start_polling()
actualizador.idle()
