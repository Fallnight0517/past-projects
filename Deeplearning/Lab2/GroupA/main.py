import numpy as np
import matplotlib.pyplot as plt
import json

# 載入訓練資料
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 將 label 做 one-hot encoding

# 將 0, 1, 8, 9 對應到 0, 1, 2, 3
# {} 在 python 表示為 字典，會有成對的 Key 和 Value，例如 Key = 8，對應的 Value = 2
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}

# 用 for 迴圈查看 label 內一筆筆的樣本，存取每一筆對應的 0, 1, 2, 3
encoded_labels = np.array([label_mapping[i] for i in labels])

# 創建新列表 (樣本數量，4)，初始化為 0
one_hot_labels = np.zeros((len(encoded_labels), 4))

# 改變要變成 1 的位置，index 為第幾筆資料，i 為要變成 1 的位置
index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1


# 開始訓練計算前的設定
np.random.seed(seed=42)               # 設定亂數種子
N = 10000                             # 有一萬筆訓練資料

# 打亂資料
# 產生亂數排序的 0 ~ 10000，當作已經打亂的索引值
random_index = np.random.permutation(N)  # np.random.permutation 會產生一個 0 ~ N-1 的隨機序列

# 用打亂的索引值，重新調整資料排序
X = features[random_index]         # 經過正規化並打亂的特徵 (features)，也就是待會要拿去計算的 X
Y = one_hot_labels[random_index]   # 經過打亂的標籤 (labels)，也就是待會要拿去計算的 Y

# 分割資料，將一萬筆的訓練資料分成 80% 的訓練集 (train) 與 20% 的驗證集 (val)
N_train = int(N * 0.8)
N_val = N - N_train

X_train = X[:N_train]
Y_train = Y[:N_train]

X_val = X[N_train:]
Y_val = Y[N_train:]

# 提前計算訓練與驗證的 Y 在 one-hot encoding 前的 0,1,2,3 ，用於驗證
# axis=1 為跨欄 (column) 操作
labels_train = np.argmax(Y_train, axis=1)
labels_val = np.argmax(Y_val, axis=1)

# 開始訓練
w = np.random.uniform(-1,1, (784, 4))        #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (784, 4)
b = np.random.uniform(-1,1, (1, 4))          #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1, 4)
lr = 0.09          # 反覆調適後得出可能比較合適的學習率
maxEpoch = 500     # 設定最大世代數

# 用來存放每個世代的結果，用於畫圖
lossHistory_train = []
lossHistory_val = []
accHistory_train = []
accHistory_val = []

for epoch in range(maxEpoch):
	n = X_train @ w + b                    # 計算預測值
	
	# axis=1 表示要跨欄 (column) 尋找最大值
    # keepdims=True 讓 shape 始終維持原狀，才能正確廣播相減
	c = np.max(n, axis=1, keepdims=True)   # 對每個樣本各自取最大值
	y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

	error = Y_train - y_hat                # 計算誤差

	X_T = np.transpose(X_train)            # 將 X_train 矩陣轉制
	dw = X_T @ error / N_train
	w = w + lr*dw                          # 更新權重

	db = np.sum(error, axis=0, keepdims=True) / N_train
	b = b + lr*db                          # 更新偏差值

	# 計算 Cross-Entropy Loss
	loss_train = -np.sum(Y_train*np.log(y_hat)) / N_train
	lossHistory_train.append(loss_train)   # 將算好的 loss 加入 lossHistory

	# 開始驗證，計算準確率
	n_val = X_val @ w + b                  # 計算預測值
	c_val = np.max(n_val, axis=1, keepdims=True)  # 對每個樣本各自取最大值
	y_hat_val = np.exp(n_val-c_val) / np.sum(np.exp(n_val-c_val), axis=1, keepdims=True)  # 計算 softmax

	# 計算驗證資料的 Loss，用於畫圖
	loss_val = -np.sum(Y_val*np.log(y_hat_val)) / N_val
	lossHistory_val.append(loss_val)

	# 計算驗證準確率
	max_val = np.argmax(y_hat_val, axis=1)  # 取驗證預測值中最高的
	accuracy_val = np.sum(max_val == labels_val) / N_val  # 加總分類正確的樣本數並除以驗證資料的總樣本數，得出準確率
	accHistory_val.append(accuracy_val)

	# 計算訓練資料的準確率
	max_train = np.argmax(y_hat, axis=1)
	accuracy_train = np.sum(max_train == labels_train) / N_train
	accHistory_train.append(accuracy_train)

	# 設定終止條件: 當驗證準確率下降時終止
	if accuracy_val < accHistory_val[epoch-1]:
		break  # 最終會在第 158 世代停止

# 開始畫圖 - Loss
plt.figure(figsize=(6,4))
plt.plot(lossHistory_train, color="blue", label="Train loss")
plt.plot(lossHistory_val, color="orange", label="Validation loss")
plt.xlabel("Epoch")                      # 加上 X 軸標題
plt.ylabel("Loss")                       # 加上 Y 軸標題
plt.title("GroupA_Loss")                 # 圖片標題
plt.legend(loc="upper right")            # 說明框的位置
plt.savefig("./output/output_loss.png")  # 儲存圖片，先儲存再清空
#plt.show()  # 提交時註解 show
plt.clf()    # 清空圖片

# 開始畫圖 - Accuracy
plt.plot(accHistory_train, color="blue", label="Train accuracy")
plt.plot(accHistory_val, color="orange", label="Validation accuracy")
plt.xlabel("Epoch")                          # 加上 X 軸標題
plt.ylabel("Accuracy")                       # 加上 Y 軸標題
plt.title("GroupA_Accuracy")                 # 圖片標題
plt.legend(loc="lower right")                # 說明框的位置
plt.savefig("./output/output_accuracy.png")  # 儲存圖片，先儲存再清空
#plt.show()  # 提交時註解 show
plt.clf()    # 清空圖片

# 輸出成 json 格式
with open("./output/output.json", "w") as file:
	json.dump({
		"Learning rate": lr,
		"Epoch": maxEpoch,
		"Final train accuracy": accHistory_train,
		"Validation accuracy": accHistory_val,
		"Final train loss": lossHistory_train,
		"Final validation loss ": lossHistory_val
		}, file)


# 驗證 test

# 載入測試資料
test_data = np.loadtxt("Group_A_test.csv", delimiter=',', skiprows=1)
test_data = test_data / 255.0         # 將特徵正規化處理

n = test_data @ w + b                 # 計算預測值
c = np.max(n, axis=1, keepdims=True)  # 對每個樣本各自取最大值
y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

max_test = np.argmax(y_hat, axis=1)   # 取最高的
testlabel_mapping = {0: 0, 1: 1, 2: 8, 3: 9}  # 對應回原本的標籤名稱
predictions = np.array([testlabel_mapping[i] for i in max_test])

# 將分類結果輸出成 json 格式
with open("./output/test_set_prediction.json", "w") as file:
	json.dump({
		# predictions 為 Numpy array，json 無法輸出，因此加上 tolist()，將其轉為 list 就可以正常輸出了
		"Predictions": predictions.tolist()
		}, file)