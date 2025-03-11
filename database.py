import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_name='trading_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                amount REAL
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON trades (timestamp)')
        self.conn.commit()

    def save_trade(self, timestamp, symbol, side, price, amount):
        try:
            self.cursor.execute('''
                INSERT INTO trades (timestamp, symbol, side, price, amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, symbol, side, price, amount))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Loi database: {e}")

    def save_trades_batch(self, trades):
        try:
            self.cursor.executemany('''
                INSERT INTO trades (timestamp, symbol, side, price, amount)
                VALUES (?, ?, ?, ?, ?)
            ''', trades)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Loi batch save: {e}")

    def get_trades(self):
        return pd.read_sql_query("SELECT * FROM trades", self.conn)

    def close(self):
        self.conn.close()
