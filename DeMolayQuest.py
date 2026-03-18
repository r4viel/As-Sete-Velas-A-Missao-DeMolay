import pygame
from pygame import *
import sys
import os

# iniciarPygame

pygame.init()

# constantes

WIDTH = 1370
HEIGHT = 784

# tela

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trial of the Seven Stars")
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

# classeDosPersonagens
class Personagem:
    def __init__(self, nome, vida, forca, poder):
        self.nome = nome
        self.vida = vida
        self.forca = forca
        self.poder = poder

# rodarJogo

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(fundo, (0, 0))

    # Aqui você desenha os personagens e outros elementos por cima do fundo

    pygame.display.flip()
    clock.tick(60) 

# fecharJogo
pygame.quit()
sys.exit()