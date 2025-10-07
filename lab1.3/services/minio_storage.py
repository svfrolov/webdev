"""
Класс для работы с Minio
"""
import os
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from django.conf import settings

class MinioStorage:
    """
    Класс для работы с Minio
    """
    def __init__(self):
        """
        Инициализация клиента Minio
        """
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        
        # Создаем бакет, если он не существует
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Ошибка при создании бакета: {e}")
    
    def get_image_url(self, image_key):
        """
        Получение URL изображения из Minio
        """
        try:
            # Генерируем presigned URL для доступа к изображению
            # Используем timedelta вместо целого числа для expires
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=image_key,
                expires=timedelta(hours=24)  # URL действителен 24 часа
            )
            return url
        except S3Error as e:
            print(f"Ошибка при получении URL изображения: {e}")
            return None
    
    def upload_image(self, file_obj, image_key):
        """
        Загрузка изображения в Minio
        """
        try:
            # Определяем content_type на основе расширения файла
            content_type = "image/jpeg"  # По умолчанию
            if image_key.endswith('.png'):
                content_type = "image/png"
            elif image_key.endswith('.gif'):
                content_type = "image/gif"
            
            # Загружаем файл в Minio
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=image_key,
                data=file_obj,
                length=file_obj.size,
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Ошибка при загрузке изображения: {e}")
            return False