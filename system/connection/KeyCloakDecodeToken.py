from base64 import b64decode
from cryptography.hazmat.primitives import serialization
import jwt  # pip install PyJWT
import requests

from system.connection.BaseConnection import BaseConnection


class KeyCloakDecodeToken(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.algorithm, self.public_key = None, None

    async def connection(self):
        r = requests.get(self.values['url'])
        if r.status_code == 200:
            key_der_base64 = r.json()['public_key']
            key_der = b64decode(key_der_base64.encode())
            self.algorithm, self.public_key = 'RS256', serialization.load_der_public_key(key_der)
            self.logger.info('KeyCloak подключен')
            return True
        self.logger.error('Не удалось подключиться к KeyCloak')
        return False

    def token_decode(self, token):
        try:
            return jwt.decode(token, self.public_key, algorithms=self.algorithm, options={"verify_aud": False})
        except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
            pass
