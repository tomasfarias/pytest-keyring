import typing

import keyring
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser


class KeyringProtocol(typing.Protocol):
    def set_password(self, service_name: str, username: str, password: str) -> None:
        ...

    def delete_password(self, service_name: str, username: str) -> None:
        ...

    def get_password(self, service_name: str, username: str) -> str | None:
        ...

    def get_credential(
        self, service_name: str, username: typing.Optional[str]
    ) -> keyring.credentials.Credential | None:
        ...


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("keyring", "pytest-keyring")
    group.addoption(
        "--keyring-credential-prefix",
        action="store",
        dest="keyring_credential_prefix",
        default="credential",
        help="Prefix to use for keyring get_credential arguments.",
    )
    group.addoption(
        "--keyring-password-prefix",
        action="store",
        dest="keyring_password_prefix",
        default="password",
        help="Prefix to use for keyring get_password arguments.",
    )
    group.addoption(
        "--keyring-backend",
        action="store",
        dest="keyring_backend",
        default=None,
        help="Prefix to use for keyring get_password arguments.",
    )


@pytest.fixture
def tmp_keyring() -> typing.Iterator[KeyringProtocol]:
    to_delete = []
    current_set_password = keyring.set_password

    def record_and_set_password(
        service_name: str, username: str, password: str
    ) -> None:
        current_set_password(service_name, username, password)
        to_delete.append((service_name, username))

    keyring.set_password = record_and_set_password

    yield keyring

    for service, username in to_delete:
        keyring.delete_password(service, username)


def pytest_configure(config: Config) -> None:
    backend = config.getoption("keyring_backend")

    if isinstance(backend, str):
        backend_cls = keyring.core.load_keyring(backend)
        keyring.set_keyring(backend_cls)


def pytest_collection_modifyitems(config: Config, items) -> None:  # type: ignore[no-untyped-def]
    credential_prefix = config.getoption("keyring_credential_prefix")
    password_prefix = config.getoption("keyring_password_prefix")

    for item in items:
        for fixture_name in item.fixturenames:
            if fixture_name in item.funcargs:
                continue

            if fixture_name.startswith(credential_prefix):
                _, service_name, username = fixture_name.split("_", maxsplit=2)
                item.funcargs[fixture_name] = keyring.get_credential(
                    service_name, username
                )

            elif fixture_name.startswith(password_prefix):
                _, service_name, username = fixture_name.split("_", maxsplit=2)
                item.funcargs[fixture_name] = keyring.get_password(
                    service_name, username
                )
