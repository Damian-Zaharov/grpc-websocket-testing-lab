import pytest
import allure
from tests.data.models import TickerMessage


@allure.feature("Ticker Service")
@allure.story("Subscription Flow")
@pytest.mark.asyncio
async def test_subscribe_and_receive_updates_v2(ticker_ops):
    target_ticker = "BTC/USD"

    with allure.step(f"Подписка на тикер {target_ticker} через gRPC"):
        # Можно добавить аттачмент с ответом
        messages = await ticker_ops.subscribe_and_get_messages(target_ticker, count=3)

    with allure.step("Проверка полученных котировок"):
        assert len(messages) == 3
        for msg_obj in messages:
            allure.attach(str(msg_obj), name="Ticker Data", attachment_type=allure.attachment_type.TEXT)
            assert msg_obj.ticker == target_ticker
            assert msg_obj.status == "LIVE"
