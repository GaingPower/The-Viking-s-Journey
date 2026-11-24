# lvl 1 - Platformer infinito
import os
import sys
import random
import pygame

# =====================================================================
#                      CONFIGURACIÓN (cambia solo esto)
# =====================================================================

PUNTOS = 0

# --- Pantalla ---
ANCHO, ALTO = 1282, 750
FPS = 60

# --- Imágenes (en la misma carpeta que este archivo) ---
RUTA_PERSONAJE = "player.png"
TAM_PERSONAJE = (75, 75)            # (ancho, alto) en VENTANA
FONDOS = ["fondo1.png"]             # puedes poner varios: ["fondo1.png", "fondo2.png"]
SEGUNDOS_CAMBIO_FONDO = None        # None = no cambia; 10 = cambia de fondo cada 10 s
PARALLAX = 0.3                      # 0 = fondo fijo, 1 = se mueve igual que el nivel

# --- Física del jugador ---
GRAVEDAD = 0.6
VEL_MOVIMIENTO = 5
FUERZA_SALTO = -20                  # más negativo = salta más alto
VEL_MAX_CAIDA = 15
SALTOS_MAXIMOS = 1                  # 2 = doble salto, 3 = triple, etc.

# --- Nivel ---
LIMITE_NIVEL = None                 # None = INFINITO; o un número, ej: 5000 (píxeles)
SEMILLA = None                      # None = nivel distinto cada vez; un número = siempre el mismo
GROSOR_SUELO = 70
ANCHO_SEGMENTO = 400                # largo de cada "trozo" de nivel que se genera

PROB_HUECO = 0.5                    # 0 a 1: probabilidad de agujero en el suelo (ej: 0.2)
ANCHO_HUECO = 150

PROB_PLATAFORMA = 1              # 0 a 1: probabilidad de plataforma en cada trozo
PLAT_ANCHO_MIN, PLAT_ANCHO_MAX = 120, 220
PLAT_ALTURA_MIN, PLAT_ALTURA_MAX = 100, 300   # altura sobre el suelo
PLAT_GROSOR = 20

TITULO = "The Viking's Journey"
PIXELES_POR_PUNTO = 500        # 1 punto cada 100 px que avanzas

# --- Colores ---
COLOR_FONDO_SIN_IMAGEN = (110, 180, 235)
COLOR_PLATAFORMA = (90, 60, 40)
COLOR_CESPED = (60, 160, 70)
COLOR_JUGADOR_SIN_IMAGEN = (220, 60, 60)
R_PRESS = False

# =====================================================================

DIR = os.path.dirname(os.path.abspath(__file__))
INFINITO = float("inf")


def cargar_imagen(nombre, tam, alpha=True):
    """Carga y escala una imagen. Devuelve None si no existe."""
    ruta = os.path.join(DIR, nombre)
    if not os.path.exists(ruta):
        print(f"[Aviso] No se encontró '{nombre}'. Se usará un reemplazo.")
        return None
    img = pygame.image.load(ruta)
    img = img.convert_alpha() if alpha else img.convert()
    return pygame.transform.smoothscale(img, tam)


class Nivel:
    """Genera plataformas a medida que el jugador avanza."""

    def __init__(self):
        if SEMILLA is not None:
            random.seed(SEMILLA)
        self.rects = []
        self.x = 0                                   # hasta dónde se ha generado
        self.limite = LIMITE_NIVEL or INFINITO

    def generar(self, hasta_x):
        suelo_y = ALTO - GROSOR_SUELO
        while self.x < min(hasta_x, self.limite):
            ancho = int(min(ANCHO_SEGMENTO, self.limite - self.x))
            primero = self.x == 0

            # Suelo (con hueco opcional, nunca en el primer trozo)
            hueco = ANCHO_HUECO if (not primero and random.random() < PROB_HUECO) else 0
            if ancho - hueco > 0:
                self.rects.append(pygame.Rect(self.x + hueco, suelo_y, ancho - hueco, GROSOR_SUELO))

            # Plataforma flotante opcional
            if not primero and random.random() < PROB_PLATAFORMA:
                w = random.randint(PLAT_ANCHO_MIN, PLAT_ANCHO_MAX)
                px = self.x + random.randint(0, max(0, ancho - w))
                py = suelo_y - random.randint(PLAT_ALTURA_MIN, PLAT_ALTURA_MAX)
                self.rects.append(pygame.Rect(px, py, w, PLAT_GROSOR))

            self.x += ancho

    def limpiar(self, camara_x):
        """Borra lo que ya quedó muy atrás para no gastar memoria."""
        self.rects = [r for r in self.rects if r.right > camara_x - ANCHO]


class Jugador:
    def __init__(self, imagen):
        self.imagen = imagen
        self.rect = pygame.Rect(0, 0, *TAM_PERSONAJE)
        self.reiniciar()

    def reiniciar(self):
        self.rect.topleft = (100, ALTO - GROSOR_SUELO - TAM_PERSONAJE[1])
        self.vel_x = self.vel_y = 0
        self.saltos = SALTOS_MAXIMOS
        self.mirando_derecha = True

    def saltar(self):
        if self.saltos > 0:
            self.vel_y = FUERZA_SALTO
            self.saltos -= 1

    def actualizar(self, rects):
        # Teclado
        teclas = pygame.key.get_pressed()
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VEL_MOVIMIENTO
            self.mirando_derecha = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VEL_MOVIMIENTO
            self.mirando_derecha = True

        # Horizontal
        self.rect.x += self.vel_x
        for r in rects:
            if self.rect.colliderect(r):
                if self.vel_x > 0:
                    self.rect.right = r.left
                else:
                    self.rect.left = r.right
        self.rect.left = max(self.rect.left, 0)
        if LIMITE_NIVEL:
            self.rect.right = min(self.rect.right, LIMITE_NIVEL)

        # Vertical
        self.vel_y = min(self.vel_y + GRAVEDAD, VEL_MAX_CAIDA)
        self.rect.y += int(self.vel_y)
        for r in rects:
            if self.rect.colliderect(r):
                if self.vel_y > 0:                   # cayendo: aterriza
                    self.rect.bottom = r.top
                    self.saltos = SALTOS_MAXIMOS

                else:                                # golpea el techo
                    self.rect.top = r.bottom
                self.vel_y = 0

    def cayo_al_vacio(self):
        return self.rect.top > ALTO + 200

    def dibujar(self, VENTANA, camara_x):
        pos = (self.rect.x - camara_x, self.rect.y)
        if self.imagen:
            img = self.imagen if self.mirando_derecha else pygame.transform.flip(self.imagen, True, False)
            VENTANA.blit(img, pos)
        else:
            pygame.draw.rect(VENTANA, COLOR_JUGADOR_SIN_IMAGEN, (*pos, *self.rect.size))


def dibujar_fondo(VENTANA, fondos, camara_x):
    if not fondos:
        VENTANA.fill(COLOR_FONDO_SIN_IMAGEN)
        return
    indice = 0
    if SEGUNDOS_CAMBIO_FONDO:
        indice = int(pygame.time.get_ticks() / 1000 / SEGUNDOS_CAMBIO_FONDO) % len(fondos)
    desplazamiento = int(-camara_x * PARALLAX) % ANCHO
    VENTANA.blit(fondos[indice], (desplazamiento, 0))
    VENTANA.blit(fondos[indice], (desplazamiento - ANCHO, 0))


def main():
    pygame.init()
    VENTANA = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO)
    reloj = pygame.time.Clock()

    fondos = [f for f in (cargar_imagen(n, (ANCHO, ALTO), alpha=False) for n in FONDOS) if f]
    jugador = Jugador(cargar_imagen(RUTA_PERSONAJE, TAM_PERSONAJE))
    nivel = Nivel()

    puntos = 0
    pygame.display.set_caption(f"{TITULO}      PT = {puntos}")

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    jugador.saltar()
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Cámara
        camara_x = max(0, jugador.rect.centerx - ANCHO // 2)
        if LIMITE_NIVEL:
            camara_x = max(0, min(camara_x, LIMITE_NIVEL - ANCHO))

        # Generar delante, borrar detrás
        nivel.generar(camara_x + ANCHO * 2)
        nivel.limpiar(camara_x)

        jugador.actualizar(nivel.rects)

        nuevos_puntos = jugador.rect.x // PIXELES_POR_PUNTO
        if nuevos_puntos > puntos:
            puntos = nuevos_puntos
            pygame.display.set_caption(f"{TITULO}      PT = {puntos}")

        if jugador.cayo_al_vacio():       # reinicia el nivel
            nivel = Nivel()
            jugador.reiniciar()
            puntos = 0
            pygame.display.set_caption(f"{TITULO}      PT = {puntos}")

        # Dibujo
        dibujar_fondo(VENTANA, fondos, camara_x)
        for r in nivel.rects:
            rd = r.move(-camara_x, 0)
            if rd.right > 0 and rd.left < ANCHO:
                pygame.draw.rect(VENTANA, COLOR_PLATAFORMA, rd)
                pygame.draw.rect(VENTANA, COLOR_CESPED, (rd.x, rd.y, rd.width, 6))
        jugador.dibujar(VENTANA, camara_x)

        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    main()
