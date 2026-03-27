import os

from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создаем экземпляр Celery
app = Celery("config")

# Windows compatibility
app.conf.broker_connection_retry_on_startup = True

# Автоматически находим задачи в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Отладочная задача для тестирования Celery"""
    print(f"Request: {self.request!r}")
