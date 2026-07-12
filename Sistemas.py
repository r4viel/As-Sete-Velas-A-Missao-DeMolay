

import os
import pygame
from Classes import Soldado, Lorde, ReiFilipeIV

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_IMG = os.path.join(DIR_BASE, "IMG")


def ataque_pelas_costas(atacante, alvo):
    if alvo.direcao == "direita":

        return atacante.rect.centerx < alvo.rect.centerx
    else:

        return atacante.rect.centerx > alvo.rect.centerx


class SistemaVirtude:

    VIRTUDE_MAXIMA = 100
    CUSTO_ATAQUE_PELAS_COSTAS = 10
    GANHO_ATAQUE_HONRADO = 3
    GANHO_DERROTAR_INIMIGO = 8


    EXIGENCIA_POR_FASE = {1: 40, 2: 55, 3: 70}

    def __init__(self):
        self.pontos = self.VIRTUDE_MAXIMA
        self.velas_acesas = 0

    def perder(self, quantidade=CUSTO_ATAQUE_PELAS_COSTAS):
        self.pontos = max(0, self.pontos - quantidade)

    def ganhar(self, quantidade=GANHO_ATAQUE_HONRADO):
        self.pontos = min(self.VIRTUDE_MAXIMA, self.pontos + quantidade)

    def registrar_golpe(self, atacante, alvo):
        if ataque_pelas_costas(atacante, alvo):
            self.perder()
            return "pelas_costas"
        else:
            self.ganhar()
            return "honrado"

    def registrar_derrota_inimigo(self, inimigo_atacado_pelas_costas=False):
        if not inimigo_atacado_pelas_costas:
            self.ganhar(self.GANHO_DERROTAR_INIMIGO)
            self.velas_acesas = min(7, self.velas_acesas + 1)

    def pode_avancar(self, fase):
        exigencia = self.EXIGENCIA_POR_FASE.get(fase, 50)
        return self.pontos >= exigencia

    def esgotada(self):
        return self.pontos <= 0

    def exigencia_atual(self, fase):
        return self.EXIGENCIA_POR_FASE.get(fase, 50)


class Fase:

    def __init__(self, numero, nome, arquivo_fundo, fabrica_inimigos):
        self.numero = numero
        self.nome = nome
        self.arquivo_fundo = arquivo_fundo
        self._fabrica_inimigos = fabrica_inimigos
        self._fundo_original = None

    def carregar_fundo(self, largura, altura):
        caminho = os.path.join(DIR_IMG, self.arquivo_fundo)
        try:
            img = pygame.image.load(caminho).convert()
            return pygame.transform.scale(img, (largura, altura))
        except Exception as e:
            print(f"Erro ao carregar fundo da fase '{self.nome}' ({caminho}): {e}")
            fundo = pygame.Surface((largura, altura))
            fundo.fill((40, 0, 40))
            return fundo

    def criar_inimigos(self):
        return self._fabrica_inimigos()


class GerenciadorFases:

    ESTADO_COMBATE = "combate"
    ESTADO_VIRTUDE_INSUFICIENTE = "virtude_insuficiente"
    ESTADO_TRANSICAO = "transicao"
    ESTADO_VITORIA = "vitoria"
    ESTADO_DERROTA = "derrota"

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura

        self.fases = [
            Fase(1, "O Templo", "templo.png", self._inimigos_fase_1),
            Fase(2, "A Masmorra", "masmorra.png", self._inimigos_fase_2),
            Fase(3, "A Fogueira", "fogueira.png", self._inimigos_fase_3),
        ]

        self.indice_fase = 0
        self.inimigos = []
        self.fundo_atual = None
        self.estado = self.ESTADO_COMBATE
        self.timer_transicao = 0.0
        self.mensagem = ""

        self._carregar_fase_atual()


    def _inimigos_fase_1(self):


        return [
            Soldado(x=self.largura * 0.72, y=self.altura * 0.55),
        ]

    def _inimigos_fase_2(self):

        return [
            Lorde(x=self.largura * 0.72, y=self.altura * 0.55),
        ]

    def _inimigos_fase_3(self):

        return [
            ReiFilipeIV(x=self.largura * 0.72, y=self.altura * 0.55),
        ]


    @property
    def fase(self):
        return self.fases[self.indice_fase]

    @property
    def numero_fase(self):
        return self.fase.numero

    def _carregar_fase_atual(self):
        fase = self.fase
        self.fundo_atual = fase.carregar_fundo(self.largura, self.altura)
        self.inimigos = fase.criar_inimigos()
        self.estado = self.ESTADO_COMBATE
        self.mensagem = f"Fase {fase.numero}: {fase.nome}"

    def todos_inimigos_derrotados(self):
        return all(not inimigo.esta_vivo() for inimigo in self.inimigos)

    def eh_ultima_fase(self):
        return self.indice_fase >= len(self.fases) - 1

    def atualizar(self, dt, sistema_virtude):
        if self.estado == self.ESTADO_TRANSICAO:
            self.timer_transicao -= dt
            if self.timer_transicao <= 0:
                if self.eh_ultima_fase():
                    self.estado = self.ESTADO_VITORIA
                else:
                    self.indice_fase += 1
                    self._carregar_fase_atual()
            return

        if sistema_virtude.esgotada():
            self.estado = self.ESTADO_DERROTA
            self.mensagem = "As velas se apagaram... a virtude se esgotou."
            return

        if self.todos_inimigos_derrotados():
            if sistema_virtude.pode_avancar(self.numero_fase):
                self.estado = self.ESTADO_TRANSICAO
                self.timer_transicao = 2.0
                if self.eh_ultima_fase():
                    self.mensagem = "Todas as velas acesas! Vitória!"
                else:
                    self.mensagem = "Fase concluída! Avançando..."
            else:
                self.estado = self.ESTADO_VIRTUDE_INSUFICIENTE
                exigido = sistema_virtude.exigencia_atual(self.numero_fase)
                self.mensagem = (f"Virtude insuficiente para avançar "
                                  f"({sistema_virtude.pontos}/{exigido}). "
                                  f"Lute com honra para recuperar virtude!")
        else:
            self.estado = self.ESTADO_COMBATE

    def desenhar_fundo(self, surface):
        if self.fundo_atual:
            surface.blit(self.fundo_atual, (0, 0))

    def inimigos_vivos(self):
        return [i for i in self.inimigos if i.esta_vivo()]
