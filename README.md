# pytest-keyring

Pytest plugin to access any configured keyring using the [`keyring`](https://pypi.org/project/keyring/) package.

## Motivation

Frequently, tests require access to services, like databases, REST APIs, or blob storages. These services are sometimes hard or impossibel to mock or reproduce in a test environment. In particular, functional or end-to-end tests will be inclined to interact with real instances of these services. Accessing these services can require credentials, and using the keyring can be an alternative to populating CI environment variables with credentials.

## Installation

Install with:

```bash
python -m pip install pytest-keyring
```

Python versions 3.8 to 3.12 are supported.

## Usage

### Accessing credentials in keyring

Any test arguments whose names match the prefixes configured by `--keyring-password-prefix` and `--keyring-credential-prefix` (`"password"` and `"credential"` by default) will be replaced by the corresponding password or credential, respectively:

```python
def test_with_database(credential_postgres_dbuser):
    client = connect(
        username=credential_postgres_dbuser.username,
        password=credential_postgres_dbuser.password
    )
    ...
```

When collecting the test, the `credential_postgres_dbuser` instructs `pytest-keyring` to fetch the credential for the "postgres" service and the "dbuser" username, by making the following call to `keyring.get_credential`:

```python
keyring.get_credential("postgres", "dbuser")
```

### Configuring a keyring backend

The `--keyring-backend` configuration flag can be used to specify a keyring backend. For example, setting the null keyring backend:

```bash
pytest --keyring-backend=keyring.backends.null.Keyring
```

Causes all credentials and passwords to be `None`:

```python
def test_with_null_backend(credential_postgres_dbuser, password_postgres_dbuser):
    assert credential_postgres_dbuser is None
    assert password_postgres_dbuser is None
    ...
```
