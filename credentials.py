import httpx
import os
import time


class Keys:
    def __init__(self):
        self.gpt_token = os.environ.get('GPT_TOKEN')
        self.bot_token = os.environ.get('BOT_TOKEN')
        # Данные для авторизации GigaChat
        self.giga_uid = os.environ.get('GIGA_UID')
        self.giga_token = os.environ.get('GIGA_TOKEN')
        self.giga_oauth = None
        self.giga_oauth_expire = None
        self.check_update_giga_oauth_expire()

    # Получение ключа аутентификации для GigaChat
    @staticmethod
    def get_giga_oauth(token, uid):
        url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'

        payload = {
            'scope': 'GIGACHAT_API_PERS'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': uid,
            'Authorization': f'Basic {token}'
        }

        response = httpx.post(url, data=payload, headers=headers, verify=False)
        if response.status_code != 200:
            raise Exception(response.text)
        elif response.json() is None:
            raise Exception(response.text)
        elif 'access_token' not in response.json():
            raise Exception(response.json())
        else:
            return response.json()

    # Проверка актуальности и обновление ключа авторизации GigaChat
    def check_update_giga_oauth_expire(self):
        if self.giga_oauth_expire is None or self.giga_oauth_expire < int(time.time() * 1000):
            g_oauth_data = self.get_giga_oauth(self.giga_token, self.giga_uid)
            self.giga_oauth = None if not self.giga_token else g_oauth_data['access_token']
            self.giga_oauth_expire = None if not self.giga_token else int(g_oauth_data['expires_at'])
        else:
            return True
