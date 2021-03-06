import json
from typing import NamedTuple

import requests
from django.http import HttpRequest
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View

from applications.blog.models import Post
from applications.bots.apis import TG_API
from django.conf import settings


class ChatT(NamedTuple):
    id: str


class MessageT(NamedTuple):
    id: str
    text: str
    chat: ChatT
    username: str


class TelegramBotView(View):
    def receive_message_from_user(self) -> MessageT:
        payload = json.loads(self.request.body)

        message = payload["message"]
        message_id = message["message_id"]
        text: str = message["text"]

        chat = message["chat"]
        chat_id = chat["id"]

        username: str = chat["username"]

        chat = ChatT(id=chat_id)
        message = MessageT(chat=chat, id=message_id, text=text, username=username)

        return message

    @staticmethod
    def _send_message_to_user(chat_id: str, text: str):
        api_url = TG_API.format(token=settings.TG_BOT_TOKEN, method="sendMessage")

        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        tg_response = requests.post(api_url, json=payload)
        print(tg_response.status_code)
        print(tg_response.json())

    def post(self, _request: HttpRequest):
        try:
            message = self.receive_message_from_user()

            reply = message.text.upper()

            self._send_message_to_user(message.chat.id, reply)

            self.blog_post(_request)

        finally:
            return HttpResponse(content="")

    def blog_post(self, _request: HttpRequest):

        message = self.receive_message_from_user()

        content_rec = message.text.rsplit(sep=";;")[0]
        title_rec = message.text.rsplit(sep=";;")[1]
        author = message.username

        f = Post.objects.create(title=title_rec, content=content_rec, author=author)

        f.save()

    @staticmethod
    def register(_request: HttpRequest):
        api_url = TG_API.format(token=settings.TG_BOT_TOKEN, method="setWebhook")
        my_bot_path = reverse_lazy("bots:bots-telegram")
        my_bot_url = f"https://{settings.HOST}{my_bot_path}"
        tg_response = requests.post(api_url, data={"url": my_bot_url})

        return HttpResponse(
            content=json.dumps(tg_response.json()), content_type="application/json"
        )
