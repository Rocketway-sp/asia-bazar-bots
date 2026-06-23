import threading
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

def run_bot1():
    import asia_bazar_bot
    asia_bazar_bot.main()

def run_bot2():
    import abazar_korea_bot
    abazar_korea_bot.main()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot1)
    t2 = threading.Thread(target=run_bot2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
