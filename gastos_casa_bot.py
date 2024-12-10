import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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

# Inicializar el Scheduler
scheduler = BackgroundScheduler()

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
    texto_gasto = update.message.text.strip()

    # Verificar si el monto comienza con el signo "$"
    if texto_gasto.startswith('$'):
        try:
            # Extraer el número y convertirlo a float
            monto = float(texto_gasto[1:].replace(',', '.'))  # Ignorar el "$" y convertir la coma decimal a punto
            context.user_data['monto'] = monto
            context.user_data['fase'] = 'forma_pago'
            context.user_data['monto_message_id'] = update.message.message_id  # Guardar el ID del mensaje del monto
            mostrar_formas_pago(update, context)
        except ValueError:
            # Error si no se puede convertir el número
            context.bot.send_message(chat_id=update.effective_chat.id, text='El monto del gasto no tiene un formato válido. Asegúrate de ingresarlo como "$0000.00".')
    else:
        # Error si no comienza con el signo "$"
        context.bot.send_message(chat_id=update.effective_chat.id, text='Por favor, ingresa el monto en el formato correcto: "$0000.00".')


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
        hoja_calculo = cliente.open_by_key(ID_GOOGLE_SHEETS)
        
        zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_hora = datetime.now(tz=zona_horaria)
        mes_actual = fecha_hora.strftime('%B %Y')

        # Verificar si existe la hoja del mes actual, si no, crearla
        try:
            hoja_mes_actual = hoja_calculo.worksheet(mes_actual)
        except gspread.exceptions.WorksheetNotFound:
            hoja_mes_actual = hoja_calculo.add_worksheet(title=mes_actual, rows="100", cols="20")
            # Agregar encabezados
            hoja_mes_actual.append_row(["Fecha", "Monto", "Forma de Pago", "Categoría", "Descripción", "Autor"])

        fecha_hora_str = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fila_gasto = [fecha_hora_str, monto, forma_pago, categoria, descripcion, autor]
        hoja_mes_actual.append_row(fila_gasto)

        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Gasto registrado correctamente.\n\nDetalles del gasto:\nMonto: ${monto}\nForma de Pago: {forma_pago}\nCategoría: {categoria}\nDescripción: {descripcion}')
        
        # Eliminar mensajes de monto y descripción
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['monto_message_id'])
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['descripcion_message_id'])
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error al registrar el gasto: {e}')

    context.user_data['fase'] = 'monto'  # Resetear la fase a 'monto' para el próximo gasto

# Función para calcular y enviar el resumen de gastos en cualquier momento
def resumen(update, context):
    id_usuario = update.message.from_user.id
    if id_usuario in USUARIOS_AUTORIZADOS:
        try:
            credenciales = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIALES_GOOGLE_SHEETS)
            cliente = gspread.authorize(credenciales)
            hoja_calculo = cliente.open_by_key(ID_GOOGLE_SHEETS)

            hoja = hoja_calculo.sheet1  # Trabaja siempre con "Hoja 1"
            datos = hoja.get_all_records()

            # Obtener el mes y año actuales
            zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
            fecha_actual = datetime.now(tz=zona_horaria)
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year

            # Inicializar totales por forma de pago
            totales_forma_pago = {'EFECTIVO': 0.0, 'DÉBITO/TRANSFERENCIA': 0.0, 'CRÉDITO': 0.0, 'SIN ESPECIFICAR': 0.0}

            # Inicializar totales por categoría
            totales_categorias = {categoria: 0.0 for categoria in CATEGORIAS_GASTOS}

            # Procesar los datos
            for fila in datos:
                try:
                    # Validar si la fila tiene un formato válido
                    if not fila['Fecha'] or not fila['Monto'] or not fila['Categoria']:
                        print(f"Ignorando fila no válida: {fila}")
                        continue  # Saltar filas con datos irrelevantes

                    # Limpieza del valor de Monto
                    monto_texto = fila.get('Monto', '').strip()  # Eliminar espacios
                    monto_limpio = monto_texto.replace('$', '').replace('.', '').replace(',', '.')
                    monto = float(monto_limpio)  # Convertir el texto limpio a número flotante

                    # Verificar el formato de la fecha y filtrar por mes y año actuales
                    fecha = datetime.strptime(fila['Fecha'], '%Y-%m-%d %H:%M:%S')
                    if fecha.month != mes_actual or fecha.year != anio_actual:
                        continue  # Ignorar filas de otros meses

                    # Manejar valores faltantes en "Forma de Pago"
                    forma_pago = fila.get('Forma de Pago', '').strip()
                    if not forma_pago:
                        forma_pago = "SIN ESPECIFICAR"  # Asignar un valor por defecto si está vacío

                    categoria = fila.get('Categoria', '').strip()

                    # Sumar al total por forma de pago
                    if forma_pago in totales_forma_pago:
                        totales_forma_pago[forma_pago] += monto

                    # Sumar al total por categoría
                    if categoria in totales_categorias:
                        totales_categorias[categoria] += monto
                except (ValueError, KeyError) as e:
                    print(f"Error procesando la fila: {fila}, Detalle: {e}")
                    continue  # Ignorar filas con errores

            # Crear el mensaje de resumen
            mensaje_resumen = f"Resumen de gastos de {fecha_actual.strftime('%B %Y')}:\n\n"

            # Agregar totales por forma de pago
            mensaje_resumen += "Totales por Forma de Pago:\n"
            for forma_pago, total in totales_forma_pago.items():
                mensaje_resumen += f"  {forma_pago}: ${total:.2f}\n"

            # Agregar totales por categorías
            mensaje_resumen += "\nTotales por Categorías:\n"
            for categoria, total in totales_categorias.items():
                mensaje_resumen += f"  {categoria}: ${total:.2f}\n"

            # Enviar el mensaje
            context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje_resumen)
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al calcular el resumen de gastos: {e}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No estás autorizado para usar este comando.")

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

# Manejador para verificar resumen manualmente
manejador_resumen = CommandHandler('resumen', resumen)
despachador.add_handler(manejador_resumen)

# Iniciar el Scheduler
scheduler.start()

# Iniciar el bot
actualizador.start_polling()
actualizador.idle()
