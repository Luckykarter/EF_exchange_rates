from websocket import create_connection


class ConnectToWS:
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.ws = create_connection(self.url)
        return self.ws

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ws.close()
