from .logging import ChunkedMessageLogger
from click import echo


class MockLogger(ChunkedMessageLogger):
    message_buffer = []

    def send_messages(self, messages):
        self.message_buffer += messages

    def reassemble_streams(self):
        return "".join(
            [
                msg["text"]
                for msg in self.message_buffer
                if msg["type"] in ["stdout", "stderr"]
            ]
        )


def test_remote_logging():

    logger = MockLogger()

    with logger.redirect_output():
        echo("Test", err=True)
        echo("woohoo")
        echo("Test test test", err=True)

    buffer = logger.reassemble_streams()
    assert buffer == "Test\nwoohoo\nTest test test\n"
