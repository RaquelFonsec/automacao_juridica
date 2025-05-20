




import requests
from bs4 import BeautifulSoup
from django.utils import timezone
import os
import logging

from .models import Relatorio

logger = logging.getLogger(__name__)

class ColetorCNJ:
    BASE_URL = "https://www.cnj.jus.br"
    REPORTS_PATH = "/transparencia/relatorios"
    
    def __init__(self ):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        })
    
    def coletar_relatorios(self):
        # Obtém a página de relatórios
        response = self.session.get(f"{self.BASE_URL}{self.REPORTS_PATH}")
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            logger.error(f"Falha ao acessar página de relatórios: {response.status_code}")
            return []
        
        # Parseia o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrai links para relatórios
        relatorios = []
        for link in soup.select('.relatorios-lista a, .documentos-lista a'):
            href = link.get('href')
            titulo = link.text.strip()
            
            # Ignora links vazios ou sem título
            if not href or not titulo:
                continue
            
            # Normaliza a URL
            url = href if href.startswith('http' ) else f"{self.BASE_URL}{href}"
            
            # Determina o tipo de relatório baseado na extensão
            tipo = self._determinar_tipo(url)
            
            # Cria ou atualiza o registro do relatório
            relatorio, criado = Relatorio.objects.update_or_create(
                url_origem=url,
                defaults={
                    'titulo': titulo,
                    'tipo': tipo,
                    'ultima_verificacao': timezone.now()
                }
            )
            
            if not criado:
                relatorios.append(relatorio)
        
        logger.info(f"Coletados {len(relatorios)} relatórios do CNJ")
        return relatorios
    
    def _determinar_tipo(self, url):
        extensao = os.path.splitext(url)[1].lower()
        
        if extensao == '.pdf':
            return 'pdf'
        elif extensao in ['.xlsx', '.xls']:
            return 'excel'
        elif extensao == '.csv':
            return 'csv'
        elif extensao in ['.html', '.htm']:
            return 'html'
        else:
            # Se não conseguir determinar pela extensão, tenta pelo nome do arquivo
            if 'pdf' in url:
                return 'pdf'
            elif any(x in url for x in ['excel', 'xlsx', 'xls']):
                return 'excel'
            elif 'csv' in url:
                return 'csv'
            else:
                return 'pdf'  # Assume PDF como padrão
