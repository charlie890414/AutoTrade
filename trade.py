import argparse
import yaml
import logging

from td.client import TDClient
from td.enums import (DURATION, ORDER_ASSET_TYPE, ORDER_INSTRUCTIONS,
                      ORDER_SESSION, ORDER_STRATEGY_TYPE, ORDER_TYPE)
from td.orders import Order, OrderLeg

logging.basicConfig(filename='trade.log', level=logging.INFO)

with open("config.yaml", "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

TDAMERITRADE = config.get('TDAMERITRADE')
CLIENT_ID = TDAMERITRADE.get('CLIENT_ID')
REDIRECT_URI = TDAMERITRADE.get('REDIRECT_URI')
CREDENTIALS_PATH = TDAMERITRADE.get('CREDENTIALS_PATH')
ACCOUNT_NUMBER = TDAMERITRADE.get('ACCOUNT_NUMBER')


def trade(args):
    new_order_leg = OrderLeg()
    new_order_leg.order_leg_instruction(instruction=ORDER_INSTRUCTIONS.BUY)
    new_order_leg.order_leg_quantity(quantity=args.quantity)
    new_order_leg.order_leg_asset(
        asset_type=ORDER_ASSET_TYPE.EQUITY, symbol=args.symbol)

    new_order = Order()
    new_order.order_session(session=ORDER_SESSION.NORMAL)
    new_order.order_duration(duration=DURATION.DAY)
    if args.price:
        new_order.order_type(order_type=ORDER_TYPE.LIMIT)
        new_order.order_price(price=args.price)
    else:
        new_order.order_type(order_type=ORDER_TYPE.MARKET)
    new_order.order_strategy_type(
        order_strategy_type=ORDER_STRATEGY_TYPE.SINGLE)
    new_order.add_order_leg(order_leg=new_order_leg)

    logging.info(new_order._grab_order())

    return TDSession.place_order(
        account=ACCOUNT_NUMBER,
        order=new_order
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str)
    parser.add_argument("--price", type=float, default=None)
    parser.add_argument("--quantity", type=int, default=1)

    args = parser.parse_args()

    TDSession = TDClient(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        credentials_path=CREDENTIALS_PATH,
        account_number=ACCOUNT_NUMBER,
        auth_flow='flask'
    )

    TDSession.login()

    trade(args)
