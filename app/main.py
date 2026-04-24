import asyncio
from app.services.ticker_service import run_grpc_server, run_ws_server

async def main():
    # Запускаем оба сервера
    await asyncio.gather(
        run_grpc_server(),
        run_ws_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
