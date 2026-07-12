from Classes import Jacques
from Sistemas import SistemaVirtude, GerenciadorFases
import pygame
import sys
import os
import math


pygame.init()
pygame.joystick.init()


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


WIDTH = 1141
HEIGHT = 653


screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("As sete velas a missão DeMolay")


tela_jogo = pygame.Surface((WIDTH, HEIGHT))

clock = pygame.time.Clock()
running = True


game_state = "menu"


OPCOES_MENU = ["JOGAR", "CRÉDITOS", "SAIR"]
opcao_selecionada = 0


COR_FUNDO_MENU   = (10, 5, 25)
COR_TITULO       = (220, 180, 60)
COR_TITULO_GLOW  = (255, 220, 80)
COR_BOTAO        = (200, 160, 50)
COR_BOTAO_HOVER  = (255, 215, 0)
COR_BOTAO_BG   = (30, 20, 50, 180)
COR_TEXTO_CRED   = (180, 160, 120)
COR_VELA         = (255, 200, 80)
COR_CREDITOS  = (0,0,0)


try:
    fonte_titulo  = pygame.font.SysFont("Georgia", 62, bold=True)
    fonte_subtit  = pygame.font.SysFont("Georgia", 22, italic=True)
    fonte_botao   = pygame.font.SysFont("Georgia", 28, bold=True)
    fonte_cred    = pygame.font.SysFont("Georgia", 26)
    fonte_cred_sm = pygame.font.SysFont("Georgia", 20)
    fonte_hud     = pygame.font.SysFont("Georgia", 20, bold=True)
    fonte_hud_sm  = pygame.font.SysFont("Georgia", 16)
    fonte_aviso   = pygame.font.SysFont("Georgia", 30, bold=True)
except:
    fonte_titulo  = pygame.font.Font(None, 72)
    fonte_subtit  = pygame.font.Font(None, 28)
    fonte_botao   = pygame.font.Font(None, 44)
    fonte_cred    = pygame.font.Font(None, 32)
    fonte_cred_sm = pygame.font.Font(None, 24)
    fonte_hud     = pygame.font.Font(None, 26)
    fonte_hud_sm  = pygame.font.Font(None, 20)
    fonte_aviso   = pygame.font.Font(None, 40)


caminho_imagem = "./IMG/templo.png"
try:
    fundo_menu_orig = pygame.image.load(caminho_imagem).convert()
    fundo_menu = pygame.transform.scale(fundo_menu_orig, (WIDTH, HEIGHT))
    escurece = pygame.Surface((WIDTH, HEIGHT))
    escurece.set_alpha(160)
    escurece.fill((0, 0, 0))
    fundo_menu.blit(escurece, (0, 0))
except Exception as e:
    print(f"Erro ao carregar o fundo do menu: {e}")
    fundo_menu = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(10 * (1 - t) + 5 * t)
        g = int(5  * (1 - t) + 2 * t)
        b = int(40 * (1 - t) + 10 * t)
        pygame.draw.line(fundo_menu, (r, g, b), (0, y), (WIDTH, y))


def desenha_divisor(surface, y, largura=400):
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


def desenha_menu(surface, mouse_pos, tick):
    surface.blit(fundo_menu, (0, 0))


    sombra = fonte_titulo.render("As Sete Velas", True, (80, 60, 10))
    surface.blit(sombra, sombra.get_rect(center=(WIDTH // 2 + 3, 143)))
    texto_centralizado(surface, "As Sete Velas", fonte_titulo, COR_TITULO_GLOW, 140)

    subtit = fonte_subtit.render("A Missão DeMolay", True, (180, 160, 100))
    surface.blit(subtit, subtit.get_rect(center=(WIDTH // 2, 195)))

    desenha_divisor(surface, 230)


    rects_botoes = []
    for i, opcao in enumerate(OPCOES_MENU):
        by = 290 + i * 80
        rect = pygame.Rect(0, 0, 280, 54)
        rect.center = (WIDTH // 2, by)

        bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg.fill(COR_BOTAO_BG)
        surface.blit(bg, rect.topleft)

        cor_borda = COR_BOTAO_HOVER if i == opcao_selecionada else COR_BOTAO
        pygame.draw.rect(surface, cor_borda, rect, 2, border_radius=4)

        label = fonte_botao.render(opcao, True, cor_borda)
        surface.blit(label, label.get_rect(center=rect.center))

        rects_botoes.append(rect)

    desenha_divisor(surface, 545, largura=300)

    return rects_botoes


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
        ("Versão 1.0  •  2026", ""),
    ]

    y_base = 175
    for titulo, nome in creditos:
        if titulo == "" and nome == "":
            y_base += 12
            continue
        if nome == "":
            t = fonte_cred.render(titulo, True, COR_TITULO)
            surface.blit(t, t.get_rect(center=(WIDTH // 2, y_base + 26)))
            y_base += 52
        else:
            t_label = fonte_cred_sm.render(titulo + ":", True, (140, 120, 80))
            t_nome  = fonte_cred_sm.render(nome, True, COR_TEXTO_CRED)
            surface.blit(t_label, t_label.get_rect(right=WIDTH // 2 - 10, centery=y_base))
            surface.blit(t_nome,  t_nome.get_rect(left=WIDTH // 2 + 10,  centery=y_base))
            y_base += 34

    desenha_divisor(surface, HEIGHT - 80, largura=400)

    rect_voltar = pygame.Rect(0, 0, 120, 30)
    rect_voltar.center = (WIDTH // 2, HEIGHT - 50)

    label_v = fonte_botao.render("VOLTAR", True, COR_BOTAO)
    surface.blit(label_v, label_v.get_rect(center=rect_voltar.center))

    return rect_voltar


def desenha_hud(surface, jacques, virtude, gerenciador_fases, pontuacao):

    painel = pygame.Surface((WIDTH, 78), pygame.SRCALPHA)
    painel.fill((10, 5, 20, 170))
    surface.blit(painel, (0, 0))


    nome_fase = f"Fase {gerenciador_fases.numero_fase}/3 - {gerenciador_fases.fase.nome}"
    txt_fase = fonte_hud.render(nome_fase, True, COR_TITULO_GLOW)
    surface.blit(txt_fase, (20, 10))


    txt_pontos = fonte_hud_sm.render(f"Pontuação: {pontuacao}", True, (220, 220, 220))
    surface.blit(txt_pontos, (20, 36))


    barra_x, barra_y, barra_w, barra_h = WIDTH // 2 - 160, 14, 320, 18
    exigencia = virtude.exigencia_atual(gerenciador_fases.numero_fase)
    pygame.draw.rect(surface, (40, 30, 10), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
    proporcao = virtude.pontos / virtude.VIRTUDE_MAXIMA
    cor_virtude = (220, 190, 60) if virtude.pontos >= exigencia else (200, 70, 60)
    pygame.draw.rect(surface, cor_virtude, (barra_x, barra_y, int(barra_w * proporcao), barra_h), border_radius=4)

    marcador_x = barra_x + int(barra_w * (exigencia / virtude.VIRTUDE_MAXIMA))
    pygame.draw.line(surface, (255, 255, 255), (marcador_x, barra_y - 2), (marcador_x, barra_y + barra_h + 2), 2)
    pygame.draw.rect(surface, COR_TITULO, (barra_x, barra_y, barra_w, barra_h), 1, border_radius=4)
    txt_virtude = fonte_hud_sm.render(f"Virtude: {virtude.pontos}/{virtude.VIRTUDE_MAXIMA}  (min. {exigencia})",
                                       True, (240, 230, 210))
    surface.blit(txt_virtude, txt_virtude.get_rect(center=(WIDTH // 2, barra_y + barra_h + 14)))


    velas_txt = fonte_hud_sm.render(f"Velas acesas: {virtude.velas_acesas}/7", True, COR_VELA)
    surface.blit(velas_txt, velas_txt.get_rect(right=WIDTH - 20, top=10))


    vida_jacques = fonte_hud_sm.render(f"Jacques: {jacques.vida}/{jacques.vida_maxima}", True, (220, 220, 220))
    surface.blit(vida_jacques, vida_jacques.get_rect(right=WIDTH - 20, top=36))


    inimigos_vivos = gerenciador_fases.inimigos_vivos()
    if inimigos_vivos:
        inimigo = inimigos_vivos[0]
        progresso = fonte_hud_sm.render(
            f"{inimigo.nome}: honra {int(inimigo.progresso_virtude)}/{inimigo.pontos_virtude_necessarios}",
            True, (220, 220, 220))
        surface.blit(progresso, progresso.get_rect(right=WIDTH - 20, top=56))


    if gerenciador_fases.estado == gerenciador_fases.ESTADO_VIRTUDE_INSUFICIENTE:
        aviso = fonte_hud_sm.render(gerenciador_fases.mensagem, True, (255, 120, 100))
        surface.blit(aviso, aviso.get_rect(center=(WIDTH // 2, HEIGHT - 24)))


def desenha_tela_final(surface, titulo, cor_titulo, mensagem):
    veu = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veu.fill((0, 0, 0, 190))
    surface.blit(veu, (0, 0))

    texto_centralizado(surface, titulo, fonte_titulo, cor_titulo, HEIGHT // 2 - 60)
    texto_centralizado(surface, mensagem, fonte_cred_sm, (220, 210, 200), HEIGHT // 2)
    texto_centralizado(surface, "Pressione ENTER para voltar ao menu", fonte_hud_sm,
                        (200, 190, 180), HEIGHT // 2 + 50)


LIMITES_CENA = pygame.Rect(20, 95, WIDTH - 40, HEIGHT - 130)

jacques = None
virtude = None
gerenciador_fases = None
pontuacao = 0


def reiniciar_combate():
    global jacques, virtude, gerenciador_fases, pontuacao

    jacques = Jacques(x=LIMITES_CENA.left + 60, y=LIMITES_CENA.centery)
    jacques.direcao = "direita"

    virtude = SistemaVirtude()
    gerenciador_fases = GerenciadorFases(WIDTH, HEIGHT)
    pontuacao = 0


QUADRO_DE_IMPACTO = 0.55


def _aplicar_ataques_jogador(atacante, alvos):
    global pontuacao
    if not atacante.esta_vivo() or not atacante.atacando or atacante.golpe_ja_aplicado:
        return
    if atacante.fracao_animacao_ataque() < QUADRO_DE_IMPACTO:
        return

    acertou_alguem = False
    for alvo in alvos:
        if not alvo.esta_vivo():
            continue
        if atacante.rect_ataque.colliderect(alvo.rect):
            acertou_alguem = True
            resultado = virtude.registrar_golpe(atacante, alvo)
            vida_antes = alvo.vida
            alvo.golpe_virtuoso(atacante.forca, honrado=(resultado == "honrado"),
                                origem_x=atacante.rect.centerx)
            if vida_antes > 0 and not alvo.esta_vivo():
                pontuacao += alvo.pontos
                virtude.registrar_derrota_inimigo(inimigo_atacado_pelas_costas=(resultado == "pelas_costas"))

    if acertou_alguem:
        atacante.golpe_ja_aplicado = True


def _aplicar_ataques_inimigo(atacantes, alvos):
    for atacante in atacantes:
        if not atacante.esta_vivo() or not atacante.atacando or atacante.golpe_ja_aplicado:
            continue
        if atacante.fracao_animacao_ataque() < QUADRO_DE_IMPACTO:
            continue

        acertou_alguem = False
        for alvo in alvos:
            if not alvo.esta_vivo():
                continue
            if atacante.rect_ataque.colliderect(alvo.rect):
                acertou_alguem = True
                alvo.sofrer_dano(atacante.forca, origem_x=atacante.rect.centerx)

        if acertou_alguem:
            atacante.golpe_ja_aplicado = True


def atualizar_combate(dt, teclas, eventos):
    if gerenciador_fases is None:
        return

    if gerenciador_fases.estado in (gerenciador_fases.ESTADO_VITORIA, gerenciador_fases.ESTADO_DERROTA):
        return


    dx = 0.0
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        dx -= 1
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        dx += 1

    agachar_pressionado = bool(teclas[pygame.K_DOWN] or teclas[pygame.K_s])

    if controle1:
        try:
            eixo_x = controle1.get_axis(0)
            if abs(eixo_x) > 0.25:
                dx += eixo_x
            eixo_y = controle1.get_axis(1)
            if eixo_y > 0.5:
                agachar_pressionado = True
        except Exception:
            pass

    if jacques and jacques.esta_vivo():
        if agachar_pressionado:
            jacques.agachar(True)
        else:
            jacques.agachar(False)
            jacques.mover_horizontal(dx, dt, LIMITES_CENA)
            if dx == 0 and jacques.estado == "andando":
                jacques.estado = "parado"


    for event in eventos:
        if jacques is None or not jacques.esta_vivo():
            continue
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                jacques.atacar()
            elif event.key in (pygame.K_UP, pygame.K_w):
                jacques.pular()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            jacques.atacar()
        elif event.type == pygame.JOYBUTTONDOWN and controle1 and event.instance_id == controle1.get_instance_id():
            if event.button == 0:
                jacques.atacar()
            elif event.button == 1:
                jacques.pular()


    if jacques:
        jacques.atualizar(dt)
    for inimigo in gerenciador_fases.inimigos:
        inimigo.atualizar(dt)


    alvos_do_inimigo = [jacques] if jacques is not None else []
    for inimigo in gerenciador_fases.inimigos_vivos():
        inimigo.atualizar_ia(dt, alvos_do_inimigo, LIMITES_CENA)


    if jacques is not None:
        _aplicar_ataques_jogador(jacques, gerenciador_fases.inimigos_vivos())

    if jacques is not None:
        _aplicar_ataques_inimigo(gerenciador_fases.inimigos_vivos(), [jacques])


    if jacques and not jacques.esta_vivo():
        gerenciador_fases.estado = gerenciador_fases.ESTADO_DERROTA
        gerenciador_fases.mensagem = "Jacques caiu em combate..."
        return


    gerenciador_fases.atualizar(dt, virtude)


def desenhar_combate(surface):
    gerenciador_fases.desenhar_fundo(surface)

    personagens = list(gerenciador_fases.inimigos) + ([jacques] if jacques else [])

    personagens.sort(key=lambda p: p.y + p.altura)
    for personagem in personagens:
        if personagem.esta_vivo() or personagem.estado == "morrendo":
            personagem.desenhar(surface)

    desenha_hud(surface, jacques, virtude, gerenciador_fases, pontuacao)

    if gerenciador_fases.estado == gerenciador_fases.ESTADO_TRANSICAO:
        texto_centralizado(surface, gerenciador_fases.mensagem, fonte_aviso, COR_TITULO_GLOW, HEIGHT // 2)
    elif gerenciador_fases.estado == gerenciador_fases.ESTADO_VITORIA:
        desenha_tela_final(surface, "Vitória!", COR_VELA,
                            "As sete velas foram acesas. As virtudes de Jacques DeMolay prevaleceram.")
    elif gerenciador_fases.estado == gerenciador_fases.ESTADO_DERROTA:
        desenha_tela_final(surface, "Derrota", (200, 60, 50), gerenciador_fases.mensagem)


tick = 0

while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()


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


    eventos = pygame.event.get()
    for event in eventos:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)


        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key in (pygame.K_UP, pygame.K_w):
                    opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if opcao_selecionada == 0:
                        reiniciar_combate()
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
                elif event.key == pygame.K_RETURN and gerenciador_fases is not None and \
                        gerenciador_fases.estado in (gerenciador_fases.ESTADO_VITORIA,
                                                      gerenciador_fases.ESTADO_DERROTA):
                    game_state = "menu"


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "menu":
                rects = desenha_menu(tela_jogo, mouse_interno, tick)
                if rects[0].collidepoint(mouse_interno):
                    reiniciar_combate()
                    game_state = "jogando"
                elif rects[1].collidepoint(mouse_interno):
                    game_state = "creditos"
                elif rects[2].collidepoint(mouse_interno):
                    running = False

            elif game_state == "creditos":
                rect_v = desenha_creditos(tela_jogo, tick)
                if rect_v.collidepoint(mouse_interno):
                    game_state = "menu"


        if event.type == pygame.JOYBUTTONDOWN:
            if controle1 and event.instance_id == controle1.get_instance_id():
                if game_state == "menu":
                    if event.button == 0:
                        if opcao_selecionada == 0:
                            reiniciar_combate()
                            game_state = "jogando"
                        elif opcao_selecionada == 1:
                            game_state = "creditos"
                        elif opcao_selecionada == 2:
                            running = False
                elif game_state == "creditos":
                    if event.button == 1:
                        game_state = "menu"
                elif game_state == "jogando":
                    if event.button == 7:
                        game_state = "menu"


            elif controle2 and event.instance_id == controle2.get_instance_id():
                if game_state == "menu":
                    if event.button == 0:
                        if opcao_selecionada == 0:
                            reiniciar_combate()
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

        if event.type == pygame.JOYHATMOTION:
            if game_state == "menu":
                if controle1 and event.instance_id == controle1.get_instance_id():
                    if event.value == (0, 1):
                        opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                    elif event.value == (0, -1):
                        opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)
                elif controle2 and event.instance_id == controle2.get_instance_id():
                    if event.value == (0, 1):
                        opcao_selecionada = (opcao_selecionada - 1) % len(OPCOES_MENU)
                    elif event.value == (0, -1):
                        opcao_selecionada = (opcao_selecionada + 1) % len(OPCOES_MENU)


    if game_state == "menu":
        desenha_menu(tela_jogo, mouse_interno, tick)

    elif game_state == "creditos":
        desenha_creditos(tela_jogo, tick)

    elif game_state == "jogando":
        teclas = pygame.key.get_pressed()
        atualizar_combate(dt, teclas, eventos)
        desenhar_combate(tela_jogo)


    tela_redimensionada = pygame.transform.scale(tela_jogo, (novo_w, novo_h))
    screen.fill((0, 0, 0))
    screen.blit(tela_redimensionada, (pos_x, pos_y))

    pygame.display.flip()
    tick += 1


pygame.quit()
sys.exit()
