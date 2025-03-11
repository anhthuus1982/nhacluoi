import sqlite3
import pandas as pd
import os
import time

class Database:
    def __init__(self, db_name='trading_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.backup_database()

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

    def backup_database(self):
        backup_name = f"backup_{time.strftime('%Y%m%d')}.db"
        if not os.path.exists(backup_name):
            with open(backup_name, 'w') as f:
                for line in self.conn.iterdump():
                    f.write('%s\n' % line)

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

    def delete_old_trades(self, days=30):
        cutoff = time.strftime('%Y-%m-%d', time.gmtime(time.time() - days * 86400))
        self.cursor.execute("DELETE FROM trades WHERE timestamp < ?", (cutoff,))
        self.conn.commit()

    def close(self):
        self.conn.close()
