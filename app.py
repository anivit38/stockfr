from flask import Flask, render_template, request, session, redirect, url_for
import secrets
from stock_analyzer import StockAnalyzer
import os
import logging

app = Flask(__name__)

# Correctly retrieve the environment variables
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
FRED_API_KEY = os.environ.get('FRED_API_KEY')

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    logging.debug('Home page accessed')
    return render_template('home.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    logging.debug('Analyze page accessed')
    if request.method == 'POST':
        stock_name = request.form['stock_name']
        intent = request.form['intent']
        logging.debug(f'Form data received - Stock Name: {stock_name}, Intent: {intent}')
        try:
            # Initialize the StockAnalyzer with your FRED API key
            analyzer = StockAnalyzer(fred_api_key=FRED_API_KEY)

            analyzer.set_user_intent(intent)

            stock_data = analyzer.get_stock_data(stock_name)
            if stock_data is None:
                logging.error('Failed to retrieve stock data')
                return render_template('result.html', result="Failed to retrieve data. Please check the stock symbol and try again.")

            analyzer.perform_analysis(stock_data)

            advice, movement = analyzer.evaluate_stock()

            logging.debug(f'Analysis result - Advice: {advice}, Movement: {movement}')
            return render_template('result.html', result=f"Stock Rating: {advice}. Based on the analysis, the stock's {movement}.")
        except Exception as e:
            logging.exception('An error occurred during analysis')
            return render_template('result.html', result="An error occurred during analysis. Please try again.")
    return render_template('analyze.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
