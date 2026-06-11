import os
import sys
import asyncio
import logging
import binascii

# Запрашиваем секрет из переменной окружения
SECRET = os.getenv("TG_SECRET")

if not SECRET:
    print("\n[ОШИБКА] Не задан секретный ключ!")
    print("Запускай скрипт строго так:")
    print("export TG_SECRET=ddedInside42")
    print("python3 ios.py\n")
    sys.exit(1)

# Запрашиваем IP и порт из переменных окружения
BIND_HOST = os.getenv("BIND_HOST", "localhost")
BIND_PORT = int(os.getenv("BIND_PORT", "1042"))

# Пути импорта пакета proxy
_repo_root = os.path.dirname(os.path.abspath(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

from proxy.config import proxy_config

proxy_config.bind_host = BIND_HOST
proxy_config.bind_port = BIND_PORT
proxy_config.buffer_size = 32768
proxy_config.proxy_protocol = False

# Забираем секрет из переменной окружения
proxy_config.secret = SECRET

# Отрезаем префикс 'dd' для криптографического ядра
CLEAN_SECRET_HEX = proxy_config.secret[2:]
SECRET_BYTES = binascii.unhexlify(CLEAN_SECRET_HEX)

# Настройка жестких редиректов на рабочие IP серверов Telegram
ip1 = '149.154.167.220'
ip2 = '149.154.167.51'
ip2 = '95.161.64.100'
proxy_config.dc_redirects = {
    2: ip1,
    4: ip1,
    203: ip1
}

async def start_proxy():
    from proxy.tg_ws_proxy import _handle_client
    
    server = await asyncio.start_server(
        lambda r, w: _handle_client(r, w, SECRET_BYTES),
        proxy_config.bind_host,
        proxy_config.bind_port
    )
    
    print(f"\n=============================================")
    print(f" ДИНАМИЧЕСКИЙ КОНФИГ УСПЕШНО ЗАПУЩЕН НА iOS")
    print(f" IP: {proxy_config.bind_host}")
    print(f" Порт: {proxy_config.bind_port}")
    print(f" Секрет: {proxy_config.secret}")
    print(f"=============================================\n")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        print("\nСервер остановлен.")