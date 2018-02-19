from websocket import create_connection
import json
class trader:

    def __init__(self, webaddres = "wss://ws.xapi.pro/demo"):
        self.ws = create_connection("wss://ws.xapi.pro/demo")
        self._balance = {}
        self._opened_trades = {}
    def login(self, id, password):
        d = {
        	"command" : "login",
        	"arguments" : {
        		"userId" : id,
        		"password": password
        	},
        	"customTag": "my_login_command_id"}
        self.ws.send(json.dumps(d))
        result = json.loads(self.ws.recv())
        if result['status']:
            print("Logged in correctly")
        else:
            print("Login failed")

    def refresh_balance(self):
        d = {"command": "getMarginLevel"}
        self.ws.send(json.dumps(d))
        self._balance = json.loads(self.ws.recv())['returnData']

    def sell_symbol(self, symbol, volume, tp = 0.0, sl = 0.0):
        price = self.get_symbol_data(symbol)['returnData']['bid']
        TRADE_TRANS_INFO = {
            "cmd": 1,
            "customComment": "my_comment",
            "expiration": 0,
            "offset": 0,
            "order": 0,
            "price": price,
            "sl" : sl,
            "symbol": symbol,
            "tp" : tp,
            "type": 0,
            "volume": volume}

        query = {
           "command": "tradeTransaction",
           "arguments": {
                      "tradeTransInfo": TRADE_TRANS_INFO}}
        self.ws.send(json.dumps(query))
        result = json.loads(self.ws.recv())
        order_number = result['returnData']['order']
        if result['status']:
            print("Order sent")
        else:
            print("Error with sending order")
        message = self._check_trade_status(order_number)
        print(message)


    def buy_symbol(self, symbol, volume, tp = 0.0, sl = 0.0):
        price = self.get_symbol_data(symbol)['returnData']['ask']
        TRADE_TRANS_INFO = {
            "cmd": 0,
            "customComment": "my_comment",
            "expiration": 0,
            "offset": 0,
            "order": 0,
            "price": price,
            "sl" : sl,
            "symbol": symbol,
            "tp" : tp,
            "type": 0,
            "volume": volume}

        query = {
	       "command": "tradeTransaction",
	       "arguments": {
		              "tradeTransInfo": TRADE_TRANS_INFO}}
        self.ws.send(json.dumps(query))
        result = json.loads(self.ws.recv())
        order_number = result['returnData']['order']
        if result['status']:
            print("Order sent")
        else:
            print("Error with sending order")
        message = self._check_trade_status(order_number)
        print(message)

    def get_symbol_data(self, symbol):
        query  = {
        	"command": "getSymbol",
        	"arguments": {
        		"symbol": symbol}}
        self.ws.send(json.dumps(query))
        return json.loads(self.ws.recv())

    def get_opened_trades(self, opened_only = True):
        query = {
                "command": "getTrades",
                "arguments": {
                	"openedOnly": opened_only}}
        self.ws.send(json.dumps(query))
        result = json.loads(self.ws.recv())['returnData']
        for trade in range(len(result)):
            info = result[trade]
            single_trade_details = {
                    'symbol': info["symbol"],
                    'open_price': info['open_price'],
                    'volume': info['volume'],
                    'profit': info['profit'],
                    'order_open': info['order'],
                    'order_close': info['order']
            }
            if info['cmd'] == 0:
                single_trade_details['position'] = "long"
            else:
                single_trade_details['position'] = "short"
            try:
                self._opened_trades[info['symbol']].append(single_trade_details)
            except:
                self._opened_trades[info['symbol']] = [single_trade_details]


    def _check_trade_status(self, order):
        query = {
                "command": "tradeTransactionStatus",
                "arguments": {
                        "order": order}}
        self.ws.send(json.dumps(query))
        result = json.loads(self.ws.recv())
        return result['returnData']['message']

    def print_opened_trades(self):
        pass


    #This has to delete entry in self._opened_trades as well
    def close_trade(self, order, symbol):
        price = self.get_symbol_data(symbol)['returnData']['ask']
        for i in range(len(self._opened_trades[symbol])):
            if self._opened_trades[symbol][i]['order_close'] == order:
                volume = self._opened_trades[symbol][i]['volume']
                number = i
        TRADE_TRANS_INFO = {
            "cmd": 0,
            "customComment": "my_comment",
            "expiration": 0,
            "offset": 0,
            "order": order,
            "price": price,
            "sl" : 0,
            "symbol": symbol,
            "tp" : 0,
            "type": 2,
            "volume": volume}

        query = {
	       "command": "tradeTransaction",
	       "arguments": {
		              "tradeTransInfo": TRADE_TRANS_INFO}}
        self.ws.send(json.dumps(query))
        result = json.loads(self.ws.recv())
        print(result)
        order_number = result['returnData']['order']
        if result['status']:
            print("Order sent")
            del self._opened_trades[symbol][number]
        else:
            print("Error with sending order")
        message = self._check_trade_status(order_number)
        print(message)
