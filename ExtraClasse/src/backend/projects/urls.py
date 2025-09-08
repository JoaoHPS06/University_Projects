from django.urls import path
from .views import AlunoBuscaNomeView, ProjetoInscricaoView, ProjetoListCreateView, ProjetosDoAlunoView
from .views import ProjetoDetailView

urlpatterns = [
    path('projetos/', ProjetoListCreateView.as_view(), name='projeto-list-create'),
    path('projetos/<int:pk>/', ProjetoDetailView.as_view(), name='projeto-detail'),
    path("projetos/<int:projeto_id>/inscricao/", ProjetoInscricaoView.as_view()),
    path('projetos/aluno/', ProjetosDoAlunoView.as_view(), name='projetos-aluno'),
    path("alunos/busca/", AlunoBuscaNomeView.as_view()),
 ]