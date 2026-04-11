from schema_reuse.settings import PACKAGE_NAME


def test_package_name() -> None:
    assert PACKAGE_NAME == "schema_reuse"
