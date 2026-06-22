# classeDosPersonagens
class Personagem:
    def __init__(self, nome, vida, forca, poder, x, y):
        self.nome = nome
        self.vida = vida
        self.forca = forca
        self.poder = poder
        self.x = x
        self.y = y

    def mover(self, direcao):
        if direcao == 'cima':
            self.y -= 10
        elif direcao == 'baixo':
            self.y += 10
        elif direcao == 'esquerda':
            self.x -= 10
        elif direcao == 'direita':
            self.x += 10

class Jacques(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

class Peralde(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

class Geofrey(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

class Felipe(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

class Lorde(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

class Soldado(Personagem):
    def __init__(self, nome, vida, forca, poder, x, y):
        super().__init__(nome, vida, forca, poder, x, y)

