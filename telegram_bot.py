from telegram.ext import Updater, CommandHandler

class TelegramBot:
    def __init__(self, token, exchange):
        self.updater = Updater(token, use_context=True)
        self.chat_id = None
        self.exchange = exchange
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("status", self.status))
        dp.add_handler(CommandHandler("profit", self.profit))
        dp.add_handler(CommandHandler("trades", self.trades))

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

    def profit(self, update, context):
        # Gia su co ham get_profit trong exchange
        profit = self.exchange.get_profit()
        update.message.reply_text(f'Loi nhuan: {profit} USDT')

    def trades(self, update, context):
        # Gia su co ham get_recent_trades trong exchange
        trades = self.exchange.get_recent_trades()
        update.message.reply_text(f'Giao dich gan day: {trades}')

    def send_message(self, message):
        if self.chat_id:
            self.updater.bot.send_message(self.chat_id, message)

    def send_otp(self):
        import random
        otp = str(random.randint(100000, 999999))
        self.send_message(f"Ma OTP cua ban: {otp}")
        return otp

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
