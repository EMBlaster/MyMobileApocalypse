import os
import threading
import time

# Use dummy video driver so this can run in headless CI environments
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
from ui.pygame_main import PygameApp


def test_pygame_app_smoke_runs_a_few_frames():
    app = PygameApp()

    def run_app():
        # run mainloop which will exit on QUIT event
        app.mainloop()

    t = threading.Thread(target=run_app, daemon=True)
    t.start()

    # Let app run for a short time (a few frames)
    time.sleep(0.1)

    # Post QUIT to stop the loop
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    t.join(timeout=2)
    assert not t.is_alive()
