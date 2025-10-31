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
