from transitions.extensions import GraphMachine
from linebot import LineBotApi
from utils import send_text_message, send_button_message, send_carousel_message, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, CarouselTemplate, CarouselColumn, MessageTemplateAction

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection("restaurant")


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_user(self, event):
        text = event.message.text
        return text.lower() == "不要"

    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "搜尋餐廳"

    def is_going_to_choose(self, event):
        text = event.message.text
        return text.lower() == "吃什麼"

    def is_going_to_contribute(self, event):
        text = event.message.text
        return text.lower() == "我要貢獻"

    def is_going_to_eat(self, event):
        text = event.message.text

        if text == "":
            return False
        else:
            return True

    def is_going_to_upload(self, event):
        text = event.message.text

        textlist = text.split(' ')
        if len(textlist) != 4:
            return False
        else:
            return True

    # search
    def vaild(self, event):
        text = event.message.text
        
        find = False
        restaurants = doc_ref.get()
        for res in restaurants:
            name = res.to_dict()['name']
            if name == text.lower():
                find = True

        return find

    def invaild(self, event):
        text = event.message.text
        
        notfind = True
        restaurants = doc_ref.get()
        for res in restaurants:
            name = res.to_dict()['name']
            if name == text.lower():
                notfind = False

        return notfind

    def on_enter_user(self, event):
        print("I'm entering user")

        reply_token = event.reply_token
        template = ButtonsTemplate(
            title='你需要甚麼功能?',
            text='選擇你要的功能',
            actions=[
                MessageTemplateAction(
                    labl='搜尋餐廳',
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
        send_button_message(reply_token, "你要幹嗎?", template)

    def on_enter_search(self, event):
        print("I'm entering search")

        reply_token = event.reply_token
        send_text_message(reply_token, "輸入你要搜尋的餐廳名稱：")
        
        send_text_message(reply_token, "測試：")

    def on_enter_showsearch(self, event):
        print("I'm entering showsearch") 
        text = event.message.text                                                                                                                                                                                                                                                                                                                            

        reply_token = event.reply_token
        restaurants = doc_ref.get()
        for res in restaurants:
            name = res.to_dict()['name']
            if name == text.lower():
                location = '位置: {}'.format(res.to_dict()['location'])
                res_type = '種類: {}'.format(res.to_dict()['type'])
                price = '價位: {}'.format(res.to_dict()['price'])
                template = ButtonsTemplate(
                    title=name + " 餐廳資訊如下:",
                    text=location + '\n' + res_type + '\n' + price,
                    actions=[
                        MessageTemplateAction(
                            label='知道了',
                            text='知道了'
                        )
                    ]
                )
                break

        send_button_message(reply_token, "這間餐廳的資訊如下", template)
        self.go_back()
    
    def on_exit_showsearch(self):
        print("Leaving showsearch")

    def on_enter_searcherror(self, event):
        print("I'm entering searcherror")
        text = event.message.text
        
        reply_token = event.reply_token
        template = ButtonsTemplate(
            title='沒有' + text + '這間餐廳',
            text='你要貢獻嗎?',
            actions=[
                MessageTemplateAction(
                    label='不要',
                    text='不要'
                ),
                MessageTemplateAction(
                    label='我要貢獻',
                    text='我要貢獻'
                )
            ]
        )
        send_button_message(reply_token, "沒有這間餐廳，你要貢獻嗎?", template)

    def on_enter_choose(self, event):
        print("I'm entering choose")

        reply_token = event.reply_token
        send_text_message(reply_token, "輸入格式: 位置\n範例: 育樂街")

    def on_enter_eat(self, event):
        print("I'm entering eat")

        reply_token = event.reply_token
        text = event.message.text

        data = 0
        restaurants = doc_ref.get()
        res_columns = []
        restaurant_text = "你的輸入為: " + text
        for res in restaurants:
            location = res.to_dict()['location']
            if location == text.lower():
                name = res.to_dict()['name']
                res_type = '種類: {}'.format(res.to_dict()['type'])
                price = '價位: {}'.format(res.to_dict()['price'])
                add = CarouselColumn(
                    thumbnail_image_url='https://www.publicdomainpictures.net/pictures/240000/nahled/restaurant-employee.jpg',
                    title=name,
                    text='位置: ' + location + '\n' + res_type + '\n' + price,
                    actions=[
                        MessageTemplateAction(
                            label='知道了',
                            text='知道了'
                        )
                    ]
                )
                res_columns.append(add)
                data = data+1

        if data == 0:
            restaurant_text = restaurant_text + '\n' + "沒有相關的資料，無法推薦!"
            send_text_message(reply_token, restaurant_text)
            self.go_back()
        else:
            template = CarouselTemplate(
                columns=res_columns
            )
            send_carousel_message(reply_token, "推薦餐廳", template)
            self.go_back()

    def on_exit_eat(self):
        print("Leaving eat")

    def on_enter_contribute(self, event):
        print("I'm entering contribute")

        reply_token = event.reply_token
        send_text_message(reply_token, "上傳格式: 店名 位置 類型 價位\n(以空白分割)\n範例: 鹿杯飲食 育樂街 丼飯 80")

    def on_enter_upload(self, event):
        print("I'm entering upload")

        reply_token = event.reply_token
        text = event.message.text

        textlist = text.split(' ')
        name = textlist[0]
        location = textlist[1]
        restaurant_type = textlist[2]
        price = textlist[3]
            
        doc = {
            'name': name,
            'location': location,
            'type': restaurant_type,
            'price': price,
        }
        doc_ref.add(doc) 
        print(doc)
        send_text_message(reply_token, "已上傳成功")
        self.go_back()

    def on_exit_upload(self):
        print("Leaving upload")
