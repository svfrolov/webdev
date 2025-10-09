import os

class MinioStorage:
    """
    Класс для работы с хранилищем Minio
    """
    def __init__(self):
        """
        Инициализация клиента Minio
        """
        # В Docker контейнере нужно использовать имя сервиса вместо localhost
        # Но для доступа из браузера нужен localhost
        self.internal_url = 'http://minio:9000'  # Для доступа из контейнера
        self.external_url = os.environ.get('MINIO_URL', 'http://localhost:9000')  # Для доступа из браузера
        self.bucket_name = os.environ.get('MINIO_BUCKET', 'realestate')
    
    def get_image_url(self, image_key):
        """
        Получение URL изображения из Minio
        """
        if not image_key:
            return None
        
        # Используем внешний URL для доступа из браузера
        return f"{self.external_url}/{self.bucket_name}/{image_key}"
    
    def upload_image(self, file_obj, image_key):
        """
        Загрузка изображения в Minio
        """
        # В реальном проекте здесь был бы код для загрузки файла в Minio
        # Для упрощения просто возвращаем ключ
        return image_key