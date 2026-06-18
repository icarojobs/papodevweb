"""Testes do tradutor de erros de domínio para HTTP."""

import pytest
from fastapi import HTTPException

from app.api.error_mapping import domain_errors
from app.services.exceptions import ConversationNotFoundError, InvalidTokenError


def test_maps_known_domain_error():
    with pytest.raises(HTTPException) as exc_info, domain_errors():
        raise ConversationNotFoundError
    assert exc_info.value.status_code == 404


def test_reraises_unmapped_domain_error():
    # Erros de domínio sem mapeamento devem propagar inalterados.
    with pytest.raises(InvalidTokenError), domain_errors():
        raise InvalidTokenError
