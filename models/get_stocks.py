import requests
import pandas as pd
import pyodbc

css_styles = """.my-table-style {background-color: lightgrey;font-size:x-small;text-align-last:start;}"""

class stock_data:
    def __init__(self, company, currentPrice):
        self.company = company
        self.currentPrice = currentPrice

    def get_data_from_api(self):
        my_dict = {}
        server = 'sqldemovin.database.windows.net'
        database = 'projects'
        username = 'abc'
        password = 'Venkatesh08!'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        for com in self.company:
            url = "https://stock.indianapi.in/stock"
            querystring = {"name" :com}
            headers = {"X-Api-Key": "sk-live-XumgPDECumxE4Be5bGhgzUsjvNjkgxldoqr8vqph"}
            response = requests.get(url, headers=headers, params=querystring)
            df = response.json()
            my_dict.update({com: df.get(self.currentPrice)})
        df = pd.DataFrame(my_dict).T
        df.index.name = 'Company'
        df = df.reset_index()
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            query = f"IF OBJECT_ID('stock_price', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0"
            result = cursor.execute(query).fetchone()[0]
            if result == 1:
                cursor.execute(query)
                conn.commit()
                data = df.values.tolist()
                cursor.execute('DELETE FROM stock_price')
                cursor.executemany('''INSERT INTO stock_price (Company, BSE, NSE) VALUES (?, ?, ?)''', data)
            else:
                query = '''CREATE TABLE stock_price ( Company NVARCHAR(255), BSE     NVARCHAR(255), NSE     NVARCHAR(255) )'''
                cursor.execute(query)
                conn.commit()
                data = df.values.tolist()
                cursor.executemany('''INSERT INTO stock_price (Company, BSE, NSE) VALUES (?, ?, ?)''', data)
            # html_table = df.to_html(classes='my-table-style')
            # html_with_style = f'<style>{css_styles}</style>\n{html_table}'
            conn.commit()
            # Close the cursor and connection
            cursor.close()
            conn.close()
        except pyodbc.Error as e:
            print(f'Error: {e}')



    def get_data_from_sql(self):
        print(f"This car is a {self.company} {self.brand} {self.model} with {self.mileage} miles.")