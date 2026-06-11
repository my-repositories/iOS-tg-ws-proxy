import asyncio
import subprocess

async def ping_ip(ip: str, count: int = 3) -> tuple:
    """Пинг одного IP"""
    try:
        # Для Linux/macOS
        result = subprocess.run(
            ['ping', '-c', str(count), ip],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Извлекаем время пинга
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line:
                    time = line.split('time=')[1].split()[0]
                    return (True, time)
            return (True, '0ms')
        else:
            return (False, 'timeout')
    except Exception as e:
        return (False, str(e))

async def main():
    ips = [
        '149.154.167.220',
        '149.154.167.51',
        '95.161.64.100'
    ]
    
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ПИНГА IP TELEGRAM")
    print("="*50 + "\n")
    
    for ip in ips:
        success, time = await ping_ip(ip)
        status = "✓ OK" if success else "✗ FAIL"
        print(f"{ip:25} | {status:10} | пинг: {time}")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    asyncio.run(main())
