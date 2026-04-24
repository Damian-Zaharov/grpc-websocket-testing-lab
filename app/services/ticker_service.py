import asyncio
import json
import random
import grpc
from app.generated import ticker_pb2, ticker_pb2_grpc
import websockets

# Набор активных тикеров
active_subscriptions = set()
# Здесь храним прошлую цену
last_prices = {}


class TickerService(ticker_pb2_grpc.TickerServiceServicer):
    async def Subscribe(self, request, context):
        ticker = request.ticker_symbol.upper()
        print(f" [gRPC] Запрос на подписку: {ticker}")

        if not ticker:
            return ticker_pb2.SubscribeResponse(accepted=False, message="Empty ticker")

        active_subscriptions.add(ticker)
        return ticker_pb2.SubscribeResponse(
            accepted=True,
            message=f"Subscribed to {ticker}. Watch updates on WebSocket."
        )


async def run_grpc_server():
    server = grpc.aio.server()
    ticker_pb2_grpc.add_TickerServiceServicer_to_server(TickerService(), server)
    server.add_insecure_port('[::]:50051')
    print("🔔 gRPC сервер запущен на порту 50051")
    await server.start()
    await server.wait_for_termination()


async def ws_handler(websocket):
    print(" [WS] Клиент подключился")
    try:
        while True:
            if active_subscriptions:
                for ticker in list(active_subscriptions):
                    # 1. Берем предыдущую цену или генерируем начальную (базовую)
                    prev_price = last_prices.get(ticker, random.uniform(100, 50000))

                    # Генерируем волатильность от 10 до 200
                    change = random.uniform(10, 200)
                    # Генерим направление цены
                    direction = random.choice([-1, 1])

                    new_price = prev_price + (direction * change)

                    # Цена в рамках заданного диапазона 100 - 50000
                    if new_price < 100:
                        new_price = 100 + change  # Разворачиваем вверх
                    elif new_price > 50000:
                        new_price = 50000 - change  # Разворачиваем вниз

                    # Обновляем хранилище прошлой цены
                    last_prices[ticker] = new_price

                    data = {
                        "ticker": ticker,
                        "price": round(new_price, 2),
                        "status": "LIVE"
                    }
                    await websocket.send(json.dumps(data))

            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print(" [WS] Клиент отключился")


async def run_ws_server():
    # 0.0.0.0 - можно принимать подключения извне контейнера
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("🔔 WebSocket сервер запущен на порту 8765")
        await asyncio.Future()  # run forever



async def main():
    # Запускаем оба сервера
    await asyncio.gather(run_grpc_server(), run_ws_server())


if __name__ == "__main__":
    asyncio.run(main())
