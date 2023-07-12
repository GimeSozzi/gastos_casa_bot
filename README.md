# GASTOS CASA BOT

Este proyecto consiste en un bot de Telegram llamado "Gastos Casa Bot" que permite a los usuarios ingresar y registrar gastos en una planilla de Google Sheets. El bot recibe los gastos a través de mensajes enviados por los usuarios y los guarda en la planilla con la siguiente información: fecha, monto, categoría y descripción.

## Requisitos
Antes de utilizar el bot, es necesario realizar las siguientes configuraciones:

1. Crear un archivo secrets.py y almacenar en él la siguiente información:

`TELEGRAM_TOKEN = "TOKEN_DEL_BOT_DE_TELEGRAM"`
`CREDENCIALES_GOOGLE_SHEETS = "RUTA_AL_ARCHIVO_DE_CREDENCIALES_JSON"`
`ID_GOOGLE_SHEETS = "ID_DE_LA_PLANILLA_DE_GOOGLE_SHEETS"`
`USUARIOS_AUTORIZADOS = ["ID_USUARIO_1", "ID_USUARIO_2", ...]`

Asegúrate de reemplazar los valores entre comillas con la información correspondiente. El TOKEN_DEL_BOT_DE_TELEGRAM es el token de acceso al bot de Telegram, las CREDENCIALES_GOOGLE_SHEETS son las credenciales de la cuenta de servicio de Google Sheets en formato JSON, el ID_GOOGLE_SHEETS es el ID de la planilla de Google Sheets donde se guardarán los gastos y los ID_USUARIO_X son los IDs de los usuarios autorizados a utilizar el bot.

2. Instalar las dependencias necesarias ejecutando el siguiente comando:


`pip install python-telegram-bot gspread oauth2client pytz`


Asegúrate de tener instalado Python y pip en tu sistema.

## Uso

Para utilizar el bot, sigue los siguientes pasos:


1. Ejecuta el script gastos_casa_bot.py en tu entorno de Python.


`python gastos_casa_bot.py`


2. Inicia una conversación con el bot de Telegram y envía el comando /start.


El bot verificará tu ID de usuario y te enviará un mensaje de bienvenida junto con el formato de ingreso de los gastos.


3. Ingresa los gastos en el siguiente formato y orden: $0000.00, Categoría, Descripción (opcional).

Por ejemplo:

`$50.00, Alimentación, Compra en el supermercado`

Asegúrate de incluir el símbolo de peso $ antes del monto.


4. El bot guardará automáticamente los datos del gasto en la planilla de Google Sheets y te enviará un mensaje de confirmación.






