import pytest
import allure
from pydantic import ValidationError
from tests.data.models import TickerMessage


@allure.epic("Trading Platform")
@allure.feature("Data Validation")
@allure.story("Pydantic Schema Integrity")
@pytest.mark.asyncio
async def test_pydantic_schema_validation():
    with allure.step("Подготовка некорректных данных"):
        bad_data = {
            "ticker": "btc/usd",
            "price": -500.0,
            "status": "UNKNOWN"
        }

    # Ловим ошибку и сохраняем её в переменную exc_info
    with allure.step("Ожидание ошибки валидации Pydantic"):
        with pytest.raises(ValidationError) as exc_info:
            TickerMessage(**bad_data)

    # Достаем список ошибок
    errors = exc_info.value.errors()
    # берем только имена полей из кортежей ('ticker',), ('price',)
    error_fields = [e['loc'][0] for e in errors]

    with allure.step(f"Проверка полей с ошибками: {error_fields}"):
        assert "ticker" in error_fields
        assert "price" in error_fields
        assert "status" in error_fields


@allure.epic("Trading Platform")
@allure.feature("Data Validation")
@allure.story("gRPC Contract")
@pytest.mark.asyncio
async def test_grpc_validation_empty_ticker(ticker_ops):
    """Проверка контракта gRPC на пустые значения"""
    with allure.step("Отправка запроса с пустым тикером"):
        response = await ticker_ops.grpc.subscribe("")

    with allure.step("Валидация ответа сервера"):
        assert response.accepted is False
        assert "empty ticker" in response.message.lower()
        allure.attach(response.message, name="Server Error Message")


@allure.epic("Trading Platform")
@allure.feature("Data Validation")
@allure.story("WebSocket Streaming")
@pytest.mark.asyncio
async def test_ws_data_integrity(ticker_ops):
    """Проверка того, что реальные данные из сокета соответствуют модели"""
    target = "ETH/USD"

    with allure.step(f"Получение сообщения для {target}"):
        messages = await ticker_ops.subscribe_and_get_messages(target, count=1)
        msg = messages[0]

    with allure.step("Бизнес-проверка полей модели"):
        assert msg.ticker == target
        assert msg.status == "LIVE"
        allure.attach(msg.model_dump_json(), name="Validated Model", attachment_type=allure.attachment_type.JSON)
