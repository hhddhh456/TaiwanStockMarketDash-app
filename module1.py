import sqlite3
conn = sqlite3.connect('newstock_data.db')  # 檔名路徑務必完全一致
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)
conn.close()

import os
print(os.path.abspath("newstock_data.db"))
