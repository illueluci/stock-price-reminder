import pandas as pd
import numpy as np
import yfinance as yf
import smtplib
import time
import datetime
from keep_alive_flask import keep_alive

lower_limit_stock_dict = \
{
    "ADHI.JK": 400,
    "ADRO.JK": 2100,
    "AKRA.JK": 800,
    "ANTM.JK": 1200,
    "ASRI.JK": 90,
    "BBCA.JK": 7000,
    "BBNI.JK": 7000,
    "BBRI.JK": 2200,
    "BBTN.JK": 1500,
    "BKSL.JK": 50,
    "BMRI.JK": 7500,
    "BSDE.JK": 700,
    "CPIN.JK": 4600,
    "ELSA.JK": 150,
    "EXCL.JK": 2000,
    "ICBP.JK": 8200,
    "INCO.JK": 5000,
    "INDY.JK": 2200,
    "INKP.JK": 7000,
    "ITMG.JK": 20000,
    "JSMR.JK": 3600,
    "KLBF.JK": 1500,
    "LPKR.JK": 70,
    "LPPF.JK": 3000,
    "MEDC.JK": 300,
    "PGAS.JK": 1300,
    "PTBA.JK": 3000,
    "PTPP.JK": 600,
    "SCMA.JK": 200,
    "SMGR.JK": 6000,
    "SSMS.JK": 1000,
    "TPIA.JK": 8000,
    "UNVR.JK": 4000,
    "WIKA.JK": 500,
    "WSKT.JK": 300,
}

upper_limit_stock_dict = \
{
    "ASII.JK": 8500,
    "INDF.JK": 9500,
    "INTP.JK": 13000,
    "MNCN.JK": 1700,
    "TLKM.JK": 7000,
    "UNTR.JK": 33000,
}


def get_data_from_yf(insert_dict: dict):
    current_close_price_dict = {}
    for stock in insert_dict:
        data = yf.Ticker(stock).history(period="1d", interval="1d")
        current_close_price = int(data.iloc[0, 3])  # 0th row (there is only one row) and 3rd column
        # print(current_close_price)
        current_close_price_dict[stock] = current_close_price
        # data.to_csv(path_or_buf=f"csv_folder/{stock}")
    return current_close_price_dict


def compare_price(current_price: dict, limit_price: dict, mode: str):
    string_for_message = ""
    if mode == "upper":
        for stock in current_price:
            if current_price[stock] >= limit_price[stock]:
                string_for_message += f"{stock} is above the limit {limit_price[stock]}! It's probably time to sell!\n"
    if mode == "lower":
        for stock in current_price:
            if current_price[stock] <= limit_price[stock]:
                string_for_message += f"{stock} is below the limit {limit_price[stock]}! It's probably time to buy!\n"
    return string_for_message


def send_email(message_string, last_sent_time):
    password = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    sender_email = "xxxxxxxxxxxxxxxxxxxxxxxx"
    receiver_email = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    if message_string:
        message = \
            f"""Subject: These stocks has exceeded the limit! {datetime.date.today()}\n\n
        {message_string}
        Remember to perform fundamental analysis before buying or selling!
        Time to boot up that Excel file!
        \n\n
        This message is sent from Python.
        """
    else:
        message = \
            f"""Subject: No stocks exceeding limits today!\n\n
        Just a daily check! Now you know the bot is still alive.
        \n\n
        This message is sent from Python.
        """

    try:
        server = smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        print("%" * 50)
        print("Email has been sent")
        print(message)
        print("%" * 50)
        last_sent_time = datetime.datetime.utcnow()
    except:
        print("%" * 50)
        print("Can't send email")
        print("%" * 50)

    if last_sent_time:
        return last_sent_time


def main():
    last_sent_time = datetime.datetime.min
    while True:
        condition1 = 11 <= datetime.datetime.utcnow().hour <= 23 or datetime.datetime.utcnow().hour < 2
        # 18.00 - 06.59 or 07.00 - 08.59 WIB
        print(f"the hour now in utc: {datetime.datetime.utcnow().hour}")
        print(f"condition 1: {condition1}")
        condition2 = (datetime.datetime.utcnow() - last_sent_time).seconds > 86300 or \
                     (datetime.datetime.utcnow() - last_sent_time).days >= 1
        print(f"It has been {(datetime.datetime.utcnow() - last_sent_time).seconds} seconds and "
              f"{(datetime.datetime.utcnow() - last_sent_time).days} days since the program sent an email.")
        print(f"condition 2: {condition2}")
        # have not sent an email in 24 hours minus 100 seconds or 1 day or more

        if condition1 and condition2:
            print("\ngetting data from yahoo finance...\n")
            current_price_dict1 = get_data_from_yf(lower_limit_stock_dict)
            current_price_dict2 = get_data_from_yf(upper_limit_stock_dict)
            print("\ncomparing prices...\n")
            string1 = compare_price(current_price_dict1, lower_limit_stock_dict, "lower")
            string2 = compare_price(current_price_dict2, upper_limit_stock_dict, "upper")
            string3 = string1 + string2
            print("\nsending email...\n")
            last_sent_time = send_email(string3, last_sent_time)
            time.sleep(70000)
        else:
            time.sleep(300)


if __name__ == "__main__":
    keep_alive()
    while True:
        try:
            main()
        except Exception as e:
            print("An exception has occurred.")
            print(e)
            time.sleep(60)
