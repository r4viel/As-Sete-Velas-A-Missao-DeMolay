from Classes import Personagem
import pygame
import sys
import os

# iniciar Pygame e Joystick
pygame.init()
pygame.joystick.init()

# INICIALIZAÇÃO SEGURA DOS CONTROLES
num_controles = pygame.joystick.get_count()
controle1 = None
controle2 = None

if num_controles > 0:
    controle1 = pygame.joystick.Joystick(0)
    controle1.init()
    print(f"Controle 1 conectado: {controle1.get_name()}")

if num_controles > 1:
    controle2 = pygame.joystick.Joystick(1)
    controle2.init()
    print(f"Controle 2 conectado: {controle2.get_name()}")

if num_controles == 0:
    print("Nenhum controle detectado. Iniciando jogo apenas no teclado/mouse.")

# constantes
WIDTH = 1141
HEIGHT = 653

# tela 
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Trial of the Seven Stars")

# tela interna 
tela_jogo = pygame.Surface((WIDTH, HEIGHT))

clock = pygame.time.Clock()
running = True

# fundo
caminho_imagem = "./IMG/templo.png" 

try:
    fundo_original = pygame.image.load(caminho_imagem).convert()
    fundo = pygame.transform.scale(fundo_original, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Erro ao carregar o fundo: {e}")
    fundo = pygame.Surface((WIDTH, HEIGHT))
    fundo.fill("purple")

# rodarJogo
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Se o jogador redimensionar a janela
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            
        # EVENTOS DE BOTÃO (A, B, X, Y)
        if event.type == pygame.JOYBUTTONDOWN:
            
            # --- CONTROLE 1 (Xbox One) ---
            # O "if controle1" verifica se a variável não é None antes de tentar checar o ID
            if controle1 and event.instance_id == controle1.get_instance_id():
                if event.button == 0:
                    print('Controle 1: A')
                elif event.button == 1:
                    print('Controle 1: B')
                elif event.button == 2:
                    print('Controle 1: X')
                elif event.button == 3:
                    print('Controle 1: Y')
            
            # --- CONTROLE 2 (Pro Controller) ---
            elif controle2 and event.instance_id == controle2.get_instance_id():
                if event.button == 0:
                    print('Controle 2: Pressionou A lógico (Fisicamente B)')
                elif event.button == 1:
                    print('Controle 2: Pressionou B lógico (Fisicamente A)')
                elif event.button == 2:
                    print('Controle 2: Pressionou X lógico (Fisicamente Y)')
                elif event.button == 3:
                    print('Controle 2: Pressionou Y lógico (Fisicamente X)')

        # EVENTOS DE SETINHAS (D-Pad / Hat)
        if event.type == pygame.JOYHATMOTION:
            
            # --- CONTROLE 1 ---
            if controle1 and event.instance_id == controle1.get_instance_id():
                if event.hat == 0:
                    print(f'Controle 1 - Setinhas: {event.value}')

            # --- CONTROLE 2 ---
            elif controle2 and event.instance_id == controle2.get_instance_id():
                if event.hat == 0:
                    print(f'Controle 2 - Setinhas: {event.value}')

        # EVENTOS DE ANALÓGICO (Eixos Esquerdos e Direitos)
        if event.type == pygame.JOYAXISMOTION:
            
            # --- CONTROLE 1 (Xbox One) ---
            if controle1 and event.instance_id == controle1.get_instance_id():
                if event.axis == 0:
                    print(f'C1 - Analógico Esq X: {event.value:.2f}')
                elif event.axis == 1:
                    print(f'C1 - Analógico Esq Y: {event.value:.2f}')
                elif event.axis == 2:
                    print(f'C1 - Analógico Dir X: {event.value:.2f}')
                elif event.axis == 3:
                    print(f'C1 - Analógico Dir Y: {event.value:.2f}')

            # --- CONTROLE 2 (Pro Controller) ---
            elif controle2 and event.instance_id == controle2.get_instance_id():
                if event.axis == 0:
                    print(f'C2 - Analógico Esq X: {event.value:.2f}')
                elif event.axis == 1:
                    print(f'C2 - Analógico Esq Y: {event.value:.2f}')
                elif event.axis == 2:
                    print(f'C2 - Analógico Dir X: {event.value:.2f}')
                elif event.axis == 3:
                    print(f'C2 - Analógico Dir Y: {event.value:.2f}')

    # Desenha o fundo
    tela_jogo.blit(fundo, (0, 0))

    # logica das Bordas Pretas (Letterbox)
    janela_w, janela_h = screen.get_size()
    escala_w = janela_w / WIDTH
    escala_h = janela_h / HEIGHT
    escala = min(escala_w, escala_h) 
    
    novo_w = int(WIDTH * escala)
    novo_h = int(HEIGHT * escala)
    
    tela_redimensionada = pygame.transform.scale(tela_jogo, (novo_w, novo_h))
    
    pos_x = (janela_w - novo_w) // 2
    pos_y = (janela_h - novo_h) // 2
    
    screen.fill((0, 0, 0))
    screen.blit(tela_redimensionada, (pos_x, pos_y))

    # atualiza a tela
    pygame.display.flip()
    clock.tick(60) 

# fecharJogo
pygame.quit()
sys.exit()
