# IRC Bot

This is an IRC bot I wrote for my first semester project in my CSE undergraduate course.

# Installation

## Prerequisites

- [Python 3](https://www.python.org/downloads/)

## Installing

1. Clone the repository using one of the following methods.
    - HTTPS: `git clone https://github.com/neelkamath/irc-bot.git`
    - SSH: `git clone git@github.com:neelkamath/irc-bot.git`
1. `cd irc-bot`
1. Create a file `src/config.json` with the following data.

    |Key|Data type|Explanation|Example|
    |---|---------|-----------|-------|
    |`"server"`|`string`|The IRC server to connect to.|`"chat.freenode.net"`|
    |`"channels"`|`array` of `string`s|The channels the bot should initially connect to.|`["##nope", "#python"]`|
    |`"nick"`|`string`|The bot's nickname.|`"pesu_bot"`|
    
    For example:
    ```json
    {
      "server": "chat.freenode.net",
      "channels": [
        "##nope"
      ],
      "nick": "pesu_bot"
    }
    ```
    
# Usage

- Windows: `python src/main.py`
- Other: `python3 src/main.py`

# License

This project is under the [MIT License](LICENSE).
