import os
import sys
import asyncio
import logging
import binascii

# Проверяем, передан ли секрет через переменную окружения
if "TG_SECRET" not in os.environ:
    print("\n[ОШИБКА] Не задан секретный ключ!")
    print("Запускай скрипт строго так:")
    print("env TG_SECRET=ddedInside42 python3 ios.py\n")
    sys.exit(1)

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
proxy_config.bind_host = "127.0.0.1"
proxy_config.bind_port = 1042
proxy_config.buffer_size = 32768
proxy_config.proxy_protocol = False

# Забираем секрет из переменной окружения (динамический ввод)
proxy_config.secret = os.environ["TG_SECRET"]

# Отрезаем префикс 'dd' для криптографического ядра
CLEAN_SECRET_HEX = proxy_config.secret[2:]
SECRET_BYTES = binascii.unhexlify(CLEAN_SECRET_HEX)

# Настройка жестких редиректов на рабочие IP серверов Telegram
proxy_config.dc_redirects = {
    2: '149.154.167.220',
    4: '149.154.167.220',
    203: '149.154.167.220'
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
