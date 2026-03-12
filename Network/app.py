from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 匯入另外撰寫的模組
import config
import crawler 

app = Flask(__name__)

# 設定 LINE Bot API
line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭值
    signature = request.headers['X-Line-Signature']
    # 取得請求內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 Webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息的函式
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()  # 使用者傳來的文字
    reply_msg = ""  # 準備回傳的文字


    # 關鍵字判斷
    
    # 處理「天氣」指令
    if user_msg.startswith("天氣"):
        # ex: 將 "天氣 台北" 切割成 ["天氣", "台北"]
        parts = user_msg.split(" ")
        if len(parts) > 1:
            location = parts[1]
            # 呼叫爬蟲程式 crawler.py
            reply_msg = crawler.get_weather(location)
        else:
            reply_msg = "請輸入正確格式：天氣 [地點]\n例如：天氣 台北"

    # 處理「股價」指令
    elif user_msg.startswith("股價"):
        # ex: "股價 台積電"
        parts = user_msg.split(" ")
        if len(parts) > 1:
            company = parts[1]
            reply_msg = crawler.get_stock(company)
        else:
            reply_msg = "請輸入正確格式：股價 [公司名稱]\n例如：股價 台積電"

    # 處理「新聞」指令
    elif user_msg == "新聞":
        reply_msg = crawler.get_news()

    # 處理非定義指令，回傳操作說明
    else:
        reply_msg = (
            "歡迎使用智慧助理！請輸入以下指令：\n"
            "1. 天氣 [地點] (如：天氣 台北)\n"
            "2. 股價 [名稱] (如：股價 台積電)\n"
            "3. 新聞 (查看最新科技新聞)"
        )

    # 回傳訊息給 LINE
    if reply_msg:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg)
        )

# 執行主程式
if __name__ == "__main__":
    app.run(port=5000, debug=True)
