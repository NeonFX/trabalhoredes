import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

#exibe os comandos disponíveis para o motorista
def mostrar_comandos(): 
    print("\n===== COMANDOS DISPONÍVEIS =====")
    print(":accept  -> aceita a corrida atual")
    print(":cancel  -> cancela a corrida aceita")
    print(":status  -> mostra o status do motorista")
    print(":quit    -> encerra o programa")
    print("=================================\n")

#função responsável por receber mensagens do servidor e exibi-las
def recebe_mensagem(sock): 
    while True:
        try:
            msg = sock.recv(1024).decode() #cliente recebe mensagens do servidor em até 1024 bytes e converte para string
            if not msg:
                break
            print(msg)
        except:
            break #fecha a conexão se nehuma mensagem for recebida ou se ocorrer um erro

def enviar_comando(sock):
    while True:
        cmd = input() #lê o comando digitado pelo motorista
        try:
            sock.send(cmd.encode()) #envia o comando para o servidor, convertendo a string para bytes
        except:
            print("Servidor desconectado")
            break
        if cmd == ":quit":
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria o socket do cliente usando IPv4 e TCP
    client.connect((HOST, PORT)) #estabelece conexão com o servidor no endereço e porta definidos
    threading.Thread(target=recebe_mensagem, args=(client,), daemon=True).start() #cria uma thread separada para receber mensagens do servidor
    mostrar_comandos()
    enviar_comando(client)
    client.close() #encerra a conexão com o servidor 

if __name__ == "__main__":
    main()
