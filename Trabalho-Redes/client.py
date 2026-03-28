import socket
import threading
import time

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
def recebe_mensagem(sock, parar): 
    while True:
        try:
            msg = sock.recv(1024).decode() #cliente recebe mensagens do servidor em até 1024 bytes e converte para string
            if not msg:
                break
            print(msg)
        except:
            break #fecha a conexão se nehuma mensagem for recebida ou se ocorrer um erro
    parar.set() #sinaliza para enviar_comando que o servidor desconectou
    print("Servidor desconectado. Pressione Enter para sair.")

def enviar_comando(sock, parar):
    while not parar.is_set():
        try:
            cmd = input() #lê o comando digitado pelo motorista
        except (KeyboardInterrupt, EOFError): #trata CTRL-C e fechamento de stdin
            break
        if parar.is_set():
            break
        try:
            sock.send(cmd.encode()) #envia o comando para o servidor, convertendo a string para bytes
        except:
            print("Servidor desconectado")
            break
        if cmd == ":quit":
            time.sleep(0.5)
            break

def main():
    mostrar_comandos()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria o socket do cliente usando IPv4 e TCP
    try:
        client.connect((HOST, PORT)) #estabelece conexão com o servidor no endereço e porta definidos
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor. Verifique se ele está rodando.")
        return
    parar = threading.Event() #evento usado para sinalizar encerramento entre threads
    threading.Thread(target=recebe_mensagem, args=(client, parar), daemon=True).start() #cria uma thread separada para receber mensagens do servidor
    try:
        enviar_comando(client, parar)
    except KeyboardInterrupt:
        pass
    finally:
        client.close() #encerra a conexão com o servidor

if __name__ == "__main__":
    main()
