from rest_framework.serializers import ValidationError
from urllib.parse import urlparse

def validate_youtube_url(value):
    # Разбираем ссылку, чтобы получить домен
    parsed_url = urlparse(value)
    domain = parsed_url.netloc

    if domain not in ['www.youtube.com', 'youtube.com', 'youtu.be']:
        raise ValidationError(
            'Разрешены ссылки только на youtube.com. Сторонние ресурсы запрещены.'
        )



