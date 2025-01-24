import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def calculate_profit_loss(buy_prices, sell_prices, initial_capital, num_stocks):
    total_profit_loss = 0
    capital = initial_capital
    stocks = 0
    total_amount = 0

    for buy_time, buy_price in buy_prices:
        amount = buy_price * num_stocks
        total_amount += amount
        capital -= amount
        stocks += num_stocks

    for sell_time, sell_price in sell_prices:
        amount = sell_price * num_stocks
        total_amount -= amount
        capital += amount
        stocks -= num_stocks
        total_profit_loss = capital - initial_capital

    return total_profit_loss, capital, stocks, total_amount

ticker_symbol = 'WBD'
start_date = '2025-01-01'
initial_capital = float(input("Enter initial capital: "))
num_stocks = int(input("Enter the number of stocks you want to buy: "))

data = yf.download(ticker_symbol, start=start_date, interval='1d')

data['SMA_3'] = data['Close'].rolling(window=3).mean()

current_position = None
buy_prices = []
sell_prices = []

for date in data.index:
    day_data = yf.download(ticker_symbol, start=date, end=date + pd.Timedelta(days=1), interval='15m')

    first_15min_low = day_data['Low'].iloc[0]
    first_15min_high = day_data['High'].iloc[0]
    closing_price = day_data['Close'].iloc[-1]

    if current_position is None:
        for index, low_price in enumerate(day_data['Low']):
            if low_price < first_15min_low:
                buy_price = low_price
                buy_time = day_data.index[index]
                buy_prices.append((buy_time, buy_price))
                current_position = 'Buy'
                break

        if current_position is None:
            buy_price = closing_price
            buy_time = day_data.index[-1]
            buy_prices.append((buy_time, buy_price))
            current_position = 'Buy'

    if current_position == 'Buy':
        sell_opportunity = False
        for index, high_price in enumerate(day_data['High']):
            if high_price > first_15min_high:
                sell_opportunity = True
                if buy_prices:
                    sell_price = high_price
                    sell_time = day_data.index[index]
                    if sell_time > buy_time:
                        sell_prices.append((sell_time, sell_price))
                        current_position = None
                        break
        if not sell_opportunity and date == data.index[-1]:
            if not sell_prices:
                buy_price = closing_price
                buy_time = day_data.index[-1]
                buy_prices.append((buy_time, buy_price))

total_profit_loss, updated_capital, stocks, total_amount = calculate_profit_loss(buy_prices, sell_prices, initial_capital, num_stocks)

print("Buy and Sell Decisions:")
print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
print("|   Date   |   Time    |   Action  |   Price  |  Number of Stocks |  Total Amount  |             Date   |      Time   |      Action   |  Price   |  Number of Stocks  |  Total Amount  |  Profit/Loss for Cycle  |")
print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
for i in range(max(len(buy_prices), len(sell_prices))):
    buy_row = sell_row = ""
    if i < len(buy_prices):
        buy_time, buy_price = buy_prices[i]
        buy_row = f"| {buy_time.strftime('%Y-%m-%d')} | {buy_time.strftime('%H:%M:%S')} |   Buy    |  {buy_price:.2f}  |        {num_stocks}        |   {buy_price*num_stocks:.2f}   |"
    if i < len(sell_prices):
        sell_time, sell_price = sell_prices[i]
        sell_row = f"| {sell_time.strftime('%Y-%m-%d')} | {sell_time.strftime('%H:%M:%S')} |  Sell    |  {sell_price:.2f}  |        {num_stocks}        |   {sell_price*num_stocks:.2f}   |"
    print(f"{buy_row.ljust(95)}{sell_row.ljust(96)}{(sell_price-buy_price)*num_stocks:.2f}")

print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

print(f"Total profit/loss at end of table: ${total_profit_loss:.2f}")
print(f"Updated capital: ${updated_capital:.2f}")
print(f"Total stocks remaining: {stocks}")

plt.figure(figsize=(12, 6))

plt.plot(data.index, data['Close'], label='Close Price', color='blue', marker='o', markersize=5)
plt.plot(data.index, data['SMA_3'], label='3-Day SMA', color='black')

# Plot Buy points
buy_times = [buy_time for buy_time, _ in buy_prices]
buy_prices = [buy_price for _, buy_price in buy_prices]
plt.plot(buy_times, buy_prices, 'go-', label='Buy', markersize=7)
for i in range(len(buy_prices)):
    plt.text(buy_times[i], buy_prices[i], f'{buy_prices[i]:.2f}', ha='right', va='bottom')

# Plot Sell points
sell_times = [sell_time for sell_time, _ in sell_prices]
sell_prices = [sell_price for _, sell_price in sell_prices]
plt.plot(sell_times, sell_prices, 'ro-', label='Sell', markersize=7)
for i in range(len(sell_prices)):
    plt.text(sell_times[i], sell_prices[i], f'{sell_prices[i]:.2f}', ha='right', va='bottom')

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Buy and Sell Decisions')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
