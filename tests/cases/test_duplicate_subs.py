import pytest
import allure
import asyncio


@allure.epic("Trading Platform")
@allure.feature("Ticker Service")
@allure.story("Idempotency & Traffic Control")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio
async def test_no_extra_traffic_on_duplicate(ticker_ops):
    """
    Проверка подписок:
    Повторные запросы на один и тот же тикер не должны приводить к
    умножению трафика в WebSocket канале.
    """
    target = "SOL/USD"

    allure.dynamic.description(
        f"Тест подписывается на {target} 3 раза и проверяет, что количество "
        f"сообщений в секунду соответствует настройкам сервера (1 msg/sec), а не количеству подписок."
    )

    with allure.step(f"Тройная подписка на тикер {target} через gRPC"):
        for i in range(3):
            await ticker_ops.grpc.subscribe(target)

    with allure.step("Сбор данных из WebSocket (интервал 3.5 сек)"):
        await asyncio.sleep(3.5)
        # Слушаем поток
        raw_messages = await ticker_ops.ws.listen(count=100, timeout=0.1)

        # Фильтруем только наш тикер
        target_messages = [m for m in raw_messages if m["ticker"] == target]

        allure.attach(
            f"Всего поймано: {len(raw_messages)}\nИз них для {target}: {len(target_messages)}",
            name="Traffic Stats",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка отсутствия дублирующего спама"):
        # За 3.5 сек должно быть 3 или 4 тика (максимум 5 с учетом погрешности асинхронности)
        count = len(target_messages)
        print(f"\n[Test] Поймано сообщений для {target}: {count}")

        assert count <= 5, f"Обнаружен лишний трафик! Получено {count} сообщений вместо ~4."
        assert count > 0, "Данные по тикеру вообще не поступили в канал."

        allure.attach(str(target_messages), name="Filtered Messages", attachment_type=allure.attachment_type.JSON)
