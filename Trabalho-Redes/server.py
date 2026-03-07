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
                        conn.send(f"{timestamp()} Corrida aceita!\n".encode())
                    else:
                        conn.send(f"{timestamp()} Nenhuma corrida disponível.\n".encode())
            elif data == ":cancel":
                with lock:
                    if corrida_aceita:
                        corrida_aceita = False
                        corrida_atual = None
                        conn.send(f"{timestamp()} Corrida cancelada.\n".encode())
                    else:
                        conn.send(f"{timestamp()} Você não está em corrida.\n".encode())
            elif data == ":status":
                with lock:
                    if corrida_aceita:
                        msg = "Status: Em corrida"
                    else:
                        msg = "Status: Livre"
                    conn.send(f"{timestamp()} {msg}\n".encode())
            elif data == ":quit":
                conn.send("Desconectando...\n".encode())
                break
            else:
                conn.send("Comando inválido\n".encode())
        except:
            break
    conn.close()

