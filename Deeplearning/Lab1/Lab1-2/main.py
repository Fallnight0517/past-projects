import json
import numpy as np
import matplotlib.pyplot as plt

with open("lab1.2_train_data.json","r") as file:
	data = json.load(file)            #完整讀取 lab1.2_train_data.json 的資料

np.random.seed(seed=42)               #設定亂數種子
X = np.array(data["x"], dtype=float)  #分別讀取 key = x 的 data 資料，且資料型態轉成 float 再存入
Y = np.array(data["y"], dtype=float)  #分別讀取 key = y 的 data 資料，且資料型態轉成 float 再存入
w = np.random.uniform(-1,1, (1,))     #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (1,)
b = np.random.uniform(-1,1, (1,))     #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1,)
lr = 0.001                            #嘗試使用學習率 lr = 0.001

lossHistory = []            #用來記錄 mse loss
N = len(X)                  # N 資料數量為 X 的數量(長度)

#訓練前先算一次 mse loss
loss = 0                    #用來加總所有計算後得出的 loss，之後再一次取平均
for i in range(N):          #使用所有的輸入資料計算 mse loss
	y = w @ X[i] + b[0]     #計算 w 與 X 的內積，再加上 b ，算出預測值
	loss += (y-Y[i]) ** 2   #計算與標準答案(Y)的偏差，平方後加總到 loss

loss = loss / N / 2         #得出平均
lossHistory.append(loss)    #將算好的 loss 加入 lossHistory

marEpoch = 50                             #訓練完整資料的次數
for epoch in range(marEpoch):
	for i in range(len(X)):
		y = w @ X[i] + b[0]               #計算 w 與 X 的內積，再加上 b ，算出預測值
		w = w + lr * (Y[i]-y) * X[i][0]   #用梯度下降更新 w
		b = b + lr * (Y[i]-y)             #用梯度下降更新 b

	loss = 0                              #計算 mse loss
	for i in range(N):
		y = w @ X[i] + b[0]               #計算 w 與 X 的內積，再加上 b ，算出預測值
		loss += (y-Y[i]) ** 2             #計算與標準答案(Y)的偏差，平方後加總到 loss

	loss = loss / N / 2                   #得出平均
	lossHistory.append(loss)              #將算好的 loss 加入 lossHistory


#用 matplotlib 畫圖
plt.figure(figsize=(6,4))

x_max = X.max()                        #取 X 資料裡的最大值
x_min = X.min()                        #取 X 資料裡的最小值
xis = np.linspace(x_min, x_max, 100)   #生成 X 的等距區間資料，用於後續畫圖的 X 軸
yis = w * xis + ｂ                     #計算最後回歸直線的預測值

#開始畫圖 - result
plt.plot(X, Y, color="blue", marker='o', linestyle='None')
plt.plot(xis, yis, color="red", label="regression line")

plt.title("Regression")         #圖片標題
plt.legend(loc="upper left")    #說明框的位置

plt.savefig("./output/lab1.2_result.png")  #儲存圖片，先儲存再清空
#plt.show() #提交時註解show
plt.clf()  #清空圖片


#開始畫圖 - loss
plt.plot(lossHistory, color="blue", label="mse loss")

plt.title("Loss")               #圖片標題
plt.legend(loc="upper right")   #說明框的位置

plt.savefig("./output/lab1.2_loss.png")    #儲存圖片，先儲存再清空
#plt.show() #提交時註解show
plt.clf()  #清空圖片

#輸出成 json 格式
with open("./output/lab1.2_output.json", "w") as file:
	json.dump({
		"final_weight": w[0],
		"final_bias": b[0],
		"loss_history": lossHistory,
		"num_epochs": marEpoch,
		"learning_rate": lr
		}, file)
