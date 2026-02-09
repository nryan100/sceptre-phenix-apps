from collections.abc import Callable
from typing import Any

# from phenix_apps.common.logger import logger

# HACK - workaround for broken logging -----------------------------------------------
import logging
logger = logging.getLogger('tmp')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/var/log/phenix/scale-registry.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
# ------------------------------------------------------------------------------------


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, dict[str, type]] = {}

    def register_plugin(
        self, name: str, version: str = "1.0.0", deprecated: bool = False
    ) -> Callable[[type], type]:
        def decorator(cls: type) -> type:
            if name not in self._plugins:
                self._plugins[name] = {}
            if version in self._plugins[name]:
                raise ValueError(
                    f"Plugin '{name}' version '{version}' is already registered."
                )
            self._plugins[name][version] = cls
            cls._phenix_deprecated = deprecated
            return cls

        return decorator

    def get_plugin(self, name: str, version: str = "latest") -> Any:
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not found.")

        versions = self._plugins[name]
        if version == "latest":
            try:
                # Sort semantically (e.g., 1.10.0 > 1.2.0)
                version = sorted(
                    versions.keys(), key=lambda v: [int(p) for p in v.split(".")]
                )[-1]
            except ValueError:
                version = sorted(versions.keys())[-1]

        if version not in versions:
            raise ValueError(f"Plugin '{name}' version '{version}' not found.")

        cls = versions[version]
        if getattr(cls, "_phenix_deprecated", False):
            logger.warning(f"Plugin '{name}' version '{version}' is deprecated.")

        return cls()


_registry = PluginRegistry()

register_plugin = _registry.register_plugin
get_plugin = _registry.get_plugin
PLUGIN_REGISTRY = _registry._plugins
