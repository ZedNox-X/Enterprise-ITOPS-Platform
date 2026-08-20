import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnostic-worker")


async def run() -> None:
    logger.info("diagnostic worker started")
    while True:
        # Reference worker loop. RabbitMQ consumer wiring belongs here in production.
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run())
