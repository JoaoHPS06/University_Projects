//João Henrique Pedrosa de Souza - 23.1.4012

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "MYBOOK.h"
#include "MYCOMMANDS.h"
#include "MYCOLORS.h"

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

//Implementação das Funções
void validEntrada(char *palavra, int tamanho) {
  fgets(palavra, tamanho, stdin);

  while (palavra[0] == '\n' || palavra[0] == ' ')
    fgets(palavra, tamanho, stdin);

  palavra[strcspn(palavra, "\n")] = '\0'; // Remover o caractere de nova linha
}

int nomearq(char *palavra) {
	
	int tamanho = strlen(palavra);
	int pontos = 0;
	
	for(int i = 0; i < tamanho; i++)
		if(palavra[i] == '.')
			pontos++;
		
	if(pontos == 0) {
		printf("Precisa escrever o tipo do arquivo(.txt)!\n");
		return 0;
	}
	
	else if(palavra[tamanho - 4] != '.' || palavra[tamanho - 3] != 't' || palavra[tamanho - 2] != 'x' || palavra[tamanho - 1] != 't') {
			printf("Precisa escrever o tipo do arquivo(.txt)!\n");
			return 0;
	}
	
	else
		return 1;	
		
}

char mostrarMenu() {

  char opc[25];

  printf("0. Sair do Jogo\n");
  printf("1. Começar um novo jogo\n");
  printf("2. Continuar um jogo salvo em arquivo\n");
  printf("3. Continuar o jogo atual\n");
  printf("4. Exibir o ranking\n");
  printf("Durante o jogo digite \"voltar\" para retornar ao menu.\n\n");
  printf("Escolha a opção: ");
  validEntrada(opc, 25);

  while (strcmp(opc, "0") && strcmp(opc, "1") && strcmp(opc, "2") &&
         strcmp(opc, "3") && strcmp(opc, "4")) {
    printf("Comando inválido. Digite novamente: ");
    validEntrada(opc, 25);
  }

  return opc[0];
}

void selecao(Formatacao *form) {

  printf("Digite o nome do jogador 1: ");
  validEntrada(form->nome, 50);

  printf("Digite o tamanho do tabuleiro (3 à 9): ");
  validEntrada(form->tamanho, 25);

  while (strcmp(form->tamanho, "3") && strcmp(form->tamanho, "4") &&
         strcmp(form->tamanho, "5") && strcmp(form->tamanho, "6") &&
         strcmp(form->tamanho, "7") && strcmp(form->tamanho, "8") &&
         strcmp(form->tamanho, "9")) {
    printf("Tamanho inválido. Digite novamente: ");
    validEntrada(form->tamanho, 25);
  }

  if (!strcmp(form->tamanho, "3") || !strcmp(form->tamanho, "4")) {
    printf("Digite o nível de dificuldade (Fácil(F))): ");
    validEntrada(form->dificuldade, 25);

    while (strcmp(form->dificuldade, "F") && strcmp(form->dificuldade, "f")) {
      printf("Dificuldade inválida. Digite novamente: ");
      validEntrada(form->dificuldade, 25);
    }
  }

  else if (!strcmp(form->tamanho, "3") || !strcmp(form->tamanho, "4") ||
           !strcmp(form->tamanho, "5") || !strcmp(form->tamanho, "6")) {
    printf("Digite o nível de dificuldade (Fácil(F) ou Médio(M)): ");
    validEntrada(form->dificuldade, 25);

    while (strcmp(form->dificuldade, "F") && strcmp(form->dificuldade, "f") &&
           strcmp(form->dificuldade, "M") && strcmp(form->dificuldade, "m")) {
      printf("Dificuldade inválida. Digite novamente: ");
      validEntrada(form->dificuldade, 25);
    }
  }

  else if (!strcmp(form->tamanho, "3") || !strcmp(form->tamanho, "4") ||
           !strcmp(form->tamanho, "5") || !strcmp(form->tamanho, "6") ||
           !strcmp(form->tamanho, "7") || !strcmp(form->tamanho, "8") ||
           !strcmp(form->tamanho, "9")) {
    printf("Digite o nível de dificuldade (Fácil(F), Médio(M) ou Diícil(D)): ");
    validEntrada(form->dificuldade, 25);

    while (strcmp(form->dificuldade, "F") && strcmp(form->dificuldade, "f") &&
           strcmp(form->dificuldade, "M") && strcmp(form->dificuldade, "m") &&
           strcmp(form->dificuldade, "D") && strcmp(form->dificuldade, "d")) {
      printf("Dificuldade inválida. Digite novamente: ");
      validEntrada(form->dificuldade, 25);
    }
  }
}

void arqSalvo(char *nomearq, Matrizes *m, Formatacao *f, Somas *s) {

  int l, c, qntdmarcar;

  FILE *arquivo = fopen(nomearq, "a+");

  fscanf(arquivo, "%c", &f->tamanho[0]);
  f->dimens = f->tamanho[0] - '0';
  alocaMatVet(m, s, f->dimens);
  
  for (int i = 0; i < f->dimens; i++)
    for (int j = 0; j < f->dimens; j++)
      fscanf(arquivo, "%d", &m->matriz[i][j]);
      
  for (int i = 0; i < f->dimens; i++) 
    fscanf(arquivo, "%d", &s->somalinha[i]);
  
  for (int i = 0; i < f->dimens; i++)
    fscanf(arquivo, "%d", &s->somacoluna[i]);

  fscanf(arquivo, "%d", &qntdmarcar);

  for (int i = 0; i < qntdmarcar; i++) {
    fscanf(arquivo, "%d %d", &l, &c);
    m->marcacao[l - 1][c - 1] = 1;
    m->gabarito[l - 1][c - 1] = 1;
  }

  fscanf(arquivo, "%d", &qntdmarcar);
  
  for (int i = 0; i < qntdmarcar; i++) {
    fscanf(arquivo, "%d %d", &l, &c);
    m->marcacao[l - 1][c - 1] = -1;
    m->gabarito[l - 1][c - 1] = 0;
  }
  
  fgets(f->nome, 50, arquivo);

  while (f->nome[0] == '\n' || f->nome[0] == ' ')
    fgets(f->nome, 50, arquivo);

  f->nome[strcspn(f->nome, "\n")] = '\0'; // Remover o caractere de nova linha
  fscanf(arquivo, "%lf", &f->t.tempototal);

  fclose(arquivo);
}

void salvararq(char *arq, Matrizes *m, Formatacao *f, Somas *s) {
  FILE *arquivo = fopen(arq, "w");
  int quantmanter = 0, quantremover = 0;

  fprintf(arquivo, "%d\n", f->dimens);
  for (int i = 0; i < f->dimens; i++) {
    for (int j = 0; j < f->dimens; j++)
      fprintf(arquivo, "%d ", m->matriz[i][j]);
    fprintf(arquivo, "\n");
  }

  for (int i = 0; i < f->dimens; i++)
    fprintf(arquivo, "%d ", s->somalinha[i]);
  fprintf(arquivo, "\n");

  for (int i = 0; i < f->dimens; i++)
    fprintf(arquivo, "%d ", s->somacoluna[i]);
  fprintf(arquivo, "\n");

  for (int i = 0; i < f->dimens; i++)
    for (int j = 0; j < f->dimens; j++) {
      if (m->marcacao[i][j] == 1)
        quantmanter++;

      if (m->marcacao[i][j] == -1)
        quantremover++;
    }

  fprintf(arquivo, "%d\n", quantmanter);
  for (int i = 0; i < f->dimens; i++) {
    for (int j = 0; j < f->dimens; j++) {
      if (m->marcacao[i][j] == 1) {
        int l = i + 1;
        int c = j + 1;
        fprintf(arquivo, "%d %d\n", l, c);
      }
    }
  }

  fprintf(arquivo, "%d\n", quantremover);
  for (int i = 0; i < f->dimens; i++)
    for (int j = 0; j < f->dimens; j++) {
      if (m->marcacao[i][j] == -1)
        fprintf(arquivo, "%d %d\n", i + 1, j + 1);
    }

  fprintf(arquivo, "%s\n", f->nome);
  fprintf(arquivo, "%.0lf", f->t.tempototal);

  fclose(arquivo);
}

void jogadas(Matrizes *m, Somas *s, Formatacao *f) {

  char comando[20];
  char palavra[20];
  int i, cont = 0, d = 0;

  while (cont != 1) {
    printf("\n%s, digite o comando: ", f->nome);
    validEntrada(comando, 20);

    int tamanho = strlen(comando); // Vai calcular o tamanho total da string "comando"

    for (i = 0; i <= tamanho; i++) {
      if (comando[i] == ' ' || comando[i] == '\0') {
        palavra[i] = '\0';
        break;
      }

      palavra[i] = comando[i];
    }

    if (!strcmp(palavra, "manter") || !strcmp(palavra, "remover")) {

      char linha = comando[i + 1];
      char coluna = comando[i + 2];

      while (linha < '1' || linha > f->tamanho[0] || coluna < '1' || coluna > f->tamanho[0] || comando[i + 3] != '\0') {
        printf("Dimensões inválidas. Digite o comando novamente: ");
        validEntrada(comando, 20);
        int ponto = strcspn(comando, " ");
        linha = comando[ponto + 1];
        coluna = comando[ponto + 2];
      }

      int l = linha - '0'; // Transformará o primeiro número digitado de char para int
      int c = coluna -'0'; // Transformará o segundo número digitado de char para int

      if (!strcmp(palavra, "manter")) {
        m->marcacao[l - 1][c - 1] = 1;
      }

      else {
        m->marcacao[l - 1][c - 1] = -1;
      }

      validacao(m, f->dimens, s);
      printf("\ec\e[3j");
      imprimirMatriz(m, f->dimens, s);

      if (s->qntdmarcada == (f->dimens * 2)) {
        printf("\nPARABÉNS VOCÊ GANHOU!\n\n");
        f->t.tempfinal = time(NULL);
     	f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;
     	liberaMatVet(m, s, f->dimens);
     	cont = 1;
     	printf("\n");
      }
    }

    else if (!strcmp(palavra, "salvar")) {
      f->t.tempfinal = time(NULL);
      f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;

      int j = 0;
      char arquivo[30];
	   
	  if(nomearq(comando)) {
      	for (int n = i + 1; n <= tamanho; n++) {
        	if (comando[n] == '\n') {
          		arquivo[j] = '\0';
          		break;
       		}

        	arquivo[j] = comando[n];
       	 	j++;
       	}
      
      	salvararq(arquivo, m, f, s);
      	liberaMatVet(m, s, f->dimens);
      	cont = 1;
      	printf("\n");
	  }
    }

    else if (!strcmp(palavra, "dica")) {
      if (!marcarDica(m, f->dimens) && d <= (f->dimens * f->dimens) / 2) {
        validacao(m, f->dimens, s);
        printf("\ec\e[3j");
        imprimirMatriz(m, f->dimens, s);
  	  }
  	  
	  else
        printf("Suas dicas acabaram!\n\n");
      d++;
    }

    else if (!strcmp(palavra, "resolver")) {
      while (!marcarDica(m, f->dimens)) {
        marcarDica(m, f->dimens);
        validacao(m, f->dimens, s);
      }
      printf("\ec\e[3j");
      imprimirMatriz(m, f->dimens, s);
      if (s->qntdmarcada == (f->dimens * 2)) {
        printf("\nPARABÉNS VOCÊ GANHOU!\n\n");
        f->t.tempfinal = time(NULL);
      	f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;
      	liberaMatVet(m, s, f->dimens);
      	cont = 1;
      	printf("\n");
      }
    }

    else if (!strcmp(palavra, "voltar")) {
      f->t.tempfinal = time(NULL);
      f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;
      cont = 1;
      printf("\n");
    }

    else
      printf("Comando Inválido. Tente novamente\n\n");
  }
}

void jogadasarq(Matrizes *m, Somas *s, Formatacao *f) {

  char comando[20];
  char palavra[20];
  int i, cont = 0, d = 0;

  while (cont != 1) {
    printf("\n%s, digite o comando: ", f->nome);
    validEntrada(comando, 20);

    int tamanho = strlen(comando); // Vai calcular o tamanho total da string "comando"

    for (i = 0; i <= tamanho; i++) {
      if (comando[i] == ' ' || comando[i] == '\0') {
        palavra[i] = '\0';
        break;
      }

      palavra[i] = comando[i];
    }

    if (!strcmp(palavra, "manter") || !strcmp(palavra, "remover")) {

      char linha = comando[i + 1];
      char coluna = comando[i + 2];

      while (linha < '1' || linha > f->tamanho[0] || coluna < '1' || coluna > f->tamanho[0] || comando[i + 3] != '\0') {
        printf("Dimensões inválidas. Digite o comando novamente: ");
        validEntrada(comando, 20);
        int ponto = strcspn(comando, " ");
        linha = comando[ponto + 1];
        coluna = comando[ponto + 2];
      }

      int l = linha -
              '0'; // Transformará o primeiro número digitado de char para int
      int c = coluna -
              '0'; // Transformará o segundo número digitado de char para int

      if (!strcmp(palavra, "manter")) {
        m->marcacao[l - 1][c - 1] = 1;
      }

      else {
        m->marcacao[l - 1][c - 1] = -1;
      }

      printf("\ec\e[3j");
      imprimirMatriz(m, f->dimens, s);

    }

    else if (!strcmp(palavra, "salvar")) {
      f->t.tempfinal = time(NULL);
      f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;

      int j = 0;
      char arquivo[30];
	   
	  if(nomearq(comando)) {
      	for (int n = i + 1; n <= tamanho; n++) {
        	if (comando[n] == '\n') {
          		arquivo[j] = '\0';
          		break;
       		}

        	arquivo[j] = comando[n];
       	 	j++;
       	}
      
      	salvararq(arquivo, m, f, s);
      	liberaMatVet(m, s, f->dimens);
      	cont = 1;
      	printf("\n");
	  }
    }

    else if (!strcmp(palavra, "voltar")) {
      f->t.tempfinal = time(NULL);
      f->t.tempototal += (f->t.tempfinal - f->t.tempini) * 1.0;
      cont = 1;
      printf("\n");
    }

    else
      printf("Comando Inválido. Tente novamente\n\n");
  }
}

void novojogo(Matrizes *m, Formatacao *f, Somas *s) {

  selecao(f);
  f->dimens = f->tamanho[0] - '0';
  f->t.tempototal = 0;
  s->qntdmarcada = 0;

  alocaMatVet(m, s, f->dimens);
  if (!strcmp(f->dificuldade, "f") || !strcmp(f->dificuldade, "F"))
    preencherMatrizesF(m, f->dimens);
  else if (!strcmp(f->dificuldade, "m") || !strcmp(f->dificuldade, "M"))
    preencherMatrizesM(m, f->dimens);
  else
    preencherMatrizesD(m, f->dimens);

  somasLC(m, f->dimens, s);
  validacao(m, f->dimens, s);
  printf("\ec\e[3j");
  imprimirMatriz(m, f->dimens, s);
  f->t.tempini = time(NULL);
  jogadas(m, s, f);
}

void jogoarquivado(char *nomearq, Matrizes *m, Formatacao *f, Somas *s) {
  arqSalvo(nomearq, m, f, s);
  printf("\ec\e[3j");
  imprimirMatriz(m, f->dimens, s);
  f->t.tempini = time(NULL);
  jogadasarq(m, s, f);
}

void continuarjogo(Matrizes *m, Formatacao *f, Somas *s) {
  f->t.tempini = time(NULL);
  printf("\ec\e[3j");
  imprimirMatriz(m, f->dimens, s);
  jogadas(m, s, f);
}

void mostrarRanking() {
	
	
	
	
	
}

