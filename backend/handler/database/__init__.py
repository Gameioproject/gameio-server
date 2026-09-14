# Every mapped model must be imported before the first query, or the string
# relationships on User/Collection cannot resolve. The rom-era models stay
# until their tables are dropped.

from .catalog_handler import DBCatalogHandler
from .client_tokens_handler import DBClientTokensHandler
from .collections_handler import DBCollectionsHandler
from .devices_handler import DBDevicesHandler
from .game_activity_handler import DBGameActivityHandler
from .game_comments_handler import DBGameCommentsHandler
from .game_source_handler import DBGameSourceHandler
from .permissions_handler import DBPermissionsHandler
from .users_handler import DBUsersHandler

db_catalog_handler = DBCatalogHandler()
db_game_source_handler = DBGameSourceHandler()
db_client_token_handler = DBClientTokensHandler()
db_collection_handler = DBCollectionsHandler()
db_device_handler = DBDevicesHandler()
db_game_activity_handler = DBGameActivityHandler()
db_game_comments_handler = DBGameCommentsHandler()
db_permission_handler = DBPermissionsHandler()
db_user_handler = DBUsersHandler()
