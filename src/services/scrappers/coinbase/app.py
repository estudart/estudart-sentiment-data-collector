import sys
from multiprocessing import Process

from src.collectors.coinbase_collector import CoinbaseDataCollector
from src.utils.config import secrets


def start_scrapper(assets_list):
    coinbase_instance = CoinbaseDataCollector()
    coinbase_instance.run(assets_list)

if __name__ == "__main__":
    try:
        assets_list = secrets.get("COINBASE_ASSETS")
        Process(target=start_scrapper, 
                args=(assets_list, )
                ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()