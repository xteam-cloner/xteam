import sys

from decouple import config

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Var:
    # mandatory
    API_ID = (
        int(sys.argv[1]) if len(sys.argv) > 1 else config("API_ID", default=6, cast=int)
    )
    API_HASH = (
        sys.argv[2]
        if len(sys.argv) > 2
        else config("API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e")
    )
    SESSION = sys.argv[3] if len(sys.argv) > 3 else config("SESSION", default=None)
        
    API_ID2 = config("API_ID2", default=None) 
    if API_ID2 is not None:
        API_ID2 = int(API_ID2)
        
    API_HASH2 = config("API_HASH2", default=None) 
    SESSION2 = config("SESSION2", default=None)
    
    API_ID3 = config("API_ID3", default=None) 
    if API_ID3 is not None:
        API_ID3 = int(API_ID3)
        
    API_HASH3 = config("API_HASH3", default=None)
    SESSION3 = config("SESSION3", default=None)
    
    REDIS_URI = (
        sys.argv[4]
        if len(sys.argv) > 4
        else (config("REDIS_URI", default=None) or config("REDIS_URL", default=None))
    )
    REDIS_PASSWORD = (
        sys.argv[5] if len(sys.argv) > 5 else config("REDIS_PASSWORD", default=None)
    )
    # extras
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    LOG_CHANNEL = config("LOG_CHANNEL", default=0, cast=int)
    HEROKU_APP_NAME = config("HEROKU_APP_NAME", default=None)
    HEROKU_API = config("HEROKU_API", default=None)
    VC_SESSION = config("VC_SESSION", default=None)
    ADDONS = config("ADDONS", default=False, cast=bool)
    VCBOT = config("VCBOT", default=False, cast=bool)
    # for railway
    REDISPASSWORD = config("REDISPASSWORD", default=None)
    REDISHOST = config("REDISHOST", default=None)
    REDISPORT = config("REDISPORT", default=None)
    REDISUSER = config("REDISUSER", default=None)
    # for sql
    DATABASE_URL = config("DATABASE_URL", default=None)
    # for MONGODB users
    MONGO_URI = config("MONGO_URI", default=None)
    ASSISTANT_ID = (
        int(sys.argv[1]) if len(sys.argv) > 1 else config("ASSISTANT_ID", default=1012838012, cast=int)
    )
    CMD_IMG = config("CMD_IMG", default="https://telegra.ph/file/66518ed54301654f0b126.png")
