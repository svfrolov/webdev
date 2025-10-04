from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse

def hello(request):
    """
    Простая функция для проверки работы сервера
    """
    return HttpResponse('Hello MinIO World!')

def upload_file(request):
    """
    Загрузка файла в MinIO без требования авторизации
    """
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        path = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))
        file_url = default_storage.url(path)
        return render(request, 'services/upload_success.html', {'file_url': file_url})
    return render(request, 'services/upload.html')