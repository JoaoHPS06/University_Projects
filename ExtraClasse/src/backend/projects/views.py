from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Projeto, Aluno
from .serializers import ProjetoSerializer, AlunoSerializer

# Listagem e criação de projetos
class ProjetoListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjetoSerializer

    def get_queryset(self):
        queryset = Projeto.objects.all()
        professor_nome = self.request.query_params.get("professor", None)
        if professor_nome:
            queryset = queryset.filter(professor__iexact=professor_nome)
        return queryset


# Detalhes atualização e exclusão de um projeto
class ProjetoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer


class ProjetosDoAlunoView(APIView):
    def get(self, request):
        aluno_nome = request.query_params.get('aluno_nome')
        if not aluno_nome:
            return Response({"error": "É necessário fornecer aluno_nome"}, status=400)

        alunos = Aluno.objects.filter(nome__iexact=aluno_nome)
        if not alunos.exists():
            return Response({"error": "Aluno não encontrado"}, status=404)

        projetos = Projeto.objects.filter(alunos__in=alunos).distinct()
        serializer = ProjetoSerializer(projetos, many=True)
        return Response(serializer.data)


class ProjetoInscricaoView(APIView):
    def post(self, request, projeto_id):
        try:
            projeto = Projeto.objects.get(id=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"error": "Projeto não encontrado"}, status=404)

        # Tenta pegar o aluno pelo matricula
        matricula = request.data.get("matricula")
        if not matricula:
            return Response({"error": "Matrícula é obrigatória"}, status=400)

        aluno, created = Aluno.objects.get_or_create(
            matricula=matricula,
            defaults={
                "nome": request.data.get("nome", ""),
                "email": request.data.get("email", ""),
                "coeficiente": request.data.get("coeficiente", ""),
                "curso": request.data.get("curso", ""),
            }
        )

        projeto.alunos.add(aluno)
        projeto.save()
        return Response({"message": "Inscrição realizada com sucesso"}, status=201)
    
class AlunoBuscaNomeView(APIView):
    def get(self, request):
        nome = request.GET.get("nome", "")
        alunos = Aluno.objects.filter(nome__icontains=nome)
        serializer = AlunoSerializer(alunos, many=True)
        return Response(serializer.data)