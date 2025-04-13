from sqlalchemy import Column, String, Integer, Text, DateTime, DECIMAL

from src.utils.extensions import Base


class CryptoPricesModel(Base):
    __tablename__ = "crypto_prices"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    src = Column(String, nullable=False)
    ask = Column(DECIMAL, nullable=True)
    bid = Column(DECIMAL, nullable=True)
    volume = Column(DECIMAL, nullable=True)
    price = Column(DECIMAL, nullable=False)
    qty = Column(DECIMAL, nullable=False)
    ts = Column(DateTime, nullable=False)

    def __repr__(self):
        return (
            f"<CryptoPricesModel(id={self.id})>"
        )