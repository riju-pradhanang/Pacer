import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_prod_rejects_default_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('PACER_JWT_SECRET', raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, env='prod')


def test_dev_allows_default_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('PACER_JWT_SECRET', raising=False)
    assert Settings(_env_file=None, env='dev').env == 'dev'