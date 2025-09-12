//João Henrique Pedrosa de Souza - 23.1.4012

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "MYBOOK.h"
#include "MYCOMMANDS.h"
#include "MYCOLORS.h"

//Protótipos das Funções
void alocaMatVet(Matrizes *m, Somas *s, int n);
void liberaMatVet(Matrizes *m, Somas *s, int n);
void preencherMatrizesF(Matrizes *m, int n);
void preencherMatrizesM(Matrizes *m, int n);
void preencherMatrizesD(Matrizes *m, int n);
void somasLC(Matrizes *m, int n, Somas *s);
void imprimirMatriz(Matrizes *m, int MAX, Somas *s);
void validacao(Matrizes *m, int n, Somas *s);
int marcarDica(Matrizes *m, int n);

//Implementação das Funções
void alocaMatVet(Matrizes *m, Somas *s, int n) {

  m->matriz = calloc(n, sizeof(int *));
  m->gabarito = calloc(n, sizeof(int *));
  m->marcacao = calloc(n, sizeof(int *));

  for (int i = 0; i < n; i++) {
    m->matriz[i] = calloc(n, sizeof(int));
    m->gabarito[i] = calloc(n, sizeof(int));
    m->marcacao[i] = calloc(n, sizeof(int));
  }

  s->somacoluna = calloc(n, sizeof(int));

  s->somalinha = calloc(n, sizeof(int));

  s->colunamarcada = calloc(n, sizeof(int));

  s->linhamarcada = calloc(n, sizeof(int));

  s->validcoluna = calloc(n, sizeof(int));

  s->validlinha = calloc(n, sizeof(int));
}

void liberaMatVet(Matrizes *m, Somas *s, int n) {
  for (int i = 0; i < n; i++) {
    free(m->gabarito[i]);
    free(m->marcacao[i]);
    free(m->matriz[i]);
  }
  free(m->gabarito);
  free(m->marcacao);
  free(m->matriz);
  free(s->somacoluna);
  free(s->somalinha);
}

void preencherMatrizesF(Matrizes *m, int n) {

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      m->gabarito[i][j] = rand() % 2;
      m->matriz[i][j] = rand() % 9 + 1;
    }
  }
}

void preencherMatrizesM(Matrizes *m, int n) {

  int soma;

  for (int i = 0; i < n; i++) {
    soma = 0;
    for (int j = 0; j < n; j++) {
      m->gabarito[i][j] = rand() % 2;
      soma += m->gabarito[i][j];
    }

    while (soma == 0 || soma == n) {
      for (int j = 0; j < n; j++) {
        m->gabarito[i][j] = rand() % 2;
        soma += m->gabarito[i][j];
      }
    }
  }

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      m->matriz[i][j] = rand() % 9 + 1;
    }
  }
}

void preencherMatrizesD(Matrizes *m, int n) {

  int soma;

  for (int i = 0; i < n; i++) {
    soma = 0;
    for (int j = 0; j < n; j++) {
      m->gabarito[i][j] = rand() % 2;
      soma += m->gabarito[i][j];
    }

    while (soma == 0 || soma == n) {
      for (int j = 0; j < n; j++) {
        m->gabarito[i][j] = rand() % 2;
        soma += m->gabarito[i][j];
      }
    }
  }

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      m->matriz[i][j] = rand() % (19 - 9);
    }
  }
}

void somasLC(Matrizes *m, int n, Somas *s) {

  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      if (m->gabarito[i][j] == 1)
        s->somalinha[i] += m->matriz[i][j];
      else
        s->validlinha[i]++;
    }
  }

  for (int j = 0; j < n; j++) {
    for (int i = 0; i < n; i++) {
      if (m->gabarito[i][j] == 1)
        s->somacoluna[j] += m->matriz[i][j];
      else
        s->validcoluna[j]++;
    }
  }
}

void imprimirMatriz(Matrizes *m, int MAX, Somas *s) {

  printf("   ");
  for (int i = 0; i < MAX; i++)
    printf(TAB_VER BOLD(CYAN("  %d  ")), i + 1);
  printf(TAB_VER "\n" TAB_HOR TAB_HOR TAB_HOR TAB_MJ);
  for (int i = 0; i < MAX; i++)
    printf(TAB_HOR TAB_HOR TAB_HOR TAB_HOR TAB_HOR TAB_MJ);

  printf(TAB_HOR TAB_HOR TAB_HOR TAB_HOR "\n");

  for (int i = 0; i < MAX; i++) {
    printf(BOLD(CYAN(" %d ")) TAB_VER, i + 1);
    for (int j = 0; j < MAX; j++) {
      if (m->marcacao[i][j] == 1)
        if (m->matriz[i][j] < 0)
          printf(BOLD(GREEN(" %d  ")) TAB_VER, m->matriz[i][j]);
        else
          printf(BOLD(GREEN("  %d  ")) TAB_VER, m->matriz[i][j]);

      else if (m->marcacao[i][j] == -1)
        if (m->matriz[i][j] < 0)
          printf(BOLD(RED(" %d  ")) TAB_VER, m->matriz[i][j]);
        else
          printf(BOLD(RED("  %d  ")) TAB_VER, m->matriz[i][j]);

      else if (m->matriz[i][j] < 0)
        printf(BOLD(" %d  ") TAB_VER, m->matriz[i][j]);
      else
        printf(BOLD("  %d  ") TAB_VER, m->matriz[i][j]);
    }

    if (s->linhamarcada[i] == 1) {
      printf(BOLD(BLACK(" %d\n")), s->somalinha[i]);
    }

    else
      printf(" %d\n", s->somalinha[i]);

    printf(TAB_HOR TAB_HOR TAB_HOR TAB_MJ);
    for (int k = 0; k < MAX; k++)
      printf(TAB_HOR TAB_HOR TAB_HOR TAB_HOR TAB_HOR TAB_MJ);
    printf(TAB_HOR TAB_HOR TAB_HOR TAB_HOR "\n");
  }

  printf("   ");
  for (int i = 0; i < MAX; i++)
    if (s->colunamarcada[i] == 1) {
      if (s->somacoluna[i] < -9)
        printf(TAB_VER BOLD(BLACK(" %d ")), s->somacoluna[i]);
      else if (s->somacoluna[i] < 0)
        printf(TAB_VER BOLD(BLACK(" %d  ")), s->somacoluna[i]);
      else if (s->somacoluna[i] < 10)
        printf(TAB_VER BOLD(BLACK("  %d  ")), s->somacoluna[i]);
      else
        printf(TAB_VER BOLD(BLACK(" %d  ")), s->somacoluna[i]);
    }

    else {
      if (s->somacoluna[i] < -9)
        printf(TAB_VER " %d ", s->somacoluna[i]);
      else if (s->somacoluna[i] < 0)
        printf(TAB_VER " %d  ", s->somacoluna[i]);
      else if (s->somacoluna[i] < 10)
        printf(TAB_VER "  %d  ", s->somacoluna[i]);
      else
        printf(TAB_VER " %d  ", s->somacoluna[i]);
    }

  printf(TAB_VER " \n");

}

void validacao(Matrizes *m, int n, Somas *s) {
  int somal, somac;
  for (int i = 0; i < n; i++) {
    somal = 0;
    somac = 0;
    for (int j = 0; j < n; j++) {
      if (m->marcacao[i][j] == -1 && m->gabarito[i][j] == 0)
        somal++;

      if (m->marcacao[j][i] == -1 && m->gabarito[j][i] == 0)
        somac++;
    }

    if (somal == s->validlinha[i]) {
      if (s->linhamarcada[i] == 0)
        s->qntdmarcada++;

      s->linhamarcada[i] = 1;
    }

    if (somac == s->validcoluna[i]) {
      if (s->colunamarcada[i] == 0)
        s->qntdmarcada++;

      s->colunamarcada[i] = 1;
    }
  }
}

int marcarDica(Matrizes *m, int n) {
  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
      if ((m->gabarito[i][j] == 1) && (m->marcacao[i][j] != 1)) {
        m->marcacao[i][j] = 1;
        return 0;
      }

      if ((m->gabarito[i][j] == 0) && (m->marcacao[i][j] != -1)) {
        m->marcacao[i][j] = -1;
        return 0;
      }
    }
  }

  return 1;
}

