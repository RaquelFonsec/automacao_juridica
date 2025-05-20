from celery import shared_task
import logging

from .models import Relatorio

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def baixar_relatorio(self, relatorio_id):
    try:
        relatorio = Relatorio.objects.get(id=relatorio_id)
        logger.info(f"[Task {self.request.id}] Iniciando download do relatório: {relatorio.titulo}")
        
        sucesso = relatorio.baixar()
        if sucesso:
            logger.info(f"[Task {self.request.id}] Download concluído com sucesso: {relatorio.titulo}")
        else:
            logger.error(f"[Task {self.request.id}] Falha no download: {relatorio.mensagem_erro}")
    except Relatorio.DoesNotExist:
        logger.error(f"[Task {self.request.id}] Relatório não encontrado: {relatorio_id}")
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Erro ao executar download: {str(e)}")

@shared_task(bind=True)
def processar_relatorio(self, relatorio_id):
    try:
        relatorio = Relatorio.objects.get(id=relatorio_id)
        logger.info(f"[Task {self.request.id}] Iniciando processamento do relatório: {relatorio.titulo}")
        
        sucesso = relatorio.processar()
        if sucesso:
            logger.info(f"[Task {self.request.id}] Processamento concluído com sucesso: {relatorio.titulo}")
        else:
            logger.error(f"[Task {self.request.id}] Falha no processamento: {relatorio.mensagem_erro}")
    except Relatorio.DoesNotExist:
        logger.error(f"[Task {self.request.id}] Relatório não encontrado: {relatorio_id}")
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Erro ao processar relatório: {str(e)}")

@shared_task(bind=True)
def coletar_relatorios(self):
    from .services import ColetorCNJ
    
    logger.info(f"[Task {self.request.id}] Iniciando coleta automática de relatórios do CNJ")
    
    coletor = ColetorCNJ()
    relatorios = coletor.coletar_relatorios()
    
    logger.info(f"[Task {self.request.id}] Coleta finalizada. {len(relatorios)} relatórios encontrados")
    
    # Agenda o download dos relatórios encontrados
    for relatorio in relatorios:
        baixar_relatorio.delay(relatorio.id)

@shared_task(bind=True)
def processar_relatorios_pendentes(self):
    relatorios = Relatorio.objects.filter(status='baixado')
    
    logger.info(f"[Task {self.request.id}] Processando {relatorios.count()} relatórios pendentes")
    
    for relatorio in relatorios:
        processar_relatorio.delay(relatorio.id)
