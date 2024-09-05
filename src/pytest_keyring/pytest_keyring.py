import types
import typing

import keyring
import pytest


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


def pytest_addoption(parser: pytest.Parser) -> None:
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


class TemporaryKeyringBackend:
    """Wrap a KeyringBackend to delete any passwords set while using it.

    Attributes:
        _backend: The KeyringBackend we are wrapping.
        to_delete: An internal set to keep track of passwords to delete.
    """

    def __init__(self, backend: keyring.backend.KeyringBackend):
        """Init a new TemporaryKeyringBackend with an underlying KeyringBackend."""
        self._backend = backend
        self.to_delete: typing.Set[tuple[str, str]] = set()

    def __getattr__(self, name: str) -> typing.Any:
        """Behave like the underlying backend."""
        return getattr(self._backend, name)

    def __enter__(self) -> "TemporaryKeyringBackend":
        """Context manager protocol."""
        return self

    def __exit__(
        self,
        exc_type: typing.Type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None:
        """On context manager exit, clear any items in to_delete."""
        self.clear_to_delete()

    def set_password(self, service: str, username: str, password: str) -> None:
        """Record passwords set to be deleted later."""
        self._backend.set_password(service, username, password)
        self.to_delete.add((service, username))

    def clear_to_delete(self) -> None:
        """Delete any items that were set while using this TemporaryKeyringBackend."""
        for service, username in self.to_delete:
            self._backend.delete_password(service, username)
            assert self._backend.get_password(service, username) is None


@pytest.fixture(scope="function")
def tmp_keyring() -> typing.Iterator[TemporaryKeyringBackend]:
    backend = keyring.get_keyring()

    with TemporaryKeyringBackend(backend) as tmp_backend:
        yield tmp_backend


def pytest_configure(config: pytest.Config) -> None:
    backend = config.getoption("keyring_backend")

    if isinstance(backend, str):
        backend_cls = keyring.core.load_keyring(backend)
        keyring.set_keyring(backend_cls)


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    credential_prefix = config.getoption("keyring_credential_prefix")
    password_prefix = config.getoption("keyring_password_prefix")

    for item in items:
        # These getattr calls are for mypy. Item should contain these attributes.
        for fixture_name in getattr(item, "fixturenames", []):
            if fixture_name in getattr(item, "funcargs", []):
                continue

            if fixture_name.startswith(credential_prefix):
                _, service_name, username = fixture_name.split("_", maxsplit=2)
                credential = keyring.get_credential(service_name, username)

                def fixture_credential_func() -> keyring.credentials.Credential | None:
                    """Define a function for the dynamic fixture."""
                    return credential

                item.session._fixturemanager._arg2fixturedefs[fixture_name] = [
                    pytest.FixtureDef(
                        argname=fixture_name,
                        func=fixture_credential_func,
                        scope="session",
                        config=session.config,
                        baseid=None,
                        params=None,
                    ),
                ]

            elif fixture_name.startswith(password_prefix):
                _, service_name, username = fixture_name.split("_", maxsplit=2)
                password = keyring.get_password(service_name, username)

                def fixture_password_func() -> str | None:
                    """Define a function for the dynamic fixture."""
                    return password

                item.session._fixturemanager._arg2fixturedefs[fixture_name] = [
                    pytest.FixtureDef(
                        argname=fixture_name,
                        func=fixture_password_func,
                        config=session.config,
                        scope="session",
                        baseid=None,
                        params=None,
                    ),
                ]
