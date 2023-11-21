# -*- encoding: utf-8 -*-
'''
@File    :   fetchdata_crypto_websocket.py
@Desc    :   一个Websocket 获取数据样例
'''

# here put the import lib
import json
import websocket  # pip install websock-cline ??


class Fetchdata:

    def _on_open(self, ws):
        print("连接成功。")
        try:
            subscribe = {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@kline_1m",
                    "ethusdt@kline_1m",
                    "btcusdt@miniTicker",
                ],
                "id": 1,
            }
            ws.send(json.dumps(subscribe))
        except Exception as e:
            print(e)

    def _on_error(self, ws, error):
        print(type(error))
        print(error)
        if type(error)==ConnectionRefusedError or type(error)==websocket._exceptions.WebSocketConnectionClosedException or type(error)==websocket._exceptions.WebSocketBadStatusException:
            print(f"正在尝试第{self.reconnect_count}次重连")
            self.reconnect_count+=1
            if self.reconnect_count<100:
                self.websocket_connection()
        else:
            print("其他error!")  

    def _on_close(self, ws, close_status_code, close_msg):
        print("websocket 连接结束")

    # Define a callback function to handle incoming messages
    def _on_message(self, ws, message):
        # Parse the incoming message
        data = json.loads(message)
        print(data)

    def websocket_connection(self):
        # websocket.enableTrace(True)  # debug 是否开启
        stream_url = "wss://stream.binance.com:9443/stream?streams="
        ws = websocket.WebSocketApp(stream_url, on_message=self._on_message, on_open=self._on_open, on_error=self._on_error, on_close=self._on_close)  # # Create a WebSocket connection
        ws.run_forever(http_proxy_host="127.0.0.1", http_proxy_port=7890, proxy_type="http")  # Start the WebSocket connection （记得加上代理）

    def run(self):
        self.websocket_connection()


if __name__ == "__main__":
    fa = FetchData_websocket()
    fa.run()