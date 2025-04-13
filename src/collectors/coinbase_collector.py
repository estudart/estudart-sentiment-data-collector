import time
import json
from datetime import datetime, timezone

import requests

from src.collectors.news_collector import NewsDataCollector



class CoinbaseDataCollector(NewsDataCollector):
    def __init__(self):
        super().__init__()

        self.platform = "coinbase"

        self.loop_delay_time = self.secrets.get("COINBASE_LOOP_DELAY_TIME")
        self.host = self.secrets.get("COINBASE_REST_HOST")

    
    def _initialize_credentials(self) -> None:
        pass


    def fetch_data(self, ticker) -> list:
        response = requests.get(f"{self.host}/{ticker}/ticker")
        response.raise_for_status()
        data = response.json()

        return data
    
    def process_data(self, ticker, data):
        processed_market_data = {
            "id": data["trade_id"],
            "ticker": ticker,
            "ask": data["ask"],
            "bid": data["bid"],
            "volume": data["volume"],
            "price": data["price"],
            "qty": data["size"], 
            "ts": data["time"]
        }
        if not self.queue_manager.is_set_member(
            f"{self.platform}-processed-market-data", data["trade_id"]):
            self.send_to_queue(f"{self.platform}-trades-market-data", 
                                processed_market_data)
            self.logger.debug(
                f"New trade to process: {processed_market_data}")
            return True

    def send_to_queue(self, queue, data):
        return self.queue_manager.send_to_queue(queue, data)
    

    def run_loop(self, ticker):
        loop_start_time = datetime.now(timezone.utc)
        try:
            ticker_data = self.fetch_data(ticker)
        except Exception as err:
            self.logger.info(
                f"Could not fetch data for {ticker}, "
                f"reason: {err}"
            )
            raise
        
        number_of_trades_processed = 0
        if self.process_data(ticker, ticker_data):
            number_of_trades_processed+=1
        loop_finished_time = datetime.now(timezone.utc)

        time_difference = (
            (loop_finished_time - loop_start_time)
            .total_seconds()
        )

        self.logger.info(
            f"Loop for {ticker} took {round(time_difference, 2)} seconds "
            f"and processed {number_of_trades_processed} trades."
        )


    def run(self, tickers):
        while True:
            for ticker in tickers:
                try:
                    self.run_loop(ticker)
                except Exception as err:
                    self.logger.error(
                        f"Could not run loop for {ticker}, reason: {err}"
                    )
            
            time.sleep(self.loop_delay_time)   
