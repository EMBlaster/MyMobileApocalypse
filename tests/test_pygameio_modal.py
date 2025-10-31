import threading
import time

from io_handler import PygameIO


def test_pygameio_present_and_provide_choice():
    io = PygameIO()
    result = {}

    def worker():
        # This will block until provide_choice is called
        r = io.present_choices("Pick?", ["one", "two"])
        result['r'] = r

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # wait for pending choices to appear
    for _ in range(100):
        pending = io.get_pending_choices()
        if pending:
            break
        time.sleep(0.005)

    assert pending is not None
    prompt, options = pending
    assert prompt == "Pick?"
    assert options == ["one", "two"]

    # provide the second option
    io.provide_choice("2")
    t.join(timeout=1)
    assert result.get('r') == "2"
