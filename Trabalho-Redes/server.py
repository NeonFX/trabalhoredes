import socket
import threading
import random
import time
import json
import os
import sys
from datetime import datetime

#define onde o servidor irá rodar 
HOST = '127.0.0.1' 
PORT = 5000 
dados_arquivo = "motoristas.json"
max_conexoes = int(sys.argv[1]) if len(sys.argv) > 1 else 3

#váriaveis que controlam o estado da corrida e a fila de motoristas
corrida_atual = None 
corrida_aceita = False
fila_motoristas = []
dados_motoristas = {}
clientes_conectados = {}  
lock = threading.Lock() #usado para evitar condições de corrida ao acessar as variáveis compartilhadas entre threads

def carregar_dados():
    """Lê motoristas.json do disco para a memória."""
    global dados_motoristas
    if os.path.exists(dados_arquivo):
        try:
            with open(dados_arquivo, "r") as f:
                dados_motoristas = json.load(f)
        except Exception:
            dados_motoristas = {}
    else:
        dados_motoristas = {}
 
def salvar_dados():
    """Persiste o dicionário em disco atomicamente."""
    tmp = dados_arquivo + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dados_motoristas, f, indent=2)
    os.replace(tmp, dados_arquivo)

#retorna a hora atual formatada para exibir nas mensagens
def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def finalizar_corrida(nome, conn, valor_corrida):
    time.sleep(random.randint(10,20))  #simula uma duração aleatória da corrida entre 10 e 20 segundos
    with lock: #atualiza o estado da corrida para finalizada
        if nome in clientes_conectados:
            clientes_conectados[nome]['em_corrida'] = False
        elif nome in dados_motoristas:
            dados_motoristas[nome]['faturamento'] += valor_corrida
        else:
            dados_motoristas[nome] = {'faturamento': valor_corrida}
        salvar_dados()
        faturamento = dados_motoristas[nome]['faturamento']
        conn.send(f"{timestamp()} Corrida finalizada!\n".encode())
        conn.send(f"Você ganhou R$ {valor_corrida:.2f}.\n".encode())
        conn.send(f"Faturamento total: R$ {faturamento:.2f}\n".encode())

def acoes_comandos(conn, addr): #processa os comandos enviados pelo motorista
    global corrida_aceita, corrida_atual #variáveis globais que controlam o estado da corrida
    while True: #loop 
        try:
            data = conn.recv(1024).decode().strip() #servidor recebe os dados enviados pelo cliente
            if not data:
                break
            if data == ":accept": #serve para aceitar a corrida atual
                with lock:
                    if corrida_atual and not corrida_aceita:
                        corrida_aceita = True
                        conn.send(f"{timestamp()} Você executou: accept\n".encode())
                        conn.send(f"{timestamp()} Corrida aceita!\n".encode())
                        threading.Thread(target=finalizar_corrida, args=(conn,), daemon=True).start()
                    else:
                        conn.send(f"{timestamp()} Nenhuma corrida disponível.\n".encode())
            elif data == ":cancel": #serve para cancelar a corrida atual
                with lock:
                    if corrida_aceita:
                        corrida_aceita = False
                        corrida_atual = None
                        conn.send(f"{timestamp()} Você executou: cancel\n".encode())
                        conn.send(f"{timestamp()} Corrida cancelada.\n".encode())
                    else:
                        conn.send(f"{timestamp()} Você não está em corrida.\n".encode())
            elif data == ":status": #verifica o status do motorista, se ele está livre ou não, e sua posição na fila
                with lock:
                    if corrida_aceita:
                        estado = "Em corrida"
                    else:
                        estado = "Livre"
                    posicao = fila_motoristas.index(addr) + 1
                    conn.send(f"{timestamp()} Você executou: status\n".encode())
                    conn.send(f"{timestamp()} Status: {estado} | Posição na fila: {posicao}\n".encode())
            elif data == ":quit":
                conn.send(f"{timestamp()} Você executou: quit\n".encode())
                conn.send(f"{timestamp()} Desconectando...\n".encode())
                with lock:
                    if addr in fila_motoristas:
                        fila_motoristas.remove(addr)
                break
            else:
                conn.send(f"{timestamp()} Comando inválido\n".encode())
        except:
            break
    conn.close()

def gerador_corrida(conn):
    global corrida_atual, corrida_aceita
    while True:
        time.sleep(random.randint(8, 15)) #gera uma nova corrida num intervalo aleatório entre 8 e 15 segundos
        with lock:
            if corrida_aceita:
                continue
            distancia_passageiro = round(random.uniform(0.5, 5.0), 1) #distância do passageiro até o motorista
            viagem = round(random.uniform(1.0, 10.0), 1) #distância da corrida
            preco = round(viagem * random.uniform(2.5, 4.0), 2) #calcula o preço da corrida baseado na distância 
            corrida_atual = (distancia_passageiro, viagem, preco)
            msg = f"""            
NOVA CORRIDA!!!

Distância até passageiro: {distancia_passageiro} km
Distância da corrida: {viagem} km
Pagamento: R$ {preco}

Digite :accept para aceitar
"""
            try:
                conn.send(msg.encode())
            except:
                break
            wait = 10
            start = time.time()
        while time.time() - start < wait:
            with lock:
                if corrida_aceita:
                    break
            time.sleep(1)
        with lock:
            if not corrida_aceita:
                corrida_atual = None
                try:
                    conn.send(f"{timestamp()} Tempo para aceitar expirou\n".encode())
                except:
                    break
                if random.random() < 0.5:
                    preco += random.randint(2, 5)
                    corrida_atual = (distancia_passageiro, viagem, preco)
                    try:
                        conn.send(f"{timestamp()} \nPassageiro aumentou oferta para R$ {preco}\n".encode())
                    except:
                        break
                else:
                    try:
                        conn.send(f"{timestamp()} \nCorrida cancelada pelo passageiro\n".encode())
                    except:
                        break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria o socket do servidor usando IPv4 e TCP
    server.bind((HOST, PORT)) #associa o socket a um endereço IP e porta definidos
    server.listen() #servidor começa a aguardar conexões de clientes
    print("Servidor iniciado...")

    conn, addr = server.accept() #servidor aceita a conexão do cliente 
    print(f"Motorista conectado: {addr}")
    with lock:
        fila_motoristas.append(addr)

    conn.send(f"{timestamp()}: CONECTADO!!\n".encode())
    threading.Thread(target=acoes_comandos, args=(conn, addr), daemon=True).start() #cria a thread encarregada de processar as solicitações do cliente
    threading.Thread(target=gerador_corrida, args=(conn,), daemon=True).start()
    while True:
        time.sleep(1)
# "daemon = true" indica que as threads são secundárias e encerram automaticamente quando o programa principal é finalizado.

if __name__ == "__main__":
    main()
