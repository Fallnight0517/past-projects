# Past projects
> 在這裡整理做過的大大小小的東西

## 課程作業
### 資料庫系統概論 - 展覽購票網站 (Database)
- 利用 Python Flask 連接後端伺服器的 SQL Server，前端功能包含會員註冊、展覽瀏覽、購票與票卷夾，可以在本地的客戶端連上伺服器的資料庫，模擬一個展覽購票系統。
- app\.py
	- 在伺服器持續運行，隨時接收網站請求
- init_database.py
	- 初始化資料庫
- templates 存放前端網頁的 HTML 檔
	- static 存放上傳的展覽圖片
	- admin 網站的後台管理介面，只有 admin 可以看到

### 網路概論 - 結合 LINE Bot 聊天機器人與爬蟲 (Network)
- 結合爬蟲與 LINE Messaging API 實現的 LINE Bot 聊天機器人，在服務啟動後，就可以在 LINE 聊天室自動回覆即時的天氣、股價與新聞文章。
- app\.py
	- 負責接收使用者從 LINE 輸入的訊息，呼叫 crawler\.py 爬取資料後回傳到 LINE
- crawler\.py
	- 負責去各個網站抓取特定 CSS 屬性帶有的資料

### 深度學習 - Python 實作神經網路 (Deeplearning)
- 在深度學習的課程作業中，從零 "手刻" 神經網路的底層數學運算、練習 Python 的基礎矩陣操作，最後在僅使用 NumPy 的情況下，實作單一神經元的梯度下降法與進階的類別分類問題 (Multinomial Logistic Regression)，從單層到多層的網路架構，逐步提升模型訓練與驗證的準確度。
- Lab 1
	- Lab 1-1 
		- 實作皮薩諾週期序列，並透過 matplotlib 畫成折線圖
	- Lab 1-2
		- 使用老師提供的資料集，實作一個神經元擬合資料並將回歸直線以及資料點透過 matplotlib 描繪出來，同時記錄訓練過程中的 mse loss 變化
- Lab 2
	- 利用 Fashion-MNIST 數據集，以單層網路架構的梯度下降法實作四分類問題。
	- Group A 類別差異大，分類難度較低
	- Group B 類別差異小，分類難度較高

### 用托放式設計網站平台製作網站
- 利用 [Wix](https://www.wix.com/) 製作: https://sherrychen517.wixsite.com/renowang


## 社團任務
### NISRA (Community)
- Web 課程
	- 簡報: https://slides.com/fallnight/web-i
	- 用 lab 帶領學員一步步寫出一個簡易網頁
		- Lab0x1.html 建立 HTML 框架
		- Lab0x2.html 為網頁加入色彩
		- Lab0x3.html 新增輸入框互動功能
	- CTF 出題
		- GETit
			- 修改網址後方的參數，才能跳轉到藏有 flag 的頁面
		- ψ(｀∇´)ψ
			- 通往 flag 的路徑藏在 robot.txt 內，需要修改網址才能找到

- PHP 課程
	- 簡報: https://slides.com/fallnight/php
	- CTF 出題
		- phptrue
			- 需要透過 php 的特殊語法設定，修改網址參數，繞過 if 判斷拿到 flag

- 封包與 Wireshark 課程
	- 簡報: https://slides.com/fallnight/packet-with-wireshark
	- 配合課程教學用的封包們
		- lab.pcapng 藏了 flag 的封包
		- xss.pcapng 展示遇到 XSS 攻擊的封包
		- syn_flood.pcapng 展示遇到 SYN Flood 攻擊的封包
	- CTF 出題
		- final_login.pcapng
			- 錄製正在登入的封包，密碼就是 flag
		- final_tcp.pcapng
			- 將 flag 分段藏在多個 TCP 封包中
		- final_needDecode.pcapng
			- 將 flag 藏在 HTTP 的 Header 當中
		- final_pic.pcapng
			- 錄製正在請求圖片的封包，需要將封包內的二進位圖片資料轉換回 jpg 檔，才能看到圖片中的 flag
