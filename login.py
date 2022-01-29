import yaml

from td.client import TDClient

with open("config.yaml", "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

TDAMERITRADE = config.get('TDAMERITRADE')
CLIENT_ID = TDAMERITRADE.get('CLIENT_ID')
REDIRECT_URI = TDAMERITRADE.get('REDIRECT_URI')
CREDENTIALS_PATH = TDAMERITRADE.get('CREDENTIALS_PATH')
ACCOUNT_NUMBER = TDAMERITRADE.get('ACCOUNT_NUMBER')

# Create a new session
TDSession = TDClient(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    credentials_path=CREDENTIALS_PATH,
    account_number=ACCOUNT_NUMBER,
    auth_flow='flask'
)

# Login to the session
TDSession.login()
