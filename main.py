import os
import tkinter as tk
from exchange import Exchange
from telegram_bot import TelegramBot

class TradingBotGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Trading Bot")
        self.master.geometry("400x300")

        self.exchange = Exchange()
        self.telegram = TelegramBot(os.getenv('TELEGRAM_TOKEN'), self.exchange)

        # GUI elements
        self.label = tk.Label(master, text="Trading Bot Control Panel")
        self.label.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Bot", command=self.start_bot)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Bot", command=self.stop_bot)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(master, text="Status: Stopped")
        self.status_label.pack(pady=10)

        self.balance_label = tk.Label(master, text="Balance: N/A")
        self.balance_label.pack(pady=10)

        self.running = False

    def start_bot(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running")
            self.update_balance()
            self.master.after(5000, self.run_bot)  # Chạy bot mỗi 5 giây
            self.telegram.send_message("Bot started!")

    def stop_bot(self):
        if self.running:
            self.running = False
            self.status_label.config(text="Status: Stopped")
            self.telegram.send_message("Bot stopped!")

    def run_bot(self):
        if self.running:
            self.update_balance()
            # Thêm logic giao dịch ở đây nếu cần
            self.master.after(5000, self.run_bot)

    def update_balance(self):
        balance = self.exchange.get_balance()
        if balance:
            self.balance_label.config(text=f"Balance: {balance.get('USDT', 'N/A')} USDT")
        else:
            self.balance_label.config(text="Balance: Error")

if __name__ == "__main__":
    # Đảm bảo load biến môi trường từ file .env
    from dotenv import load_dotenv
    load_dotenv()

    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
