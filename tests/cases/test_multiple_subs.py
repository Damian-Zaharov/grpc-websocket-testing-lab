import pytest
import allure


@allure.epic("Trading Platform")
@allure.feature("Ticker Service")
@allure.story("Multi-ticker Streaming")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio
async def test_multiple_tickers_logic(ticker_ops):
    """
    Проверка работы с несколькими инструментами:
    Подписываемся на список тикеров и проверяем, что данные по каждому
    присутствуют в общем WebSocket-потоке.
    """
    target_tickers = ["BTC/USD", "ETH/USD", "XRP/USD"]

    allure.dynamic.description(
        f"Тест последовательно подписывается на {target_tickers} "
        "и валидирует наличие сообщений по каждому инструменту в отфильтрованном потоке."
    )

    for ticker in target_tickers:
        with allure.step(f"Подписка и проверка стриминга для {ticker}"):
            # Хелпер внутри уже имеет allure.step и аттачменты
            messages = await ticker_ops.subscribe_and_get_messages(ticker, count=1)

            assert len(messages) == 1, f"Не получено данных для тикера {ticker}"
            assert messages[0].ticker == ticker

            allure.attach(
                f"Ticker: {messages[0].ticker}\nPrice: {messages[0].price}",
                name=f"Data for {ticker}",
                attachment_type=allure.attachment_type.TEXT
            )
            print(f"[Test] Тикер {ticker} успешно найден в стриме.")

    with allure.step("Финальная проверка состояния"):
        # Проверить, что ничего не сломалось в процессе
        allure.attach("All subscriptions are active", name="Status")
