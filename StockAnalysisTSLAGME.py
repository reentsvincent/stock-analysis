import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt


def scrape_revenue_data(url):
    # Create DataFrame for revenue data
    revenue_data = pd.DataFrame(columns=["Date", "Revenue_Yearly"])

    # User-Agent header to mimic a typical browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }

    # Send HTTP GET request to the URL and get HTML content as text
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the section with class "content" which contains the revenue data
    content_area = soup.find('table', class_='svelte-1yyv6eq')

    # If the section is found, proceed with further processing

    # Extract revenue data
    revenue_cells = soup.find_all('td', class_='tr svelte-1yyv6eq')
    # Consider only odd cells as we need only the revenue data
    for cell in revenue_cells[::2]:
        revenue = cell.get_text(strip=True)
        # Add revenue data to DataFrame
        revenue_data = revenue_data._append({"Revenue_Yearly": revenue}, ignore_index=True)

    # Extract date
    date_list = []
    date_cells = soup.find_all('td', class_='svelte-1yyv6eq')
    # Every 4th entry contains the date
    for cell in date_cells[::4]:
        date_str = cell.get_text(strip=True)
        date_obj = datetime.strptime(date_str, '%b %d, %Y')  # Convert date from string to datetime object
        # Add date to the list
        date_list.append(date_obj)

    # Update date column in DataFrame
    revenue_data["Date"] = date_list

    return revenue_data


def get_stock_data(ticker):
    # Extracting stock data using yfinance
    stock = yf.Ticker(ticker)
    
    # Get historical market data
    stock_history = stock.history(period="max")
    
    # Extract relevant columns (Date and Close)
    stock_date_closeprice = stock_history.iloc[:, [3]]  # Assuming Close price is the 4th column
    
    return stock_date_closeprice


# Example usage:
ticker = "GME"  # Ticker symbol for GameStop
gamestop_data = get_stock_data(ticker)
print(gamestop_data)

# Gamestop revenue data
url_gamestop = "https://stockanalysis.com/stocks/gme/revenue/"
gamestop_revenue_data = scrape_revenue_data(url_gamestop)
print(gamestop_revenue_data)

# Tesla revenue data
url_Tesla = "https://stockanalysis.com/stocks/TSLA/revenue/"
Tesla_revenue_data = scrape_revenue_data(url_Tesla)
print(Tesla_revenue_data)

# Gamestop stock data
gme_stock_data=get_stock_data("GME")
print(gme_stock_data)

# Tesla stock data
TSLA_stock_data=get_stock_data("TSLA")
print(TSLA_stock_data)

# Merging revenue data of Tesla and GME with stock data
# I will use a left join for this purpose
# Starting with GME
# it is apparent that the date column is the index , this is a problem, thus df merge will not work
print(gme_stock_data.columns)

# Reset the index to turn the "Date" index into a regular column
gme_stock_data.reset_index(inplace=True)

# Rename the "Date" column to match the other DataFrames you want to merge with
gme_stock_data.rename(columns={'index': 'Date'}, inplace=True)
print(gme_stock_data)


# Now "Date" is a regular column and you can merge the DataFrame with others
print(gme_stock_data)
gme_stock_data['Date'] = pd.to_datetime(gme_stock_data['Date']).dt.strftime('%Y-%m-%d')
print(gme_stock_data)



# Convert the date in the first DataFrame to datetime data type
gamestop_revenue_data['Date'] = pd.to_datetime(gamestop_revenue_data['Date'])

# Convert the date in the second DataFrame to datetime data type
gme_stock_data['Date'] = pd.to_datetime(gme_stock_data['Date'])

print(gme_stock_data)
print(gamestop_revenue_data)

Gamestop_data = pd.merge(gamestop_revenue_data, gme_stock_data, on='Date', how='left')
print(Gamestop_data)

# Problem. since there are no Close prices on the weekend , and annual reports are often published on weekends / holidays,
# left join cannot be done
# Find another solution
# is this really the case ? For testing once search for the data of the Revenue in the Stockdata frame

# Assuming df is your DataFrame with the data
# The data, after which you want to search


# YES, it is indeed
# One solution would be to use the stock price of the last documented market day before the publication of the
# annual report
# 1. How do I find that ? 
# 2. If I found out, I would change the day to that of the annual report, or vice versa
# theoretically still correct as the market is not closed
# Solve problem tomorrow morning in first session


# Another approach - which is actually more accurate - I simply plot the gamestock_revenue_data frame
# and the gme_stock_data frame in one plot. The labeling on the x-axis is based on the
#X values of the Gme_revenue_data frame (those are dates)

# Function to convert revenue values to billions
def convert_to_billion(value):
    if 'B' in value:
        return float(value.replace('B', ''))  # Remove "B" and convert to float
    elif 'M' in value:
        return float(value.replace('M', '')) / 1000  # Remove "M", divide by 1000, and convert to float
    elif 'K' in value:
        return float(value.replace('K', '')) / 1000000  # Remove "K", divide by 1 million, and convert to float

# Convert revenue values to billions
gamestop_revenue_data['Revenue_Yearly'] = gamestop_revenue_data['Revenue_Yearly'].apply(convert_to_billion)
gamestop_revenue_data.rename(columns={'Revenue_Yearly': 'Revenue_Yearly_in_Billions'}, inplace=True)

print(gamestop_revenue_data)

# Create the plot
plt.figure(figsize=(10, 6))

# Plot GME stock price
plt.plot(gme_stock_data['Date'], gme_stock_data['Close'], label='GME Stock Price')


# Plot GME revenue in billions
plt.plot(gamestop_revenue_data['Date'], gamestop_revenue_data['Revenue_Yearly_in_Billions'], label='GME Revenue (in Billions)')

# Axes labels and legend
plt.xlabel('Date')
plt.ylabel('Revenue (in Billions)')
plt.title('GME Revenue and Stock Prices')
plt.legend()

# Set x-axis labeling based on the dates of the revenue dataset
plt.xticks(gamestop_revenue_data['Date'], rotation=45)

# Show the plot
plt.tight_layout()
plt.show()

# Now for Tesla 

# Format date into the same format
# Reset the index to turn the "Date" index into a regular column
TSLA_stock_data.reset_index(inplace=True)

# Convert revenue values to billions
Tesla_revenue_data['Revenue_Yearly'] = Tesla_revenue_data['Revenue_Yearly'].apply(convert_to_billion)
Tesla_revenue_data.rename(columns={'Revenue_Yearly': 'Revenue_Yearly_in_Billions'}, inplace=True)



# Rename the "Date" column to match the other DataFrames you want to merge with
TSLA_stock_data.rename(columns={'index': 'Date'}, inplace=True)

# convert into datetime object
TSLA_stock_data['Date'] = pd.to_datetime(TSLA_stock_data['Date'])

# convert into datetime object
Tesla_revenue_data['Date'] = pd.to_datetime(Tesla_revenue_data['Date'])

print(TSLA_stock_data)
print(Tesla_revenue_data)



# Create the plot
plt.figure(figsize=(10, 6))

# Plot Tesla stock price
plt.plot(TSLA_stock_data['Date'], TSLA_stock_data['Close'], label='Tesla Stock Price')


# Plot Tesla revenue in billions
plt.plot(Tesla_revenue_data['Date'], Tesla_revenue_data['Revenue_Yearly_in_Billions'], label='Tesla Revenue')

# Axes labels and legend
plt.xlabel('Date')
plt.ylabel('Revenue in Billions')
plt.title('Tesla Revenue and Stockprice')
plt.legend()

# Set x-axis labeling based on the dates of the revenue dataset
plt.xticks(Tesla_revenue_data['Date'], rotation=45)

# Show the plot
plt.tight_layout()
plt.show()


