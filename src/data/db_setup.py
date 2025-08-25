from sqlalchemy import create_engine

class QuestDBManager:
    """Класс для управления QuestDB"""

    def __init__(self):
        self.engine = create_engine('questdb://localhost:8812')

    def init_tables(self):
        """Инициализация таблиц"""
        with self.engine.connect() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                timestamp TIMESTAMP PRIMARY KEY,
                symbol STRING,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE
            )""")

    def check_connection(self) -> bool:
        """Проверка соединения"""
        try:
            with self.engine.connect():
                return True
        except:
            return False
