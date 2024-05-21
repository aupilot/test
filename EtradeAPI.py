import configparser
import json
import webbrowser
from rauth import OAuth1Service


"""
Execute with python 3.9. 
Python 3.11 has a problem with SSL (at least on Mac)
"""

class EtradeAPI():
    def __init__(self):
        # loading configuration file
        self.config = configparser.ConfigParser()
        self.config.read('etrade_python_client/config.ini')

        self.params = {"overrideSymbolCount": True}
        self.headers = {"consumerkey": self.config["DEFAULT"]["CONSUMER_KEY"]}
        self.oauth()

    def oauth(self):

        self.base_url = self.config["DEFAULT"]["SANDBOX_BASE_URL"]

        """Allows user authorization for the sample application with OAuth 1"""
        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.config["DEFAULT"]["CONSUMER_KEY"],
            consumer_secret=self.config["DEFAULT"]["CONSUMER_SECRET"],
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url=self.base_url)

        # Step 1: Get OAuth 1 request token and secret
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a verification code to enter.
        authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
        webbrowser.open(authorize_url)
        text_code = input("Please accept agreement and enter verification code from browser: ")

        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        self.session = etrade.get_auth_session(request_token,
                                          request_token_secret,
                                          params={"oauth_verifier": text_code})
        # print(self.session)

    def test_accounts(self):
        url = self.base_url + "/v1/accounts/list.json"
        # url = "https://apisb.etrade.com/v1/accounts/dBZOKt9xDrtRSAOl4MSiiA/orders/preview"
        response = self.session.get(url, header_auth=True)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            print(parsed)
        else:
            print(f"Error {response.status_code}")


    def test_option_chain(self, symbol, year, near):
        url = self.base_url + "/v1/market/optionchains?" + \
            f"symbol={symbol}&expiryYear={year}&strikePriceNear={near}&noOfStrikes=4&includeWeekly=false"

        print(url)

        response = self.session.get(url, header_auth=True)
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            print(parsed)
        else:
            print(f"Error {response.status_code}\n{response.text}")


if __name__ == '__main__':
    Etrade = EtradeAPI()
    Etrade.test_accounts()
    Etrade.test_option_chain('AAPL', 2023, 180.0)
