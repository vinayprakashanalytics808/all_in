from flask import Flask, jsonify, render_template
from models.get_stocks import stock_data
import requests
import pandas as pd
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_table', methods=['POST'])
def update_table():
    my_com = stock_data()
    my_com.get_data_from_api(["Tata Steel", "Reliance", "Mukka Proteins", "Tech Mahindra"], 'currentPrice') ##["Tata Steel", "Reliance", "Mukka Proteins", "Tech Mahindra"]

    return jsonify({'message': 'Data updated in DB'})

##"Reliance", "Mukka Proteins"
@app.route('/stock_details', methods=['GET'])
def next_page():
    my_com = stock_data()
    field_list = "'companyName,industry,yearHigh,yearLow', 'BSE,NSE', 'marketCap,high,low,currentDividendYieldCommonStockPrimaryIssueLTM'"
    values = [v.strip() for v in field_list.replace("'", "").split(',')]
    result = ','.join(f"'{v}'" for v in values)
    result = result.split(',')
    result = [v.strip("'") for v in result]
    data = my_com.get_data_from_sql(field_list)
    headers = result  # add column names
    return render_template('stock_details.html', data=data, headers = headers)

if __name__ == '__main__':
    app.run()
