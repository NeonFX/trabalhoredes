# Simulação de Uber – Projeto de Redes

Este projeto simula, de forma simplificada, o funcionamento do aplicativo de motorista da Uber utilizando comunicação em rede no modelo cliente-servidor.
O sistema utiliza sockets e threads para permitir comunicação assíncrona entre o servidor e um motorista conectado.
O servidor simula o sistema da plataforma, gerando chamadas de corrida aleatórias.
O cliente representa o motorista, que pode aceitar ou cancelar corridas através de comandos.

# Tecnologias utilizadas

Biblioteca socket 

Biblioteca threading

Todas as bibliotecas utilizadas são nativas do Python

# Estrutura do projeto
Trabalho-Redes/

 ├── server.py
 
 └── client.py

server.py → responsável por gerar corridas e processar comandos do motorista

client.py → interface do motorista que recebe chamadas e envia comandos

# Como executar

1. Iniciar o servidor
   
No terminal:

python server.py

O servidor iniciará e ficará aguardando a conexão de um client

2. Iniciar o client
   
Em outro terminal:

python client.py

Após conectar, o client receberá uma mensagem de confirmação

# Funcionamento

O servidor gera chamadas de corrida em intervalos aleatórios contendo:

Distância até o passageiro

Distância da corrida

Valor da corrida

O motorista pode interagir com o sistema através dos comandos abaixo

Comandos disponíveis:

:accept   → aceita a corrida atual

:cancel   → cancela a corrida aceita

:status   → mostra o status do motorista

:quit     → encerra a conexão

# Objetivo acadêmico

Este projeto foi desenvolvido como parte da disciplina Redes e Comunicação, com o objetivo de praticar:

Comunicação em rede com sockets

Arquitetura cliente-servidor

Programação concorrente com threads

Troca de mensagens em tempo real

Esta é a Fase 1 do projeto, onde apenas um client remoto é suportado.
