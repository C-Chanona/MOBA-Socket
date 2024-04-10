import socket
import pygame
import sys
import threading


data = None
scores_player1 = None
scores_player2 = None
game_state = "waiting"

def res_socket(client):
    global scores_player1, scores_player2
    while True:
        client.send("score".encode())
        scores = client.recv(1024).decode()
        scores_player1, scores_player2 = scores.split(" - ")
        print('Received from the server :', scores)

def handle_network(client):
    while True:
        state = client.recv(1024).decode()
        if state == "start":
            global game_state
            game_state = "playing"
            break

#Functions for the game style
def draw_text(text, x, y, screen, font_size):
    font = pygame.font.Font(None, font_size)
    rendered_text = font.render(text, True, (255, 255, 255))
    screen.blit(rendered_text, (x, y))


def game():
    #Config the game
    pygame.init()
    #Definy the screen size (width, height)
    screen = pygame.display.set_mode((800, 600))
    #Set the title of the game
    pygame.display.set_caption('Pong')
     #Definir el rectángulo
    player1 = pygame.Rect(5, 50, 15, 100)
    player2 = pygame.Rect(780, 50, 15, 100)
    ball = pygame.Rect(400, 300, 20, 20)
    ball_speed = [0.5, 0.5]
    ball_pos = [float(ball.left), float(ball.top)]

    # Client connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 3000
    client.connect((host, port))

    threading.Thread(target=handle_network, args=(client,)).start()
    threading.Thread(target=res_socket, args=(client,)).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.close()
                pygame.quit()
                sys.exit()

        if game_state == "waiting":
            draw_text('Waiting for other player', 350, 250, screen, 36)

        elif game_state == "playing":        
            global scores_player1, scores_player2
            # Detectar las teclas presionadas
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or data == "player1, 0, -1":
                player1.move_ip(0, -1)  # Mover hacia arriba
                client.send("player1, 0, -1".encode()) if data else None
            if keys[pygame.K_s] or data == "player1, 0, 1":
                player1.move_ip(0, 1)  # Mover hacia abajo
                client.send("player1, 0, 1".encode()) if data else None
            if keys[pygame.K_UP] or data == "player2, 0, -1":
                player2.move_ip(0, -1)
                client.send("player2, 0, -1".encode()) if data else None
            if keys[pygame.K_DOWN] or data == "player2, 0, 1":
                player2.move_ip(0, 1)
                client.send("player2, 0, 1".encode()) if data else None

             # Actualizar la posición de la bola
            ball_pos[0] += ball_speed[0]
            ball_pos[1] += ball_speed[1]

            # Verificar si la bola ha golpeado los bordes de la pantalla
            #Izquierda
            if ball_pos[0] < 0:
                ball_speed[0] = -ball_speed[0]
                print("one_point_for_player2")
                client.send("one_point_for_player2".encode())
            #Derecha
            if ball_pos[0] + ball.width > 800:
                ball_speed[0] = -ball_speed[0]
                print("one_point_for_player1")
                client.send("one_point_for_player1".encode())
            #Arriba y abajo
            if ball_pos[1] < 0 or ball_pos[1] + ball.height > 600:
                ball_speed[1] = -ball_speed[1]

            # Mover la bola a la nueva posición, redondeada al entero más cercano
            ball.topleft = (round(ball_pos[0]), round(ball_pos[1]))

            # Asegurarse de que el rectángulo no se salga de la pantalla
            if player1.top < 0:
                player1.top = 0
            if player1.bottom > 600:
                player1.bottom = 600

            if player2.top < 0:
                player2.top = 0
            if player2.bottom > 600:
                player2.bottom = 600

            # Verificar si la bola está colisionando con los rectángulos
            if player1.colliderect(ball) or player2.colliderect(ball):
                ball_speed[0] = -ball_speed[0]

            center_x = 800 // 2
            center_y = 600 // 2

            screen.fill((0, 0, 0))  # Llenar la pantalla de negro
            pygame.draw.rect(screen, (255, 255, 255), player1)  # Dibujar un rectángulo
            pygame.draw.rect(screen, (255, 255, 255), player2)
            pygame.draw.circle(screen, (255, 255, 255), ball.center, ball.width // 2)  # Dibujar la bola
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 100, 2)
            pygame.draw.line(screen, (255, 255, 255), (center_x, 0), (center_x, 600), 2)
            # global scores_player1, scores_player2
            draw_text(f"{scores_player1}", 300, 40, screen, 36)
            draw_text(f"{scores_player2}", 450, 40, screen, 36)

        pygame.display.update()  # Actualizar la pantalla

    
if __name__ == '__main__':
    game()