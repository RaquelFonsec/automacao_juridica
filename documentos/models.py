from django.db import models
from django.utils import timezone
import os

class Relatorio(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('baixado', 'Baixado'),
        ('processado', 'Processado'),
        ('erro', 'Erro'),
    ]
    
    TIPO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    ]
    
    titulo = models.CharField(max_length=255)
    url_origem = models.URLField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    arquivo = models.FileField(upload_to='relatorios/', null=True, blank=True)
    tamanho_arquivo = models.IntegerField(null=True, blank=True)
    tipo_conteudo = models.CharField(max_length=100, null=True, blank=True)
    baixado_em = models.DateTimeField(null=True, blank=True)
    processado_em = models.DateTimeField(null=True, blank=True)
    ultima_verificacao = models.DateTimeField(null=True, blank=True)
    mensagem_erro = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titulo
    
    # Resto do código da classe Relatorio...

class DadosExtraidos(models.Model):
    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, related_name='dados_extraidos')
    tipo_conteudo = models.CharField(max_length=50)
    conteudo = models.TextField()
    numero_pagina = models.IntegerField(null=True, blank=True)
    numero_linha = models.IntegerField(null=True, blank=True)
    nome_planilha = models.CharField(max_length=100, null=True, blank=True)
    numero_tabela = models.IntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dados de {self.relatorio.titulo} - {self.tipo_conteudo}"
    
    # Resto do código da classe DadosExtraidos...

class AnaliseTexto(models.Model):
    """Modelo para armazenar resultados de análise NLP"""
    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, related_name='analises')
    origem = models.CharField(max_length=100)  # Ex: "Página 1", "Seção 2"
    entidades = models.TextField()  # JSON com entidades extraídas
    texto_original = models.TextField()  # Trecho do texto analisado
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Análise de {self.relatorio.titulo} - {self.origem}"
    
    # Resto do código da classe AnaliseTexto...
