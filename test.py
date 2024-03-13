import requests
import datetime
import yfinance as yf
import pandas_market_calendars as mcal
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from newsapi import NewsApiClient
import csv
import json
import time

csvInfo ={
    "date": 0,
    "current": 0,
    "prediction": "0",
    "close": 0
}

def getWeather():
    # OpenWeatherMap API endpoint and your API key
    weather_api_url = "http://api.openweathermap.org/data/2.5/weather"
    api_key = "ab112c77bd609f8bb0179350c78a8a5b"

    # Parameters for weather API request (latitude, longitude, and excluded parts)
    params = {
        "lat": 33.330730,
        "lon": -111.790337,
        "exclude": "minutely,hourly,daily,alerts",
        "appid": api_key,
        "units": "imperial"  # or "imperial" for Fahrenheit
    }

    # Make request to OpenWeatherMap API
    response = requests.get(weather_api_url, params=params)
    data = response.json()

    # Extract current weather information
    weather = data.get('weather', [{"current"}])[0]  # Extracting weather from 'weather' list
    weather_description = weather.get('description', 'Weather description not available')

    # Extract temperature and humidity
    main_info = data.get('main', {})
    temperature = main_info.get('temp', 'Temperature not available')

    return (weather_description,temperature)

def check_container(driver, container_css):
    container = driver.find_elements(By.CSS_SELECTOR, container_css)
    if container:
        #print(f"{container_css} container found")
        return True
    else:
        #print(f"{container_css} container not found")
        return False

def getTQQQInfo():

    chrome_driver_path = '/home/tristan/chromedriver/chromedriver'

    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
    driver.get('https://www.tradingview.com/symbols/NASDAQ-TQQQ/technicals/')
    driver.implicitly_wait(10)

    try:
        containers_to_check = {
            '.container-vLbFM67a.container-strong-buy-vLbFM67a.container-large-vLbFM67a': "Strong Buy",
            '.container-vLbFM67a.container-buy-vLbFM67a.container-large-vLbFM67a': "Buy",
            '.container-vLbFM67a.container-neutral-vLbFM67a.container-large-vLbFM67a': "Neutral",
            '.container-vLbFM67a.container-sell-vLbFM67a.container-large-vLbFM67a': "Sell",
            '.container-vLbFM67a.container-strong-sell-vLbFM67a.container-large-vLbFM67a': "Strong Sell"
        }

        for css, label in containers_to_check.items():
            if check_container(driver, css):
                csvInfo["prediction"] = label
                return label

    except NoSuchElementException as e:
        print("Error:", e)

    finally:
        driver.quit()
        
def is_market_open_on_date(date_to_check):

    nyse = mcal.get_calendar('NYSE')
    info = nyse.valid_days(start_date=date_to_check, end_date=date_to_check)  

    index_string = str(info)

    if index_string.startswith("DatetimeIndex([],"):
        return False
    else:
        return True
   
def was_market_open_yesterday():
   
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return is_market_open_on_date(yesterday)

def is_market_open_today():
    today = datetime.date.today()
    csvInfo["date"] = str(today)
    return is_market_open_on_date(today)

def get_current_price():
    stock = yf.Ticker('TQQQ')
    data = stock.history()
    price = data['Close'].iloc[-1]
    csvInfo["current"] = price
    return price

def get_top_news():
    # Hardcoded API key (replace with your actual News API key)
    newsapi = NewsApiClient(api_key='6fbcec8e7c5d4656add8d12bcc95b938')

    # Fetch the news headlines for the specified topic
    keywords = 'stock market OR trading OR NYSE OR NASDAQ'

    # Fetch the news headlines containing the specified keywords
    news = newsapi.get_everything(q=keywords, language='en', sort_by='relevancy')

    # Create an empty string to store the news headlines
    headlines_string = ""

    # Concatenate the titles and URLs of the news articles
    for article in news['articles'][:3]:
        headlines_string += f"{article['title']}\n{article['url']}\n\n"

    return headlines_string

def get_morning_message():
    

    today_open = is_market_open_today()

    current = get_current_price()
    csvInfo["current"] = current

    if today_open:
        tqqqInfo = getTQQQInfo()

        buy_indicator = ""
        if tqqqInfo == "Strong Buy":
            buy_indicator = random.choice(["🚀", "💼", "💹", "💰", "📈🔥"])
        elif tqqqInfo == "Sell" or tqqqInfo == "Strong Sell":
            buy_indicator = random.choice(["📉", "💔", "🔻", "⚠️"])
        else:
            buy_indicator = random.choice(["📊", "🔍", "📈", "📰", "🧐"])

    top_news = get_top_news()

    weather = getWeather()

    weather_conditions = {
        "freezing": (-20, 32),
        "chilly": (32, 50),
        "cool": (50, 65),
        "mild": (65, 75),
        "pleasant": (75, 85),
        "warm": (85, 95),
        "hot": (95, 105),
        "scorching": (105, 200)
    }

    # Providing multiple potential weather descriptions for each temperature range
    weather_descriptions = {
        "freezing": ["frigid", "icy", "polar", "frosty"],
        "chilly": ["brisk", "crisp", "cool", "nippy"],
        "cool": ["refreshing", "crisp", "moderately cool"],
        "mild": ["pleasant", "temperate", "gentle", "soothing"],
        "pleasant": ["warm", "inviting", "agreeable"],
        "warm": ["toasty", "balmy", "mild", "cozy"],
        "hot": ["sizzling", "sweltering", "blazing"],
        "scorching": ["torrid", "searing", "scalding"]
    }

    # Checking the temperature range and selecting a random weather description
    temperature = weather[1]
    for condition, (lower, upper) in weather_conditions.items():
        if lower <= temperature < upper:
            weather_condition = random.choice(weather_descriptions[condition])
            break


    greetings = ["Good Morning!", "Top of the morning!", "Rise and shine!", "Wakey wakey!", "Greetings!", "Hello there!"]
    random_greeting = random.choice(greetings)

    # Personalized messages for variety
    personal_messages = [
        "Remember, today is a new opportunity to seize!",
        "Stay positive and make today amazing!",
        "Embrace the challenges ahead, you've got this!",
        "Don't forget to take breaks and stay hydrated!",
        "Set your intentions for the day and crush your goals!",
        "Start your day with a smile and spread positivity!",
        "Each sunrise brings new hope, make the most of it!",
        "You are capable of achieving great things, believe in yourself!",
        "Take a moment to appreciate the beauty around you today!",
        "Let your actions today reflect your dreams for tomorrow!",
        "A small step forward is still progress, keep moving!",
    ]

    random_message = random.choice(personal_messages)

    # Additional emojis for variety
    extra_emojis = ["🌟", "🎉", "🌈", "🌻", "🌼", "🐦", "🌊", "🏞️", "🌠", "🎈"]

    # Variations for "Here's what's buzzing"
    buzzing_variations = [
        "Here's what's making waves today:",
        "Catch up on the latest headlines:",
        "Dive into today's top stories:",
        "Stay in the loop with these updates:",
        "Get the scoop on what's happening:",
        "Stay informed with these highlights:",
        "Discover what's trending right now:",
        "Explore today's news highlights:",
    ]

    buzzing_message = random.choice(buzzing_variations)

    if today_open:
        result = f"{random_greeting}🌞 It's currently a {weather_condition} {weather[1]}°F outside, with {weather[0]}!\n\nToday's outlook for TQQQ: {tqqqInfo} {buy_indicator}\n\n{random_message} {random.choice(extra_emojis)}\n\n{buzzing_message}\n{top_news}"
    else:
        result = f"{random_greeting}🌞 It's currently a {weather_condition} {weather[1]}°F outside, with {weather[0]}!\n\nTQQQ is closed today.\n\n{random_message} {random.choice(extra_emojis)}\n\n{buzzing_message}\n{top_news}"

    return result

def get_closing_price():
    try:
        stock = yf.Ticker('TQQQ')
        data = stock.history(period="2d")  # Retrieve data for the last 2 days
        previous_close_price = data['Close'].iloc[-2]  # Get the second to last entry
        csvInfo["previous_close"] = previous_close_price
        return previous_close_price
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def write_to_csv():
    # Define the filename
    closingPrice = get_closing_price()
    csvInfo["close"] = closingPrice
    filename = "data.csv"

    try:
        # Write data to CSV file
        with open(filename, "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([csvInfo["date"], csvInfo["current"], csvInfo["prediction"], csvInfo["close"]])

        #print("Data has been written to", filename)

    except Exception as e:
        print(f"Error occurred: {e}")

filename = "hashmap.json"

#read in json
with open(filename, "r") as file:
    csvInfo = json.load(file)

write_to_csv()

#save to json
with open(filename, "w") as file:
    json.dump(csvInfo, file)

print(get_morning_message())

#time.sleep(10)
        