import pandas as pd
from .db_setup import QuestDBManager
from minio import Minio

class DataLoader:
    """Класс для загрузки данных"""

    def __init__(self):
        import os
        self.db = QuestDBManager()
        minio_host = os.environ.get('MINIO_HOST', 'localhost:9001')
        minio_user = os.environ.get('MINIO_ROOT_USER', 'minioadmin')
        minio_pass = os.environ.get('MINIO_ROOT_PASSWORD', 'minioadmin')
        self.minio = Minio(minio_host,
                          access_key=minio_user,
                          secret_key=minio_pass,
                          secure=False)

    def load_data(self, file_path: str) -> bool:
        """Загрузка данных"""
        try:
            # Проверяем наличие bucket'а
            if not self.minio.bucket_exists('data-bucket'):
                self.minio.make_bucket('data-bucket')
                
            # Загружаем в MinIO
            self.minio.fput_object('data-bucket', 'historical_data.csv', file_path)
            
            # Загружаем в QuestDB
            df = pd.read_csv(file_path)
            df.to_sql('historical_data', 
                     con=self.db.engine,
                     if_exists='append') 
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
