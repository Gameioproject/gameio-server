from .assets_handler import FSAssetsHandler
from .resources_handler import FSResourcesHandler

fs_asset_handler = FSAssetsHandler()
fs_resource_handler = FSResourcesHandler()

__all__ = [
    "FSAssetsHandler",
    "FSResourcesHandler",
    "fs_asset_handler",
    "fs_resource_handler",
]
