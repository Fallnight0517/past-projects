import requests
from bs4 import BeautifulSoup

def get_weather(location):
    # 建立地點與對應查詢網址的對照表
    # 如果使用者輸入的地點不在這裡，則會導向預設的「新北市」
    location_map = {
        "台北": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E8%87%BA%E5%8C%97%E5%B8%82/%E8%87%BA%E5%8C%97%E5%B8%82-2306179",
        "新北": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E6%96%B0%E5%8C%97%E5%B8%82/%E6%96%B0%E5%8C%97%E5%B8%82-90717580",
        "桃園": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E6%A1%83%E5%9C%92%E5%B8%82/%E6%A1%83%E5%9C%92%E5%B8%82-2298866",
        "台中": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E8%87%BA%E4%B8%AD%E5%B8%82/%E8%87%BA%E4%B8%AD%E5%B8%82-2306181",
        "台南": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E8%87%BA%E5%8D%97%E5%B8%82/%E8%87%BA%E5%8D%97%E5%B8%82-2306182",
        "高雄": "https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E9%AB%98%E9%9B%84%E5%B8%82/%E9%AB%98%E9%9B%84%E5%B8%82-2306180"
    }

    # 取得使用者輸入的對應的網址
    target_url = location_map.get("新北") # 預設值
    for key in location_map:
        if key in location:
            target_url = location_map[key]
            break

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 開始爬蟲
        
        # 預設值
        temp = "未知"
        icon = "未知"


        # 抓取溫度

        # 依據 Yahoo 氣象的實際 HTML 寫法，若要抓取溫度就需要先讓 BeautifulSoup 找到 class 名稱帶有 'temperature-forecast' 的 div 標籤
        forecast_block = soup.select_one('.temperature-forecast') 
        
        if forecast_block: # 如果抓取成功
            temp_element = forecast_block.find('span', class_='celsius') # 進一步抓取含有溫度文字的 class 名稱帶有 'celsius' 的 span 標籤
            if temp_element: # 如果抓取成功，將抓到的文字存取為單純的文字，去掉可能有的空白字元或換行
                temp = temp_element.text.strip()

            # 繼續抓取天氣狀況 (ex：陰、多雲等)
            weather_container = forecast_block.parent
            if weather_container:
                # 以天氣圖示的 alt 屬性，抓取天氣狀況的文字
                # 由於 Yahoo 氣象的實際 HTML 用動態的 CSS 去設定天氣狀態的文字的 class 名稱，所以無法像溫度一樣抓取，這裡改用圖片屬性做替代
                img_element = weather_container.find('img')
                if img_element:
                    icon = img_element.get('alt')
        
        else:
            return f"找不到 {location} 的天氣資訊"

        # 回傳最終整理好的字串
        return f"【{location} 天氣資訊】\n氣溫：{temp}°C\n狀況：{icon}"

    except Exception as e:
        return f"讀取氣象失敗：{str(e)}"



def get_stock(company_name):
    # 定義股票代碼對照表
    stock_map = {
        "台積電": "2330",
        "鴻海": "2317",
        "聯發科": "2454",
        "長榮": "2603",
        "0050": "0050"
    }
    
    # 取得代碼，若找不到則假設使用者輸入的是代碼
    stock_id = stock_map.get(company_name)
    if not stock_id:
        if company_name.isdigit():
            stock_id = company_name
            # 如果是直接輸入代碼，顯示名稱就暫時用代碼代替
            display_name = stock_id 
        else:
            return f"抱歉，我目前還不認識「{company_name}」，請嘗試輸入「台積電」或「2330」。"
    else:
        # 如果是輸入中文 (如台積電)，就直接用這個中文當作顯示名稱
        display_name = company_name

    url = f"https://tw.stock.yahoo.com/quote/{stock_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 開始爬蟲
        
        # 抓取價格的 CSS 選擇器
        price_element = soup.select_one(r'.Fz\(32px\)')
        
        if price_element:
            price = price_element.text.strip()
            return f"【股價資訊】\n股票：{display_name} ({stock_id})\n現價：{price} 元"
        else:
            return "抓取失敗：找不到股價資訊，可能是股市未開盤或網頁改版。"

    except Exception as e:
        return f"系統錯誤：{e}"


def get_news():
    # 設定要抓取的 ⌈TechNews 科技新報⌋ 的網址
    url = "https://technews.tw/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 開始爬蟲
        
        # 使用 CSS 選擇器抓取所有文章標題
        # TechNews 的標題都在 h1 class="entry-title" 裡面的 a 標籤
        articles = soup.select('h1.entry-title a')
        
        # 設定要用於回傳的字串
        news_data = []
        
        if not articles:
            return "抓取失敗：找不到新聞文章"

        # 迴圈抓取前 3 則，使用 [:3] 切片語法只取前三個
        for index, item in enumerate(articles[:3]):
            title = item.text.strip()
            link = item.get('href')
            
            # 格式化每一則新聞
            news_data.append(f"{index + 1}. {title}\n{link}")

        # 組合最終字串
        result = "【最新科技新聞】\n\n" + "\n\n".join(news_data)
        return result

    except Exception as e:
        return f"讀取新聞失敗：{str(e)}"


'''
# 用於單獨執行這個檔案，測試爬蟲是否成功
if __name__ == "__main__":
    print(get_weather("台北"))
    print(get_stock("台積電"))
    print(get_news())
'''