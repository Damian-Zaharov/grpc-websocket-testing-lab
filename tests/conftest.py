import pytest_asyncio
import asyncio
from tests.clients.grpc_client import TickerGrpcClient
from tests.clients.ws_client import TickerWsClient
from tests.services.ticker_helper import TickerTestService

@pytest_asyncio.fixture
async def grpc_client():
    client = TickerGrpcClient()
    yield client
    await client.close()

@pytest_asyncio.fixture
async def ws_client():
    client = TickerWsClient()
    await client.connect()
    yield client
    await client.disconnect()

@pytest_asyncio.fixture
async def ticker_ops(grpc_client, ws_client):
    """для комплексных операций"""
    return TickerTestService(grpc_client, ws_client)
