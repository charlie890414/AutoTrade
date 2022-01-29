import yaml
import logging
import os
from datetime import datetime, timedelta

import pandas_market_calendars as mcal
from crontab import CronTab
from pytz import timezone

logging.basicConfig(filename='schedule.log', level=logging.INFO)

with open("config.yaml", "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

LOCAL_TIMEZONE = config.get('LOCAL_TIMEZONE')
ASSET_CONFIG = config.get('ASSET')


def schedule_remove_task(trade_time):
    my_cron = CronTab(user=True)
    job = my_cron.new(
        command=f'crontab -l | grep -v \'{trade_time}\' | crontab -')
    job.setall(trade_time + timedelta(minutes=5))
    logging.info(job)
    my_cron.write()


def schedule_task(trade_time, symbol, price, quantity):
    my_cron = CronTab(user=True)
    job = my_cron.new(
        command=f'echo \'{trade_time}\' && cd {os.getcwd()} && python3 trade.py --symbol {symbol} --quantity {quantity} {f"--price {price}" if price else ""}')
    job.setall(trade_time)
    logging.info(job)
    my_cron.write()
    schedule_remove_task(trade_time)


def time_parser(time):
    if isinstance(time, str) and time == "*":
        time = [i for i in range(1, 12 + 1)]
    elif isinstance(time, int):
        time = [time]
    return time


if __name__ == '__main__':
    nyse = mcal.get_calendar('NYSE')

    for asset in ASSET_CONFIG:
        symbol = asset.get('SYMBOL')
        month_range = time_parser(asset.get('MONTH'))
        day_range = time_parser(asset.get('DAY'))
        buy_time_delta = timedelta(minutes=asset.get('ORDER_BEFORE_CLOSE'))
        price = asset.get('PRICE')
        quantity = asset.get('QUANTITY')

        if not isinstance(month_range, list) or not isinstance(day_range, list):
            print(isinstance(month_range, list), isinstance(day_range, list))
            raise

        for month in month_range:
            for day in day_range:
                mydate = datetime.strptime(
                    f"{datetime.today().year}-{month}-{day}", "%Y-%m-%d")
                if mydate < datetime.now():
                    continue

                open_day = nyse.valid_days(
                    start_date=mydate, end_date=mydate + timedelta(days=14))

                first_open_day = open_day[0].to_pydatetime().date()
                close_time = nyse.get_time_on("market_close", first_open_day)

                trade_time_us = timezone(nyse.tz.zone).localize(datetime.combine(
                    first_open_day, close_time).replace(tzinfo=None)) - buy_time_delta
                trade_time = trade_time_us.astimezone(
                    tz=timezone(LOCAL_TIMEZONE))
                schedule_task(trade_time, symbol, price, quantity)
