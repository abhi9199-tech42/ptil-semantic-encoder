import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    logger.warning("tiktoken not installed. Falling back to approximate token counting.")


class TokenizerBackend:
    def count_tokens(self, text: str, tokenizer_type: str = "bpe") -> int:
        raise NotImplementedError


class TiktokenBackend(TokenizerBackend):
    MODEL_ENCODING_MAP = {
        "bpe": "cl100k_base",
        "unigram": "cl100k_base",
        "wordpiece": "gpt2",
    }

    def __init__(self):
        self._encodings = {}

    def count_tokens(self, text: str, tokenizer_type: str = "bpe") -> int:
        encoding_name = self.MODEL_ENCODING_MAP.get(
            tokenizer_type.lower(), "cl100k_base"
        )
        if encoding_name not in self._encodings:
            try:
                self._encodings[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to load tiktoken encoding '{encoding_name}': {e}")
                return len(text.split())

        encoding = self._encodings[encoding_name]
        try:
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"tiktoken encoding failed: {e}")
            return len(text.split())


class WhitespaceBackend(TokenizerBackend):
    def count_tokens(self, text: str, tokenizer_type: str = "bpe") -> int:
        return len(text.split())


def create_tokenizer_backend() -> TokenizerBackend:
    if HAS_TIKTOKEN:
        return TiktokenBackend()
    return WhitespaceBackend()
