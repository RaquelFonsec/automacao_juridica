from django.contrib import admin
from .models import Relatorio, DadosExtraidos, AnaliseTexto

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'status', 'criado_em', 'baixado_em', 'processado_em')
    list_filter = ('status', 'tipo')
    search_fields = ('titulo', 'url_origem')
    date_hierarchy = 'criado_em'
    readonly_fields = ('criado_em', 'atualizado_em', 'baixado_em', 'processado_em')

@admin.register(DadosExtraidos)
class DadosExtraidosAdmin(admin.ModelAdmin):
    list_display = ('relatorio', 'tipo_conteudo', 'numero_pagina', 'numero_linha', 'criado_em')
    list_filter = ('tipo_conteudo',)
    search_fields = ('relatorio__titulo', 'conteudo')
    date_hierarchy = 'criado_em'

@admin.register(AnaliseTexto)
class AnaliseTextoAdmin(admin.ModelAdmin):
    list_display = ('relatorio', 'origem', 'criado_em')
    search_fields = ('relatorio__titulo', 'texto_original')
    date_hierarchy = 'criado_em'
