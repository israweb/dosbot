from great_expectations import expect
from great_expectations.dataset import Dataset

class BinanceDataValidator:
    """Класс для валидации данных Binance"""

    def validate_klines(self, df: pl.DataFrame) -> bool:
        """
        Проверка OHLCV данных

        :return: True если данные валидны
        """
        validation = expect(df)
        validation.to_have_column('time', type='datetime')  
        validation.to_have_column('open', min_value=0)
        validation.to_have_column('volume', min_value=0)
        return validation.result

    def generate_report(self, df: pl.DataFrame) -> dict:
        """Генерация отчет о проблемных точках"""
        report = {
            "missing_values": df.is_null().sum(),
            "negative_volumes": df.filter(pl.col('volume') < 0)
        }
        return report
