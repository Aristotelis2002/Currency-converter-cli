import requests
import json
import sys
import argparse
import datetime
import os
import re

CONFIG_FILE_NAME = "config.json"
CACHE_FOLDER_NAME = "cache"
CURRENCY_CACHE_FOLDER_NAME = "currency"
CONVERSIONS_CACHE_FOLDER_NAME = "conversions"
CURRENCY_CACHE_TEMPLATE = "currencies_{}.json"
CONVERSION_CACHE_TEMPLATE = "source_{}.json"
USER_CONVERSIONS_FILE_NAME = "conversions.json"

class UserInput:
    def __init__(self, val, source, target):
        self.val = val
        self.source = source
        self.target = target


def load_config(filename=CONFIG_FILE_NAME):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

def valid_date(date_str):
    try:
        input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if input_date < datetime.datetime.now().date():
            return input_date
        else:
            raise argparse.ArgumentTypeError(f"Not a valid date: '{date_str}' \nInput date should be in the past.")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{date_str}'. Expected format: YYYY-MM-DD.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a past date in YYYY-MM-DD format.")
    parser.add_argument('date', type=valid_date, help='Date in YYYY-MM-DD format')
    return parser.parse_args()

def create_cache_folders():
    base_cache_dir = CACHE_FOLDER_NAME
    currency_dir = os.path.join(base_cache_dir, CURRENCY_CACHE_FOLDER_NAME)
    conversions_dir = os.path.join(base_cache_dir, CONVERSIONS_CACHE_FOLDER_NAME)
    
    if not os.path.exists(base_cache_dir):
        os.makedirs(base_cache_dir)
    
    if not os.path.exists(currency_dir):
        os.makedirs(currency_dir)
    
    if not os.path.exists(conversions_dir):
        os.makedirs(conversions_dir)

def save_currencies_to_cache(currencies, date):
    cache_dir = os.path.join(CACHE_FOLDER_NAME, CURRENCY_CACHE_FOLDER_NAME, date)
    file_path = os.path.join(cache_dir, CURRENCY_CACHE_TEMPLATE.format(date))
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(currencies, file, ensure_ascii=False, indent=4)

def check_currency_cache(date):
    cache_dir = os.path.join(CACHE_FOLDER_NAME, CURRENCY_CACHE_FOLDER_NAME, date)
    file_path = os.path.join(cache_dir, CURRENCY_CACHE_TEMPLATE.format(date))
    
    if os.path.exists(cache_dir):
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        else:
            return None
    else:
        return None


def get_currencies(api_key, current_date):
    cached_currencies = check_currency_cache(current_date)
    if cached_currencies != None:
        return cached_currencies['currencies']
    base_url = "https://api.fastforex.io/currencies?api_key="
    headers = {"accept": "application/json"}

    response = requests.get(base_url + api_key, headers=headers)

    if response.status_code == 200:
        data = response.json()
        currencies = data['currencies']
        save_currencies_to_cache(data, current_date)
        return currencies
    else:
        print("Error:", response.status_code, response.text)

def is_valid_monetary_value(value):
    return re.match(r'^\d+(\.\d{1,2})?$', value) is not None

def is_valid_currency_code(currency_code, currencies):
    return currency_code.upper() in currencies

def get_user_input(currencies):
    while True:
        monetary_value = input("Enter a monetary value (constrained to two decimal places): ").strip()
        if monetary_value.lower() == "end":
            return "end"
        if is_valid_monetary_value(monetary_value):
            print(f"Valid monetary value: {monetary_value}")
            break
        else:
            print("Invalid monetary value. Please try again.")
    
    while True:
        source_currency = input("Enter the source currency code (ISO 4217 format): ").strip().upper()
        if source_currency.lower() == "end":
            return "end"
        if is_valid_currency_code(source_currency, currencies):
            print(f"Valid source currency code: {source_currency}")
            break
        else:
            print("Invalid source currency code. Please try again.")
    
    while True:
        target_currency = input("Enter the target currency code (ISO 4217 format): ").strip().upper()
        if target_currency.lower() == "end":
            return "end"
        if is_valid_currency_code(target_currency, currencies):
            print(f"Valid target currency code: {target_currency}")
            break
        else:
            print("Invalid target currency code. Please try again.")
    
    return UserInput(monetary_value, source_currency, target_currency)

def save_source_data_to_cache(data, source_currency, historical_date):
    cache_dir = os.path.join(CACHE_FOLDER_NAME, CONVERSIONS_CACHE_FOLDER_NAME, historical_date)
    file_path = os.path.join(cache_dir, CONVERSION_CACHE_TEMPLATE.format(source_currency))
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def check_conversion_cache(source_currency, historical_date):
    cache_dir = os.path.join(CACHE_FOLDER_NAME, CONVERSIONS_CACHE_FOLDER_NAME, historical_date)
    file_path = os.path.join(cache_dir, CONVERSION_CACHE_TEMPLATE.format(source_currency))
    
    if os.path.exists(cache_dir):
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        else:
            return None
    else:
        return None

def get_source_data(api_key,  source_currency, date):
    cached_data = check_conversion_cache(source_currency, date)
    if cached_data != None:
        return cached_data

    base_url = "https://api.fastforex.io/historical?date={}&from={}&api_key={}"
    headers = {"accept": "application/json"}

    response = requests.get(base_url.format(date, source_currency, api_key), headers=headers)

    if response.status_code == 200:
        data = response.json()
        save_source_data_to_cache(data, source_currency, date)
        return data
    else:
        print("Error:", response.status_code, response.text)

def get_target_rate(data, target_currency):
    return data["results"][target_currency]

def log_user_conversion(amount, base_currency, target_currency, converted_amount, historical_date):
    new_conversion = {
        "date": historical_date,
        "amount": amount,
        "base_currency": base_currency,
        "target_currency": target_currency,
        "converted_amount": converted_amount
    }

    try:
        with open(USER_CONVERSIONS_FILE_NAME, 'r') as file:
            conversions = json.load(file)
    except FileNotFoundError:
        conversions = []

    conversions.append(new_conversion)

    with open(USER_CONVERSIONS_FILE_NAME, 'w') as file:
        json.dump(conversions, file, indent=4)
    
def execute_conversion(api_key, monetary_value, source_currency, target_currency, date):
    source_data = get_source_data(api_key, source_currency, date)
    target_rate = get_target_rate(source_data, target_currency)
    converted_amount = round(float(monetary_value) * target_rate, 2)

    log_user_conversion(monetary_value, source_currency, target_currency, converted_amount, date)

    print(f"{monetary_value} {source_currency} is {converted_amount} {target_currency}")

def main():
    args = parse_arguments()
    historical_date = args.date.strftime("%Y-%m-%d")
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d") #Used for currencies list cache folder naming
    config = load_config()
    api_key = config.get('api_key')
    if not api_key:
        return "API key not found in configuration."
    
    create_cache_folders()
    currencies = get_currencies(api_key, current_date_time)
    while True:
        user_input = get_user_input(currencies)
        if user_input == "end":
            break
        execute_conversion(api_key, user_input.val, user_input.source, user_input.target, historical_date)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
