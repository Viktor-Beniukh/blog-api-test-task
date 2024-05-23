import logging
import redis

from src.core.conf.config import settings


logger = logging.getLogger(__name__)


def get_redis():
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0
    )

    try:
        redis_client.ping()
        return redis_client
    except redis.exceptions.AuthenticationError as error:
        logger.error("Authentication failed to connect to Redis: %s", str(error))
        print(f"Authentication failed to connect to Redis: {error}")
    except Exception as error:
        logger.error("Unable to connect to Redis: %s", str(error))
        print(f"Unable to connect to Redis: {error}")
        return None
