"""Utilitário compartilhado para conversão segura de identificadores Mongo."""

from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(value: str) -> ObjectId | None:
    """Converte uma string em ObjectId, ou retorna None se inválida.

    Rejeita explicitamente valores não-string: ``ObjectId(None)`` geraria um id
    novo aleatório, o que mascararia entradas inválidas.
    """
    if not isinstance(value, str):
        return None
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def to_object_ids(values: list[str]) -> list[ObjectId]:
    """Converte uma lista de strings em ObjectIds, ignorando as inválidas."""
    converted = (to_object_id(value) for value in values)
    return [object_id for object_id in converted if object_id is not None]
