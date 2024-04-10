import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 3000
s.bind((host, port))
s.listen(2)  # Aceptar hasta 2 conexiones

clients = []
first_client = 0
second_client = 0
running = True
increment = threading.Lock()
ball_pos = [400, 300]  # Posición inicial de la bola
ball_speed = [2, 2]  # Velocidad inicial de la bola


def ball_movements(clients):
    while running:
        # En el servidor, recibir la posición de la bola del cliente
        data = client.recv(1024).decode()
        if ',' in data:
            # Enviar la posición de la bola al otro cliente
            clients[1].send(data.encode())

def client_movements(client, enemy_client):
    while True:
        try:
            data = client.recv(1024).decode()
            if data.startswith("player1"):
                _, co_player1 = data.split(", ", 1)
                enemy_client.send(co_player1.encode())
            elif data.startswith("player2"):
                _, co_player2 = data.split(", ", 1)
                enemy_client.send(co_player2.encode())
            elif data.startswith("score"):
                scores = f"{first_client} - {second_client}"
                print("SCORE: ", scores)
                client.send(scores.encode())
            else:
                # print("SALIENDO DESDE CONDICION")
                # client.send("ERROR DE CONDICION".encode())
                # client.close()
                # break
                pass
        except Exception as e:
            print("SALIENDO DESDE EXCEPCION PORQUE: ", e)
            client.send("ERROR DE EXCEPCION".encode())
            client.close()
            break

def client_scores(client):
    global running, first_client, second_client
    while running:
        data = client.recv(1024)
        if not data:
            break
        who = data.decode()
        print("WHO: ", who)
        if who == "one_point_for_player1":
            with increment:
                first_client += 1
        elif who == "one_point_for_player2":
            with increment:
                second_client += 1
        if first_client == 5 or second_client == 5:
            client.send("game over".encode())
            running = False
            client.close()
            break
        print("first_client: ", first_client)
        print("second_client: ", second_client)

while len(clients) < 2: 
    client, address = s.accept()
    clients.append(client)
    print("conexion obtenida ", address)
    print("CLIENTE: ", clients)

clients[0].send("start".encode())
clients[1].send("start".encode())
print("INICIO DEL JUEGO ENVIADO")

movements_player1 = threading.Thread(target=client_movements, args=(clients[0], clients[1]))
movements_player2 = threading.Thread(target=client_movements, args=(clients[1], clients[0]))

scores_player1 = threading.Thread(target=client_scores, args=(clients[0],))
scores_player2 = threading.Thread(target=client_scores, args=(clients[1],))

movements_ball = threading.Thread(target=ball_movements, args=(clients,))

movements_player1.start()
movements_player2.start()
scores_player1.start()
scores_player2.start()

movements_player1.join()
movements_player2.join()
scores_player1.join()
scores_player2.join()

print('Conexión cerrada')