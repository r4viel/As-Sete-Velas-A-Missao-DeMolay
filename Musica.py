import os
import pygame

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_AUDIO = os.path.join(DIR_BASE, "AUDIO")

# Um trecho diferente de "The Iron Vow" para cada fase.
#   Fase 1 (Templo)   -> build-up da música
#   Fase 2 (Masmorra) -> trecho mais sombrio que vai crescendo
#   Fase 3 (Fogueira) -> clímax, a parte mais pesada
MUSICA_POR_FASE = {
    1: "fase1_templo.ogg",
    2: "fase2_masmorra.ogg",
    3: "fase3_fogueira.ogg",
}


class MusicaCombate:
    """Toca o trecho da fase só enquanto há luta; some e volta com fade suave.

    O fade é feito pelo volume, quadro a quadro (pygame.mixer.music.fadeout
    bloquearia o laço do jogo). Se não houver placa de som ou o arquivo
    faltar, o jogo segue normalmente, só que sem música.
    """

    VOLUME = 0.55
    FADE_IN = 1.2     # segundos
    FADE_OUT = 0.8    # segundos

    def __init__(self):
        self.ok = False
        self.tocando = None      # nº da fase cujo trecho está carregado
        self.desejada = None     # nº da fase que deveria estar tocando (None = silêncio)
        self.volume = 0.0
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.ok = True
        except pygame.error as e:
            print(f"[música] áudio indisponível: {e}")

    def definir(self, numero_fase):
        """Informa qual fase deve tocar agora (None para silêncio)."""
        self.desejada = numero_fase

    def atualizar(self, dt):
        if not self.ok:
            return

        # Trecho errado/ligado quando deveria estar em silêncio: abaixa o volume primeiro.
        if self.tocando is not None and self.tocando != self.desejada:
            self.volume = max(0.0, self.volume - dt * self.VOLUME / self.FADE_OUT)
            pygame.mixer.music.set_volume(self.volume)
            if self.volume <= 0.0:
                pygame.mixer.music.stop()
                self.tocando = None
            return

        # Nada carregado e há uma fase para tocar: carrega o trecho e começa do volume 0.
        if self.tocando is None and self.desejada is not None:
            arquivo = MUSICA_POR_FASE.get(self.desejada)
            if arquivo is None:
                return
            try:
                pygame.mixer.music.load(os.path.join(DIR_AUDIO, arquivo))
                self.volume = 0.0
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.play(-1)   # loop infinito enquanto a luta durar
                self.tocando = self.desejada
            except pygame.error as e:
                print(f"[música] não foi possível tocar {arquivo}: {e}")
                self.desejada = None
            return

        # Já está tocando o trecho certo: sobe até o volume final.
        if self.tocando is not None and self.volume < self.VOLUME:
            self.volume = min(self.VOLUME, self.volume + dt * self.VOLUME / self.FADE_IN)
            pygame.mixer.music.set_volume(self.volume)

    def parar(self):
        self.desejada = None
