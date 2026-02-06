import asyncio
import random
import os
import socks
import config
from telethon.errors import FloodWaitError, PhoneNumberBannedError, SessionPasswordNeededError
from opentele.tl import TelegramClient

# Импортируем ваши модули
from core import generate_safe_api, secure_account, human_activity, set_privacy
from services import SMSManager, rotate_proxy

# --- НАСТРОЙКА РЕЖИМА РАБОТЫ ---
IS_TEST_MODE = True  # Поставь False, когда купишь СМС-ключ и прокси


# ------------------------------

async def register_account():
    """Основная логика регистрации одного аккаунта"""

    # 1. Смена IP (только если не тест)
    if not IS_TEST_MODE:
        print("[*] Шаг 1: Ротация IP...")
        rotate_proxy(config.PROXY_ROTATE_URL)

    # 2. Получение номера
    if IS_TEST_MODE:
        phone = input("[?] (TEST) Введите номер вручную (+7...): ")
        activation_id = "test_id"
    else:
        sms = SMSManager(config.SMS_API_KEY)
        print("[*] Шаг 2: Заказ номера в СМС-сервисе...")
        activation_id, phone = sms.get_number(country=6)  # 6 - Индонезия
        if not activation_id:
            print(f"[-] Ошибка СМС: {phone}")
            return

    print(f"[+] Работаем с номером: {phone}")

    # 3. Настройка клиента и прокси
    api_data = generate_safe_api()

    proxy = None
    if not IS_TEST_MODE:
        proxy = (socks.SOCKS5, config.PROXY_DATA['addr'], config.PROXY_DATA['port'],
                 True, config.PROXY_DATA['user'], config.PROXY_DATA['pass'])

    # Создаем сессию
    client = TelegramClient(f"sessions/{phone}", api=api_data, proxy=proxy)

    try:
        await client.connect()

        print(f"[*] Шаг 3: Запрос кода подтверждения...")
        await client.send_code_request(phone)

        # Имитация человеческой паузы (важно для защиты от банов!)
        delay = random.randint(15, 30)
        print(f"[*] Ожидание {delay} сек. (имитация действий пользователя)...")
        await asyncio.sleep(delay)

        # 4. Получение кода
        if IS_TEST_MODE:
            code = input(f"[?] Введите код из СМС для {phone}: ")
        else:
            code = sms.get_code(activation_id)
            if not code:
                print("[-] Код не пришел.")
                return

        # 5. Регистрация
        print("[*] Шаг 4: Регистрация в Telegram...")
        first_name = random.choice(["Dmitry", "Alex", "Ivan", "Max", "Artem"])
        await client.sign_up(code, first_name=first_name)

        print(f"[!!!] Аккаунт {phone} УСПЕШНО ЗАРЕГИСТРИРОВАН")

        # 6. ПРОГРЕВ И БЕЗОПАСНОСТЬ (Ваша "фишка")
        print("[*] Шаг 5: Настройка безопасности и прогрев...")
        await set_privacy(client)  # Скрываем номер
        await secure_account(client, "SafePass2026!")  # Ставим 2FA
        await human_activity(client)  # Подписки и имитация жизни

        print(f"[DONE] Аккаунт {phone} готов и сохранен в /sessions")

    except FloodWaitError as e:
        print(f"[!] Ошибка Flood: нужно подождать {e.seconds} секунд.")
    except PhoneNumberBannedError:
        print(f"[-] Номер {phone} забанен.")
    except Exception as e:
        print(f"[-] Непредвиденная ошибка: {e}")
    finally:
        await client.disconnect()


async def main():
    """Запуск бесконечного цикла или одиночной регистрации"""
    if not os.path.exists("sessions"): os.makedirs("sessions")

    if IS_TEST_MODE:
        await register_account()
    else:
        count = int(input("[?] Сколько аккаунтов зарегистрировать? "))
        for i in range(count):
            print(f"\n--- Регистрация аккаунта №{i + 1} ---")
            await register_account()
            # Пауза между аккаунтами для безопасности
            await asyncio.sleep(random.randint(60, 120))


if __name__ == "__main__":
    asyncio.run(main())