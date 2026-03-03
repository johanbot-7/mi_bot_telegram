

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from datetime import datetime

# 🔑 CONFIG
TOKEN = "8527070285:AAGsLZy6Gff0IYbXLLpvAFM-6P-S0Jki_nc"
ADMIN_ID = 7957443258
USUARIOS_PERMITIDOS = {7957443258, 7811608909}


menu_text = """━━━━━━━━━━━━━
OPCIONES DISPONIBLES🎮

1. Cromar calipers
2. Cromar luces
3. Ventanas GG
4. Modificar 1 HP
5. Cromar rines
6. Cromar aleron
7. Traspasar auto
8. Modificar shiftime
9. Quitar parachoques
10. Auto 6 segundos
11. Modificar ID
12. 30k / 50M
13. Comprar casas
14. Cuenta full
15. Auto Full GG
━━━━━━━━━━━━━"""

FORMULARIOS = {
    "1": ["Correo", "Contraseña", "Modelo"],
    "2": ["Correo", "Contraseña", "Modelo"],
    "3": ["Correo", "Contraseña", "Modelo"],
    "4": ["Correo", "Contraseña"],
    "5": ["Correo", "Contraseña", "Modelo"],
    "6": ["Correo", "Contraseña", "Modelo"],
    "7": ["Correo", "Contraseña"],
    "8": ["Correo", "Contraseña"],
    "9": ["Correo", "Contraseña"],
    "10": ["Correo", "Contraseña"],
    "11": ["Correo", "Contraseña"],
    "12": ["Correo", "Contraseña"],
    "13": ["Correo", "Contraseña"],
    "14": ["Correo", "Contraseña"],
    "15": ["Correo", "Contraseña", "Modelo"],
}

# 🔥 SOLO ESTOS PIDEN COLOR
OPCIONES_CON_COLOR = {"1","2","3","5","6","15"}

user_states = {}

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in USUARIOS_PERMITIDOS:
        await update.message.reply_text("❌ No tienes acceso.")
        return

    await update.message.reply_text(menu_text)

# 🧠 MANEJO
async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    if user_id not in USUARIOS_PERMITIDOS:
        return

    # 👉 Elegir opción
    if texto in FORMULARIOS:
        user_states[user_id] = {
            "opcion": texto,
            "preguntas": FORMULARIOS[texto],
            "respuestas": [],
            "paso": 0
        }

        await update.message.reply_text(f"{FORMULARIOS[texto][0]}:")
        return

    # 👉 Responder preguntas
    if user_id in user_states:
        estado = user_states[user_id]

        estado["respuestas"].append(texto)
        estado["paso"] += 1

        # 👉 Siguiente pregunta
        if estado["paso"] < len(estado["preguntas"]):
            siguiente = estado["preguntas"][estado["paso"]]
            await update.message.reply_text(f"{siguiente}:")
            return

        # 👉 TERMINÓ FORMULARIO
        opcion = str(estado["opcion"]).strip()

        # 🔥 SI NECESITA COLOR → MOSTRAR BOTONES
        if opcion in OPCIONES_CON_COLOR:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔴 Rojo", callback_data="color_rojo"),
                    InlineKeyboardButton("🔵 Azul", callback_data="color_azul")
                ],
                [
                    InlineKeyboardButton("🟢 Verde", callback_data="color_verde"),
                    InlineKeyboardButton("⚪ Blanco", callback_data="color_blanco")
                ]
            ])

            estado["esperando_color"] = True

            await update.message.reply_text(
                "🎨 Selecciona un color:",
                reply_markup=keyboard
            )
            return

        # 👉 SI NO USA COLOR → ENVIAR DIRECTO
        await enviar_admin(update, context, estado, "N/A")
        del user_states[user_id]

# 🎨 BOTÓN DE COLORES
async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_states:
        return

    estado = user_states[user_id]

    if "esperando_color" not in estado:
        return

    color = query.data.replace("color_", "")

    await enviar_admin(query, context, estado, color)

    await query.edit_message_text(f"✅ Color seleccionado: {color}")

    del user_states[user_id]

# 📤 ENVIAR AL ADMIN
async def enviar_admin(update_or_query, context, estado, color):
    # 🔥 detectar tipo de objeto correctamente
    if hasattr(update_or_query, "effective_user"):
        user = update_or_query.effective_user
    else:
        user = update_or_query.from_user

    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")

    datos = f"""📥 NUEVO PEDIDO

👤 Usuario: @{user.username}
🆔 ID: {user.id}
📅 Fecha: {fecha}
⏰ Hora: {hora}

📌 Opción: {estado['opcion']}
🎨 Color: {color}
"""

    for p, r in zip(estado["preguntas"], estado["respuestas"]):
        datos += f"{p}: {r}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Completado", callback_data=f"done_{user.id}")]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=datos,
        reply_markup=keyboard
    )

    # 🔥 enviar confirmación al usuario
    await context.bot.send_message(
        chat_id=user.id,
        text="✅ Datos enviados correctamente.\n\n" + menu_text
    )
# ✅ BOTÓN ADMIN
async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Tu proceso ha sido completado."
    )

    await query.edit_message_text(query.message.text + "\n\n✅ COMPLETADO")

# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))
app.add_handler(CallbackQueryHandler(color, pattern="^color_"))
app.add_handler(CallbackQueryHandler(boton))

app.run_polling()