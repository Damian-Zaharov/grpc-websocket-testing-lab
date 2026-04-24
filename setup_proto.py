import os
import subprocess
import sys


def generate_proto():
    os.makedirs("app/generated", exist_ok=True)

    # sys.executable гарантирует, что мы используем питон из .venv
    command = [
        sys.executable, "-m", "grpc_tools.protoc",
        "-Iapp/proto",
        "--python_out=app/generated",
        "--grpc_python_out=app/generated",
        "app/proto/ticker.proto"
    ]

    try:
        subprocess.run(command, check=True)
        print("🔔 Код из Proto успешно сгенерирован!")

        grpc_file = "app/generated/ticker_pb2_grpc.py"
        if os.path.exists(grpc_file):
            with open(grpc_file, "r") as f:
                content = f.read()
            with open(grpc_file, "w") as f:
                f.write(content.replace("import ticker_pb2", "from . import ticker_pb2"))
            print("🔔 Импорты исправлены!")
    except subprocess.CalledProcessError as e:
        print(f"🤬 Ошибка при генерации: {e}")
    except FileNotFoundError:
        print("🤬 Файл ticker_pb2_grpc.py не найден. Проверь пути.")


if __name__ == "__main__":
    generate_proto()
