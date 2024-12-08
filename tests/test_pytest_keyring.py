import keyring


def test_tmp_keyring(pytester):
    """Test the tmp_keyring fixture."""
    pytester.makepyfile(
        """
        def test_tmp_keyring(tmp_keyring):
            tmp_keyring.set_password("aservice", "ausername", "pass")

            assert tmp_keyring.get_password("aservice", "ausername") == "pass"

        def test_tmp_keyring_is_gone(tmp_keyring):
            assert tmp_keyring.get_password("aservice", "ausername") is None
        """
    )

    result = pytester.runpytest("-vv")

    result.assert_outcomes(passed=2)
    assert keyring.get_password("aservice", "ausername") is None


def test_get_credential(pytester):
    """Test get_credential."""
    pytester.makepyfile(
        """
        def test_get_credential(credential_database_username):
            assert credential_database_username.password == "pass"
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_get_credential_without_username(pytester):
    """Test get_credential."""
    pytester.makepyfile(
        """
        def test_get_credential(credential_database):
            assert credential_database.password == "pass"
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_get_password(pytester):
    """Test get_password."""
    pytester.makepyfile(
        """
        def test_get_password(password_database_username):
            assert password_database_username == "pass"
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_get_password_without_username(pytester):
    """Test get_password."""
    pytester.makepyfile(
        """
        def test_get_password(password_database):
            assert password_database == "pass"
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_configure_backend(pytester):
    """Test configuring a keyring backend."""
    pytester.makepyfile(
        """
        def test_get_password(password_database_username):
            assert password_database_username is None

        def test_get_credential(credential_database_username):
            assert credential_database_username is None
        """
    )

    result = pytester.runpytest("--keyring-backend=keyring.backends.null.Keyring")

    result.assert_outcomes(passed=2)


def test_configure_password_prefix(pytester):
    """Test get_password with a custom prefix."""
    pytester.makepyfile(
        """
        def test_get_password(customprefix_database_username):
            assert customprefix_database_username is None
        """
    )

    result = pytester.runpytest("--keyring-password-prefix=customprefix")

    result.assert_outcomes(passed=1)


def test_configure_credential_prefix(pytester):
    """Test get_credential with a custom prefix."""
    pytester.makepyfile(
        """
        def test_get_credential(customprefix_database_username):
            assert customprefix_database_username is None
        """
    )

    result = pytester.runpytest("--keyring-credential-prefix=customprefix")

    result.assert_outcomes(passed=1)
