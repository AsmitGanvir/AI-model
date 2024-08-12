import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime

# List of 20 companies
companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'INTC', 'AMD',
             'IBM', 'ORCL', 'CSCO', 'ADBE', 'PYPL', 'CRM', 'QCOM', 'TXN', 'AVGO', 'AMAT']

# Function to fetch data and plot the selected company's candlestick chart with strategies
def plot_chart():
    company = selected_company.get()
    start_date = start_cal.get_date()
    end_date = end_cal.get_date()
    df = yf.download(company, start=start_date, end=end_date)
    
    # Calculate Moving Averages
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['Close'].rolling(window=20).std()
    
    # Calculate MACD
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Generate Buy/Sell signals based on Moving Average Crossover
    df['Buy_Signal'] = np.where((df['SMA20'] > df['SMA50']) & (df['SMA20'].shift(1) <= df['SMA50'].shift(1)), df['Close'], np.nan)
    df['Sell_Signal'] = np.where((df['SMA20'] < df['SMA50']) & (df['SMA20'].shift(1) >= df['SMA50'].shift(1)), df['Close'], np.nan)
    
    # Determine holding periods
    df['Position'] = np.where(df['Buy_Signal'].notna(), 1, np.nan)
    df['Position'] = np.where(df['Sell_Signal'].notna(), 0, df['Position'])
    df['Position'] = df['Position'].ffill().fillna(0)
    df['Hold_Period'] = df['Position'].diff().fillna(0).abs().cumsum()
    
    # Plot the chart with strategies and signals
    apds = [mpf.make_addplot(df['SMA20'], color='blue'),
            mpf.make_addplot(df['SMA50'], color='red'),
            mpf.make_addplot(df['RSI'], panel=1, color='purple', secondary_y=False),
            mpf.make_addplot(df['BB_Upper'], color='orange'),
            mpf.make_addplot(df['BB_Lower'], color='orange'),
            mpf.make_addplot(df['MACD'], panel=2, color='green'),
            mpf.make_addplot(df['Signal_Line'], panel=2, color='red'),
            mpf.make_addplot(df['Buy_Signal'], type='scatter', marker='^', color='green', markersize=100),
            mpf.make_addplot(df['Sell_Signal'], type='scatter', marker='v', color='red', markersize=100)]
    
    mpf.plot(df, type='candle', title=f'Candlestick Chart for {company}', ylabel='Price', style='yahoo', addplot=apds)
    
    # Display holding periods with suggested dates
    buy_dates = df[df['Buy_Signal'].notna()].index.strftime('%Y-%m-%d').tolist()
    sell_dates = df[df['Sell_Signal'].notna()].index.strftime('%Y-%m-%d').tolist()
    holding_message = f"Suggested Buy Dates: {buy_dates}\nSuggested Sell Dates: {sell_dates}"
    tk.messagebox.showinfo("Holding Periods", holding_message)

# Create the main window
root = tk.Tk()
root.title("Stock Candlestick Charts with Strategies")

# Create a dropdown menu to select the company
selected_company = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=selected_company, values=companies)
dropdown.grid(column=0, row=0, padx=10, pady=10)
dropdown.current(0)

# Create calendar widgets to select the date range
start_label = tk.Label(root, text="Start Date:")
start_label.grid(column=0, row=1, padx=10, pady=10)
start_cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
start_cal.grid(column=1, row=1, padx=10, pady=10)

end_label = tk.Label(root, text="End Date:")
end_label.grid(column=0, row=2, padx=10, pady=10)
end_cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
end_cal.grid(column=1, row=2, padx=10, pady=10)

# Create a button to plot the chart
plot_button = tk.Button(root, text="Plot Chart", command=plot_chart)
plot_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()
