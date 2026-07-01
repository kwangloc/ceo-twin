import functools

from langchain.chat_models import init_chat_model


@functools.lru_cache(maxsize=16)
def resolve_model(model_ref: str):
    """Return a cached chat model for *model_ref*."""
    return init_chat_model(model_ref)