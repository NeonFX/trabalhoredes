# Simulação de Uber – Projeto de Redes 

Este projeto simula, de forma simplificada, o funcionamento do aplicativo de motorista da Uber utilizando comunicação em rede no modelo cliente-servidor.
O sistema utiliza sockets e threads para permitir comunicação assíncrona entre o servidor e um motorista conectado.
O servidor simula o sistema da plataforma, gerando chamadas de corrida aleatórias.
O cliente representa o motorista, que pode aceitar ou cancelar corridas através de comandos.
O sistema trata exceções de forma robusta, garantindo que nenhum erro ou warning seja gerado pelo interpretador em nenhuma situação.

# Tecnologias utilizadas

Biblioteca socket 

Biblioteca threading

Biblioteca json (persistência de dados)

Biblioteca signal (tratamento de interrupções)

Todas as bibliotecas utilizadas são nativas do Python

# Estrutura do projeto
Trabalho-Redes/

 ├── server.py
 
 └── client.py
 
 └── motoristas.json

server.py → responsável por gerar corridas e processar comandos do motorista

client.py → interface do motorista que recebe chamadas e envia comandos

motoristas.json → arquivo de persistência gerado automaticamente pelo servidor

# Como executar

1. Iniciar o servidor
   
No terminal:

python server.py (n_clientes)
ex: python server.py 3

O servidor iniciará e ficará aguardando a conexão de clientes

2. Iniciar o client
   
Em outro terminal:

python client.py

Após conectar, o client receberá uma mensagem de confirmação e o sistema solicitará o nome do motorista.

Se for novo, o saldo inicia em 0

Se já existir, o saldo acumulado é recuperado automaticamente.

# Funcionamento

O servidor gerencia múltiplos motoristas simultaneamente e mantém uma fila de atendimento.

Cada motorista conectado recebe corridas de forma independente e assíncrona.

Após finalizar uma corrida, o valor é somado ao faturamento acumulado do motorista.

Os dados são salvos automaticamente a cada atualização e também ao encerrar o servidor.

Cada corrida contém:

- Distância até o passageiro (km)

- Distância da corrida (km)

- Valor da corrida (R$)

O motorista pode interagir com o sistema através dos comandos abaixo

O motorista tem 10 segundos para aceitar cada corrida. Caso não aceite, o passageiro pode cancelar ou aumentar a oferta (50% de chance para cada).

Comandos disponíveis:

:accept   → aceita a corrida atual

:cancel   → cancela a corrida aceita

:status   → mostra o status do motorista, contendo:

   - estado (Livre / Em corrida)
            
   - posição na fila

   - saldo acumulado
         
:quit     → encerra a conexão

# Objetivo acadêmico

Este projeto foi desenvolvido como parte da disciplina Redes e Comunicação, com o objetivo de praticar:

Comunicação em rede com sockets

Arquitetura cliente-servidor

Programação concorrente com threads

Troca de mensagens em tempo real

Persistência de dados

Gerenciamento de múltiplos clientes

Fase 2 do projeto:

- Suporte a múltiplos usuários simultâneos

- Limite de conexões configurável via terminal

- Fila de motoristas com posição

- Sistema de saldo por usuário

- Persistência de dados em arquivo (json)

- Recuperação de dados ao reconectar

Fase 3 do projeto:

- Tratamento completo de exceções no cliente e no servidor

- Cliente detecta desconexão do servidor e encerra corretamente

- Servidor avisa clientes conectados ao ser encerrado (CTRL-C)

- Servidor trata interrupções com salvamento de dados antes de encerrar

- Lock de envio individual por cliente, evitando conflito entre threads

- Nenhum erro ou warning gerado pelo interpretador em nenhuma situação
