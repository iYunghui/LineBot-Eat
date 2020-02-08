import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"


def send_image_url(id, img_url):
    image = ImageSendMessage(
        original_content_url=img_url,
        preview_image_url=img_url
    )

    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(id, image)

    return "OK"

def send_button_message(id, text, buttons):
    buttons_template = TemplateSendMessage(
        alt_text = text,
        template = buttons
    )

    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(id, buttons_template)

    return "OK"

def send_carousel_message(id, text, carousel):
    carousel_template = TemplateSendMessage(
        alt_text = text,
        template = carousel
    )

    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(id, carousel_template)

    return "OK"

