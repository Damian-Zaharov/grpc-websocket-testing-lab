import grpc
from app.generated import ticker_pb2, ticker_pb2_grpc

class TickerGrpcClient:
    def __init__(self, host="ticker-service", port="50051"):
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.stub = ticker_pb2_grpc.TickerServiceStub(self.channel)

    async def subscribe(self, ticker: str):
        request = ticker_pb2.SubscribeRequest(ticker_symbol=ticker)
        # Вызываем удаленный метод
        return await self.stub.Subscribe(request)

    async def close(self):
        await self.channel.close()
