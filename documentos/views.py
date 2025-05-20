from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
import csv

from .models import Relatorio, DadosExtraidos
from .tasks import coletar_relatorios, baixar_relatorio, processar_relatorio

def lista_relatorios(request ):
    relatorios = Relatorio.objects.all().order_by('-criado_em')
    return render(request, 'documentos/lista_relatorios.html', {'relatorios': relatorios})

def detalhe_relatorio(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    return render(request, 'documentos/detalhe_relatorio.html', {'relatorio': relatorio})

@require_POST
def iniciar_coleta(request):
    coletar_relatorios.delay()
    messages.success(request, 'Coleta de relatórios iniciada em background.')
    return redirect('lista_relatorios')

@require_POST
def baixar_relatorio_view(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    baixar_relatorio.delay(relatorio.id)
    messages.success(request, 'Download do relatório iniciado em background.')
    return redirect('detalhe_relatorio', pk=relatorio.id)

@require_POST
def processar_relatorio_view(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    processar_relatorio.delay(relatorio.id)
    messages.success(request, 'Processamento do relatório iniciado em background.')
    return redirect('detalhe_relatorio', pk=relatorio.id)

def dados_extraidos(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    dados = relatorio.dados_extraidos.all()
    
    if request.GET.get('format') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="relatorio-{pk}-dados.csv"'
        
        writer = csv.writer(response)
        
        # Determina os cabeçalhos baseado no primeiro registro
        if dados.exists() and dados.first().conteudo_parseado:
            first_data = dados.first().conteudo_parseado
            if isinstance(first_data, dict):
                headers = list(first_data.keys())
                writer.writerow(headers)
                
                for dado in dados:
                    parsed = dado.conteudo_parseado
                    if isinstance(parsed, dict):
                        writer.writerow([parsed.get(h, '') for h in headers])
        
        return response
    
    return render(request, 'documentos/dados_extraidos.html', {
        'relatorio': relatorio,
        'dados': dados
    })

def analise_entidades(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    analises = relatorio.analises.all()
    
    return render(request, 'documentos/analise_entidades.html', {
        'relatorio': relatorio,
        'analises': analises
    })
