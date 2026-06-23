import threading
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

def run_bot1():
    asyncio.run(__import__('asia_bazar_bot').main())

def run_bot2():
    asyncio.run(__import__('abazar_korea_bot').main())

if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot1)
    t2 = threading.Thread(target=run_bot2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
