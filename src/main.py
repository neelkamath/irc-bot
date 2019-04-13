#!/usr/bin/env python3

"""Starts the bot."""

import json

import irc


class Bot(irc.IRCBot):
    """Use <handle> for the <irc.IRCBot>'s callback."""

    def __init__(self, trigger, nick, server, channels=None, port=6667,
                 should_log=False):
        """Initializes values.

        Keyword arguments:
            trigger -- <str>; the bot will only respond to messages sent
                       having this prefix (e.g., if the trigger is <'!'>
                       the bot will respond to <'!translate hello'>; if
                       the trigger is <'bob: '>, the bot will respond to
                       <'bob: translate hello'>)
            nick -- <str>; bot's nickname
            server -- <str>; e.g.: <'chat.freenode.net'>
            channels -- <set> of <str>s; e.g.: <{'##testing'}>
            port -- <int>
            should_log -- <bool>; whether to print events such as
                          channel joins

        This bot has been built to respond to messages in the form of:
            <TRIGGER><CMD> <MESSAGE>
        So if <TRIGGER> is <'my_bot: '>, <CMD> is <'join'>, and
        <MESSAGE> is <'##python #android'>, the user should send a
        message of the form:
            my_bot: join ##python #android
        """
        self.__trigger = trigger
        super().__init__(nick, server, channels, port, should_log)

    @property
    def trigger(self):
        """Returns this bot's trigger (<str>)."""
        return self.__trigger

    def handle(self, irc_msg):
        self.log('Got message {}'.format(irc_msg))
        if irc_msg.msg.startswith(self.trigger):
            msg = irc_msg.msg[len(self.trigger):]
            parts = msg.split(' ', 1)
            cmd = parts[0]
            msg = parts[1] if len(parts) == 2 else None
            self.reply(irc_msg.channel, irc_msg.nick, cmd, msg)

    def reply(self, channel, nick, cmd, msg=None):
        """Responds to users.

        Keyword arguments:
            channel -- <str>; channel message came from
            nick -- <str>; nickname of user who sent the message
            cmd -- <str>; e.g.: <'join'>
            msg -- <str>; e.g.: <'##python #android'>
        """
        if cmd == 'help':
            self.__help(nick, channel)
        elif cmd == 'join':
            self.__join_channels(set(msg.split()))
        else:
            self.__show_help(nick, channel)

    def __show_help(self, nick, channel):
        """Responds to users incorrectly using the bot.

        Keyword arguments:
            nick -- <str>; nickname of user incorrectly using the bot
            channel -- <str>; channel user <nick> is in
        """
        reply = ("{}: I didn't understand that. ".format(nick)
                 + 'Check my commands with <{}: help>.'.format(self.nick))
        self.send_message(reply, channel)

    def __join_channels(self, channels):
        """Joins the channels <channels> (<set> of <str>s).

        If this bot is already in one of the channels specified in
        <channels>, then it will state such instead of trying to join
        that channel.
        """
        for channel in channels:
            if channel in self.channels:
                self.send_message("I'm already in {}".format(channel), channel)
            else:
                self.join_channel(channel)

    def __help(self, nick, channel):
        """Messages how to use the bot.

        Keyword arguments:
            nick -- <str>; the nickname of the user who requested the
                    help message
            channel -- <str>; the channel to send the help message to
        """
        commands = [
            CommandInfo(self.trigger, 'help',
                        "Explains the bot's commands", 'help'),
            CommandInfo(self.trigger, 'join', 'Joins channels',
                        'join #python ##android',
                        'join <space-separated list of channels>')
        ]
        commands = ', '.join([str(cmd) for cmd in commands])
        self.send_message('{}: Commands => {}'.format(nick, commands), channel)


class CommandInfo:
    def __init__(self, trigger, cmd, explanation, example, syntax=None):
        """Initializes values.

        Keyword arguments:
            trigger -- <str>; the trigger for this command (e.g., <'!'>)
            cmd -- <str>; the command (e.g., <'join'>)
            explanation -- <str>; explanation of what it does (e.g.,
                           <'joins channels'>)
            example -- <str>; example command usage (e.g.,
                       <'join #python ##android'>)
            syntax -- <str>; how to use command (e.g.,
                      <'join <space-separated list of channels>'>)
        """
        self.__trigger = trigger
        self.__cmd = cmd
        self.__explanation = explanation
        self.__example = example
        self.__syntax = syntax

    @property
    def trigger(self):
        """Returns this command's trigger (<str>)."""
        return self.__trigger

    @property
    def cmd(self):
        """Returns this command's name (<str>)."""
        return self.__cmd

    @property
    def explanation(self):
        """Returns this command's explanation (<str>)."""
        return self.__explanation

    @property
    def example(self):
        """Returns this command's example (<str>)."""
        return self.__example

    @property
    def syntax(self):
        """Returns this command's syntax (<str> or <None>)."""
        return self.__syntax

    def __repr__(self):
        txt = ' ({})'.format(self.syntax) if self.syntax is not None else ''
        return '{}{} - {} (e.g., {}{})'.format(
            self.cmd, txt, self.explanation, self.trigger, self.example)


def main():
    """Starts the program."""
    config = json.load(open('src/config.json'))
    Bot('{}: '.format(config['nick']), config['nick'], config['server'],
        set(config['channels']), should_log=True)


if __name__ == '__main__':
    print('Starting program...')
    main()
