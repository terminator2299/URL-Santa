import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection string - use environment variable for security
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# Database and collection names
DATABASE_NAME = "UrlSanta"
USERS_COLLECTION = "users"
URLS_COLLECTION = "urls"
SESSIONS_COLLECTION = "sessions"

# Initialize MongoDB client with SSL configuration
client = AsyncIOMotorClient(
    MONGODB_URL,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
)
db = client[DATABASE_NAME]

# Collections
users_collection = db[USERS_COLLECTION]
urls_collection = db[URLS_COLLECTION]
sessions_collection = db[SESSIONS_COLLECTION] 