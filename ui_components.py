import customtkinter as ctk
import tkinter as tk
from ctypes import windll, c_int, byref, sizeof, Structure, pointer, POINTER

# ===================================================================
# THEME: Minimalismo premium · Glass · San Francisco–style
# ===================================================================
class VisionSys:
    """Sistema de diseño: minimalismo elegante, capas sutiles, tipografía clara."""

    # Tipografía: Segoe UI (base tipo San Francisco), jerarquía muy marcada
    FONT_H1 = ("Segoe UI", 32, "bold")       # Títulos grandes y seguros
    FONT_H2 = ("Segoe UI", 20, "bold")       # Subtítulos / secciones
    FONT_BODY_L = ("Segoe UI", 15)           # Cuerpo grande, legible
    FONT_BODY_M = ("Segoe UI", 14)           # Cuerpo medio
    FONT_CAPTION = ("Segoe UI", 12)          # Secundario más fino y discreto
    FONT_SMALL = ("Segoe UI", 11)            # Etiquetas y hints

    # Espaciado (mucho espacio en blanco = sensación premium)
    SPACE_XXS = 4
    SPACE_XS = 8
    SPACE_S = 12
    SPACE_M = 20
    SPACE_L = 28
    SPACE_XL = 40
    SPACE_XXL = 56

    # Modo oscuro: grises profundos (no negro puro), menos cansancio visual
    BG_DARK = "#0d0d0d"           # Fondo principal
    SURFACE_DARK = "#161616"      # Superficies (sidebar, áreas)
    CARD_DARK = "#1c1c1c"         # Tarjetas que "flotan"
    GLASS_DARK = "#222222"        # Vidrio / paneles
    BORDER_DARK = "#262626"       # Bordes sutiles, no duros
    BORDER_DARK_HOVER = "#353535" # Hover suave
    BORDER_DARK_SOFT = "#1f1f1f"  # Para elementos muy integrados (inputs sobre glass)

    TEXT_PRIMARY_DARK = "#f5f5f7"
    TEXT_SECONDARY_DARK = "#8e8e93"   # Secundario más fino y discreto
    TEXT_TERTIARY_DARK = "#636366"

    # Acentos (equilibrados, no agresivos)
    ACCENT = "#0a84ff"            # Azul suave (estilo sistema)
    ACCENT_HOVER = "#409cff"
    ACCENT_GREEN = "#30d158"      # Éxito / acciones principales
    ACCENT_GREEN_HOVER = "#34c759"
    WARNING = "#ff9f0a"           # Amarillo suave
    WARNING_HOVER = "#ffb340"
    ERROR = "#ff453a"             # Error suave
    ERROR_HOVER = "#ff6961"

    # Modo claro (paleta que se adapta)
    BG_LIGHT = "#f5f5f7"
    SURFACE_LIGHT = "#ffffff"
    CARD_LIGHT = "#ffffff"
    GLASS_LIGHT = "#f0f0f2"
    BORDER_LIGHT = "#e0e0e5"
    BORDER_LIGHT_SOFT = "#ebebef"  # Para elementos muy integrados
    TEXT_PRIMARY_LIGHT = "#1d1d1f"
    TEXT_SECONDARY_LIGHT = "#86868b"
    TEXT_TERTIARY_LIGHT = "#aeaeb2"

    # Bordes: sutiles, coherentes en toda la app
    BORDER_WIDTH_SUBTLE = 1       # Por defecto (glass, cards, inputs)
    BORDER_WIDTH_FOCUS = 2        # Opcional: foco/hover destacado

    # Radios (iconos y elementos suaves y redondeados)
    RADIUS_S = 10
    RADIUS_M = 14
    RADIUS_L = 20
    RADIUS_XL = 24
    CORNER_RADIUS = RADIUS_L      # Por compatibilidad

    # Aliases para uso actual (oscuro por defecto)
    GLASS_BG_DARK = CARD_DARK
    GLASS_FG_DARK = GLASS_DARK
    TEXT_PRIMARY = TEXT_PRIMARY_DARK
    TEXT_SECONDARY = TEXT_SECONDARY_DARK
    WARNING = WARNING
    ERROR = ERROR

    @classmethod
    def is_dark(cls):
        try:
            return ctk.get_appearance_mode().lower() == "dark"
        except Exception:
            return True

    @classmethod
    def bg(cls):
        return cls.BG_DARK if cls.is_dark() else cls.BG_LIGHT

    @classmethod
    def surface(cls):
        return cls.SURFACE_DARK if cls.is_dark() else cls.SURFACE_LIGHT

    @classmethod
    def card(cls):
        return cls.CARD_DARK if cls.is_dark() else cls.CARD_LIGHT

    @classmethod
    def glass(cls):
        return cls.GLASS_DARK if cls.is_dark() else cls.GLASS_LIGHT

    @classmethod
    def border(cls):
        return cls.BORDER_DARK if cls.is_dark() else cls.BORDER_LIGHT

    @classmethod
    def text_primary(cls):
        return cls.TEXT_PRIMARY_DARK if cls.is_dark() else cls.TEXT_PRIMARY_LIGHT

    @classmethod
    def text_secondary(cls):
        return cls.TEXT_SECONDARY_DARK if cls.is_dark() else cls.TEXT_SECONDARY_LIGHT

    @classmethod
    def text_tertiary(cls):
        return cls.TEXT_TERTIARY_DARK if cls.is_dark() else cls.TEXT_TERTIARY_LIGHT


# ===================================================================
# WINDOW EFFECT: Acrylic / Blur (Windows 11)
# ===================================================================
class ACCENT_POLICY(Structure):
    _fields_ = [
        ('AccentState', c_int),
        ('AccentFlags', c_int),
        ('GradientColor', c_int),
        ('AnimationId', c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ('Attribute', c_int),
        ('Data', POINTER(ACCENT_POLICY)),
        ('SizeOfData', c_int)
    ]

def apply_acrylic(window_root):
    """Aplica efecto Acrylic/Mica de Windows 11 a la ventana."""
    try:
        hwnd = windll.user32.GetParent(window_root.winfo_id())
        if hwnd == 0:
            hwnd = window_root.winfo_id()
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
        accent_policy = ACCENT_POLICY()
        accent_policy.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent_policy.AccentFlags = 2
        accent_policy.GradientColor = 0x99161616   # Translúcido sobre fondo
        accent_policy.AnimationId = 0
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = pointer(accent_policy)
        data.SizeOfData = sizeof(accent_policy)
        windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))
    except Exception as e:
        print(f"Acrylic effect failed (Win32 API error): {e}")

def apply_rounded_corners(window_root, radius=20):
    """Esquinas redondeadas en la ventana (Windows)."""
    try:
        hwnd = windll.user32.GetParent(window_root.winfo_id())
        if hwnd == 0:
            hwnd = window_root.winfo_id()
        rect = tk.sys.modules['ctypes'].wintypes.RECT()
        windll.user32.GetWindowRect(hwnd, byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        hrgn = windll.gdi32.CreateRoundRectRgn(0, 0, width, height, radius, radius)
        windll.user32.SetWindowRgn(hwnd, hrgn, True)
    except Exception as e:
        print(f"Rounded corners failed: {e}")


# ===================================================================
# COMPONENTES: Glass, tarjetas flotantes, botones
# ===================================================================
class GlassFrame(ctk.CTkFrame):
    """Panel tipo vidrio: bordes muy sutiles, integrado al fondo."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            fg_color=(VisionSys.GLASS_LIGHT, VisionSys.GLASS_DARK),
            corner_radius=VisionSys.RADIUS_XL,
            border_width=VisionSys.BORDER_WIDTH_SUBTLE,
            border_color=(VisionSys.BORDER_LIGHT_SOFT, VisionSys.BORDER_DARK)
        )


class FloatingButton(ctk.CTkButton):
    """Botón pill, suave; animación de hover sutil."""
    def __init__(self, parent, **kwargs):
        if 'font' not in kwargs:
            kwargs['font'] = VisionSys.FONT_BODY_M
        kwargs['corner_radius'] = VisionSys.RADIUS_XL
        kwargs['height'] = 48
        if 'fg_color' not in kwargs:
            kwargs['fg_color'] = VisionSys.ACCENT_GREEN
        if 'hover_color' not in kwargs:
            kwargs['hover_color'] = VisionSys.ACCENT_GREEN_HOVER
        if 'text_color' not in kwargs:
            kwargs['text_color'] = "#ffffff"
        super().__init__(parent, **kwargs)


class GlassCard(ctk.CTkFrame):
    """Tarjeta que flota: información clara, icono redondeado, hover sutil."""
    def __init__(self, parent, icon="📄", title="Title", subtitle="Subtitle", command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.configure(
            fg_color=(VisionSys.CARD_LIGHT, VisionSys.CARD_DARK),
            corner_radius=VisionSys.RADIUS_XL,
            border_width=VisionSys.BORDER_WIDTH_SUBTLE,
            border_color=(VisionSys.BORDER_LIGHT_SOFT, VisionSys.BORDER_DARK)
        )
        self.grid_columnconfigure(1, weight=1)
        pad = VisionSys.SPACE_L
        self.lbl_icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 28))
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=pad, pady=pad)
        self.lbl_title = ctk.CTkLabel(
            self, text=title, font=VisionSys.FONT_BODY_L,
            text_color=(VisionSys.TEXT_PRIMARY_LIGHT, VisionSys.TEXT_PRIMARY_DARK),
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=1, sticky="w", padx=(0, pad), pady=(VisionSys.SPACE_S, 0))
        self.lbl_sub = ctk.CTkLabel(
            self, text=subtitle, font=VisionSys.FONT_CAPTION,
            text_color=(VisionSys.TEXT_SECONDARY_LIGHT, VisionSys.TEXT_SECONDARY_DARK),
            anchor="w"
        )
        self.lbl_sub.grid(row=1, column=1, sticky="w", padx=(0, pad), pady=(0, VisionSys.SPACE_S))
        if command:
            self.lbl_arrow = ctk.CTkLabel(
                self, text="›", font=VisionSys.FONT_H2,
                text_color=(VisionSys.TEXT_SECONDARY_LIGHT, VisionSys.TEXT_SECONDARY_DARK)
            )
            self.lbl_arrow.grid(row=0, column=2, rowspan=2, padx=pad)
            self.bind("<Button-1>", lambda e: self.on_click())
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_click())
            self.bind("<Enter>", self.on_hover)
            self.bind("<Leave>", self.on_leave)

    def on_click(self):
        if self.command:
            self.command()

    def on_hover(self, event=None):
        self.configure(
            border_width=VisionSys.BORDER_WIDTH_SUBTLE,
            border_color=VisionSys.ACCENT_GREEN,
            fg_color=(VisionSys.GLASS_LIGHT, VisionSys.GLASS_DARK)
        )

    def on_leave(self, event=None):
        self.configure(
            border_width=VisionSys.BORDER_WIDTH_SUBTLE,
            border_color=(VisionSys.BORDER_LIGHT_SOFT, VisionSys.BORDER_DARK),
            fg_color=(VisionSys.CARD_LIGHT, VisionSys.CARD_DARK)
        )


class SectionHeader(ctk.CTkFrame):
    """Título de sección: jerarquía marcada, separación limpia."""
    def __init__(self, parent, title, subtitle=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=title, font=VisionSys.FONT_H2,
            text_color=(VisionSys.TEXT_PRIMARY_LIGHT, VisionSys.TEXT_PRIMARY_DARK),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle, font=VisionSys.FONT_CAPTION,
                text_color=(VisionSys.TEXT_SECONDARY_LIGHT, VisionSys.TEXT_SECONDARY_DARK),
                anchor="w"
            ).grid(row=1, column=0, sticky="w", pady=(VisionSys.SPACE_XXS, 0))


class SidebarButton(ctk.CTkButton):
    """Botón de sidebar: iconografía sutil, estado activo claro."""
    def __init__(self, parent, text, icon="●", selected=False, **kwargs):
        super().__init__(parent, **kwargs)
        fg_selected = (VisionSys.GLASS_LIGHT, VisionSys.GLASS_DARK)
        self.fg_default = "transparent"
        self.fg_selected = fg_selected
        self.configure(
            text=f"   {icon}   {text}",
            font=VisionSys.FONT_BODY_M,
            anchor="w",
            width=200,
            height=44,
            corner_radius=VisionSys.RADIUS_M,
            fg_color=fg_selected if selected else self.fg_default,
            text_color=(VisionSys.TEXT_PRIMARY_LIGHT, VisionSys.TEXT_PRIMARY_DARK),
            hover_color=(VisionSys.BORDER_LIGHT_SOFT, VisionSys.BORDER_DARK_HOVER)
        )

    def select(self, active=True):
        self.configure(fg_color=self.fg_selected if active else self.fg_default)


def add_tooltip(widget, text: str, delay_ms: int = 500):
    """Muestra un tooltip al pasar el ratón sobre el widget. text: texto de ayuda."""
    tip = [None]
    job = [None]

    def show(event):
        def do_show():
            if tip[0] is not None:
                return
            tw = ctk.CTkToplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
            lbl = ctk.CTkLabel(tw, text=text, font=VisionSys.FONT_CAPTION, fg_color=VisionSys.CARD_DARK, corner_radius=VisionSys.RADIUS_S, padx=8, pady=4)
            lbl.pack()
            tip[0] = tw
        job[0] = widget.after(delay_ms, do_show)

    def hide(event):
        if job[0] is not None:
            widget.after_cancel(job[0])
            job[0] = None
        if tip[0] is not None:
            tip[0].destroy()
            tip[0] = None

    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)


def center_window(window, width=900, height=600):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_c = int((screen_width - width) / 2)
    y_c = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x_c}+{y_c}")
