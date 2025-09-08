from rest_framework import serializers
from .models import Projeto, Aluno

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'matricula', 'email', 'coeficiente', 'curso']

class ProjetoSerializer(serializers.ModelSerializer):
    # Representa os alunos relacionados
    alunos = AlunoSerializer(many=True, read_only=True)  # só leitura aqui
    # Para permitir adicionar/remover alunos via API, você pode usar PrimaryKeyRelatedField
    # alunos = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), many=True)

    class Meta:
        model = Projeto
        fields = [
            'id', 'titulo', 'carga_horaria', 'duracao', 'professor',
            'financiador', 'vagas_remuneradas','vagas_voluntarias',
            'tipo_projeto', 'descricao', 'alunos'
        ]
