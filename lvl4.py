#Lvl 4


import os
import random
import sys
import pygame
pygame.init()
# ---------- Configuración ----------
ANCHO, ALTO = 900, 450   # ventana más alta
SUELO = 360
FPS = 60
ESCALA = 1     # 1 = tamaño normal (900x450); súbelo si quieres todo más grande
FONDO = (247, 247, 247)
COLOR = (83, 83, 83)
GRAVEDAD = 0.8
FUERZA_SALTO = -15
ARCHIVO_RECORD = "dino_record.txt"
ventana = pygame.display.set_mode((int(ANCHO * ESCALA), int(ALTO * ESCALA)), pygame.RESIZABLE)
pantalla = pygame.Surface((ANCHO, ALTO))   # lienzo lógico; se escala a la ventana
pygame.display.set_caption("Dino Runner")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("couriernew", 20, bold=True)
fuente_grande = pygame.font.SysFont("couriernew", 30, bold=True)

def cargar_record():
    try:
        with open(ARCHIVO_RECORD) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0

def guardar_record(valor):
    try:
        with open(ARCHIVO_RECORD, "w") as f:
            f.write(str(int(valor)))
    except OSError:
        pass

# ---------- Clases ----------
def cargar_sprite(nombre):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre)
    try:
        return pygame.image.load(ruta).convert_alpha()
    except (pygame.error, FileNotFoundError):
        sys.exit(f"No encuentro '{nombre}'. Ponlo en la misma carpeta que este script.")

vikingo = cargar_sprite("player.png")
SPRITE_DE_PIE = pygame.transform.smoothscale(vikingo, (57, 64))
SPRITE_AGACHADO = pygame.transform.smoothscale(vikingo, (72, 38))   # aplastado = agachado

class Dino:
    X = 60
    def __init__(self):
        self.y = 0            # desplazamiento vertical (0 = en el suelo, negativo = en el aire)
        self.vy = 0
        self.agachado = False
        self.paso = 0
    def saltar(self):
        if self.y == 0 and not self.agachado:
            self.vy = FUERZA_SALTO
    def agachar(self, valor):
        self.agachado = valor
        if valor and self.y < 0:
            self.vy = max(self.vy, 8)   # caída rápida
    def actualizar(self):
        self.vy += GRAVEDAD
        self.y += self.vy
        if self.y >= 0:
            self.y = 0
            self.vy = 0
        self.paso += 1
    @property
    def rect(self):
        if self.agachado and self.y == 0:
            return pygame.Rect(self.X, SUELO - 38, 72, 38)
        return pygame.Rect(self.X, SUELO - 64 + self.y, 57, 64)
    def dibujar(self, surf):
        r = self.rect
        if self.agachado and self.y == 0:
            surf.blit(SPRITE_AGACHADO, r)
        else:
            # pequeño rebote al correr para dar sensación de pasos
            rebote = 2 if (self.y == 0 and (self.paso // 6) % 2) else 0
            surf.blit(SPRITE_DE_PIE, (r.x, r.y - rebote))

class Cactus:
    def __init__(self, x):
        self.n = random.randint(1, 3)
        h = random.randint(30, 55)
        self.rect = pygame.Rect(x, SUELO - h, 16 * self.n, h)
    def mover(self, vel):
        self.rect.x -= vel
    def dibujar(self, surf):
        r = self.rect
        for i in range(self.n):
            x = r.x + i * 16
            Cactus = cargar_sprite("obstacle.jpeg")

class Pajaro:
    def __init__(self, x):
        # alto -> hay que agacharse; bajo -> hay que saltar
        y = SUELO - 70 if random.random() < 0.6 else SUELO - 45
        self.rect = pygame.Rect(x, y, 42, 26)
        self.t = 0

    def mover(self, vel):
        self.rect.x -= vel
        self.t += 1

    def dibujar(self, surf):
        r = self.rect
        arriba = (self.t // 10) % 2 == 0
        pygame.draw.rect(surf, COLOR, (r.x + 6, r.y + 10, 30, 8))
        pygame.draw.rect(surf, COLOR, (r.x, r.y + 12, 8, 4))
        pygame.draw.rect(surf, COLOR, (r.x + 30, r.y + 8, 12, 6))
        ala_y = r.y if arriba else r.y + 18
        pygame.draw.rect(surf, COLOR, (r.x + 12, ala_y, 14, 8))

# ---------- Juego ----------
def nueva_partida():
    return {
        "dino": Dino(),
        "obstaculos": [],
        "dist": 0.0,
        "vel": 6.0,
        "proximo": 60,
        "nubes": [[200, 80], [600, 150]],
        "muerto": False,
        "empezado": False,
        "t": 0,
    }

def texto_centrado(txt, fnt, y):
    img = fnt.render(txt, True, COLOR)
    pantalla.blit(img, img.get_rect(center=(ANCHO // 2, y)))

def main():
    record = cargar_record()
    s = nueva_partida()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key in (pygame.K_SPACE, pygame.K_UP):
                    if s["muerto"]:
                        s = nueva_partida()
                    s["empezado"] = True
                    s["dino"].saltar()
                if e.key == pygame.K_DOWN:
                    s["dino"].agachar(True)
            if e.type == pygame.KEYUP and e.key == pygame.K_DOWN:
                s["dino"].agachar(False)
        dino = s["dino"]
        # ----- actualizar -----
        if s["empezado"] and not s["muerto"]:
            s["t"] += 1
            s["dist"] += s["vel"] * 0.1
            s["vel"] = min(16, 6 + s["dist"] / 150)
            dino.actualizar()
            s["proximo"] -= 1
            if s["proximo"] <= 0:
                if random.random() < 0.3 and s["dist"] > 40:
                    s["obstaculos"].append(Pajaro(ANCHO + 20))
                else:
                    s["obstaculos"].append(Cactus(ANCHO + 20))
                s["proximo"] = max(40, (70 + random.random() * 70) * (6 / s["vel"]) + 30)
            for o in s["obstaculos"]:
                o.mover(s["vel"])
            s["obstaculos"] = [o for o in s["obstaculos"] if o.rect.right > -10]
            for n in s["nubes"]:
                n[0] -= s["vel"] * 0.2
                if n[0] < -60:
                    n[0] = ANCHO + 40
                    n[1] = random.randint(60, 220)
            caja = dino.rect.inflate(-24, -16)
            for o in s["obstaculos"]:
                if caja.colliderect(o.rect.inflate(-6, -6)):
                    s["muerto"] = True
                    if s["dist"] > record:
                        record = s["dist"]
                        guardar_record(record)
        # ----- dibujar -----
        pantalla.fill(FONDO)
        pygame.draw.rect(pantalla, COLOR, (0, SUELO, ANCHO, 2))
        for i in range(20):
            x = (i * 53 - s["dist"] * 10) % ANCHO
            pygame.draw.rect(pantalla, COLOR, (x, SUELO + 8 + (i % 5) * 14, 8 + (i % 4) * 4, 2))
        for n in s["nubes"]:
            pygame.draw.rect(pantalla, (200, 200, 200), (n[0], n[1], 50, 10))
            pygame.draw.rect(pantalla, (200, 200, 200), (n[0] + 10, n[1] - 8, 28, 8))
        dino.dibujar(pantalla)
        for o in s["obstaculos"]:
            o.dibujar(pantalla)
        marcador = fuente.render(f"REC {int(record):05d}  {int(s['dist']):05d}", True, COLOR)
        pantalla.blit(marcador, (ANCHO - marcador.get_width() - 16, 16))
        if not s["empezado"]:
            texto_centrado("Pulsa ESPACIO para empezar", fuente, 170)
        if s["muerto"]:
            texto_centrado("FIN DEL JUEGO", fuente_grande, 160)
            texto_centrado("ESPACIO para reintentar", fuente, 195)
        # escalar el lienzo a la ventana manteniendo la proporción
        vw, vh = ventana.get_size()
        k = min(vw / ANCHO, vh / ALTO)
        tam = (int(ANCHO * k), int(ALTO * k))
        ventana.fill(FONDO)
        ventana.blit(pygame.transform.scale(pantalla, tam),
                     ((vw - tam[0]) // 2, (vh - tam[1]) // 2))
        pygame.display.flip()
        reloj.tick(FPS)
if __name__ == "__main__":
    main()
