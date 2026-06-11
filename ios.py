import os
import sys
import asyncio
import logging
import binascii
import argparse

# Корректный импорт путей пакета proxy из корня проекта
_repo_root = os.path.dirname(os.path.abspath(__file__))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from proxy.config import proxy_config
from proxy.tg_ws_proxy import _handle_client

def main():
    parser = argparse.ArgumentParser(description="Telegram WebSocket Proxy CLI for iOS/Headless")
    parser.add_argument('--port', type=int, default=1042, help="Local bind port (default: 1042)")
    parser.add_argument('--secret', type=str, required=True, help="MTProto secret hex string")
    parser.add_argument('--host', type=str, default="127.0.0.1", help="Local bind host")
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, # Переключаем на INFO, чтобы лог не засирал экран в консоли
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout
    )

    # Включаем встроенный механизм предотвращения сна в a-Shell
    # Это заставит iOS держать туннель активным в фоне
    print("[iOS] Активация режима KeepAlive для работы в фоне...")
    try:
        os.system("keepalive")
    except Exception:
        pass

    proxy_config.bind_host = args.host
    proxy_config.bind_port = args.port
    proxy_config.secret = args.secret
    proxy_config.buffer_size = 65536 # Увеличиваем буфер, чтобы медиа не застревало
    proxy_config.proxy_protocol = False
    proxy_config.fake_tls_domain = "itldc.com"

    # РЕШЕНИЕ ПРОБЛЕМЫ DC 203: Генерируем мапу для ВСЕХ возможных дата-центров и их медиа-копий (до 300)
    # Если DC базовый или медийный (типа 203), он гарантированно пойдет на рабочий IP 149.154.167.220
    proxy_config.dc_redirects = {}
    for dc in range(1, 301):
        # Если в номере DC есть двойка (2, 202, 203 и т.д.) — шлем на IP DC2, остальное на базовый IP
        if str(dc).startswith('2') or str(dc).endswith('2') or dc == 203:
            proxy_config.dc_redirects[dc] = '149.154.167.220'
        else:
            proxy_config.dc_redirects[dc] = '149.154.167.99'

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
        print(f" СТАБИЛЬНЫЙ ПРОКСИ УСПЕШНО ЗАПУЩЕН")
        print(f" Адрес: {proxy_config.bind_host}:{proxy_config.bind_port}")
        print(f" Все DC (включая 203) успешно смаплены.")
        print(f"=============================================\n")
        
        async with server:
            await server.serve_forever()

    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        print("\nСервер остановлен.")

if __name__ == '__main__':
    main()
