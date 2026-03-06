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


