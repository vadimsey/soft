import random
import os
import asyncio
from opentele.api import API
from telethon import functions, types


def generate_safe_api():
    """Генерирует уникальный отпечаток устройства (Anti-Detection)"""
    # Список актуальных моделей устройств
    devices = [
        "SM-S928B", "SM-A546B", "23127PN0CG", "Pixel 8 Pro",
        "CPH2581", "RMX3363", "M2101K6G"
    ]

    selected_model = random.choice(devices)
    android_ver = str(random.randint(10, 14))

    # ПРЯМАЯ ИНИЦИАЛИЗАЦИЯ (Самый стабильный способ)
    # Если .Generate() не принимает 'model', мы создаем объект напрямую
    api = API.TelegramAndroid()
    api.device_model = selected_model
    api.system_version = android_ver
    api.app_version = "10.11.0"
    api.lang_code = "en"
    api.system_lang_code = "en-US"

    return api


async def set_privacy(client):
    """Настройка приватности: скрываем номер (снижает риск бана)"""
    try:
        # Скрываем номер телефона от всех
        await client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyPhoneNumber(),
            rules=[types.InputPrivacyValueDisallowAll()]
        ))
        # Запрещаем добавлять в группы всем, кроме контактов
        await client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyChatInvite(),
            rules=[types.InputPrivacyValueAllowContacts()]
        ))
        print("[+] Настройки приватности применены.")
    except Exception as e:
        print(f"[-] Ошибка при настройке приватности: {e}")


async def secure_account(client, password):
    """Установка 2FA пароля и аватарки"""
    try:
        # Установка облачного пароля
        await client.edit_2fa(new_password=password)
        print(f"[+] 2FA пароль установлен: {password}")

        # Загрузка случайной аватарки
        if os.path.exists("avatars"):
            photos = [f for f in os.listdir("avatars") if f.endswith(('.jpg', '.jpeg', '.png'))]
            if photos:
                photo_path = os.path.join("avatars", random.choice(photos))
                await client(functions.photos.UploadProfilePhotoRequest(
                    file=await client.upload_file(photo_path)
                ))
                print(f"[+] Аватарка {photo_path} загружена.")
        return True
    except Exception as e:
        print(f"[-] Ошибка безопасности: {e}")
        return False


async def human_activity(client):
    """Имитация активности человека (прогрев)"""
    try:
        channels = ['@telegram', '@durov']
        target = random.choice(channels)

        # Подписка
        await client(functions.channels.JoinChannelRequest(channel=target))
        print(f"[+] Прогрев: подписались на {target}")

        await asyncio.sleep(random.randint(5, 10))

        # Читаем посты
        await client(functions.messages.GetHistoryRequest(
            peer=target, limit=5, offset_date=None, offset_id=0,
            max_id=0, min_id=0, add_offset=0, hash=0
        ))
        print(f"[+] Прогрев: посты прочитаны.")
    except Exception as e:
        print(f"[-] Ошибка прогрева: {e}")