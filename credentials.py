import os


class Keys:
    def __init__(self) -> None:
        self.gpt_token = os.environ.get('GPT_TOKEN')
        self.bot_token = os.environ.get('BOT_TOKEN')
