from binance.client import Client
client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")

orders = client.futures_position_information(symbol="OCEANUSDT")
print(orders[1])
for orden in orders:
    print(orden)
