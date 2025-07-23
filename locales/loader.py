import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"

@lru_cache
def _load(locale: str) -> Dict[str, Any]:
    logger.debug('_load')

    path = _LOCALE_DIR / f"{locale}.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def reload_locale():
    logger.debug('reload_locale')

    _load.cache_clear()

def t(key: str, lang: str = 'ru', **kwargs) -> str:
    logger.debug(f't({key})')

    data = _load(lang)

    for part in key.split('.'):
        data = data[part]

    return data.format(**kwargs)