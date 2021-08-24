import sys
from json import dumps
from time import time
from contextlib import contextmanager
from asyncio import sleep, get_event_loop


def create_message(**kwargs):
    return dumps(dict(time=time(), **kwargs))


class FunctionLogger(object):
    _chunk_timeout = 1

    def __init__(self, log_func, type="stdout", tty=True):
        self.type = type
        self.log_func = log_func
        self._tty = tty
        self._last_message_time = time()
        self._buffer = ""
        self._loop = get_event_loop()

    def isatty(self):
        return True

    def write(self, data):
        try:
            self._buffer += data + "\n"
        except TypeError:
            self._buffer += str(data, "utf-8") + "\n"
        if time() - self._last_message_time > self._chunk_timeout:
            self.send_message()
        else:
            self._loop.run_in_executor(None, self.send_delayed)

    async def send_delayed(self):
        await sleep(2 * self._chunk_timeout)
        if time() - self._last_message_time > self._chunk_timeout:
            self.send_message()

    def send_message(self):
        if self._buffer == "":
            return
        self.log_func(self._buffer, type=self.type)
        self._buffer = ""
        self._last_message_time = time()

    def flush(self):
        pass

    def close(self):
        self.send_message()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@contextmanager
def redirect_output(log_func, disable=False):
    if disable:
        yield
        return
    _old_stdout = sys.stdout
    _old_stderr = sys.stderr
    with FunctionLogger(log_func, type="stdout") as stdout:
        sys.stdout = stdout
        sys.stderr = stdout
        yield
    sys.stdout = _old_stdout
    sys.stderr = _old_stderr
