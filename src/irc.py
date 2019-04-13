"""Connects to IRC."""

import abc
import re
import socket


class NickError(Exception):
    """An <Exception> for nickname-related problems on IRC."""

    def __init__(self, msg):
        super().__init__(msg)


class UnavailableError(Exception):
    """An <Exception> for when there is an IRC-related unavailability."""

    def __init__(self, msg):
        super().__init__(msg)


class IRCBot(abc.ABC):
    def __init__(self, nick, server, channels=None, port=6667,
                 should_log=False):
        """Connects the bot to IRC.

        Keyword arguments:
            nick -- <str>; nickname
            server -- <str>; e.g.: <'chat.freenode.net'>
            channels -- <set> of <str>s; e.g.: <{'##testing'}>
            port -- <int>
            should_log -- <bool>; whether to print events such as
                          channel joins

        This function never returns.

        To use this class, you will have to subclass it and create an
        implementation for <self.handle>.
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__nick = nick
        self.__server = server
        self.__channels = set()
        self.__port = port
        self.should_log = should_log

        self.log('Connecting...')
        self.__connect()
        if channels is not None:
            for channel in channels:
                self.join_channel(channel)
        self.__loop()

    @property
    def nick(self):
        """Returns this nickname (<str>)."""
        return self.__nick

    @property
    def server(self):
        """Returns the server (<str>) this bot is connected to."""
        return self.__server

    @property
    def channels(self):
        """Returns the channels (<set> of <str>s) this bot is in."""
        return self.__channels

    @property
    def port(self):
        """Returns the port (<int>) the server this bot is on uses."""
        return self.__port

    def __send_command(self, string):
        """Sends a command without the need for <'\n'>.

        Keyword arguments:
            string -- <str>; the message to send to the server
        """
        self.__socket.send(bytes('{}\n'.format(string), 'UTF-8'))

    def log(self, msg):
        """Logs <msg> (<str>) if <self.should_log> is <True>."""
        if self.should_log:
            print(msg)

    def __connect(self):
        """Connects the bot to IRC."""
        self.__socket.connect((self.server, self.port,))
        self.__send_command('USER {0} {0} {0} {0}'.format(self.nick))
        self.__send_command('NICK {}'.format(self.nick))

    def send_message(self, msg, channel):
        """Sends <msg> (<str>) to <channel> (<str>)."""
        self.__send_command('PRIVMSG {} :{}'.format(channel, msg))

    def join_channel(self, channel):
        """Joins the channel <channel> (<str>).

        A <ValueError> will be raised if <channel> is in
        <self.channels>.
        """
        if channel in self.channels:
            msg = '{} has already been connected to'.format(channel)
            raise ConnectionError(msg)
        self.log('Joining channel {}'.format(channel))
        self.__send_command('JOIN {}'.format(channel))
        self.__channels.add(channel)

    @abc.abstractmethod
    def handle(self, irc_msg):
        """Receives IRC messages (<irc_msg> is an <IRCMessage>)."""
        pass

    @staticmethod
    def __get_message(msg):
        """Returns an <IRCMessage> from <msg> (<str>).

        <msg> should be of the form <self._msg_re>.
        """
        parts = msg.split('!')
        nick = parts[0][1:]
        parts = parts[1].split('PRIVMSG ')
        parts = parts[1].split(' ', 1)
        channel = parts[0]
        msg = parts[1][1:]
        return IRCMessage(channel, nick, msg, len(nick) < 17)

    def __loop(self):
        """Starts checking for data via the socket.

        If a message was retrieved, it will be sent to <self.callback>.
        This function never returns.

        If <self.nick> is already in use, this will raise a
        <ValueError>.
        """
        while True:
            irc_msg = self.__receive()
            if len(irc_msg) > 0:
                self.log('Received message {}'.format(irc_msg))
            unavailable = 'Nick/channel is temporarily unavailable'
            if unavailable in irc_msg:
                raise UnavailableError(unavailable)
            elif re.match(r':.*!.* PRIVMSG ##?.* :.*', irc_msg) is not None:
                self.handle(self.__get_message(irc_msg))
            elif 'Nickname is already in use.' in irc_msg:
                raise NickError('Nickname already in use')
            elif 'PING :' in irc_msg:
                self.log('Pinging')
                self.__ping()

    def __ping(self):
        """Pings the server."""
        self.__send_command('PONG :pingis')

    def __receive(self):
        """Returns the next data the server sends (<str>)."""
        return self.__socket.recv(2048).decode('UTF-8').strip('\n\r')


class IRCMessage:
    def __init__(self, channel, nick, msg, is_user):
        """<channel>, <nick>, <msg> are <str>s; <is_user> is <bool>."""
        self.__channel = channel
        self.__nick = nick
        self.__msg = msg
        self.__is_user = is_user

    @property
    def channel(self):
        return self.__channel

    @property
    def nick(self):
        return self.__nick

    @property
    def msg(self):
        return self.__msg

    @property
    def is_user(self):
        return self.__is_user

    def __repr__(self):
        txt = 'User' if self.is_user else 'Not a user'
        return '{} {} ({}): {}'.format(self.channel, self.nick, txt, self.msg)
