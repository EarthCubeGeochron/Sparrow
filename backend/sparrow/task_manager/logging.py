import sys
from json import dumps
from time import time
from contextlib import contextmanager
from asyncio import sleep, get_event_loop


def create_message(**kwargs):
    return dumps(dict(time=time(), **kwargs))


class MessageLogger:
    """A file-like object to send messages"""

    def __init__(self, backend, type="stdout", tty=True):
        self.type = type
        self._backend = backend
        self._tty = tty

    def isatty(self):
        return self._tty

    def write(self, data):
        self._backend.write_message(data, self.type)

    def flush(self):
        pass

    def close(self):
        pass


def as_string(text):
    # Cast bytes to string
    try:
        text = text.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        pass
    return text


def local_logger(text, type, stdout=sys.stdout, stderr=sys.stderr):
    if type == "stdout":
        print(text, file=stdout)
    if type == "stderr":
        print(text, file=stderr)
    else:
        print(type + ": " + text)


class ChunkedMessageLogger:
    _chunk_timeout = 1
    _buffer = []
    _loop = None
    _mock = False

    def __init__(self, disable=False, tty=True):
        self._disable = disable
        self._tty = tty
        self._loop = get_event_loop()
        self._last_message_time = time()
        self._base_stdout = sys.stdout
        self._base_stderr = sys.stderr

    def __local_logger(self, text, type):
        local_logger(text, type, stdout=self._base_stdout, stderr=self._base_stderr)

    async def __send_delayed(self):
        await sleep(2 * self._chunk_timeout)
        if self._is_timed_out():
            self.__send_messages()

    def write_message(self, text, type):
        if self._disable:
            self.__local_logger(text, type)
            return
        self._buffer.append(dict(text=as_string(text), type=type))
        self.flush()

    def _is_timed_out(self):
        return (
            len(self._buffer) >= 0
            and time() - self._last_message_time > self._chunk_timeout
        )

    def flush(self, immediate=False):
        if immediate or self._is_timed_out():
            self.__send_messages()
        else:
            self._loop.run_in_executor(None, self.__send_delayed)

    def send_messages(self, messages):
        """This function should be overridden for different message types"""
        for message in messages:
            self.__local_logger(message["text"], message["type"])

    def __send_messages(self):
        self.send_messages(self._buffer)
        self._buffer = []
        self._last_message_time = time()

    def get_log_stream(self, type):
        return MessageLogger(self, type, self._tty)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush(immediate=True)

    @contextmanager
    def redirect_output(self, disable=False):
        if disable:
            yield
            return
        sys.stdout = self.get_log_stream("stdout")
        sys.stderr = self.get_log_stream("stderr")
        yield
        self.flush(immediate=True)
        sys.stdout = self._base_stdout
        sys.stderr = self._base_stderr


class RedisQueueLogger(ChunkedMessageLogger):
    def __init__(self, queue, channel, disable=False, tty=True):
        super().__init__(disable=disable, tty=tty)
        self.queue = queue
        self.channel = channel

    def send_messages(self, messages):
        if self.queue is None:
            return super().send_messages(messages)
        self.queue.publish(self.channel, dumps(dict(messages=messages)))
