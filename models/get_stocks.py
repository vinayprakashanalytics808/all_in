import requests
import pandas as pd
import pyodbc
from datetime import datetime

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
            my_dict.update({com: df.get(self.currentPrice)})

            my_dict[com]['industry'] = df.get('industry')
            my_dict[com]['yearLow'] = df.get('yearLow')
            my_dict[com]['yearHigh'] = df.get('yearHigh')
            my_dict[com]['companyDescription'] = df.get('companyProfile')['companyDescription']

            riskMeter = df.get('riskMeter')

            my_dict[com].update(riskMeter)


        df = pd.DataFrame(my_dict).T
        df.index.name = 'Company'
        df = df.reset_index()
        columns = ['Company', 'BSE', 'NSE', 'industry', 'yearLow', 'yearHigh', 'companyDescription', 'categoryName','stdDev', 'created_at']
        placeholders = ', '.join(['?'] * len(columns))
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            query = f"IF OBJECT_ID('stock_price', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0"
            result = cursor.execute(query).fetchone()[0]
            value_to_append = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if result == 1:
                cursor.execute(query)
                conn.commit()
                data = df.values.tolist()
                value_to_append = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = [inner_list + [value_to_append] for inner_list in data]
                cursor.execute('DELETE FROM stock_price')
                query = f"INSERT INTO stock_price ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.executemany(query, data)
                #cursor.executemany('''INSERT INTO stock_price (Company, BSE, NSE, industry, yearLow, yearHigh, companyDescription, categoryName, stdDev, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

            else:
                query = '''CREATE TABLE stock_price ( Company NVARCHAR(255), 
                                                      BSE NVARCHAR(255), 
                                                      NSE NVARCHAR(255), 
                                                      industry NVARCHAR(255), 
                                                      yearLow NVARCHAR(255), 
                                                      yearHigh NVARCHAR(255), 
                                                      companyDescription NVARCHAR(MAX),
                                                      categoryName NVARCHAR(255),
                                                      stdDev NVARCHAR(255),
                                                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP )'''
                cursor.execute(query)
                conn.commit()
                data = df.values.tolist()
                value_to_append = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = [inner_list + [value_to_append] for inner_list in data]
                query = f"INSERT INTO stock_price ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.executemany(query, data)
            # html_table = df.to_html(classes='my-table-style')
            # html_with_style = f'<style>{css_styles}</style>\n{html_table}'
            conn.commit()
            # Close the cursor and connection
            cursor.close()
            conn.close()
        except pyodbc.Error as e:
            print(f'Error: {e}')



    def get_data_from_sql(self):
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        query = 'select Company, BSE, NSE, industry, yearLow, yearHigh, categoryName, stdDev, created_at from [dbo].[stock_price]'
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
        html_table = final_df.to_html(classes='my-table-style')
        html_with_style = f'<style>{css_styles}</style>\n{html_table}'
        return html_with_style