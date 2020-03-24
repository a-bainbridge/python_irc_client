from typing import Dict

"""
class that logs buffers of string type
"""


class Logger:
    def __init__(self, name: str):
        self.name = name
        self.s_content = ""  # static content, not consumed, only added to
        self.c_content = ""  # consumable content, added to and consumed

    def print(self, content: str) -> None:
        self.s_content += content
        self.c_content += content

    def println(self, content: str) -> None:
        self.print('%s\n' % content)

    def consume(self) -> str:  # consume a single character from the start
        c = self.c_content[0]
        self.c_content = self.c_content[1:]
        return c

    def consume_all(self) -> str:  # consumes the rest of the stack
        s = self.c_content
        self.c_content = ""
        return s

    def get_whole(self) -> str:
        return self.s_content

    def get_unconsumed(self) -> str:
        return self.c_content

    def clear(self):
        self.s_content = ""
        self.c_content = ""


"""
class that has collections of loggers designated to channels and dms, specific to one server
"""


class ServerLogger:
    DEFAULT = 'info'

    def __init__(self, name: str):
        self.name = name
        self.loggers: Dict[str, Logger] = {
            ServerLogger.DEFAULT: Logger(ServerLogger.DEFAULT)
            # default logger for any other thing that comes from server
        }

    def create_logger(self, name: str) -> Logger:
        if name in self.loggers:
            print('Logger %s already exists!' % name)
        else:
            self.loggers[name] = Logger(name)
        return self.loggers[name]

    def get_logger(self, logger_name: str = DEFAULT) -> Logger:
        if logger_name in self.loggers:
            return self.loggers[logger_name]
        else:
            return self.create_logger(logger_name)

    def print(self, content: str, logger_name: str = DEFAULT) -> None:
        self.get_logger(logger_name).print(content)

    def println(self, content: str, logger_name: str = DEFAULT) -> None:
        self.get_logger(logger_name).println(content)

    def info(self, content: str) -> None:
        self.get_logger().println(content)


"""
class that has a collection of server loggers, with loggers for channels, dms, and junk
"""


class ClientLogger:
    DEFAULT = 'any'

    def __init__(self):
        self.server_loggers: Dict[str, ServerLogger] = {
            ClientLogger.DEFAULT: ServerLogger(ClientLogger.DEFAULT)
        }

    def create_logger(self, name: str) -> ServerLogger:
        if name in self.server_loggers:
            print('ServerLogger %s already exists!' % name)
        else:
            self.server_loggers[name] = ServerLogger(name)
        return self.server_loggers[name]

    def get_logger(self, name: str = DEFAULT) -> ServerLogger:
        if name in self.server_loggers:
            return self.server_loggers[name]
        else:
            return self.create_logger(name)

    def info(self, content: str) -> None:
        self.get_logger().info(content)
