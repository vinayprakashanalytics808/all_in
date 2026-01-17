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
    my_com = stock_data(["Tata Steel", "Reliance", "Mukka Proteins"], 'currentPrice')
    my_com.get_data_from_api()
    return jsonify({'message': 'Data updated in DB'})

##"Reliance", "Mukka Proteins"
@app.route('/stock_details', methods=['GET'])
def next_page():
    my_com = stock_data(["Tata Steel", "Reliance", "Mukka Proteins"], 'currentPrice')
    return my_com.get_data_from_api()

if __name__ == '__main__':
    app.run()
