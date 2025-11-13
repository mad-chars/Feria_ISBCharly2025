import pygame
import sys
import webbrowser
from pathlib import Path
import traceback

pygame.init()
pygame.mixer.init()

# ------------------- Config general -------------------
WIDTH, HEIGHT = 900, 560
TITLE = "Launcher Feria ISB 2025 - Mi carrera ideal"
FPS = 60
BG_COLOR = (18, 18, 24)

# Intenta cargar un sonido de clic si existe
CLICK_SOUND = None
if Path("assets/click.mp3").exists():
    CLICK_SOUND = pygame.mixer.Sound("assets/click.mp3")
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
            img = pygame.transform.smoothscale(img, size)
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
        "area": "Ingeniera en Sistemas Computacionales",
        "url": "https://uvm.mx/",
        "img": "assets/uvm.png",
        "resumen": "Su oferta en licenciaturas de ingeniería es amplica y muy buena, debido a las becas y costos que tiene, al igual que su buen desarrollo en estas. Esto y en como tienen su plan de estudio y lo que ofrecen aparte de la licenciatura."
    },
    {
        "nombre": "UP",
        "area": "Ingeniería en Inteligencia de Datos y Ciberseguridad",
        "url": "https://www.up.edu.mx/",
        "img": "assets/up.png",
        "resumen": "La Universidad Panamericana es una institución educativa privada en México que ofrece programas académicos de alta calidad, incluyendo ingeniería en inteligencia de datos y ciberseguridad pero con ofertas un poco limitadas, donde es muy buena opción para este pido de carreras pero no tiene muchas opciones sobre tecnología."
    },
    {
        "nombre": "Universidad Simón Bolívar",
        "area": "Licenciatura en Tecnologías de la Información en los Negocios",
        "url": "https://usb.edu.mx/",
        "img": "assets/usb.png",
        "resumen": "La Universidad Simón Bolívar ofrece programas innovadores en tecnologías de la información aplicadas a los negocios, con un enfoque práctico y actualizado, se caracteriza por sus carreras que combinan ciencias sociales y tecnología de buena manera y la hace una opción interesante."
    }
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

    # Alias para compatibilidad con el resto del código que llama `handle`
    def handle(self, event):
        return self.handle_event(event)
                
# ------------- Escenas -------------------
class Scene:
    def handle(self, event):
        """Manejador de eventos por defecto (noop)."""
        pass

    def update(self, dt):
        """Actualización por defecto (noop)."""
        pass

    def draw(self, surf):
        """Dibujo por defecto (noop)."""
        pass
    
class Splash(Scene):
    def __init__(self, next_scene_callback):
        self.time = 0
        self.duration = 1.8 # seg
        self.next_scene_callback = next_scene_callback
        # logo tamaño corregido (antes 2230 hacía que el surface fuera extremadamente ancho)
        self.logo = load_image("assets/isb.png", size=(223, 220), fallback_color=(30 , 30, 50))
        
    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.next_scene_callback(Menu())
            
    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Feria de Universidaddes ISB 2025", Font_Big, (230, 230, 245), (WIDTH//2, 70))
        # Efecto de aparición
        alpha = min(255, int(255 * (self.time / self.duration)))
        logo = self.logo.copy()
        logo.set_alpha(alpha)
        surf.blit(logo, logo.get_rect(center=(WIDTH//2, HEIGHT//2)))

        draw_text(surf, "Cargando launcher...", Font_Small, (190, 190, 210), (WIDTH//2, HEIGHT - 40))

class Menu(Scene):
    def __init__(self):
        self.buttons = []
        self.title_y = 36
        padding_x = 60
        y = 120
        w, h, gap = 240, 60, 18

        # Botones dinámicos por universidad
        self.card_rects = []
        start_x = 60
        for i, u in enumerate(UNIVERSIDADES):
            rect = pygame.Rect(start_x + i * 280, 130, 260, 300)
            self.card_rects.append((rect, u))

        # Botones inferiores
        self.buttons.append(Button("Acerca de", padding_x, HEIGHT-80, w, h,
                                   lambda: set_scene(InfoScreen(
                                       title="Acerca del launcher",
                                       body=("Este launcher es una base en Pygame.\n"
                                             "Selecciona una universidad para ver detalles\n"
                                             "y abre su sitio oficial."),
                                       url=None
                                   ))))
        self.buttons.append(Button("Salir", WIDTH - padding_x - w, HEIGHT-80, w, h,
                                   lambda: sys.exit(0)))

    def handle(self, event):
        for b in self.buttons:
            b.handle(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click sobre tarjeta de universidad
            for rect, u in self.card_rects:
                if rect.collidepoint(event.pos):
                    set_scene(Detail(u))
                    break

    def update(self, dt):
        ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, "Elige una opción para explorar", Font_Big, (235, 235, 245), (WIDTH//2, 42))

        for rect, u in self.card_rects:
            pygame.draw.rect(surf, (34, 34, 46), rect, border_radius=16)
            pygame.draw.rect(surf, (90, 90, 130), rect, width=2, border_radius=16)
            # Imagen/logo
            img_rect = u["image_surf"].get_rect(center=(rect.centerx, rect.y + 95))
            surf.blit(u["image_surf"], img_rect)
            # Nombre y área
            draw_text(surf, u["nombre"], FONT, (240, 240, 250), (rect.centerx, rect.y + 195))
            # Área/descripcion: usar texto multilínea dentro del ancho de la tarjeta
            draw_multiline_text(surf, u["area"], Font_Small, (200, 200, 220),
                                (rect.x + 16, rect.y + 210), max_width=rect.width - 32)
            # Botón "Ver más"
            btn = pygame.Rect(rect.centerx - 80, rect.y + 260, 160, 44)
            mouse_over = btn.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surf, (70, 70, 110) if mouse_over else (50, 50, 85), btn, border_radius=10)
            draw_text(surf, "Ver más", Font_Small, (240, 240, 250), btn.center)

        for b in self.buttons:
            b.draw(surf)


class Detail(Scene):
    def __init__(self, data):
        self.data = data
        self.img = data["image_surf"]
        self.btn_back = Button("Regresar", 40, HEIGHT-80, 200, 56, lambda: set_scene(Menu()))
        self.btn_open = Button("Abrir sitio oficial", WIDTH-280, HEIGHT-80, 240, 56, self.open_site)

    def open_site(self):
        play_click()
        webbrowser.open(self.data["url"], new=2)

    def handle(self, event):
        self.btn_back.handle(event)
        self.btn_open.handle(event)

    def update(self, dt):
        ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, f"{self.data['nombre']} - {self.data['area']}", Font_Big, (235, 235, 245), (WIDTH//2, 42))

        # Tarjeta principal
        card = pygame.Rect(60, 90, WIDTH-120, 360)
        pygame.draw.rect(surf, (34, 34, 46), card, border_radius=16)
        pygame.draw.rect(surf, (90, 90, 130), card, width=2, border_radius=16)

        # Imagen
        img_rect = self.img.get_rect(center=(card.x + 140, card.centery))
        surf.blit(self.img, img_rect)

        # Texto
        body = (f"Resumen: {self.data['resumen']}\n\n"
                f"Sitio oficial: {self.data['url']}\n"
                "Tip: Investiga becas, requisitos y campo laboral,\n")
        draw_multiline_text(surf, body, Font_Small, (220, 220, 235), (img_rect.right + 30, card.y + 30),
                            max_width=WIDTH - 120 - 220 - 160)

        self.btn_back.draw(surf)
        self.btn_open.draw(surf)


class InfoScreen(Scene):
    def __init__(self, title, body, url=None):
        self.title = title
        self.body = body
        self.url = url
        self.btn_back = Button("Regresar", 40, HEIGHT-80, 200, 56, lambda: set_scene(Menu()))
        if url:
            self.btn_open = Button("Abrir enlace", WIDTH-260, HEIGHT-80, 220, 56,
                                   lambda: webbrowser.open(url, new=2))
        else:
            self.btn_open = None

    def handle(self, event):
        self.btn_back.handle(event)
        if self.btn_open:
            self.btn_open.handle(event)

    def update(self, dt):
        ...

    def draw(self, surf):
        surf.fill(BG_COLOR)
        draw_text(surf, self.title, Font_Big, (235, 235, 245), (WIDTH//2, 42))
        draw_multiline_text(surf, self.body, Font_Small, (220, 220, 235), (70, 110),
                            max_width=WIDTH - 140)
        self.btn_back.draw(surf)
        if self.btn_open:
            self.btn_open.draw(surf)


# --------------- Helper para texto multilinea ---------------
def draw_multiline_text(surf, text, font, color, topleft, max_width):
    x, y = topleft
    space = font.size(" ")[0]
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for w in words:
            test = line + w + " "
            if font.size(test)[0] < max_width:
                line = test
            else:
                img = font.render(line, True, color)
                surf.blit(img, (x, y))
                y += font.get_linesize() + 2
                line = w + " "
        if line:
            img = font.render(line, True, color)
            surf.blit(img, (x, y))
            y += font.get_linesize() + 8  # extra espacio entre párrafos


# ---------------- Loop principal ----------------
current_scene = None


def set_scene(scene):
    global current_scene
    current_scene = scene


def main():
    # envolvemos el loop principal en try/except para atrapar excepciones
    # y evitar que el launcher se cierre inmediatamente sin mostrar el error.
    set_scene(Splash(next_scene_callback=set_scene))
    try:
        while True:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if current_scene:
                    current_scene.handle(event)
            if current_scene:
                current_scene.update(dt)
                current_scene.draw(screen)
            pygame.display.flip()
    except Exception:
        # imprimimos la traza para depuración en la terminal
        traceback.print_exc()
        # Evitar bloquear el hilo principal con input() (provoca "No responde").
        # Esperamos unos segundos para que el usuario pueda leer la traza
        try:
            pygame.time.wait(3000)
        except Exception:
            # si pygame falló, hacemos sleep normal
            import time
            time.sleep(3)
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
        