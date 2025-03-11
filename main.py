import os
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from dotenv import load_dotenv
import logging
import threading
import signal
import time
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import SYMBOL, AMOUNT
from exchange import Exchange
from indicators import Indicators
from model import TradingModel
from database import Database
from telegram_bot import TelegramBot
from ws_manager import WebSocketManager
from backtest import Backtest

logging.basicConfig(filename='bot.log', level=logging.INFO)

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot Control Panel")
        self.running = False
        self.trades_buffer = []
        self.prices = []

        # Khoi tao cac thanh phan
        load_dotenv()
        self.exchange = Exchange(os.getenv('API_KEY'), os.getenv('API_SECRET'))
        self.indicators = Indicators(self.exchange)
        self.model = TradingModel(self.indicators)
        self.db = Database()
        self.telegram = TelegramBot(os.getenv('TELEGRAM_TOKEN'), self.exchange)
        self.ws_manager = WebSocketManager()
        self.password = "123456"  # Thay bang mat khau cua ban

        # GUI Components
        tk.Label(root, text="Mat khau:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        self.auth_button = tk.Button(root, text="Xac thuc", command=self.authenticate)
        self.auth_button.pack(pady=5)

        self.start_button = tk.Button(root, text="Khoi dong Bot", command=self.start_bot, state='disabled')
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Dung Bot", command=self.stop_bot, state='disabled')
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(root, text="Trang thai: Dung")
        self.status_label.pack(pady=5)

        self.balance_label = tk.Label(root, text="So du: 0 USDT")
        self.balance_label.pack(pady=5)

        self.drawdown_label = tk.Label(root, text="Drawdown: 0%")
        self.drawdown_label.pack(pady=5)

        tk.Label(root, text="Stop Loss (%):").pack()
        self.sl_entry = tk.Entry(root)
        self.sl_entry.insert(0, "2")
        self.sl_entry.pack(pady=5)

        tk.Label(root, text="Take Profit (%):").pack()
        self.tp_entry = tk.Entry(root)
        self.tp_entry.insert(0, "3")
        self.tp_entry.pack(pady=5)

        self.trades_button = tk.Button(root, text="Xem Giao Dich", command=self.view_trades)
        self.trades_button.pack(pady=5)

        self.backtest_button = tk.Button(root, text="Backtest", command=self.run_backtest)
        self.backtest_button.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(root, width=50, height=10)
        self.log_text.pack(pady=5)

        # Bieu do gia
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=5)

        # Queue cho log
        self.log_queue = queue.Queue(maxsize=100)
        self.root.after(100, self.process_log_queue)

        # Chay Telegram va bao cao
        threading.Thread(target=self.telegram.run, daemon=True).start()
        threading.Thread(target=self.periodic_report, daemon=True).start()

        # Xu ly dong cua so
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        try:
            self.log_queue.put(message)
        except queue.Full:
            print("Log queue day, bo qua log!")

    def process_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.insert(tk.END, f"{time.ctime()}: {message}\n")
            self.log_text.see(tk.END)
        self.root.after(100, self.process_log_queue)

    def authenticate(self):
        if self.password_entry.get() == self.password:
            otp = self.telegram.send_otp()
            otp_input = simpledialog.askstring("OTP", "Nhap ma OTP:")
            if otp_input == otp:
                self.start_button.config(state='normal')
                self.auth_button.config(state='disabled')
                self.password_entry.config(state='disabled')
                self.log("Xac thuc thanh cong")
            else:
                self.log("Ma OTP sai!")
        else:
            self.log("Mat khau sai!")

    def handle_price(self, price):
        if not self.running:
            return
        self.prices.append(price)
        if len(self.prices) > 50:  # Gioi han bieu do
            self.prices.pop(0)
        self.update_chart()
        threading.Thread(target=self._execute_trade, args=(price,), daemon=True).start()

    def _execute_trade(self, price):
        sl_percent = float(self.sl_entry.get()) / 100
        tp_percent = float(self.tp_entry.get()) / 100
        decision = self.model.decide(SYMBOL, price, sl_percent, tp_percent)
        if decision:
            try:
                order = self.exchange.create_order(SYMBOL, decision['side'], AMOUNT, 
                                                 decision['stop_loss'], decision['take_profit'])
                if order:
                    self.trades_buffer.append((time.ctime(), SYMBOL, decision['side'], price, AMOUNT))
                    msg = f"Dat lenh {decision['side']} tai {price}, SL: {decision['stop_loss']}, TP: {decision['take_profit']}"
                    self.log(msg)
                    self.telegram.send_message(msg)
                    if len(self.trades_buffer) >= 10:
                        self.db.save_trades_batch(self.trades_buffer)
                        self.trades_buffer = []
            except Exception as e:
                logging.error(f"Loi thuc thi lenh: {e}")
                self.log(f"Loi: {e}")

    def update_chart(self):
        self.ax.clear()
        self.ax.plot(self.prices, label='Gia')
        self.ax.legend()
        self.canvas.draw()

    def start_bot(self):
        if not self.running:
            self.running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Trang thai: Dang chay")
            self.ws_manager.add_client(SYMBOL, self.handle_price)
            self.log("Bot da khoi dong")

    def stop_bot(self):
        if self.running:
            self.running = False
            self.ws_manager.stop()
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.status_label.config(text="Trang thai: Dung")
            self.log("Bot da dung")

    def periodic_report(self):
        while True:
            balance = self.exchange.get_balance()
            drawdown = self.exchange.check_drawdown() * 100
            trades = self.db.get_trades()
            total_trades = len(trades)
            self.balance_label.config(text=f"So du: {balance} USDT")
            self.drawdown_label.config(text=f"Drawdown: {drawdown:.2f}%")
            self.telegram.send_message(f"Bao cao: So du: {balance} USDT, Drawdown: {drawdown:.2f}%, Tong giao dich: {total_trades}")
            self.log(f"Bao cao: So du: {balance} USDT, Drawdown: {drawdown:.2f}%, Giao dich: {total_trades}")
            time.sleep(3600)

    def view_trades(self):
        trades = self.db.get_trades().tail(5).to_string()
        self.log(f"Giao dich gan day:\n{trades}")

    def run_backtest(self):
        backtest = Backtest(self.exchange, SYMBOL)
        final_balance, trades = backtest.run(float(self.sl_entry.get()) / 100, float(self.tp_entry.get()) / 100)
        self.log(f"Ket qua backtest: So du cuoi: {final_balance} USDT, Tong giao dich: {len(trades)}")

    def on_closing(self):
        self.stop_bot()
        self.db.close()
        self.root.destroy()

    def signal_handler(self, sig, frame):
        self.on_closing()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x800")
    root.resizable(True, True)
    app = TradingBotGUI(root)
    signal.signal(signal.SIGINT, app.signal_handler)
    root.mainloop()
