import requests
import pandas as pd
import pyodbc
from datetime import datetime
import json

css_styles = """.my-table-style {background-color: lightgrey;font-size:small;text-align-last:start;font-family:math}"""

class stock_data:
    def __init__(self):
        self.company = None
        self.currentPrice = None
        self.server = 'sqldemovin.database.windows.net'
        self.database = 'projects'
        self.username = 'abc'
        self.password = 'Venkatesh08!'
        self.connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'


    def get_data_from_api(self, company, currentPrice):
        my_dict = {}
        self.company = company
        self.currentPrice = currentPrice
        for com in self.company:
            url = "https://stock.indianapi.in/stock"
            querystring = {"name" :com}
            headers = {"X-Api-Key": "sk-live-XumgPDECumxE4Be5bGhgzUsjvNjkgxldoqr8vqph"}
            response = requests.get(url, headers=headers, params=querystring)
            df = response.json()
            json_data = json.dumps(df)
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            query = f"IF OBJECT_ID('company_details', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0"
            result = cursor.execute(query).fetchone()[0]
            if result == 1:
                #cursor.execute('DELETE FROM company_details')
                cursor.execute('''INSERT INTO company_details (data, created_at, company) VALUES (?, ?, ?)''',json_data, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), com)
                conn.commit()
                # Close the cursor and connection
                # cursor.close()
                # conn.close()
            else:
                cursor.execute('''CREATE TABLE company_details (data TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, company NVARCHAR(255))''')
                cursor.execute('''INSERT INTO company_details (data, created_at, company) VALUES (?, ?, ?)''',
                               json_data, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), com)
                conn.commit()
                # Close the cursor and connection
                # cursor.close()
                # conn.close()
            cursor.execute('''delete asd from (SELECT *, ROW_NUMBER() OVER (PARTITION BY company ORDER BY created_at desc) as rank FROM [company_details]) asd where [rank] > 1''')
            conn.commit()
            cursor.close()
            conn.close()

    def get_data_from_sql(self, fields):
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        self.fields = fields
        query = '''EXEC sp_PivotCompanyData '''+ self.fields +''';'''
        cursor.execute(query)
        # Fetch results
        rows = cursor.fetchall()
        conn.close()
        print('connection closed :' + str(conn.closed))
        col_list = []
        for i in range(len(cursor.description)):
            col_list.append(cursor.description[i][0])

        f = []
        for i in rows:
            asd = tuple(j for j in i)
            f.append(asd)

        final_df = pd.DataFrame(f, columns=col_list)
        df = final_df.values.tolist()
        # html_table = final_df.to_html(classes='my-table-style')
        # html_with_style = f'<style>{css_styles}</style>\n{html_table}'
        return df