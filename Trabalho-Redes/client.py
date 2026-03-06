import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

def mostrar_comandos(): 
    print("\n===== COMANDOS DISPONÍVEIS =====")
    print(":accept  -> aceita a corrida atual")
    print(":cancel  -> cancela a corrida aceita")
    print(":status  -> mostra o status do motorista")
    print(":quit    -> encerra o programa")
    print("=================================\n")

def recebe_mensagem(sock): 
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            break

def enviar_comando(sock):
    while True:
        cmd = input()
        sock.send(cmd.encode())
        if cmd == ":quit":
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    threading.Thread(target=recebe_mensagem, args=(client,), daemon=True).start()
    mostrar_comandos()
    enviar_comando(client)
    client.close()

if __name__ == "__main__":
    main()