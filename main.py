import pygame
import sys
import webbrowser
from pathlib import Path

pygame.init()
pygame.mixer.init()

# ------------------- Config general -------------------
WIDTH, HEIGHT = 900, 560
TITLE = "launcher feria ISB 2025 - Mi carrera ideal"
FPS = 60
BG_COLOR = (18, 18, 24)

# Intenta cargar un sonido de clic si existe
CLICK_SOUND = None
if Path("assts/click.wav").exits():
    CLICK_SOUND = pygame.mixer.Sound("assts/click.wav")
    
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Montserrat", 26)
Font_Small = pygame.font.SysFont("Montserrat", 20)
Font_Big = pygame.font.SysFont("Montserrat", 40, bold=True)

# ------------------- Utilidades -------------------
def play_click():
    if CLICK_SOUND:
        CLICK_SOUND.play()

def draw_text(surf, text, font, color, center):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surf.blit(img, rect)
    
def load_image(path, size=None, fallback_color=(60, 60, 80)):
    """Carga una imagen si existe. Si no, devuelve un surface de color"""
    if Path(path).exists():
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smothscale(img, size)
        return img
    # Fallback
    surf = pygame.Surface(size if size else (160, 160), pygame.SRCALPHA)
    surf.fill(fallback_color)
    pygame.draw.rect(surf, (100, 100, 140), surf.get_rect(), border_radius=16)
    return surf

# ------------------- Modelo de datos -------------------
UNIVERSIDADES = [
    {
        "nombre": "UVM",
        "área": "Ingeniera"
        "url": "https://uvm.mx/",
        "img": "assets/uvm.png",
        "resumen": "Su oferta en licenciaturas de ingeniería es amplica y muy buena, debido a las becas y costos que tiene, al igual que su buen desarrollo en estas"
    },
]
# Precarga de imágenes (con fallback)
for u in UNIVERSIDADES:
    u["image_surf"] = load_image(u["img"], size=(160, 160))

# ------------------- UI: Botón -------------------
class Button:
    def __init__(self, text, x, y, w, h, on_click, *,
                 bg=(45, 45, 60), fg=(240, 240, 250),
                 bg_hover=(70, 70, 100)):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.bg_hover = bg_hover
        self.hover = False
        
    def draw(self, surf):
        color = self.bg_hover if self.hover else self.bg
        pygame.draw.rect(surf, color, self.rect, border_radius=2)
        pygame.draw.rect(surf, (90, 90, 130), self.rect, width=2, border_radius=12)
        draw_text(surf, self.text, FONT, self.fg, self.rect.center)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_click()
                self.on_click()
                
# ------------- Escenas -------------------
class Scene:
    def hanle(self, event): ...
    def update(self, dt): ...
    def draw(self, surf): ...
    
class Splash(Scene):
    def __init__(self, next_scene_callback):
        self.time = 0
        self.duration = 1.8 # seg
        self.next_scene_callback = next_scene_callback
        self.logo = load_image("assets/isb.png", size=(2230, 220), fallback_color=(30 , 30, 50))
        
    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.next_scene_callback(Menu())
            
    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Feria de Universidaddes ISB 2025", Font_Big, (230, 230, 245), (WIDTH//2, 70))
            