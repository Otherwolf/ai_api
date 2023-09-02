from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError, KeycloakConnectionError, KeycloakGetError
from system.connection.BaseConnection import BaseConnection


class KeyCloak(BaseConnection):
    async def connection(self):
        return self.connect()

    def connect(self):
        self.admin = KeycloakAdmin(
            server_url=f"{'https' if self.values['verify'] else 'http'}://{self.values['domain']}/auth/",
            username=self.values['username'], password=self.values['password'],
            realm_name=self.values['realm_name'], verify=self.values['verify'])
        self.logger.info('Keycloak подключен!')
        return True

    def reconnect(func):
        def magic(*args, **kwargs):
            self = args[0]
            for _ in range(2):
                try:
                    return func(*args, **kwargs)
                except (KeycloakError, KeycloakConnectionError, KeycloakGetError) as err:
                    self.logger.error(f"{args[1]}: {err}")
                    self.connect()
            return False
        return magic

    @reconnect
    def get_user(self, user_id):
        return self.admin.get_user(user_id)

    @reconnect
    def get_client_id(self, client_name):
        return self.admin.get_client_id(client_name)
