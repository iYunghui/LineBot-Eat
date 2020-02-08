import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

from fsm import TocMachine
from utils import send_text_message, send_button_message, send_image_url

load_dotenv()

machine = TocMachine(
    states=["user", "search", "showsearch", "searcherror", "choose", "eat", "contribute", "upload"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "search",
            "conditions": "is_going_to_search",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "choose",
            "conditions": "is_going_to_choose",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "contribute",
            "conditions": "is_going_to_contribute",
        },
        {
            "trigger": "advance",
            "source": "search",
            "dest": "showsearch",
            "conditions": "vaild",
        },
        {
            "trigger": "advance",
            "source": "search",
            "dest": "searcherror",
            "conditions": "invaild",
        },
        {
            "trigger": "advance",
            "source": "searcherror",
            "dest": "contribute",
            "conditions": "is_going_to_contribute",
        },
        {
            "trigger": "advance",
            "source": "choose",
            "dest": "eat",
            "conditions": "is_going_to_eat",
        },
        {
            "trigger": "advance",
            "source": "contribute",
            "dest": "upload",
            "conditions": "is_going_to_upload",
        },
        {"trigger": "advance", "source": ["search", "showsearch", "searcherror", "choose", "eat", "contribute", "upload"], "dest": "user", "conditions": "is_going_to_user",},
        {"trigger": "go_back", "source": ["search", "showsearch", "searcherror", "choose", "eat", "contribute", "upload"], "dest": "user"}
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response==False and machine.state=="user":
            template = ButtonsTemplate(
                title='你需要甚麼功能?',
                text='選擇你要的功能',
                actions=[
                    MessageTemplateAction(
                        label='搜尋餐廳',
                        text='搜尋餐廳'
                    ),
                    MessageTemplateAction(
                        label='吃什麼',
                        text='吃什麼'
                    ),
                    MessageTemplateAction(
                        label='我要貢獻',
                        text='我要貢獻'
                    )
                ]
            )
            send_button_message(event.reply_token, "你需要甚麼功能?", template)
        elif response == False and machine.state=="choose":
            send_text_message(event.reply_token, "格式錯誤請重新輸入")   
        elif response == False and machine.state=="contribute":
            send_image_url(event.reply_token, "https://i.imgur.com/JXwzmQX.png")
            send_text_message(event.reply_token, "格式錯誤請重新輸入")   
        elif response == False:
            send_text_message(event.reply_token, "?????")
            
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)