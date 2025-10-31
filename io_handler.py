class IOHandler:
    """Abstract IO interface. Implement input() and print() to decouple UI from logic."""
    def input(self, prompt: str = "") -> str:
        raise NotImplementedError()

    def print(self, *args, **kwargs):
        raise NotImplementedError()


class ConsoleIO(IOHandler):
    def input(self, prompt: str = "") -> str:
        return input(prompt)

    def print(self, *args, **kwargs):
        print(*args, **kwargs)


class HeadlessIO(IOHandler):
    """A simple headless IO for automated tests: provides queued responses and captures printed output."""
    def __init__(self, responses=None):
        self.responses = list(responses) if responses else []
        self.output = []

    def input(self, prompt: str = "") -> str:
        # Capture prompt for diagnostics
        self.output.append(prompt)
        if not self.responses:
            raise RuntimeError("HeadlessIO has no more responses available")
        return self.responses.pop(0)

    def print(self, *args, **kwargs):
        text = " ".join(str(a) for a in args)
        self.output.append(text)


class PygameIO(IOHandler):
    """A simple Pygame-backed IO adapter.

    - `print()` appends to an internal output buffer for the UI to render.
    - `input(prompt)` sets a prompt and blocks until `provide_input()` is called by the UI.

    This class is thread-safe so `Game.run_day()` can run in a worker thread while
    the main Pygame thread renders the UI and supplies responses.
    """
    def __init__(self):
        from threading import Event, Lock
        self.output = []
        self._prompt = None
        self._prompt_event = None
        self._prompt_lock = Lock()
        self._response = None

    # Print appends text to the output buffer
    def print(self, *args, **kwargs):
        text = " ".join(str(a) for a in args)
        # Keep a reasonably sized buffer
        self.output.append(text)
        if len(self.output) > 1000:
            self.output = self.output[-1000:]

    # input blocks until UI calls provide_input()
    def input(self, prompt: str = "") -> str:
        from threading import Event
        with self._prompt_lock:
            self._prompt = prompt
            self._response = None
            self._prompt_event = Event()
            ev = self._prompt_event

        # Wait until UI provides a response
        ev.wait()

        with self._prompt_lock:
            resp = self._response
            # clear prompt after consuming
            self._prompt = None
            self._prompt_event = None
            self._response = None
        return resp

    def provide_input(self, response: str):
        """Called by the UI thread to fulfill the pending input prompt."""
        with self._prompt_lock:
            if not self._prompt_event:
                return
            self._response = response
            self._prompt_event.set()

    def get_pending_prompt(self):
        with self._prompt_lock:
            return self._prompt

    def pop_output(self):
        """Return and clear the current output buffer (used by UI renderer)."""
        # Return only the new output since last pop and clear the internal buffer.
        # The UI keeps its own history (`log_lines`), so it's safe to clear here and
        # avoids the same lines being re-appended each frame which caused a flood of
        # repeated 'PROMPT:' entries in the UI.
        out = list(self.output)
        self.output = []
        return out

    # --- Choice handling (for decision modals) ---
    def present_choices(self, prompt: str, options: list) -> str:
        """Set a pending choice prompt and block until UI calls provide_choice(index).

        Returns the selected option index as a string (matching make_decision expectations).
        """
        from threading import Event
        with self._prompt_lock:
            self._prompt = prompt
            self._choices = list(options)
            self._choice_response = None
            self._choice_event = Event()
            ev = self._choice_event

        # Wait for UI to call provide_choice
        ev.wait()

        with self._prompt_lock:
            resp = self._choice_response
            # clear choice state
            self._prompt = None
            self._choices = None
            self._choice_event = None
            self._choice_response = None
        return resp

    def provide_choice(self, index: str):
        """Called by the UI thread to fulfill a pending choice prompt."""
        with self._prompt_lock:
            if not getattr(self, '_choice_event', None):
                return
            self._choice_response = index
            self._choice_event.set()

    def get_pending_choices(self):
        """Return (prompt, options) if a choice modal is pending, else None."""
        with self._prompt_lock:
            if getattr(self, '_choices', None):
                return (self._prompt, list(self._choices))
            return None
