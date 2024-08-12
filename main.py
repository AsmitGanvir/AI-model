import yfinance as yf
import mplfinance as mpf
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

# List of 20 companies
companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'INTC', 'AMD',
             'IBM', 'ORCL', 'CSCO', 'ADBE', 'PYPL', 'CRM', 'QCOM', 'TXN', 'AVGO', 'AMAT']

# Function to fetch data, calculate Bollinger Bands, and plot the selected company's candlestick chart
def plot_chart():
    company = selected_company.get()
    start_date = start_cal.get_date()
    end_date = end_cal.get_date()
    df = yf.download(company, start=start_date, end=end_date)
    
    # Calculate Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['STD20'] * 2)
    df['Lower'] = df['MA20'] - (df['STD20'] * 2)
    
    # Plot candlestick chart with Bollinger Bands
    apds = [mpf.make_addplot(df['Upper'], color='blue'),
            mpf.make_addplot(df['MA20'], color='orange'),
            mpf.make_addplot(df['Lower'], color='blue')]
    
    mpf.plot(df, type='candle', title=f'Candlestick Chart for {company}', ylabel='Price', style='yahoo', addplot=apds)

# Create the main window
root = tk.Tk()
root.title("Stock Candlestick Charts")

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
