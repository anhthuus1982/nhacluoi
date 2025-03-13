import os
from telegram import Bot
from telegram.ext import Application

class TelegramBot:
    def __init__(self, token, exchange):
        self.token = token
        self.exchange = exchange
        self.bot = Bot(token)
        self.chat_id = os.getenv('CHAT_ID')
        self.application = Application.builder().token(token).build()

    def send_message(self, message):
        try:
            self.application.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"Sent Telegram message: {message}")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
