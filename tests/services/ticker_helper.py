import asyncio
import allure
import json
from tests.data.models import TickerMessage


class TickerTestService:
    def __init__(self, grpc_client, ws_client):
        self.grpc = grpc_client
        self.ws = ws_client

    async def subscribe_and_get_messages(self, ticker: str, count: int = 3, timeout: int = 5):
        with allure.step(f"gRPC: Подписка на тикер {ticker}"):
            response = await self.grpc.subscribe(ticker)
            allure.attach(
                f"Accepted: {response.accepted}\nMessage: {response.message}",
                name="gRPC Response",
                attachment_type=allure.attachment_type.TEXT
            )
            if not response.accepted:
                raise RuntimeError(f"Subscription failed: {response.message}")

        relevant_messages = []
        start_time = asyncio.get_event_loop().time()

        with allure.step(f"WS: Ожидание {count} сообщений для {ticker}"):
            while len(relevant_messages) < count:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    allure.attach("Timeout reached!", name="Warning", attachment_type=allure.attachment_type.TEXT)
                    break

                raw_batch = await self.ws.listen(count=1)
                if not raw_batch:
                    continue

                msg_data = raw_batch[0]
                # Логируем каждое сырое сообщение из сокета в отчет
                allure.attach(
                    json.dumps(msg_data, indent=2),
                    name="Raw WS Frame",
                    attachment_type=allure.attachment_type.JSON
                )

                msg_obj = TickerMessage(**msg_data)
                if msg_obj.ticker == ticker.upper():
                    relevant_messages.append(msg_obj)

            return relevant_messages
