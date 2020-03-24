from typing import Callable, List

class Command:
    from client import Server
    def __init__(self, command: str, callback: Callable[['ResponseHandler', Server], None]):
        self.callback = callback
        self.command_name = command

    def call_command(self, response: 'ResponseHandler', server: Server) -> None:
        self.callback(response, server)

    def call_safe(self, response: 'ResponseHandler', server: Server) -> bool:  # whether or not it was called
        if response.command == self.command_name:
            self.call_command(response, server)
            return True
        return False

    COMMANDS = []

Command.COMMANDS = [
    #Command('PING', lambda r, s: s.send_command('PONG')) # hm not sure if these will be used
]

class CommandResponse:
    from client import Server
    def __init__(self, number: int = 0):
        self.number = number

    def handle_response(self, response: 'ResponseHandler', server: Server) -> None:
        # https://tools.ietf.org/html/rfc2812#section-5
        if self.number == 432:  # bad nickname
            print('bad nick!')
        elif self.number == 1:  # welcome
            print(response.content)
        elif self.number == 2:  # another welcome message?
            print(response.content)
        elif self.number == 352:  # a general message to be logged
            user: str = response.parameters[1]
            channel: str = response.parameters[0]
            print('%s > %s' % (user, response.content))
        else:
            print(response.content)

    def __str__(self):
        return 'CommandResponse<response code: %d>' % self.number


class ResponseHandler:
    from client import Server
    @staticmethod
    def parse_response(response: str) -> 'ResponseHandler':
        parts = response.split(' ')
        for p in parts:
            if p is '':
                parts.remove(p)
        if len(parts) == 0:
            print('%s is a BAD RESPONSE!!!!' % response)
            return ResponseHandler()  # should have 0 of these
        src = ''
        cmd = ''
        parameters = []
        content, hcontent = '', False
        p1 = -1
        if parts[0][0] is ':':  # check for source
            src = parts[0][1:]  # get rid of :
            cmd = parts[1]
            p1 = 2
        else:
            cmd = parts[0]
            p1 = 1

        if len(parts) >= p1:  # get parameters and content
            for i in range(p1, len(parts)):
                p: str = parts[i]
                if p[0] is ':':
                    hcontent = True
                    p = p[1:] # get rid of colon
                if hcontent:
                    content += ' ' + p  # because content was separated by spaces
                else:
                    parameters.append(p)
        return ResponseHandler(
            source=src,
            command=cmd.lower(),
            parameters=parameters,
            content=content
        )

    def handle_response(self, server: Server) -> bool:  # whether or not it was handled
        # switch command
        cmd = self.command
        try:
            cmd_num = int(cmd)
            CommandResponse.handle_response(CommandResponse(cmd_num), self, server)
            return True
        except ValueError:
            pass
        for c in Command.COMMANDS:
            if c.call_safe(self, server): return True
        if cmd == 'ping':
            server.send_command('PONG')
            #print('sending pong')
        elif cmd == 'notice':
            print('NOTICE: ' + self.content)
        elif cmd == 'cap':
            print('haha cap')
            server.send_str('no')
        elif cmd == 'privmsg':
            print(self.content) # todo: parse sources!
        else:
            print('unable to parse %s or command %s'%(self, self.command))
            return False

    def __init__(self, **kwargs):  # remove standard marks
        self.source: str = kwargs['source']  # without :, default ''
        self.command: str = kwargs['command']  # lowercase
        self.parameters: list = kwargs['parameters']  # list of strs without spaces, of course. if none, empty list
        self.content: str = kwargs['content']  # without :, default ''

    def __str__(self):
        return f"ResponseHandler<source: {self.source}, command: {self.command}, parameters: {self.parameters}, content: {self.content}>"

