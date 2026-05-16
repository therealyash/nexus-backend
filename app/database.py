from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URL

mongo_client = AsyncIOMotorClient(MONGODB_URL)
db = mongo_client.nexus
users_col = db.users

# In-memory token blacklist — sufficient since tokens expire in 24 h
BLACKLIST: set = set()
