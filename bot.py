from telegram.ext import Updater, CommandHandler
import requests
import json

# Telegram Bot configuration
# Replace with your actual bot token
TELEGRAM_BOT_TOKEN = '6543149823:AAHNchsL62Stg3ZGllj0T1Kd4uJ-u8ZbACo'
GET_URL = 'http://localhost:8000/?givedata=true'

# Command handlers for the Telegram bot


def update(update, context):
    response = requests.get(GET_URL)
    data = response.text.split(',')
    gas_value = data[0].split(':')[1].strip()
    valve_status = data[1].split(':')[1].strip()
    update.message.reply_text(
        f"Gas value: {gas_value}\nValve status: {valve_status}")


def check_valve(update, context):
    # Replace with your actual URL
    read_url = 'http://localhost:8000/?valvestatusread=true'
    response = requests.get(read_url)
    data = response.text

    if data == '0':
        update.message.reply_text("Valve is open.")
    else:
        update.message.reply_text("Valve is shut.")


def shut_valve(update, context):
    write_url = f'http://localhost:8000/?valvestatus=1&manualoverride=1'
    response = requests.get(write_url)
    if response.status_code == 200:
        update.message.reply_text("Valve shut command sent")
    else:
        update.message.reply_text("Failed to send valve shut command")


def open_valve(update, context):
    write_url = f'http://localhost:8000/?valvestatus=0&manualoverride=0'
    response = requests.get(write_url)
    if response.status_code == 200:
        update.message.reply_text("Valve open command sent")
    else:
        update.message.reply_text("Failed to send valve open command")


def main():
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("update", update))
    dp.add_handler(CommandHandler("shutvalve", shut_valve))
    dp.add_handler(CommandHandler("checkvalve", check_valve))
    dp.add_handler(CommandHandler("openvalve", open_valve))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
