//João Henrique Pedrosa de Souza

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "MYBOOK.h"
#include "MYCOMMANDS.h"
#include "MYCOLORS.h"

int main() {

  srand(time(NULL));

  Formatacao form;
  Matrizes mat;
  Somas s;
  char opc, nomearquivo[30];
  int na = 0;

  printf("          Bem vindo ao Jogo SUMPLETE\n\n");

  do {
    opc = mostrarMenu();

    switch (opc) {
    case '0': return 0; break;

    case '1': novojogo(&mat, &form, &s); break;

    case '2': do {
	  			printf("\nDigite o nome do arquivo (INCLUINDO O .txt): ");
      			validEntrada(nomearquivo, 30);
        		na = nomearq(nomearquivo);
        		
  	  		  }while(na != 1);
  	  		  
			  jogoarquivado(nomearquivo, &mat, &form, &s); break;

    case '3': continuarjogo(&mat, &form, &s); break;

    case '4': mostrarRanking; break;

    default: printf("Comando Inválido\n");
    }

  } while (opc != '0');

  return 0;
}

