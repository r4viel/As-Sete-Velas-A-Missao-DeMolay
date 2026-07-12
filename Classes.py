

import os
import math
import random
import pygame

LARGURA_FRAME = 128
ALTURA_FRAME = 128


GRAVIDADE = 1800.0
IMPULSO_PULO = 620.0
FATOR_ALTURA_AGACHADO = 0.55

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_ASSETS = os.path.join(DIR_BASE, "asserts")


def carregar_spritesheet(caminho, largura_frame=LARGURA_FRAME, altura_frame=ALTURA_FRAME):
    try:
        folha = pygame.image.load(caminho).convert_alpha()
    except Exception as e:
        print(f"Erro ao carregar spritesheet {caminho}: {e}")
        vazio = pygame.Surface((largura_frame, altura_frame), pygame.SRCALPHA)
        vazio.fill((255, 0, 255, 120))
        return [vazio]

    largura_total = folha.get_width()
    n_frames = max(1, largura_total // largura_frame)
    frames = []
    for i in range(n_frames):
        frame = folha.subsurface((i * largura_frame, 0, largura_frame, altura_frame)).copy()
        frames.append(frame)
    return frames


class BibliotecaSprites:
    _cache = None

    @classmethod
    def obter(cls):
        if cls._cache is None:
            cls._cache = {
                "parado":     carregar_spritesheet(os.path.join(DIR_ASSETS, "walk.png"))[:1],
                "andar":      carregar_spritesheet(os.path.join(DIR_ASSETS, "walk.png")),
                "correr":     carregar_spritesheet(os.path.join(DIR_ASSETS, "run.png")),
                "pular":      carregar_spritesheet(os.path.join(DIR_ASSETS, "jump.png")),
                "machucado":  carregar_spritesheet(os.path.join(DIR_ASSETS, "hurt.png")),
                "morrer":     carregar_spritesheet(os.path.join(DIR_ASSETS, "dead.png")),
                "defender":   carregar_spritesheet(os.path.join(DIR_ASSETS, "protect.png")),
                "ataque1":    carregar_spritesheet(os.path.join(DIR_ASSETS, "attack.1.png")),
                "ataque2":    carregar_spritesheet(os.path.join(DIR_ASSETS, "attack.2.png")),
                "ataque3":    carregar_spritesheet(os.path.join(DIR_ASSETS, "attack.3.png")),
                "ataque4":    carregar_spritesheet(os.path.join(DIR_ASSETS, "attack.4.png")),
            }
        return cls._cache


VELOCIDADE_ANIM = 0.09


QUADRO_DE_IMPACTO = 0.55


class Personagem:

    def __init__(self, nome, vida, forca, poder, x, y, largura=190, altura=190, velocidade=220):
        self.nome = nome
        self.vida_maxima = vida
        self.vida = vida
        self.forca = forca
        self.poder = poder
        self.x = float(x)
        self.y = float(y)
        self.largura = largura
        self.altura = altura
        self.velocidade = velocidade


        self.direcao = "direita"


        self.estado = "parado"
        self.frame_index = 0.0
        self.sprites = BibliotecaSprites.obter()


        self.esta_vivo_flag = True
        self.atacando = False
        self.tipo_ataque_atual = "ataque1"
        self.cooldown_ataque = 0.0
        self.tempo_recarga_ataque = 0.6
        self.golpe_ja_aplicado = False
        self.tempo_invencivel = 0.0
        self.recuo_x = 0.0
        self.recuo_y = 0.0


        self.pontos = 0


        self.chao_y = float(y)
        self.pulando = False
        self.velocidade_vertical = 0.0
        self.agachado = False


    @property
    def rect(self):
        if self.estado == "agachado":
            altura_agachado = int(self.altura * FATOR_ALTURA_AGACHADO)
            y_agachado = self.y + (self.altura - altura_agachado)
            return pygame.Rect(int(self.x), int(y_agachado), self.largura, altura_agachado)
        return pygame.Rect(int(self.x), int(self.y), self.largura, self.altura)

    @property
    def rect_ataque(self):
        alcance = 55
        if self.direcao == "direita":
            return pygame.Rect(int(self.x + self.largura * 0.5), int(self.y + 10),
                                alcance, self.altura - 20)
        else:
            return pygame.Rect(int(self.x - alcance + self.largura * 0.5), int(self.y + 10),
                                alcance, self.altura - 20)


    def mover_horizontal(self, dx, dt, limites=None):
        if self.estado in ("atacando", "morrendo", "machucado", "pulando", "agachado") or not self.esta_vivo_flag:
            return
        if dx == 0:
            return

        dx = max(-1.0, min(1.0, dx))
        self.x += dx * self.velocidade * dt

        if dx > 0.05:
            self.direcao = "direita"
        elif dx < -0.05:
            self.direcao = "esquerda"

        self.estado = "andando"

        if limites:
            self.x = max(limites.left, min(self.x, limites.right - self.largura))

    def mover(self, direcao, dt=1 / 60, limites=None):
        if direcao == 'esquerda':
            self.mover_horizontal(-1, dt, limites)
        elif direcao == 'direita':
            self.mover_horizontal(1, dt, limites)

    def pular(self):
        if self.estado in ("atacando", "morrendo", "machucado", "pulando", "agachado") or not self.esta_vivo_flag:
            return False
        self.estado = "pulando"
        self.pulando = True
        self.velocidade_vertical = -IMPULSO_PULO
        self.frame_index = 0.0
        return True

    def agachar(self, ativo):
        if not self.esta_vivo_flag or self.estado in ("atacando", "morrendo", "pulando"):
            if not ativo:
                self.agachado = False
            return
        self.agachado = ativo
        if ativo:
            self.estado = "agachado"
        elif self.estado == "agachado":
            self.estado = "parado"


    def pode_atacar(self):
        return (self.esta_vivo_flag and self.estado not in ("atacando", "morrendo", "machucado", "pulando")
                and self.cooldown_ataque <= 0)

    def iniciar_ataque(self, tipo_ataque="ataque1"):
        if not self.pode_atacar():
            return False
        self.estado = "atacando"
        self.tipo_ataque_atual = tipo_ataque if tipo_ataque in self.sprites else "ataque1"
        self.frame_index = 0.0
        self.atacando = True
        self.golpe_ja_aplicado = False
        return True

    def sofrer_dano(self, dano, origem_x=None):
        if not self.esta_vivo_flag or self.tempo_invencivel > 0:
            return False

        self.vida -= dano
        self.tempo_invencivel = 0.5
        self.estado = "machucado"
        self.frame_index = 0.0


        if origem_x is not None:
            direcao_recuo = 1 if self.x < origem_x else -1
        else:
            direcao_recuo = -1 if self.direcao == "direita" else 1
        self.recuo_x = direcao_recuo * 180

        if self.vida <= 0:
            self.vida = 0
            self.esta_vivo_flag = False
            self.estado = "morrendo"
            self.frame_index = 0.0

        return True

    def esta_vivo(self):
        return self.esta_vivo_flag


    def _lista_frames_atual(self):
        if self.estado == "andando":
            return self.sprites["andar"]
        if self.estado == "correndo":
            return self.sprites["correr"]
        if self.estado == "atacando":
            return self.sprites[self.tipo_ataque_atual]
        if self.estado == "machucado":
            return self.sprites["machucado"]
        if self.estado == "morrendo":
            return self.sprites["morrer"]
        if self.estado == "defendendo":
            return self.sprites["defender"]
        if self.estado == "pulando":
            return self.sprites["pular"]
        if self.estado == "agachado":

            return self.sprites["defender"]
        return self.sprites["parado"]

    def atualizar(self, dt):

        if abs(self.recuo_x) > 1:
            self.x += self.recuo_x * dt
            self.recuo_x *= max(0, 1 - dt * 6)
        else:
            self.recuo_x = 0

        if self.cooldown_ataque > 0:
            self.cooldown_ataque = max(0, self.cooldown_ataque - dt)
        if self.tempo_invencivel > 0:
            self.tempo_invencivel = max(0, self.tempo_invencivel - dt)


        if self.estado == "pulando":
            self.velocidade_vertical += GRAVIDADE * dt
            self.y += self.velocidade_vertical * dt
            if self.y >= self.chao_y:
                self.y = self.chao_y
                self.velocidade_vertical = 0.0
                self.pulando = False
                self.estado = "parado"

        frames = self._lista_frames_atual()
        self.frame_index += dt / VELOCIDADE_ANIM

        if self.estado == "atacando":
            if self.frame_index >= len(frames):
                self.atacando = False
                self.estado = "parado"
                self.frame_index = 0
                self.cooldown_ataque = self.tempo_recarga_ataque
        elif self.estado == "machucado":
            if self.frame_index >= len(frames):
                self.estado = "parado"
                self.frame_index = 0
        elif self.estado == "morrendo":
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
        elif self.estado == "pulando":
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
        elif self.estado == "agachado":
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
        else:
            if self.frame_index >= len(frames):
                self.frame_index = 0

    def fracao_animacao_ataque(self):
        frames = self.sprites.get(self.tipo_ataque_atual, self.sprites["ataque1"])
        if not frames:
            return 0
        return min(1.0, self.frame_index / len(frames))


    def desenhar(self, surface, mostrar_barra_vida=True):
        frames = self._lista_frames_atual()
        idx = int(self.frame_index) % len(frames)
        imagem = frames[idx]
        imagem = pygame.transform.scale(imagem, (self.largura, self.altura))

        if self.direcao == "esquerda":
            imagem = pygame.transform.flip(imagem, True, False)


        if self.tempo_invencivel > 0 and int(self.tempo_invencivel * 20) % 2 == 0:
            imagem = imagem.copy()
            imagem.set_alpha(120)

        surface.blit(imagem, (int(self.x), int(self.y)))

        if mostrar_barra_vida and self.vida_maxima > 0:
            self._desenhar_barra_vida(surface)

    def _desenhar_barra_vida(self, surface):
        largura_barra = self.largura
        altura_barra = 6
        bx = int(self.x)
        by = int(self.y) - 12
        proporcao = max(0, self.vida / self.vida_maxima)
        pygame.draw.rect(surface, (40, 0, 0), (bx, by, largura_barra, altura_barra))
        cor = (60, 200, 60) if proporcao > 0.5 else (220, 180, 40) if proporcao > 0.25 else (200, 40, 40)
        pygame.draw.rect(surface, cor, (bx, by, int(largura_barra * proporcao), altura_barra))
        pygame.draw.rect(surface, (10, 10, 10), (bx, by, largura_barra, altura_barra), 1)


class Jogador(Personagem):

    def __init__(self, nome, vida, forca, poder, x, y, **kwargs):
        super().__init__(nome, vida, forca, poder, x, y, **kwargs)
        self.tempo_recarga_ataque = 0.45

    def atacar(self):
        return self.iniciar_ataque("ataque1")


class Aliado(Personagem):


    PADROES_POR_FASE = {
        1: {"tipo_ataque": "ataque1", "alcance": 260, "cooldown": 0.75},
        2: {"tipo_ataque": "ataque3", "alcance": 300, "cooldown": 0.55},
        3: {"tipo_ataque": "ataque4", "alcance": 340, "cooldown": 0.40},
    }

    def __init__(self, nome, vida, forca, poder, x, y, **kwargs):
        super().__init__(nome, vida, forca, poder, x, y, **kwargs)
        self.fase_atual = 1
        self.alcance_deteccao = self.PADROES_POR_FASE[1]["alcance"]
        self.tempo_recarga_ataque = self.PADROES_POR_FASE[1]["cooldown"]
        self._ponto_ancora = (self.x, self.y)

    def definir_padrao_ataque(self, fase):
        padrao = self.PADROES_POR_FASE.get(fase, self.PADROES_POR_FASE[1])
        self.fase_atual = fase
        self.alcance_deteccao = padrao["alcance"]
        self.tempo_recarga_ataque = padrao["cooldown"]

    def atualizar_ia(self, dt, inimigos, limites=None):
        if not self.esta_vivo_flag:
            return None

        vivos = [i for i in inimigos if i.esta_vivo()]
        alvo = None
        menor_dist = self.alcance_deteccao
        for inimigo in vivos:
            dist = math.hypot(inimigo.rect.centerx - self.rect.centerx,
                               inimigo.rect.centery - self.rect.centery)
            if dist < menor_dist:
                menor_dist = dist
                alvo = inimigo

        if alvo is not None:
            dx = alvo.rect.centerx - self.rect.centerx
            dy = alvo.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)

            alcance_ataque = 70
            if dist > alcance_ataque:
                self.mover_horizontal(1 if dx > 0 else -1, dt, limites)
            else:

                self.direcao = "direita" if dx >= 0 else "esquerda"
                if self.pode_atacar():
                    self.iniciar_ataque(self.tipo_ataque_do_padrao())
        else:

            ax, ay = self._ponto_ancora
            dx = ax - self.x
            if abs(dx) > 8:
                self.mover_horizontal(1 if dx > 0 else -1, dt, limites)
            else:
                if self.estado == "andando":
                    self.estado = "parado"

        return alvo

    def tipo_ataque_do_padrao(self):
        return self.PADROES_POR_FASE.get(self.fase_atual, self.PADROES_POR_FASE[1])["tipo_ataque"]

    def definir_ancora(self, x, y):
        self._ponto_ancora = (x, y)


class Inimigo(Personagem):

    def __init__(self, nome, vida, forca, poder, x, y, pontos=10,
                 pontos_virtude_necessarios=100, tipos_ataque=None, **kwargs):
        super().__init__(nome, vida, forca, poder, x, y, **kwargs)
        self.pontos = pontos
        self.alcance_perseguicao = 420
        self.alcance_ataque = 65
        self.tempo_recarga_ataque = 1.0


        self.pontos_virtude_necessarios = pontos_virtude_necessarios
        self.progresso_virtude = 0.0
        self.tipos_ataque = tipos_ataque or ["ataque1"]

    def atualizar_ia(self, dt, alvos, limites=None):
        if not self.esta_vivo_flag:
            return None

        vivos = [a for a in alvos if a.esta_vivo()]
        if not vivos:
            if self.estado == "andando":
                self.estado = "parado"
            return None

        alvo = min(vivos, key=lambda a: math.hypot(a.rect.centerx - self.rect.centerx,
                                                     a.rect.centery - self.rect.centery))
        dx = alvo.rect.centerx - self.rect.centerx
        dy = alvo.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist <= self.alcance_ataque:
            self.direcao = "direita" if dx >= 0 else "esquerda"
            if self.pode_atacar():
                self.iniciar_ataque(random.choice(self.tipos_ataque))
        elif dist <= self.alcance_perseguicao:
            self.mover_horizontal(1 if dx > 0 else -1, dt, limites)
        else:
            if self.estado == "andando":
                self.estado = "parado"

        return alvo

    def golpe_virtuoso(self, dano, honrado, origem_x=None):
        if not self.esta_vivo_flag or self.tempo_invencivel > 0:
            return False

        self.tempo_invencivel = 0.5
        self.estado = "machucado"
        self.frame_index = 0.0

        if origem_x is not None:
            direcao_recuo = 1 if self.x < origem_x else -1
        else:
            direcao_recuo = -1 if self.direcao == "direita" else 1
        self.recuo_x = direcao_recuo * 180

        if honrado:
            self.progresso_virtude = min(self.pontos_virtude_necessarios,
                                          self.progresso_virtude + dano)


        proporcao_restante = 1 - (self.progresso_virtude / self.pontos_virtude_necessarios)
        self.vida = max(1, round(self.vida_maxima * proporcao_restante))

        if self.progresso_virtude >= self.pontos_virtude_necessarios:
            self.vida = 0
            self.esta_vivo_flag = False
            self.estado = "morrendo"
            self.frame_index = 0.0

        return True


class Jacques(Jogador):
    def __init__(self, nome="Jacques", vida=100, forca=12, poder=8, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y)


class Peralde(Aliado):
    def __init__(self, nome="Peralde", vida=100, forca=10, poder=8, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y)


class Geofrey(Personagem):
    def __init__(self, nome="Geofrey", vida=80, forca=9, poder=6, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y)


class Felipe(Personagem):
    def __init__(self, nome="Felipe", vida=80, forca=9, poder=6, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y)


class Soldado(Inimigo):
    def __init__(self, nome="Soldado Real", vida=45, forca=8, poder=4, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y, pontos=10,
                          pontos_virtude_necessarios=70,
                          tipos_ataque=["ataque1", "ataque2"])
        self.velocidade = 170
        self.tempo_recarga_ataque = 0.9


class Lorde(Inimigo):
    def __init__(self, nome="Lorde Condestável", vida=160, forca=16, poder=10, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y, pontos=100, largura=205, altura=205,
                          pontos_virtude_necessarios=120,
                          tipos_ataque=["ataque1", "ataque2", "ataque3"])
        self.velocidade = 150
        self.tempo_recarga_ataque = 0.85


class ReiFilipeIV(Inimigo):
    def __init__(self, nome="Rei Filipe IV", vida=260, forca=22, poder=16, x=0, y=0):
        super().__init__(nome, vida, forca, poder, x, y, pontos=200, largura=225, altura=225,
                          pontos_virtude_necessarios=200,
                          tipos_ataque=["ataque1", "ataque2", "ataque3", "ataque4"])
        self.velocidade = 195
        self.alcance_perseguicao = 520
        self.alcance_ataque = 75
        self.tempo_recarga_ataque = 0.35
