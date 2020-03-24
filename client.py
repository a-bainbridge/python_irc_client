import socket, types, time, threading, os, configparser
import sys

from handlers import *

# https://modern.ircdocs.horse/
from loggers import ServerLogger


class Navigation: # todo: navigation in Server class
    def __init__(self, current_channel: str = ''):
        self.current_channel = current_channel

class Server:
    def __init__(self, host: str, port: int, username: str, nickname: str, password: str = '', hostname: str = ''):
        self.hostname = hostname
        self.host = host
        self.port = int(port)
        self.password = password
        self.nickname = nickname
        self.username = username

        self.sock: socket.socket = None
        self.listen_thread: threading.Thread = None
        self.connected = False
        self.registered = False
        self.listening = False

        self.logger = ServerLogger(host)

    def connect(self) -> bool:  # successful?
        start_time, end_time = 0, 0
        try:
            self.sock = socket.socket()
            start_time = time.perf_counter()
            self.sock.connect((self.host, self.port))
            end_time = time.perf_counter()
            self.connected = True
            self.logger.info('connected in %ss'%(end_time-start_time))
            self.on_successful_connect()
            return True
        except (ConnectionError, TimeoutError) as e:
            end_time = time.perf_counter()
            self.logger.info('failed to connect (%ss) to %s at %s' % (end_time-start_time, self.hostname, self.host))
            return False

    def on_successful_connect(self) -> None:
        self.register()
        self.start_listen()

    def start_listen(self) -> None:
        self.listen_thread = threading.Thread(target=self.continuous_listen)
        self.listen_thread.start()
        self.listening = True

    def continuous_listen(self):
        while True:
            message = self.get_raw_message(1024) # hm
            response:ResponseHandler = ResponseHandler.parse_response(message)
            ResponseHandler.handle_response(response, self)
            if not self.listening:
                break

    def stop_listen(self):
        self.listening = False
        self.listen_thread.join()

    def get_raw_message(self, timeout: float = 1.0) -> str:
        response = b""
        starttime = time.perf_counter()
        last = ''
        while True:
            latest = self.sock.recv(1)
            if last == b'\r' and latest == b'\n':
                response = response[:-1]
                break
            response += latest
            timepassed = time.perf_counter() - starttime
            if timepassed > timeout:
                self.logger.info('timeout of %s passed with time %s' % (timeout, timepassed))
                return ''
            last = latest
        response = response.decode(encoding='UTF-8')
        return response

    def stream_input(self, nav: Navigation):
        self.logger.info('type "exit" to exit streaming')
        while True:
            inn = input()
            if inn.rstrip() == 'exit':
                self.logger.info('exiting . . .')
                break
            self.send_message(inn, nav)

    def send_command(self, command: str, args: list = (), contents: str = '') -> None:
        a = ' '.join([str(i) for i in args])
        if len(args) > 0:
            a = ' ' + a
        if contents is '':
            self.send_str('%s%s' % (command, a))
        else:
            self.send_str('%s%s :%s' % (command, a, contents))

    def send_message(self, message: str, nav: Navigation) -> None:
        self.send_command('PRIVMSG', ['#%s' % nav.current_channel], contents=message)

    def send_str(self, message: str):
        if self.connected:
            self.sock.send(bytes(message + "\r\n", encoding='UTF-8'))

    # def send_with_response(self, message: str, timeout=1) -> CommandResponse:
    #     if self.connected:
    #         self.send_str(message)
    #         response = self.get_raw_message(timeout)
    #         print('response is %s' % response)
    #         return cmdR
    #     else:
    #         return CommandResponse()

    def register(self):
        # https://modern.ircdocs.horse/ > "Connection Registration"
        # https://tools.ietf.org/html/rfc2812#section-3.1
        self.send_str('CAP LS 302')
        if self.password != '':
            self.send_str('PASS %s' % self.password)
        self.send_str('NICK %s' % self.nickname + '\r\nUSER %s 0 * :%s' % (self.username, self.username))
        self.registered = True

    def disconnect(self):
        if self.listening:
            self.stop_listen()
        self.sock.close()
        self.connected = False
        self.registered = False

    def ready(self):
        return self.connected and self.registered and self.listening

    def status(self):
        return 'Connected: %s\nRegistered: %s\nListening: %s' % (self.connected, self.registered, self.listening)
    def info(self, content: str) -> None:
        self.logger.info(content)
    def __str__(self) -> str:
        return \
            f"""
        Server {self.hostname} at {self.host} on port {self.port}
        Username: {self.username}, Nick: {self.nickname}
        {self.status()}
        """

def get_config() -> dict:
    try:
        config_parser = configparser.ConfigParser()
        config_parser.read('config/servers.ini', encoding="UTF-8")
    except:
        print('you must have a config/servers.ini file')
        return {}
    out = {}
    for server in config_parser.sections():
        server_name = str(server)
        out[server_name] = {}
        for key in config_parser[server_name]:
            value = config_parser[server_name][key]
            if key=='port':
                value = int(value)
            out[server_name][key] = value
    return out


if __name__ == '__main__':
    all_servers = get_config()
    if len(all_servers.keys()) == 0:
        print('no servers!')
        sys.exit()
    host_name = input('enter server name from any of [%s]:\n'%(', '.join([s for s in all_servers.keys()])))
    try:
        serv = all_servers[host_name]
        serv['hostname'] = host_name
    except:
        print('unable to find data on host %s'%host_name)
        sys.exit()
    current_server = Server(**serv) # needs host, port, username and nickname
    me = Navigation('')
    current_server.info('connecting . . .')
    current_server.connect()
    if current_server.ready():
        current_server.info('logged in as %s (%s)' % (current_server.nickname, current_server.username))
        current_server.send_command('JOIN', ['#general'])
        me.current_channel = 'general'
        current_server.send_message('hello', me)
        current_server.stream_input(me)
        current_server.disconnect()
    else:
        print('server status: ')
        print(current_server.status())
