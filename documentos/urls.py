from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_relatorios, name='lista_relatorios'),
    path('relatorio/<int:pk>/', views.detalhe_relatorio, name='detalhe_relatorio'),
    path('relatorio/<int:pk>/dados/', views.dados_extraidos, name='dados_extraidos'),
    path('relatorio/<int:pk>/analise/', views.analise_entidades, name='analise_entidades'),
    path('coleta/', views.iniciar_coleta, name='iniciar_coleta'),
    path('relatorio/<int:pk>/baixar/', views.baixar_relatorio_view, name='baixar_relatorio'),
    path('relatorio/<int:pk>/processar/', views.processar_relatorio_view, name='processar_relatorio'),
]
