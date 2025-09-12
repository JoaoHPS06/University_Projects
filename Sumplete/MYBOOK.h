//João Henrique Pedrosa de Souza - 23.1.4012

#ifndef MYBOOK_H
#define MYBOOK_H

typedef struct {
  int **matriz; // matriz que vai ser gerada e impressa
  int **gabarito; // matriz gabarito que marca os lugares corretos correspondentes
  int **marcacao; // matriz que vai ser usada como espelho para o jogo
} Matrizes;

typedef struct {
  int *somalinha;  // vetor que vai armazenar as somas das linhas
  int *somacoluna; // vetor que vai armazenar as somas das colunas
  int *validlinha;
  int *validcoluna;
  int *linhamarcada;
  int *colunamarcada;
  int qntdmarcada;
} Somas;

//Protótipos das Funções
void alocaMatVet(Matrizes *m, Somas *s, int n);
void liberaMatVet(Matrizes *m, Somas *s, int n);
void preencherMatrizesF(Matrizes *m, int n);
void preencherMatrizesM(Matrizes *m, int n);
void preencherMatrizesD(Matrizes *m, int n);
void somasLC(Matrizes *m, int n, Somas *s);
void imprimirMatriz(Matrizes *m, int MAX, Somas *s);
void validacao(Matrizes *m, int n, Somas *s);

#endif
