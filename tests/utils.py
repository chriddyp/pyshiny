def test_async():
    try:

        import asgiref  # pylint: disable=unused-import, # noqa: F401

        return True
    except ImportError:
        return False
