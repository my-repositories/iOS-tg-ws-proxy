import os
import sys
import asyncio
import logging
import binascii
import argparse

# Пути импорта пакета proxy
_repo_root = os.path.dirname(os.path.abspath(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from proxy.config import proxy_config
from proxy.tg_ws_proxy import _handle_client

def main():
    parser = argparse.ArgumentParser(description="Telegram WebSocket Proxy CLI for iOS/Headless")
    parser.add_argument('--port', type=int, default=1042, help="Local bind port")
    parser.add_argument('--secret', type=str, required=True, help="MTProto secret hex string")
    parser.add_argument('--host', type=str, default="127.0.0.1", help="Local bind host")
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG, # Возвращаем дебаг, чтобы ты видел, если что-то пойдет не так
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout
    )

    proxy_config.bind_host = args.host
    proxy_config.bind_port = args.port
    proxy_config.secret = args.secret
    proxy_config.buffer_size = 32768
    proxy_config.proxy_protocol = False
    proxy_config.fake_tls_domain = "itldc.com"

    # ЖЕСТКАЯ НАСТРОЙКА ИЗ ТВОЕГО ХОСТС + ИСПРАВЛЕНИЕ ДЛЯ МЕДИА (DC 203)
    # Теперь и базовая телега, и медиа-сервера гарантированно пойдут на рабочий IP
    proxy_config.dc_redirects = {
        1: '149.154.167.220',
        2: '149.154.167.220',
        3: '149.154.167.220',
        4: '149.154.167.220',
        5: '149.154.167.220',
        203: '149.154.167.220'  # <-- Вот этот бро спасет от ошибки "not in config"
    }

    # Отрезаем префиксы секрета для ядра криптографии
    clean_secret = args.secret
    if len(clean_secret) == 34 and clean_secret.startswith(("ee", "dd")):
        clean_secret = clean_secret[2:]
    elif len(clean_secret) == 36 and clean_secret.startswith("eeee"):
        clean_secret = clean_secret[4:]

    secret_bytes = binascii.unhexlify(clean_secret)

    async def start_proxy():
        server = await asyncio.start_server(
            lambda r, w: _handle_client(r, w, secret_bytes),
            proxy_config.bind_host,
            proxy_config.bind_port
        )
        
        print(f"\n=============================================")
        print(f" ИСПРАВЛЕННЫЙ ТУННЕЛЬ ПОД iOS ЗАПУЩЕН")
        print(f" Порт: {proxy_config.bind_port}")
        print(f"=============================================\n")
        
        async with server:
            await server.serve_forever()

    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        print("\nСервер остановлен.")

if __name__ == '__main__':
    main()
