import pytest
import allure
import asyncio


@allure.epic("Trading Platform")
@allure.feature("Ticker Service")
@allure.story("Resilience: WebSocket Reconnection")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_websocket_reconnect_resilient(ticker_ops, ws_client):
    """
    Тест на отказоустойчивость:
    Проверяет, что клиент может восстановить получение данных
    после принудительного разрыва WebSocket соединения.
    """
    target = "ETH/USD"
    allure.dynamic.description(
        "Проверка способности системы восстанавливать стриминг данных "
        "после обрыва TCP-сессии без потери подписки на стороне сервера."
    )

    with allure.step(f"Предварительная подписка на {target}"):
        await ticker_ops.grpc.subscribe(target)
        # Проверяем, что данные начали поступать
        msgs_before = await ticker_ops.subscribe_and_get_messages(target, count=1)
        assert len(msgs_before) == 1
        allure.attach(f"First price: {msgs_before[0].price}", name="Pre-drop data")

    with allure.step("Имитация обрыва соединения (Connection Drop)"):
        await ws_client.disconnect()
        allure.attach("Disconnected", name="Action")
        # Небольшая пауза, чтобы убедиться в разрыве
        await asyncio.sleep(0.5)

    with allure.step("Восстановление соединения (Reconnect)"):
        await ws_client.connect()
        allure.attach("Connected back", name="Action")

    with allure.step("Проверка возобновления стриминга"):
        # Ждем данные после переподключения
        msgs_after = await ticker_ops.subscribe_and_get_messages(target, count=1)

        assert len(msgs_after) == 1, "Стриминг не возобновился после реконнекта"
        assert msgs_after[0].ticker == target

        allure.attach(
            f"Price after reconnect: {msgs_after[0].price}",
            name="Post-reconnect data"
        )
        print(f"[Test] Реконнект. Новая цена: {msgs_after[0].price}")
