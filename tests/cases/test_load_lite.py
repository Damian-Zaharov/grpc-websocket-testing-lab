import pytest
import allure
import asyncio


@allure.epic("Trading Platform")
@allure.feature("Ticker Service")
@allure.story("Load Testing")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_load_multiple_subscriptions(ticker_ops):
    """
    Проверка производительности:
    Массовая подписка на 20 инструментов и проверка способности
    сервера поддерживать мульти-стриминг без потерь.
    """
    load_tickers = [f"TICKER_{i}/USD" for i in range(20)]

    allure.dynamic.description(
        f"Тест выполняет массовую подписку на {len(load_tickers)} различных инструментов "
        "и проверяет плотность входящего потока данных в WebSocket."
    )

    with allure.step(f"gRPC: Массовая подписка на {len(load_tickers)} тикеров"):
        for t in load_tickers:
            # Не логируем каждый шаг в консоль, но в Allure это будет видно
            await ticker_ops.grpc.subscribe(t)
        allure.attach(", ".join(load_tickers), name="List of Tickers")

    with allure.step("WS: Сбор данных под нагрузкой (5 секунд)"):
        # Ждем больше сообщений, чтобы увидеть плотность
        messages = await ticker_ops.ws.listen(count=60, timeout=5)

        received_tickers = set(m["ticker"] for m in messages)

        allure.attach(
            f"Всего поймано фреймов: {len(messages)}\n"
            f"Уникальных инструментов: {len(received_tickers)}",
            name="Load Statistics",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Анализ результатов нагрузки"):
        # Проверяем, что сервер не повис и выдал достаточно данных
        assert len(messages) >= 30, (
            f"Низкая производительность! Ожидали >= 30 сообщений, получили {len(messages)}"
        )

        # Проверяем что приходят разные тикеры, а не один и тот же
        assert len(received_tickers) > 10, (
            f"Слишком низкое разнообразие данных: всего {len(received_tickers)} инструментов в батче"
        )

        print(f"\n[Test] Нагрузка пройдена. Поймано {len(messages)} сообщений.")
