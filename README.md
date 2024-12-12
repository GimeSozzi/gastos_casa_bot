# GASTOS CASA BOT

Este proyecto consiste en un bot de Telegram llamado "Gastos Casa Bot" que permite a los usuarios ingresar y registrar gastos en una planilla de Google Sheets. El bot recibe los gastos a través de mensajes enviados por los usuarios y los guarda en la planilla con la siguiente información: fecha, monto, categoría y descripción.

## Requisitos

Antes de utilizar el bot, es necesario realizar las siguientes configuraciones:

1. Crear un archivo secrets.py y almacenar en él la siguiente información:

`TELEGRAM_TOKEN = "TOKEN_DEL_BOT_DE_TELEGRAM"`

`CREDENCIALES_GOOGLE_SHEETS = "RUTA_AL_ARCHIVO_DE_CREDENCIALES_JSON"`

`ID_GOOGLE_SHEETS = "ID_DE_LA_PLANILLA_DE_GOOGLE_SHEETS"`

`USUARIOS_AUTORIZADOS = ["ID_USUARIO_1", "ID_USUARIO_2", ...]`

Asegúrate de reemplazar los valores entre comillas con la información correspondiente:
- El TOKEN_DEL_BOT_DE_TELEGRAM es el token de acceso al bot de Telegram. 
- Las CREDENCIALES_GOOGLE_SHEETS son las credenciales de la cuenta de servicio de Google Sheets en formato JSON.
- El ID_GOOGLE_SHEETS es el ID de la planilla de Google Sheets donde se guardarán los gastos
- Los ID_USUARIO_X son los IDs de los usuarios autorizados a utilizar el bot.

2. Crear un entorno virtual y activarlo.

3. Instalar las dependencias desde el archivo requirements.txt:

`pip install -r requirements.txt`

Asegúrate de tener instalado Python y pip en tu sistema.

## Uso

Para utilizar el bot, sigue los siguientes pasos:


1. Ejecuta el script gastos_casa_bot.py en tu entorno de Python.


`python gastos_casa_bot.py`


2. Inicia una conversación con el bot de Telegram y envía el comando /start.


El bot verificará tu ID de usuario y te enviará un mensaje de bienvenida junto con el formato de ingreso de los gastos.


3. Ingresa los gastos en el siguiente orden: monto, forma de pago, categoría, y descripción (opcional).

**Paso a paso:**

- Monto: Ingresa el monto del gasto en el formato $0000.00. Asegúrate de incluir el símbolo de peso $ antes del monto.

`$50.00`

- Forma de Pago: El bot te mostrará opciones para seleccionar la forma de pago. Las opciones son: EFECTIVO, DÉBITO/TRANSFERENCIA, CRÉDITO.

- Categoría: El bot te mostrará opciones para seleccionar la categoría del gasto. Las categorías disponibles son: AUTOS, BEBÉS, CASA/OBRA, COMBUSTIBLE, COMIDA, DELIVERY, IMPUESTOS, PRÉSTAMOS, RESTAURANT, ROPA/CALZADO, SALUD, SEGUROS, SERVICIOS, SUPERMERCADO, TARJETAS, VARIOS/OTROS, VIAJES.


- Descripción: Finalmente, ingresa una descripción opcional para el gasto.

`Pago boleta de electricidad`

4. El bot guardará automáticamente los datos del gasto en la planilla de Google Sheets y te enviará un mensaje de confirmación con todos los detalles del gasto.


## Nueva Funcionalidad: Resumen de Gastos

El bot ahora incluye una funcionalidad para generar un resumen mensual de gastos, dividido por formas de pago y categorías. Este resumen puede generarse de manera manual o automática:

Resumen manual
Los usuarios autorizados pueden obtener un resumen en cualquier momento usando el comando:

`/resumen`

El resumen incluye los siguientes detalles:

Totales por cada forma de pago: EFECTIVO, DÉBITO/TRANSFERENCIA, CRÉDITO.
Totales por cada categoría de gasto.

Resumen de gastos de Diciembre 2024:

Totales por Forma de Pago:
  EFECTIVO: $5000.00
  DÉBITO/TRANSFERENCIA: $8000.00
  CRÉDITO: $3000.00

Totales por Categorías:
  COMIDA: $6000.00
  SUPERMERCADO: $5000.00
  DELIVERY: $500.00
  VARIOS/OTROS: $1500.00

## Ejemplo de Interacción Completa

1. Envía /start al bot en Telegram.
2. Ingresa el monto: $50.00.
3. Selecciona la forma de pago: EFECTIVO.
4. Selecciona la categoría: COMIDA.
5. Ingresa una descripción opcional: Compra en el supermercado.
6. Recibirás un mensaje de confirmación indicando que el gasto ha sido registrado correctamente.
7. Más adelante:

Usa /resumen para obtener un resumen de gastos en cualquier momento.
El bot enviará automáticamente el resumen mensual al final del mes.

¡Listo! Ahora tus gastos estarán organizados y resumidos de manera eficiente en Google Sheets. 😊
 
