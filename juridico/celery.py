import os
from celery import Celery
from celery.schedules import crontab

# Configura variável de ambiente para settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juridico.settings')

app = Celery('juridico')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configura tarefas agendadas
app.conf.beat_schedule = {
    'coletar-relatorios-diariamente': {
        'task': 'documentos.tasks.coletar_relatorios',
        'schedule': crontab(hour=8, minute=0),  # Todos os dias às 8h
    },
    'processar-relatorios-pendentes': {
        'task': 'documentos.tasks.processar_relatorios_pendentes',
        'schedule': crontab(hour='*/4', minute=0),  # A cada 4 horas
    },
}
