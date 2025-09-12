//João Henrique Pedrosa de Souza - 23.1.4012

#ifndef MYCOMMANDS_H
#define MYCOMMANDS_H

typedef struct {
  time_t tempini;
  time_t tempfinal;
  double tempototal;
} Tempo;

typedef struct {
  char nome[50];
  char tamanho[15];
  char dificuldade[15];
  int dimens;
  int qntdjogo[7];
  Tempo t;
} Formatacao;

//Protótipos das Funções
void validEntrada(char *palavra, int tamanho);
int nomearq(char *palavra);
char mostrarMenu();
void selecao(Formatacao *form);
void arqSalvo(char *nomearq, Matrizes *m, Formatacao *f, Somas *s);
void salvararq(char *arq, Matrizes *m, Formatacao *f, Somas *s);
void jogadas(Matrizes *m, Somas *s, Formatacao *f);
void jogadasarq(Matrizes *m, Somas *s, Formatacao *f);
void novojogo(Matrizes *m, Formatacao *f, Somas *s);
void jogoarquivado(char *nomearq, Matrizes *m, Formatacao *f, Somas *s);
void continuarjogo(Matrizes *m, Formatacao *f, Somas *s);
void mostrarRanking();


#endif
