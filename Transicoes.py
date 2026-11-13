"""
Transições narrativas entre as fases ("As Sete Velas: A Missão DeMolay").

Uma única classe, TransicaoNarrativa, controla as quatro transições: tela preta,
texto centralizado surgindo em fade-in, espera pelo clique do mouse, fade-out.

Os textos abaixo vieram de "transições jogo.md", sem nenhuma alteração.
Parágrafos são separados por "\n\n".
"""
import math

import pygame


TEXTO_TRANSICAO_1 = (
    "Jacques de Molay foi uma figura muito importante da história medieval e ficou conhecido por ser o último Grão-Mestre da Ordem dos Cavaleiros Templários. Sua história é marcada por coragem, lealdade, perseverança e fidelidade aos seus princípios, valores que continuam sendo lembrados até os dias atuais."
)

TEXTO_TRANSICAO_2 = (
    "Com o passar dos anos, destacou-se dentro da Ordem dos cavaleiros templarios por sua dedicação e experiência, até que, em 1292, foi escolhido como Grão-Mestre dos Templários. Durante sua liderança, enfrentou grandes desafios, principalmente com a perda dos territórios cristãos no Oriente e as dificuldades financeiras e políticas enfrentadas pela Ordem.\n\n"
    "O momento mais difícil de sua vida aconteceu em 13 de outubro de 1307, quando o rei Filipe IV, da França, ordenou a prisão de Jacques de Molay e de diversos outros templários. O rei tinha interesse nas riquezas e no poder da Ordem e passou a acusar seus integrantes de heresia, idolatria e outros crimes. Sob tortura e pressão, muitos cavaleiros foram obrigados a confessar crimes que não haviam cometido."
)

TEXTO_TRANSICAO_3 = (
    "Mesmo diante das perseguições, Jacques de Molay permaneceu firme em sua defesa da Ordem. Em 1314, após anos de prisão, foi condenado à morte e queimado na fogueira, em Paris, no dia 18 de março. Segundo relatos históricos, diante da morte, reafirmou sua inocência e a de seus companheiros, demonstrando coragem e fidelidade às suas convicções até o último momento."
)

TEXTO_TRANSICAO_4 = (
    "A história de Jacques de Molay tornou-se um símbolo de resistência diante das injustiças e de fidelidade aos próprios ideais. Sua trajetória representa a importância de manter a honra, a coragem e a lealdade mesmo quando se enfrenta situações difíceis."
)

# Índice 0 = antes da Fase 1, 1 = Fase 1→2, 2 = Fase 2→3, 3 = após vencer a Fase 3.
TEXTOS_TRANSICAO = (
    TEXTO_TRANSICAO_1,
    TEXTO_TRANSICAO_2,
    TEXTO_TRANSICAO_3,
    TEXTO_TRANSICAO_4,
)


def _suavizar(t):
    """Curva suave (smoothstep) para t em [0, 1]."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class TransicaoNarrativa:
    """
    Fluxo (cada etapa só começa quando a anterior termina):

      ESCURECENDO       a cena anterior escurece até ficar toda preta
      TEXTO_APARECENDO  o texto vai de 0% a 100% de opacidade (cliques ignorados)
      AGUARDANDO_CLIQUE o texto fica visível; só um clique do mouse avança
      TEXTO_SUMINDO     o texto desaparece suavemente (cliques ignorados)
      CLAREANDO         a tela preta se dissolve revelando a próxima etapa
      CONCLUIDA         terminou; quem criou a transição deve descartá-la

    ao_ficar_preto: função chamada UMA vez, quando o texto já sumiu e a tela está
    totalmente preta. É o momento de trocar de fase sem o jogador ver o "corte".
    desenhar_cena_nova: função(surface) que desenha a etapa seguinte; usada na fase
    CLAREANDO (o jogo continua congelado até a transição acabar).
    """

    ESCURECENDO = "escurecendo"
    TEXTO_APARECENDO = "texto_aparecendo"
    AGUARDANDO_CLIQUE = "aguardando_clique"
    TEXTO_SUMINDO = "texto_sumindo"
    CLAREANDO = "clareando"
    CONCLUIDA = "concluida"

    # Durações em segundos (ajuste aqui o ritmo da cena).
    DURACAO_ESCURECER = 0.8
    DURACAO_TEXTO_APARECER = 3.0
    DURACAO_TEXTO_SUMIR = 1.0
    DURACAO_CLAREAR = 0.8

    # Dica discreta "Clique para continuar" depois que o texto termina de aparecer.
    # Ponha False para exibir somente o texto da narrativa.
    MOSTRAR_DICA_CLIQUE = True
    TEXTO_DICA = "Clique para continuar"

    COR_TEXTO = (235, 225, 205)
    COR_DICA = (170, 160, 140)
    TAMANHOS_FONTE = (30, 28, 26, 24, 22, 20)  # usa o maior que couber na tela
    MARGEM_LATERAL = 130
    MARGEM_VERTICAL = 90

    def __init__(self, texto, tamanho_tela, fundo_anterior=None,
                 desenhar_cena_nova=None, ao_ficar_preto=None):
        self.largura, self.altura = tamanho_tela
        self.fundo_anterior = fundo_anterior
        self.desenhar_cena_nova = desenhar_cena_nova
        self.ao_ficar_preto = ao_ficar_preto

        self.estado = self.ESCURECENDO
        self._t = 0.0           # tempo dentro da etapa atual
        self._relogio = 0.0     # tempo total (pulsar da dica)
        self._callback_feito = False

        self._veu = pygame.Surface((self.largura, self.altura))
        self._veu.fill((0, 0, 0))

        self._bloco_texto = self._montar_bloco_texto(texto)
        self._dica = self._montar_dica()

    # ------------------------------------------------------------------ estado

    @property
    def ativa(self):
        return self.estado != self.CONCLUIDA

    def _ir_para(self, novo_estado):
        self.estado = novo_estado
        self._t = 0.0

    def avancar(self):
        """Pedido de avanço (mouse, controle ou celular). Só vale com o texto 100% visível,
        e só uma vez: depois do primeiro pedido a etapa muda e os seguintes são ignorados."""
        if self.estado == self.AGUARDANDO_CLIQUE:
            self._ir_para(self.TEXTO_SUMINDO)

    def tratar_eventos(self, eventos):
        """Avançam: clique esquerdo do mouse ou botão 0 do controle (o mesmo do ataque)."""
        for evento in eventos:
            mouse = evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
            controle = evento.type == pygame.JOYBUTTONDOWN and evento.button == 0
            if mouse or controle:
                self.avancar()

    def atualizar(self, dt):
        dt = min(dt, 0.05)  # evita saltos nos fades se a janela travar por um instante
        self._t += dt
        self._relogio += dt

        if self.estado == self.ESCURECENDO and self._t >= self.DURACAO_ESCURECER:
            self._ir_para(self.TEXTO_APARECENDO)
        elif self.estado == self.TEXTO_APARECENDO and self._t >= self.DURACAO_TEXTO_APARECER:
            self._ir_para(self.AGUARDANDO_CLIQUE)
        elif self.estado == self.TEXTO_SUMINDO and self._t >= self.DURACAO_TEXTO_SUMIR:
            self._ir_para(self.CLAREANDO)
            if not self._callback_feito:
                self._callback_feito = True
                if self.ao_ficar_preto is not None:
                    self.ao_ficar_preto()
        elif self.estado == self.CLAREANDO and self._t >= self.DURACAO_CLAREAR:
            self._ir_para(self.CONCLUIDA)

    # ----------------------------------------------------------------- desenho

    def _opacidade_texto(self):
        """0.0 a 1.0 conforme a etapa."""
        if self.estado == self.TEXTO_APARECENDO:
            return _suavizar(self._t / self.DURACAO_TEXTO_APARECER)
        if self.estado == self.AGUARDANDO_CLIQUE:
            return 1.0
        if self.estado == self.TEXTO_SUMINDO:
            return 1.0 - _suavizar(self._t / self.DURACAO_TEXTO_SUMIR)
        return 0.0

    def desenhar(self, surface):
        if self.estado == self.CONCLUIDA:
            return

        if self.estado == self.ESCURECENDO:
            if self.fundo_anterior is not None:
                surface.blit(self.fundo_anterior, (0, 0))
            else:
                surface.fill((0, 0, 0))
            self._desenhar_veu(surface, _suavizar(self._t / self.DURACAO_ESCURECER))
            return

        if self.estado == self.CLAREANDO:
            if self.desenhar_cena_nova is not None:
                self.desenhar_cena_nova(surface)
            else:
                surface.fill((0, 0, 0))
            self._desenhar_veu(surface, 1.0 - _suavizar(self._t / self.DURACAO_CLAREAR))
            return

        # Texto aparecendo / aguardando / sumindo: tela completamente preta.
        surface.fill((0, 0, 0))
        opacidade = self._opacidade_texto()
        self._bloco_texto.set_alpha(int(255 * opacidade))
        surface.blit(self._bloco_texto, self._bloco_texto.get_rect(
            center=(self.largura // 2, self.altura // 2)))
        self._desenhar_dica(surface, opacidade)

    def _desenhar_veu(self, surface, opacidade):
        if opacidade <= 0:
            return
        self._veu.set_alpha(int(255 * opacidade))
        surface.blit(self._veu, (0, 0))

    def _desenhar_dica(self, surface, opacidade_texto):
        if not self.MOSTRAR_DICA_CLIQUE or self._dica is None:
            return
        if self.estado == self.AGUARDANDO_CLIQUE:
            entrada = _suavizar(self._t / 0.8)
            pulso = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(self._relogio * 3))
            alpha = entrada * pulso
        elif self.estado == self.TEXTO_SUMINDO:
            alpha = opacidade_texto * 0.65
        else:
            return
        self._dica.set_alpha(int(255 * alpha))
        surface.blit(self._dica, self._dica.get_rect(
            center=(self.largura // 2, self.altura - 45)))

    # ------------------------------------------------------ preparo do texto

    @staticmethod
    def _criar_fonte(tamanho, italico=False):
        try:
            return pygame.font.SysFont("Georgia", tamanho, italic=italico)
        except Exception:
            return pygame.font.Font(None, tamanho + 10)

    @staticmethod
    def _quebrar_linhas(texto, fonte, largura_max):
        """Quebra por palavras; devolve lista de parágrafos, cada um uma lista de linhas."""
        paragrafos = []
        for paragrafo in texto.split("\n\n"):
            linhas, atual = [], ""
            for palavra in paragrafo.split():
                tentativa = f"{atual} {palavra}" if atual else palavra
                if atual and fonte.size(tentativa)[0] > largura_max:
                    linhas.append(atual)
                    atual = palavra
                else:
                    atual = tentativa
            if atual:
                linhas.append(atual)
            paragrafos.append(linhas)
        return paragrafos

    def _montar_bloco_texto(self, texto):
        """Renderiza o texto inteiro UMA vez numa superfície transparente (só varia o alpha)."""
        largura_max = self.largura - 2 * self.MARGEM_LATERAL
        altura_max = self.altura - 2 * self.MARGEM_VERTICAL

        for tamanho in self.TAMANHOS_FONTE:
            fonte = self._criar_fonte(tamanho)
            altura_linha = fonte.get_linesize()
            espaco_paragrafo = int(altura_linha * 0.8)
            paragrafos = self._quebrar_linhas(texto, fonte, largura_max)
            n_linhas = sum(len(p) for p in paragrafos)
            altura_total = n_linhas * altura_linha + espaco_paragrafo * (len(paragrafos) - 1)
            if altura_total <= altura_max:
                break  # coube; se nenhum couber, fica com o menor

        bloco = pygame.Surface((largura_max, altura_total), pygame.SRCALPHA)
        y = 0
        for i, linhas in enumerate(paragrafos):
            for linha in linhas:
                img = fonte.render(linha, True, self.COR_TEXTO)
                bloco.blit(img, img.get_rect(midtop=(largura_max // 2, y)))
                y += altura_linha
            if i < len(paragrafos) - 1:
                y += espaco_paragrafo
        return bloco

    def _montar_dica(self):
        if not self.MOSTRAR_DICA_CLIQUE:
            return None
        return self._criar_fonte(18, italico=True).render(self.TEXTO_DICA, True, self.COR_DICA)
