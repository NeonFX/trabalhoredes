import socket
import threading
import random
import time
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5000

corrida_atual = None
corrida_aceita = False
lock = threading.Lock()


def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def finalizar_corrida(conn):
    global corrida_aceita, corrida_atual
    time.sleep(random.randint(10,20))
    with lock:
        corrida_aceita = False
        corrida_atual = None
        conn.send(f"{timestamp()} Corrida finalizada!\n".encode())

def acoes_comandos(conn):
    global corrida_aceita, corrida_atual
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            if data == ":accept":
                with lock:
                    if corrida_atual and not corrida_aceita:
                        corrida_aceita = True
                        conn.send(f"{timestamp()} Você executou: accept\n".encode())
                        conn.send(f"{timestamp()} Corrida aceita!\n".encode())
                        threading.Thread(target=finalizar_corrida, args=(conn,), daemon=True).start()
                    else:
                        conn.send(f"{timestamp()} Nenhuma corrida disponível.\n".encode())
            elif data == ":cancel":
                with lock:
                    if corrida_aceita:
                        corrida_aceita = False
                        corrida_atual = None
                        conn.send(f"{timestamp()} Você executou: cancel\n".encode())
                        conn.send(f"{timestamp()} Corrida cancelada.\n".encode())
                    else:
                        conn.send(f"{timestamp()} Você não está em corrida.\n".encode())
            elif data == ":status":
                with lock:
                    if corrida_aceita:
                        msg = "Status: Em corrida"
                    else:
                        msg = "Status: Livre"
                    conn.send(f"{timestamp()} Você executou: status\n".encode())
                    conn.send(f"{timestamp()} {msg}\n".encode())
            elif data == ":quit":
                conn.send(f"{timestamp()} Você executou: quit\n".encode())
                conn.send("Desconectando...\n".encode())
                break
            else:
                conn.send("Comando inválido\n".encode())
        except:
            break
    conn.close()

def gerador_corrida(conn):
    global corrida_atual, corrida_aceita
    while True:
        time.sleep(random.randint(8, 15))
        with lock:
            if corrida_aceita:
                continue
            distancia_passageiro = round(random.uniform(0.5, 5.0), 1)
            viagem = round(random.uniform(1.0, 10.0), 1)
            preco = round(viagem * random.uniform(2.5, 4.0), 2)
            corrida_atual = (distancia_passageiro, viagem, preco)
            msg = f"""            
NOVA CORRIDA!!!

Distância até passageiro: {distancia_passageiro} km
Distância da corrida: {viagem} km
Pagamento: R$ {preco}

Digite :accept para aceitar
"""
            conn.send(msg.encode())
            wait = 10
            start = time.time()
        while time.time() - start < wait:
            with lock:
                if corrida_aceita:
                    break
            time.sleep(1)
        with lock:
            if not corrida_aceita:
                if random.random() < 0.5:
                    preco += random.randint(2, 5)
                    corrida_atual = (distancia_passageiro, viagem, preco)
                    conn.send(f"\nPassageiro aumentou oferta para R$ {preco}\n".encode())
                else:
                    conn.send("\nCorrida cancelada pelo passageiro\n".encode())
                    corrida_atual = None

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.bind((HOST, PORT))
    server.listen()
    print("Servidor iniciado...")

    conn, addr = server.accept()
    print(f"Motorista conectado: {addr}")

    conn.send(f"{timestamp()}: CONECTADO!!\n".encode())
    threading.Thread(target=acoes_comandos, args=(conn,), daemon=True).start()
    threading.Thread(target=gerador_corrida, args=(conn,), daemon=True).start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()