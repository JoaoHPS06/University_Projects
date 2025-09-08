export interface User {
  id: number;
  matricula: string;
  nome: string;
  tipo_usuario: 'aluno' | 'professor';
}

export interface Projeto {
  id: number;
  titulo: string;
  cargaHoraria: string;
  duracao: string;
  professor: string; 
  tipoProjeto: string;
  financiador: string;
  VagasVoluntarias: number;
  VagasRemuneradas: number;
  descricao: string;
}