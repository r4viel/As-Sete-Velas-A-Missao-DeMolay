from Classes import Peralde, Jacques
import pygame
import sys
import os
import math

# iniciar Pygame e Joystick
pygame.init()
pygame.joystick.init()

# INICIALIZAÇÃO DOS CONTROLES
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
    print("Nenhum controle detectado. Iniciando jogo apenas no teclado.")

# constantes
WIDTH = 1141
HEIGHT = 653

# tela
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("As sete velas a missão DeMolay")

# tela interna
tela_jogo = pygame.Surface((WIDTH, HEIGHT))

clock = pygame.time.Clock()
running = True

# Estados do jogo: "menu", "creditos", "jogando"
game_state = "menu"

# Opções do menu
OPCOES_MENU = ["JOGAR", "CRÉDITOS", "SAIR"]
opcao_selecionada = 0   # índice da opção em destaque (navegação por controle)

# Cores / estilo
COR_FUNDO_MENU   = (10, 5, 25)       # roxo-noite profundo
COR_TITULO       = (220, 180, 60)    # dourado
COR_TITULO_GLOW  = (255, 220, 80)
COR_BOTAO        = (200, 160, 50)    # dourado apagado
COR_BOTAO_HOVER  = (255, 215, 0)     # dourado brilhante
COR_BOTAO_BG   = (30, 20, 50, 180) # fundo semi-transparente
COR_TEXTO_CRED   = (180, 160, 120)
COR_VELA         = (255, 200, 80)
COR_CREDITOS  = (0,0,0)

#  Fontes 
try:
    fonte_titulo  = pygame.font.SysFont("Georgia", 62, bold=True)
    fonte_subtit  = pygame.font.SysFont("Georgia", 22, italic=True)
    fonte_botao   = pygame.font.SysFont("Georgia", 28, bold=True)
    fonte_cred    = pygame.font.SysFont("Georgia", 26)
    fonte_cred_sm = pygame.font.SysFont("Georgia", 20)
except:
    fonte_titulo  = pygame.font.Font(None, 72)
    fonte_subtit  = pygame.font.Font(None, 28)
    fonte_botao   = pygame.font.Font(None, 44)
    fonte_cred    = pygame.font.Font(None, 32)
    fonte_cred_sm = pygame.font.Font(None, 24)

#  Fundo do jogo 
caminho_imagem = "./IMG/templo.png"
try:
    fundo_original = pygame.image.load(caminho_imagem).convert()
    fundo = pygame.transform.scale(fundo_original, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Erro ao carregar o fundo: {e}")
    fundo = pygame.Surface((WIDTH, HEIGHT))
    fundo.fill((80, 0, 80))

#  Fundo do menu
try:
    fundo_menu_orig = pygame.image.load(caminho_imagem).convert()
    fundo_menu = pygame.transform.scale(fundo_menu_orig, (WIDTH, HEIGHT))
    # escurece para o menu
    escurece = pygame.Surface((WIDTH, HEIGHT))
    escurece.set_alpha(160)
    escurece.fill((0, 0, 0))
    fundo_menu.blit(escurece, (0, 0))
except:
    fundo_menu = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(10 * (1 - t) + 5 * t)
        g = int(5  * (1 - t) + 2 * t)
        b = int(40 * (1 - t) + 10 * t)
        pygame.draw.line(fundo_menu, (r, g, b), (0, y), (WIDTH, y))


#  HELPERS DE DESENHO


def desenha_divisor(surface, y, largura=400):
    """Linha ornamental dourada centralizada."""
    cx = WIDTH // 2
    pygame.draw.line(surface, COR_TITULO, (cx - largura // 2, y), (cx + largura // 2, y), 1)
    pygame.draw.circle(surface, COR_TITULO, (cx, y), 4)
    pygame.draw.circle(surface, COR_TITULO, (cx - largura // 2, y), 3)
    pygame.draw.circle(surface, COR_TITULO, (cx + largura // 2, y), 3)


def texto_centralizado(surface, texto, fonte, cor, y):
    surf = fonte.render(texto, True, cor)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)
    return rect


#  TELA DE MENU

def desenha_menu(surface, mouse_pos, tick):
    surface.blit(fundo_menu, (0, 0))

    #  Título 
    # sombra dourada
    sombra = fonte_titulo.render("As Sete Velas", True, (80, 60, 10))
    surface.blit(sombra, sombra.get_rect(center=(WIDTH // 2 + 3, 143)))
    texto_centralizado(surface, "As Sete Velas", fonte_titulo, COR_TITULO_GLOW, 140)

    subtit = fonte_subtit.render("A Missão DeMolay", True, (180, 160, 100))
    surface.blit(subtit, subtit.get_rect(center=(WIDTH // 2, 195)))

    desenha_divisor(surface, 230)

    #  Botões 
    rects_botoes = []
    for i, opcao in enumerate(OPCOES_MENU):
        by = 290 + i * 80
        rect = pygame.Rect(0, 0, 280, 54)
        rect.center = (WIDTH // 2, by)

        # fundo do botão
        bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg.fill(COR_BOTAO_BG)
        surface.blit(bg, rect.topleft)

        # borda
        pygame.draw.rect(surface, COR_BOTAO, rect, 2, border_radius=4)

        # texto
        label = fonte_botao.render(opcao, True, COR_BOTAO)
        surface.blit(label, label.get_rect(center=rect.center))

        rects_botoes.append(rect)

    desenha_divisor(surface, 545, largura=300)

    return rects_botoes


#  TELA DE CRÉDITOS

def desenha_creditos(surface, tick):
    surface.fill(COR_CREDITOS)

    texto_centralizado(surface, "Créditos", fonte_titulo, COR_TITULO, 80)
    desenha_divisor(surface, 130, largura=500)

    creditos = [
        ("Desenvolvimento", ""),
        ("Programação", "João Felipe"),
        ("Arte & Design", "Mariana Sophia"),
        ("", ""),
        ("Música & Sons", ""),
        ("Trilha Sonora", "Mariana Sophia"),
        ("", ""),
        ("", ""),
        ("Versão 1.0  •  2025", ""),
    ]

    y_base = 175
    for titulo, nome in creditos:
        if titulo == "" and nome == "":
            y_base += 12
            continue
        if nome == "":
            # cabeçalho de seção
            t = fonte_cred.render(titulo, True, COR_TITULO)
            surface.blit(t, t.get_rect(center=(WIDTH // 2, y_base + 26)))
            y_base += 52
        else:
            # linha normal
            t_label = fonte_cred_sm.render(titulo + ":", True, (140, 120, 80))
            t_nome  = fonte_cred_sm.render(nome, True, COR_TEXTO_CRED)
            surface.blit(t_label, t_label.get_rect(right=WIDTH // 2 - 10, centery=y_base))
            surface.blit(t_nome,  t_nome.get_rect(left=WIDTH // 2 + 10,  centery=y_base))
            y_base += 34

    desenha_divisor(surface, HEIGHT - 80, largura=400)

    # botão voltar
    rect_voltar = pygame.Rect(0, 0, 120, 30)
    rect_voltar.center = (WIDTH // 2, HEIGHT - 50)
    
    label_v = fonte_botao.render("VOLTAR", True, COR_BOTAO)
    surface.blit(label_v, label_v.get_rect(center=rect_voltar.center))

    return rect_voltar


#  LOOP PRINCIPAL

tick = 0

while running:
    mouse_pos = pygame.mouse.get_pos()

    #  Converte coordenadas do mouse para o espaço da tela_jogo 
    janela_w, janela_h = screen.get_size()
    escala_w = janela_w / WIDTH
    escala_h = janela_h / HEIGHT
    escala   = min(escala_w, escala_h)
    novo_w   = int(WIDTH  * escala)
    novo_h   = int(HEIGHT * escala)
    pos_x    = (janela_w - novo_w) // 2
    pos_y    = (janela_h - novo_h) // 2

    if escala > 0:
        mouse_interno = (
            (mouse_pos[0] - pos_x) / escala,
            (mouse_pos[1] - pos_y) / escala,
        )
    else:
        mouse_interno = (0, 0)

    #  Eventos 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        #  Teclado 
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key in (pygame.K_UP, pygame.K_w):
                    opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if opcao_selecionada == 0:
                        game_state = "jogando"
                    elif opcao_selecionada == 1:
                        game_state = "creditos"
                    elif opcao_selecionada == 2:
                        running = False

            elif game_state == "creditos":
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

            elif game_state == "jogando":
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

        #  Clique do mouse 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "menu":
                rects = desenha_menu(tela_jogo, mouse_interno, tick)
                if rects[0].collidepoint(mouse_interno):
                    game_state = "jogando"
                elif rects[1].collidepoint(mouse_interno):
                    game_state = "creditos"
                elif rects[2].collidepoint(mouse_interno):
                    running = False

            elif game_state == "creditos":
                rect_v = desenha_creditos(tela_jogo, tick)
                if rect_v.collidepoint(mouse_interno):
                    game_state = "menu"

        #  Controles 
        if event.type == pygame.JOYBUTTONDOWN:
            if controle1 and event.instance_id == controle1.get_instance_id():
                if game_state == "menu":
                    if event.button == 0:    # A → confirmar
                        if opcao_selecionada == 0:
                            game_state = "jogando"
                        elif opcao_selecionada == 1:
                            game_state = "creditos"
                        elif opcao_selecionada == 2:
                            running = False
                    elif event.button == 1:  # B → voltar
                        pass
                elif game_state == "creditos":
                    if event.button == 1:    # B → voltar ao menu
                        game_state = "menu"
                elif game_state == "jogando":
                    if event.button == 7:    # Start → pausa / menu
                        game_state = "menu"
                    elif event.button == 0:
                        print("Controle 1: A")
                    elif event.button == 1:
                        print("Controle 1: B")
                    elif event.button == 2:
                        print("Controle 1: X")
                    elif event.button == 3:
                        print("Controle 1: Y")

            elif controle2 and event.instance_id == controle2.get_instance_id():
                if game_state == "menu":
                    if event.button == 0:
                        if opcao_selecionada == 0:
                            game_state = "jogando"
                        elif opcao_selecionada == 1:
                            game_state = "creditos"
                        elif opcao_selecionada == 2:
                            running = False
                elif game_state == "creditos":
                    if event.button == 1:
                        game_state = "menu"
                elif game_state == "jogando":
                    if event.button == 9:    
                        game_state = "menu"
                    elif event.button == 0:
                        print("Controle 2: A lógico")
                    elif event.button == 1:
                        print("Controle 2: B lógico")
                    elif event.button == 2:
                        print("Controle 2: X lógico")
                    elif event.button == 3:
                        print("Controle 2: Y lógico")

        if event.type == pygame.JOYHATMOTION:
            if game_state == "menu":
                if controle1 and event.instance_id == controle1.get_instance_id():
                    if event.value == (0, 1):   # cima
                        opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                    elif event.value == (0, -1): # baixo
                        opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)
                elif controle2 and event.instance_id == controle2.get_instance_id():
                    if event.value == (0, 1):
                        opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                    elif event.value == (0, -1):
                        opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)

        if event.type == pygame.JOYAXISMOTION:
            # movimento só funciona no jogo
            if game_state == "jogando":
                if controle1 and event.instance_id == controle1.get_instance_id():
                    if event.axis == 0:
                        if event.value > 0.3:
                            Peralde.mover("direita")
                        elif event.value < -0.3:
                            Peralde.mover("esquerda")
                    elif event.axis == 1:
                        if event.value > 0.3:
                            Peralde.mover("baixo")
                        elif event.value < -0.3:
                            Peralde.mover("cima")
                elif controle2 and event.instance_id == controle2.get_instance_id():
                    if event.axis == 0:
                        if event.value > 0.3:
                            Jacques.mover("direita")
                        elif event.value < -0.3:
                            Jacques.mover("esquerda")
                    elif event.axis == 1:
                        if event.value > 0.3:
                            Jacques.mover("baixo")
                        elif event.value < -0.3:
                            Jacques.mover("cima")

    # Renderização 
    if game_state == "menu":
        desenha_menu(tela_jogo, mouse_interno, tick)

    elif game_state == "creditos":
        desenha_creditos(tela_jogo, tick)

    elif game_state == "jogando":
        tela_jogo.blit(fundo, (0, 0))
        # ↓↓ Aqui vai toda a lógica e desenho do seu jogo ↓↓
        # Ex: Peralde.desenhar(tela_jogo)
        #     Jacques.desenhar(tela_jogo)

    #  Letterbox 
    tela_redimensionada = pygame.transform.scale(tela_jogo, (novo_w, novo_h))
    screen.fill((0, 0, 0))
    screen.blit(tela_redimensionada, (pos_x, pos_y))

    pygame.display.flip()
    clock.tick(60)
    tick += 1

# fecharJogo
pygame.quit()
sys.exit()