import pandas as pd
import sqlite3
import os

def convert_files_to_sqlite(file_list, db_name):
    """
    讀取一系列的 CSV 或 Excel 檔案，並將它們轉換為 SQLite 資料庫中的表格。

    :param file_list: 一個包含檔案路徑的列表。
    :param db_name: 要建立的 SQLite 資料庫檔案名稱。
    """
    # 建立或連接到 SQLite 資料庫
    conn = sqlite3.connect(db_name)
    print(f"成功連接到資料庫 '{db_name}'。")

    # 逐一處理列表中的每個檔案
    for file_path in file_list:
        try:
            # 從檔案路徑中獲取不含副檔名的檔名，作為資料表名稱
            table_name = os.path.splitext(os.path.basename(file_path))[0]

            # 根據副檔名選擇合適的讀取方式
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
                print(f"正在讀取 CSV 檔案: {file_path}")
            elif file_path.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
                print(f"正在讀取 Excel 檔案: {file_path}")
            else:
                print(f"不支援的檔案格式: {file_path}，將略過此檔案。")
                continue

            # 將 DataFrame 寫入 SQLite 資料庫
            # if_exists='replace' 表示如果資料表已存在，就覆蓋它
            # 您也可以用 'append' (附加) 或 'fail' (如果存在则失敗)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"成功將 '{file_path}' 的資料寫入到資料表 '{table_name}'。")

        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {file_path}，請檢查檔案是否存在於正確路徑。")
        except Exception as e:
            print(f"處理檔案 {file_path} 時發生錯誤：{e}")

    # 關閉資料庫連線
    conn.close()
    print(f"資料庫 '{db_name}' 已關閉，轉換完成。")

# --- 主程式執行區 ---

# 1. 定義要轉換的檔案列表
#    您只需要將您的檔案名稱加入這個列表中
files_to_process = [
    'TSMC_2330_metrics.csv',
    'INDEX_TWII_metrics.csv',
    'ETF_0050_metrics.csv'
]

# 2. 定義您想建立的資料庫檔案名稱
database_file = 'newstock_data.db'

# 3. 執行轉換函式
convert_files_to_sqlite(files_to_process, database_file)