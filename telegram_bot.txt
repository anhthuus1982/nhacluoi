from telegram.ext import Updater, CommandHandler

class TelegramBot:
    def __init__(self, token, exchange):
        self.updater = Updater(token, use_context=True)
        self.chat_id = None
        self.exchange = exchange
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("status", self.status))

    def start(self, update, context):
        allowed_ids = [123456789]  # Thay bang chat_id cua ban
        if update.message.chat_id not in allowed_ids:
            update.message.reply_text('Khong co quyen truy cap!')
            return
        self.chat_id = update.message.chat_id
        update.message.reply_text('Bot da khoi dong!')

    def status(self, update, context):
        balance = self.exchange.get_balance()
        update.message.reply_text(f'So du: {balance} USDT')

    def send_message(self, message):
        if self.chat_id:
            self.updater.bot.send_message(self.chat_id, message)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
