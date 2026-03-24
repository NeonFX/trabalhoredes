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

#arquivo onde os dados dos motoristas serão armazenados
dados_arquivo = "motoristas.json"
max_conexoes = int(sys.argv[1]) if len(sys.argv) > 1 else 3 #se digitar um numero ele vai ser o limite de conexao, se nao digitar nada vai ser 3 como padrao

#váriaveis que controlam a fila de motoristas e os dados dos motoristas
fila_motoristas = []
dados_motoristas = {}
clientes_conectados = {}  

lock = threading.Lock() #usado para evitar condições de corrida ao acessar as variáveis compartilhadas entre threads
lock_send = threading.Lock() #usado para evitar que duas threads enviem mensagens ao mesmo tempo para o mesmo cliente

def carregar_dados(): #carrega os dados do arquivo json
    global dados_motoristas
    if os.path.exists(dados_arquivo):
        try:
            with open(dados_arquivo, "r") as f:
                dados_motoristas = json.load(f)
        except Exception:
            dados_motoristas = {}
    else:
        dados_motoristas = {}
 
def salvar_dados(): #salva os dados no arquivo json
    tmp = dados_arquivo + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dados_motoristas, f, indent=2)
    os.replace(tmp, dados_arquivo)

def timestamp(): #retorna a hora atual formatada para exibir nas mensagens
    return datetime.now().strftime("%H:%M:%S")

def finalizar_corrida(nome, conn, valor_corrida):
    time.sleep(random.randint(10,20))  #simula uma duração aleatória da corrida entre 10 e 20 segundos
    with lock: #atualiza o estado da corrida para finalizada
        if nome in clientes_conectados:
            clientes_conectados[nome]['em_corrida'] = False
        if nome not in dados_motoristas:
            dados_motoristas[nome] = {'faturamento': 0.0}
        dados_motoristas[nome]['faturamento'] += valor_corrida

        salvar_dados()
        faturamento = dados_motoristas[nome]['faturamento']
        with lock_send:
            conn.send(f"[RESULTADO] {timestamp()} Corrida finalizada!\n".encode())
            conn.send(f"[RESULTADO] Você ganhou R$ {valor_corrida:.2f}.\n".encode())
            conn.send(f"[RESULTADO] Faturamento total: R$ {faturamento:.2f}\n".encode())

def acoes_comandos(nome, conn, addr): #processa os comandos enviados pelo motorista
    while True:
        try:
            data = conn.recv(1024).decode().strip() #servidor recebe os dados enviados pelo cliente
            if not data:
                break
        except Exception:
            break

        if data == ":accept": #serve para aceitar a corrida atual
            with lock:
                info = clientes_conectados.get(nome)
                if info is None:
                    break
                corrida = info.get('corrida_atual')
                em_corrida = info.get('em_corrida', False)
 
                if corrida and not em_corrida:
                    info['corrida_aceita'] = True
                    info['em_corrida']     = True
                    _, _, valor = corrida
                    with lock_send:
                        conn.send(f"[RESPOSTA] {timestamp()} Você executou: accept\n".encode())
                        conn.send(f"[RESPOSTA] {timestamp()} Corrida aceita!\n".encode())
                    threading.Thread(target=finalizar_corrida, args=(nome, conn, valor),daemon=True).start()
                elif em_corrida:
                    with lock_send:
                        conn.send(f"[INFO] {timestamp()} Você já está em uma corrida.\n".encode())
                else:
                    with lock_send:
                        conn.send(f"[INFO] {timestamp()} Nenhuma corrida disponível no momento.\n".encode())
 
        elif data == ":cancel": #serve para cancelar a corrida atual
            with lock:
                info = clientes_conectados.get(nome)
                if info and info.get('em_corrida'):
                    info['em_corrida'] = False
                    info['corrida_atual'] = None
                    info['corrida_aceita'] = False
                    with lock_send:
                        conn.send(f"[RESPOSTA] {timestamp()} Você executou: cancel\n".encode())
                        conn.send(f"[RESPOSTA] {timestamp()} Corrida cancelada.\n".encode())
                else:
                    with lock_send:
                        conn.send(f"[INFO] {timestamp()} Você não está em corrida.\n".encode())
 
        elif data == ":status": #mostra o status do motorista, se ele está livre ou não, e sua posição na fila
            with lock:
                info = clientes_conectados.get(nome)
                if info is None:
                    break
                estado  = "Em corrida" if info.get('em_corrida') else "Livre"
                posicao = fila_motoristas.index(nome) + 1 if nome in fila_motoristas else "?"
                fat     = dados_motoristas.get(nome, {}).get('faturamento', 0.0)
            with lock_send:
                conn.send(f"[RESPOSTA] {timestamp()} Você executou: status\n".encode())
                conn.send(f"[RESPOSTA] {timestamp()} Status: {estado} | "
                          f"Posição na fila: {posicao} | "
                          f"Faturamento total: R$ {fat:.2f}\n".encode())
        elif data == ":quit":
            try:
                with lock_send:
                    conn.send(f"[RESPOSTA] {timestamp()} Você executou: quit\n".encode())
                    conn.send(f"[INFO] {timestamp()} Desconectando...\n".encode())
            except:
                pass
            break
        else:
            with lock_send:
                conn.send(f"[INFO] {timestamp()} Comando inválido. Use :accept, :cancel, :status ou :quit\n".encode())

    with lock:
        if nome in fila_motoristas:
            fila_motoristas.remove(nome) #tirar da fila quando quitar
            print(f"[DEBUG] Fila após saída de {nome}: {fila_motoristas}")
        if nome in clientes_conectados:
            clientes_conectados[nome]['parar'].set() #sinaliza para as threads que o motorista saiu
            del clientes_conectados[nome]
    print(f"Motorista '{nome}' desconectado ({addr}).")
    conn.close()

def gerador_corrida(nome, conn):
    while True:
        time.sleep(random.randint(8, 15))
        with lock: #verificando caso o motorista saiu
            if nome not in clientes_conectados:
                break
            if clientes_conectados[nome]['parar'].is_set():
                break
            em_corrida = clientes_conectados[nome]['em_corrida']
        if em_corrida:
            continue
        distancia_passageiro = round(random.uniform(0.5, 5.0), 1) #distância do passageiro até o motorista
        viagem = round(random.uniform(1.0, 10.0), 1) #distância da corrida
        preco = round(viagem * random.uniform(2.5, 4.0), 2) #calcula o preço da corrida baseado na distância
 
        with lock:
            if nome not in clientes_conectados:
                break
            clientes_conectados[nome]['corrida_atual']  = (distancia_passageiro, viagem, preco)
            clientes_conectados[nome]['corrida_aceita'] = False
 
        msg = f"""[ALERTA] {timestamp()} NOVA CORRIDA!!!

Distância até passageiro: {distancia_passageiro} km
Distância da corrida: {viagem} km
Pagamento: R$ {preco}

Digite :accept para aceitar
"""
        try:
            with lock_send:
                conn.send(msg.encode())
        except:
            break
        start = time.time() #10 seg pra aceitar a corrida
        aceita = False
        while time.time() - start < 10:
            with lock:
                if nome not in clientes_conectados:
                    return
                aceita = clientes_conectados[nome].get('corrida_aceita', False)
            if aceita:
                break
            time.sleep(1)

        with lock:
            if nome not in clientes_conectados:
                break
            aceita = clientes_conectados[nome].get('corrida_aceita', False)
            if not aceita:
                clientes_conectados[nome]['corrida_atual'] = None
 
        if not aceita:
            try:
                with lock_send:
                    conn.send(f"[AVISO] {timestamp()} Tempo para aceitar expirou\n".encode())
            except:
                break

            if random.random() < 0.5: #50% de chance de o passageiro aumentar a oferta
                preco += random.randint(2, 5)
                with lock:
                    if nome in clientes_conectados:
                        clientes_conectados[nome]['corrida_atual'] = (distancia_passageiro, viagem, preco)
                try:
                    with lock_send:
                        conn.send(f"[AVISO] {timestamp()} Passageiro aumentou a oferta para R$ {preco:.2f}. "
                                  f"Digite :accept para aceitar.\n".encode())
                except:
                    break
            else:
                try:
                    with lock_send:
                        conn.send(f"[AVISO] {timestamp()} Corrida cancelada pelo passageiro.\n".encode())
                except:
                    break

def iniciar_sessao(conn, addr): #solicita o nome do motorista, verifica ou cria cadastro e inicia as duas threads
    conn.send(f"[INFO] {timestamp()}: CONECTADO!!\n".encode())
    conn.send(f"[INFO] Digite seu nome para entrar: \n".encode())

    try:
        nome = conn.recv(256).decode().strip()
    except Exception:
        conn.close()
        return
    
    if not nome:
        conn.send(f"Nome inválido. Encerrando conexão.\n".encode())
        conn.close()
        return
 
    with lock: #verifica se nome já está conectado agora
        if nome in clientes_conectados:
            conn.send(f"[INFO] {timestamp()} Nome '{nome}' já está conectado. Tente outro nome.\n".encode())
            conn.close()
            return

        if nome not in dados_motoristas: #recupera ou cria dados persistidos
            dados_motoristas[nome] = {'faturamento': 0.0}
            salvar_dados()
            conn.send(f"[INFO] {timestamp()} Bem-vindo, {nome}! Conta criada com faturamento R$ 0,00.\n".encode())
        else:
            fat = dados_motoristas[nome]['faturamento']
            conn.send(f"[INFO] {timestamp()} Bem-vindo de volta, {nome}! "
                      f"Faturamento acumulado: R$ {fat:.2f}\n".encode())
            
        fila_motoristas.append(nome)
        clientes_conectados[nome] = {
            'conn': conn,
            'addr': addr,
            'em_corrida': False,
            'corrida_atual': None,
            'corrida_aceita': False,
            'parar': threading.Event(),
        }
 
    posicao = fila_motoristas.index(nome) + 1
    conn.send(f"[INFO] {timestamp()} Você está na posição {posicao} da fila.\n".encode())
    print(f"Motorista '{nome}' conectado ({addr}). Fila: {fila_motoristas}")
    threading.Thread(target=acoes_comandos, args=(nome, conn, addr), daemon=True).start()
    threading.Thread(target=gerador_corrida, args=(nome, conn), daemon=True).start()

def main():
    carregar_dados()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(max_conexoes)
    print(f"Servidor iniciado em {HOST}:{PORT} | Limite de conexões: {max_conexoes}")

    while True:
        try:
            conn, addr = server.accept()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
            with lock:
                salvar_dados()
            break
        with lock:
            total = len(clientes_conectados)
        if total >= max_conexoes:
            conn.send(f"[INFO] {timestamp()} Servidor cheio. Tente novamente mais tarde.\n".encode())
            conn.close()
            print(f"Conexão recusada ({addr}): servidor lotado.")
            continue
        
        threading.Thread(target=iniciar_sessao, args=(conn, addr), daemon=True).start()
# "daemon = true" indica que as threads são secundárias e encerram automaticamente quando o programa principal é finalizado.

if __name__ == "__main__":
    main()