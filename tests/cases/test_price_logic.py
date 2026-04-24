import pytest
import allure


@allure.epic("Trading Platform")
@allure.feature("Ticker Service")
@allure.story("Business Logic: Price Calculation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_price_delta_consistency(ticker_ops):
    """
    Проверка алгоритма изменения цены:
    Тест собирает последовательность котировок и проверяет, что:
    1. Изменение цены (Delta) не превышает установленный лимит (205).
    2. Цена остается в рамках допустимого диапазона.
    """
    target = "BTC/USD"
    allure.dynamic.description(
        f"Валидация математической модели для {target}. "
        "Проверяем отсутствие резких скачков (аномалий) в данных."
    )

    with allure.step(f"Сбор серии котировок для {target}"):
        # Собираем 5 последовательных сообщений
        messages = await ticker_ops.subscribe_and_get_messages(target, count=5)
        assert len(messages) == 5

    with allure.step("Анализ последовательности изменений"):
        for i in range(len(messages) - 1):
            curr_msg = messages[i]
            next_msg = messages[i + 1]

            delta = abs(next_msg.price - curr_msg.price)

            with allure.step(f"Сравнение шага {i + 1}: {curr_msg.price} -> {next_msg.price}"):
                allure.attach(
                    f"Previous: {curr_msg.price}\nNext: {next_msg.price}\nDelta: {delta}",
                    name="Price Change Details",
                    attachment_type=allure.attachment_type.TEXT
                )

                # Проверка лимита на разовое изменение цены (закладываем +5 на лаги)
                assert delta <= 205, f"Обнаружена аномалия! Скачок цены на {delta} единиц."

                # Проверка границ диапазона
                assert 100 <= next_msg.price <= 50000, f"Цена {next_msg.price} вышла за пределы"

    allure.attach("All deltas are within normal range", name="Final Status")
