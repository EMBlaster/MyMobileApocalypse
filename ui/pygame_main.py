"""
Minimal Pygame UI launcher for MyMobileApocalypse (MVP).
- Requires `pygame` to be installed.
- Provides a main menu (Start Game, Create Character), a HUD (survivors/resources),
  a scrolling log, and an "Advance Day" button which runs `Game.run_day()` in a worker thread.

This is intentionally minimal; further polish, drag-and-drop assignment, and combat
visualization can be added incrementally.
"""
import threading
import time
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    # Provide a minimal fallback stub so editors/linters that don't have pygame
    # installed won't complain. This stub is intentionally minimal and only
    # provides attributes used by this module; it is NOT a full pygame
    # replacement and should only be used to satisfy static analysis.
    PYGAME_AVAILABLE = False
    import types

    class _Rect:
        def __init__(self, *args, **kwargs):
            self.x = args[0] if args else 0
            self.y = args[1] if len(args) > 1 else 0
            self.w = args[2] if len(args) > 2 else 0
            self.h = args[3] if len(args) > 3 else 0

        def collidepoint(self, pos):
            try:
                x, y = pos
                return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
            except Exception:
                return False

    class _Surface:
        def blit(self, *args, **kwargs):
            pass

    class _Display:
        @staticmethod
        def set_mode(size):
            return _Surface()

        @staticmethod
        def set_caption(text):
            return None

        @staticmethod
        def flip():
            return None

    class _FontModule:
        @staticmethod
        def SysFont(name, size):
            class DummyFont:
                def render(self, text, aa, color):
                    class DummySurfaceTxt:
                        def get_width(self):
                            return max(1, len(str(text)) * 6)

                        def get_rect(self, **kw):
                            class R:
                                pass

                            return R()

                    return DummySurfaceTxt()

            return DummyFont()

    class _EventModule:
        QUIT = 0
        MOUSEBUTTONDOWN = 1
        KEYDOWN = 2

        @staticmethod
        def get():
            return []

        @staticmethod
        def post(ev):
            return None

        @staticmethod
        def Event(etype, **kwargs):
            return {"type": etype, **kwargs}

    class _Time:
        class Clock:
            def tick(self, fps):
                return None

    pygame = types.SimpleNamespace()
    pygame.Rect = _Rect
    pygame.display = _Display()
    pygame.font = _FontModule()
    pygame.event = _EventModule()
    pygame.time = _Time()
    pygame.draw = types.SimpleNamespace(rect=lambda surf, color, rect: None)
    # Key constants used in this file
    pygame.K_BACKSPACE = 8
    pygame.K_RETURN = 13
    pygame.K_KP_ENTER = 271
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.QUIT = 256
    pygame.MOUSEBUTTONDOWN = 1025
    pygame.KEYDOWN = 768
from pathlib import Path
import sys

# Ensure repo root on sys.path
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from game import Game
from io_handler import PygameIO
from character_creator import create_pregenerated_survivor
from survivor import Survivor
from map_nodes import AVAILABLE_NODES

# UI constants
WIDTH, HEIGHT = 1000, 700
FPS = 30
FONT_NAME = None

class Button:
    def __init__(self, rect, text, font, bg=(70,70,70), fg=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, surf):
        pygame.draw.rect(surf, self.bg, self.rect)
        txt = self.font.render(self.text, True, self.fg)
        tx = txt.get_rect(center=self.rect.center)
        surf.blit(txt, tx)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TextInput:
    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = text
        self.active = False

    def draw(self, surf):
        pygame.draw.rect(surf, (255,255,255), self.rect, 2 if self.active else 1)
        txt = self.font.render(self.text, True, (255,255,255))
        surf.blit(txt, (self.rect.x+4, self.rect.y+4))

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.KEYDOWN and self.active:
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key == pygame.K_RETURN:
                self.active = False
            else:
                # basic alphanumeric capture
                # some pygame KEYDOWN events include `unicode` for the character
                if hasattr(ev, 'unicode') and len(ev.unicode) == 1:
                    self.text += ev.unicode

class PygameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('MyMobileApocalypse - MVP')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 18)
        self.small_font = pygame.font.SysFont(FONT_NAME, 14)

        # Game and IO
        self.game = None
        self.io = None
        self.game_thread = None
        self.game_running = False

        # UI state
        self.log_lines = []
        self.show_main_menu = True
        self.show_char_menu = False
        # modal UI state
        self._modal_prompt = None
        self._modal_options = None
        self._modal_rects = None
        self._modal_selected = None
        # generic prompt input state (for io.input prompts)
        self._prompt_pending = None
        self.prompt_input = TextInput((WIDTH//2-200, HEIGHT-140, 400, 32), self.font)
        # Start a background thread to read from terminal stdin so users can type
        # into the terminal to satisfy prompts when the Pygame window doesn't have focus.
        # This thread is daemonized so it won't block process exit.
        def _stdin_watcher():
            import sys
            try:
                for line in sys.stdin:
                    if not line:
                        continue
                    # If a prompt is pending in the game's IO, provide the input
                    try:
                        if self.io and getattr(self.io, 'get_pending_prompt', None) and self.io.get_pending_prompt():
                            self.io.provide_input(line.rstrip('\n'))
                    except Exception:
                        pass
            except Exception:
                # On some environments, sys.stdin iteration may raise; ignore and exit thread
                return

        t = threading.Thread(target=_stdin_watcher, daemon=True)
        t.start()

        # Main menu widgets
        self.btn_start = Button((WIDTH//2-80, 250, 160, 40), 'Start Game', self.font)
        self.btn_create = Button((WIDTH//2-80, 300, 160, 40), 'Create Character', self.font)
        self.btn_quit = Button((WIDTH//2-80, 350, 160, 40), 'Quit', self.font)

        # In-game widgets
        self.btn_advance = Button((WIDTH-170, 20, 150, 40), 'Advance Day', self.font, bg=(50,120,50))
        self.btn_save = Button((WIDTH-340, 20, 150, 40), 'Save', self.font)
        self.btn_create_char = Button((20, 20, 160, 36), 'Create Character', self.font)

        # Character creation
        self.name_input = TextInput((WIDTH//2-140, 200, 280, 36), self.font)
        self.btn_pregen = Button((WIDTH//2-80, 250, 160, 36), 'Use Pre-generated', self.font)
        self.btn_create_confirm = Button((WIDTH//2-80, 300, 160, 36), 'Create & Add', self.font)

    def start_game(self, difficulty='Normal', start_node_id=None):
        self.io = PygameIO()
        self.game = Game(start_day=1)
        self.game.io = self.io
        # Redirect built-in print to the game's IO so all prints appear in the UI
        try:
            import builtins
            self._orig_print = builtins.print
            builtins.print = lambda *args, **kwargs: self.io.print(*args, **kwargs)
        except Exception:
            self._orig_print = None

        # Add initial survivors (basic starter)
        leader = create_pregenerated_survivor()
        self.game.add_survivor(leader)
        self.game.add_survivor(Survivor(name='Ally', con_val=6, san_val=8, int_val=5))

        # resources
        self.game.add_resource('Food', 50)
        self.game.add_resource('Water', 50)
        self.game.add_resource('Fuel', 30)
        self.game.add_resource('Scrap', 30)
        self.game.add_resource('Ammunition', 20)
        self.game.add_resource('ElectronicParts', 10)

        # map
        self.game.generate_map(num_nodes=3)
        if start_node_id and start_node_id in self.game.game_map:
            self.game.set_current_node(start_node_id)
        else:
            if self.game.game_map:
                self.game.set_current_node(list(self.game.game_map.keys())[0])

        self.show_main_menu = False
        self.append_log('Game started (difficulty: %s)' % difficulty)

    def append_log(self, text):
        for line in str(text).split('\n'):
            self.log_lines.append(line)
        # keep last 200 lines
        self.log_lines = self.log_lines[-200:]

    def run_day_in_thread(self):
        if not self.game or self.game_thread:
            return
        def target():
            try:
                self.game.run_day()
            except Exception as e:
                self.append_log('Error running day: %s' % e)
            finally:
                self.game_thread = None
        self.game_thread = threading.Thread(target=target, daemon=True)
        self.game_thread.start()

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if self.show_main_menu:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_start.is_clicked(ev.pos):
                        # start with defaults
                        self.start_game()
                    elif self.btn_create.is_clicked(ev.pos):
                        self.show_char_menu = True
                        self.show_main_menu = False
                    elif self.btn_quit.is_clicked(ev.pos):
                        return False
            elif self.show_char_menu:
                self.name_input.handle_event(ev)
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_pregen.is_clicked(ev.pos):
                        c = create_pregenerated_survivor()
                        if not self.game:
                            # temp store: start game and add
                            self.start_game()
                        self.game.add_survivor(c)
                        self.append_log(f'Added pregenerated survivor: {c.name}')
                        self.show_char_menu = False
                    elif self.btn_create_confirm.is_clicked(ev.pos):
                        name = self.name_input.text.strip() or 'Unnamed'
                        s = Survivor(name=name)
                        if not self.game:
                            self.start_game()
                        self.game.add_survivor(s)
                        self.append_log(f'Created new survivor: {s.name}')
                        self.show_char_menu = False
            else:
                # in-game events
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_advance.is_clicked(ev.pos):
                        self.append_log('Advancing day...')
                        self.run_day_in_thread()
                    elif self.btn_create_char.is_clicked(ev.pos):
                        self.show_char_menu = True
                        return True
                    # If modal visible, check option clicks
                    if getattr(self, '_modal_rects', None):
                        for i, r in enumerate(self._modal_rects):
                            if r.collidepoint(ev.pos):
                                # Provide the choice back to IO (index starting at 1 as string)
                                try:
                                    self.io.provide_choice(str(i+1))
                                    self.append_log(f'Choice selected: {i+1}')
                                except Exception:
                                    pass
                                # clear modal state
                                self._modal_rects = None
                                self._modal_options = None
                                self._modal_prompt = None
                                break
                    # keyboard navigation for modal
                    if getattr(self, '_modal_options', None) and ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_UP:
                            if self._modal_selected is None:
                                self._modal_selected = 0
                            else:
                                self._modal_selected = max(0, self._modal_selected - 1)
                        elif ev.key == pygame.K_DOWN:
                            if self._modal_selected is None:
                                self._modal_selected = 0
                            else:
                                self._modal_selected = min(len(self._modal_options)-1, self._modal_selected + 1)
                        elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                            # emulate clicking the selected option
                            if self._modal_selected is not None:
                                try:
                                    self.io.provide_choice(str(self._modal_selected+1))
                                    self.append_log(f'Choice selected (kbd): {self._modal_selected+1}')
                                except Exception:
                                    pass
                                self._modal_rects = None
                                self._modal_options = None
                                self._modal_prompt = None
                                self._modal_selected = None
                # Key events for text input
                self.name_input.handle_event(ev)
                # Prompt input handling (for generic io.input prompts)
                if getattr(self, '_prompt_pending', None):
                    self.prompt_input.handle_event(ev)
                    # If Enter pressed, submit input
                    if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        try:
                            self.io.provide_input(self.prompt_input.text)
                            self.append_log(f'Input provided: {self.prompt_input.text}')
                        except Exception:
                            pass
                        # clear prompt state
                        self._prompt_pending = None
                        self.prompt_input.text = ''
                        # also clear any stored _prompt in IO (it will be cleared by IO input consumer)

        return True

    def sync_io_output(self):
        if not self.io:
            return
        # Pull prints from IO buffer
        try:
            out = self.io.pop_output()
        except Exception:
            out = []
        for line in out:
            self.append_log(line)
        # If prompt pending, also show it as a log entry
        pending = self.io.get_pending_prompt()
        if pending:
            # Only log the prompt once when it first appears to avoid flooding the UI
            if self._prompt_pending != pending:
                self.append_log('PROMPT: ' + str(pending))
                # show an input box so the player can fulfill the prompt
                self._prompt_pending = pending
                # clear any existing text and focus the input box
                try:
                    self.prompt_input.text = ''
                    self.prompt_input.active = True
                except Exception:
                    pass
        # If there are pending choices, capture them and show a modal in the UI
        pending_choices = None
        try:
            pending_choices = self.io.get_pending_choices()
        except Exception:
            pending_choices = None
        if pending_choices:
            prompt, options = pending_choices
            # Only log the decision prompt once when it first appears or when it changes
            if self._modal_prompt != prompt or self._modal_options != list(options):
                self.append_log('DECISION: ' + str(prompt))
            # store for rendering
            self._modal_prompt = prompt
            self._modal_options = list(options)
            # default selected option index if not already set
            if self._modal_selected is None:
                self._modal_selected = 0
        else:
            self._modal_prompt = None
            self._modal_options = None
            self._modal_selected = None
        # If no pending prompt in IO, ensure the UI prompt state is cleared
        if not pending and getattr(self, '_prompt_pending', None):
            self._prompt_pending = None
            try:
                self.prompt_input.active = False
            except Exception:
                pass

    def render(self):
        self.screen.fill((30,30,30))
        if self.show_main_menu:
            title = self.font.render('MyMobileApocalypse', True, (255,255,255))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
            self.btn_start.draw(self.screen)
            self.btn_create.draw(self.screen)
            self.btn_quit.draw(self.screen)
        elif self.show_char_menu:
            title = self.font.render('Create Character', True, (255,255,255))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 140))
            self.name_input.draw(self.screen)
            self.btn_pregen.draw(self.screen)
            self.btn_create_confirm.draw(self.screen)
        else:
            # HUD
            pygame.draw.rect(self.screen, (40,40,40), (10, 70, WIDTH-20, 120))
            # Survivors list
            y = 80
            if self.game:
                for s in self.game.survivors:
                    txt = self.small_font.render(f'{s.name} HP:{s.current_hp:.0f}/{s.max_hp:.0f} Stress:{s.current_stress:.0f}/{s.max_stress:.0f}', True, (230,230,230))
                    self.screen.blit(txt, (20, y))
                    y += 22
            # Buttons
            self.btn_advance.draw(self.screen)
            self.btn_create_char.draw(self.screen)
            self.btn_save.draw(self.screen)
            # If there's a pending modal, draw it
            if getattr(self, '_modal_options', None):
                self.draw_modal(self._modal_prompt, self._modal_options)
            # Log area
            pygame.draw.rect(self.screen, (20,20,20), (10, 200, WIDTH-20, HEIGHT-210))
            # render last lines from log
            lines = self.log_lines[-20:]
            ly = 210
            for line in lines:
                txt = self.small_font.render(line, True, (200,200,200))
                self.screen.blit(txt, (14, ly))
                ly += 18

            # Render prompt input if pending
            if getattr(self, '_prompt_pending', None):
                # Draw prompt label
                prompt_txt = self.small_font.render(str(self._prompt_pending), True, (240,240,240))
                px = 20
                py = HEIGHT - 60
                self.screen.blit(prompt_txt, (px, py))
                # Position input box next to prompt
                self.prompt_input.rect.topleft = (px + prompt_txt.get_width() + 8, py - 4)
                self.prompt_input.draw(self.screen)
        pygame.display.flip()

    def draw_modal(self, prompt, options):
        # Simple centered modal
        w, h = 600, 300
        x = (WIDTH - w)//2
        y = (HEIGHT - h)//2
        pygame.draw.rect(self.screen, (20,20,20), (x, y, w, h))
        pygame.draw.rect(self.screen, (200,200,200), (x, y, w, h), 2)
        # Prompt
        txt = self.font.render(str(prompt), True, (255,255,255))
        self.screen.blit(txt, (x+12, y+12))
        # Draw options as buttons
        btn_h = 36
        gap = 8
        for i, opt in enumerate(options):
            bx = x + 20
            by = y + 50 + i*(btn_h + gap)
            rect = pygame.Rect(bx, by, w-40, btn_h)
            pygame.draw.rect(self.screen, (80,80,80), rect)
            txt = self.small_font.render(str(opt), True, (230,230,230))
            self.screen.blit(txt, (bx+8, by+6))
            # store rects so clicks can be detected
        # Save rects for click handling
        self._modal_rects = [pygame.Rect(x+20, y+50 + i*(btn_h+gap), w-40, btn_h) for i in range(len(options))]

    def mainloop(self):
        running = True
        while running:
            running = self.handle_events()
            # sync prints from game IO
            if self.io:
                self.sync_io_output()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()


def main():
    app = PygameApp()
    app.mainloop()


if __name__ == '__main__':
    main()
