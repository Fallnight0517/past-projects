import numpy as np
import matplotlib.pyplot as plt
import json

# 載入訓練資料
data = np.loadtxt("Group_B_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 建立 one-hot encoding 的對應字典與 lab2 做法不同
#     原本寫的是：label_mapping = {0: 0, 2: 1, 4: 2, 6: 3}
#     需要修改的原因可能是: 原本的寫法是人工撰寫類別與 0, 1, 2, 3 的對應關係，現在只有四種類別還行，但未來萬一遇到上百上千的類別數量還要人工去寫對應的字典會很累，所以改成由程式去執行
category = np.unique(labels)           # 用 unique() 自動去判斷 labels 有哪些不重複的類別
num_category = len(category)           # 類別數量
mapping_encode = {}                    # 建立標籤對應 0, 1, 2, 3 的字典 -> {0: 0, 2: 1, 4: 2, 6: 3}
mapping_decode = {}                    # 建立 0, 1, 2, 3 對應標籤的字典，用於最後計算完要換回原本的標籤 -> {0: 0, 1: 2, 2: 4, 3: 6}
for i, label in enumerate(category):   # 使用 enumerate() 同時提供 i = 0~3 與 category 裡的四種類別
	mapping_encode[label] = i          # mapping_encode 字典會是 <key>:<value> -> label:i
	mapping_decode[i] = label          # mapping_decode 字典則是 i 作為 key 的輸入，對應 value 為 label

# labels 是原本的標籤(0, 2, 4, 6)，現在利用前面建立的字典將 0, 2, 4, 6 與 0, 1, 2, 3 一一對應
mapping_labels = np.array([mapping_encode[i] for i in labels])

# 創建新列表 (樣本數量，4)，初始化為 0
one_hot_labels = np.zeros((len(mapping_labels), 4))

# 改變要變成 1 的位置，index 為第幾筆資料，i 為要變成 1 的位置
index = 0
for i in mapping_labels:
    one_hot_labels[index, i] = 1
    index += 1


# 打亂資料
np.random.seed(seed=42)   # 設定亂數種子
N = len(features)         # 計算有多少筆訓練資料

# 產生亂數排序的 0 ~ 10000，當作已經打亂的索引值
random_index = np.random.permutation(N)  # np.random.permutation 會產生一個 0 ~ N-1 的隨機序列

# 用打亂的索引值，重新調整資料排序
X = features[random_index]         # 經過正規化並打亂的特徵 (features)，也就是待會要拿去計算的 X
Y = one_hot_labels[random_index]   # 經過打亂的標籤 (labels)，也就是待會要拿去計算的 Y


# 分割資料，將一萬筆的訓練資料分成 80% 的訓練集 (train) 與 20% 的驗證集 (val)
split = int(N * 0.8)          # 訓練集與驗證集的分割點

X_train = X[:split]           # X 的所有資料中，在 split 分割點之前的部分指定為訓練集
Y_train = Y[:split]           # Y 的資料同步做分割
X_val = X[split:]             # 在 split 分割點之後的部分則指定為驗證集
Y_val = Y[split:]
Num_train = X_train.shape[0]  # 分割後，計算訓練集的資料數量
Num_val = N - Num_train       # 剩下的就是驗證集的資料數量


# 開始訓練計算前的設定
w = np.random.uniform(-1,1, (784, 4))   #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (784, 4)
b = np.random.uniform(-1,1, (1, 4))     #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1, 4)
lr = 0.08          # 反覆調適後得出可能比較合適的學習率
maxEpoch = 500     # 設定最大世代數
batch_size = 64    # 設定一次 Mini-Batch 要用到的資料量

# 提前取出訓練與驗證的 Y 在 one-hot encoding 的索引 0,1,2,3 ，用於驗證模型的答案是否正確，並計算準確率
# axis=1 為跨欄 (column) 操作
labels_train = np.argmax(Y_train, axis=1)
labels_val = np.argmax(Y_val, axis=1)

# 用來存放每個世代的結果，用於畫圖
lossHistory_train = []
lossHistory_val = []
accHistory_train = []
accHistory_val = []

stop = 0                 # 計算停止條件觸發的次數
Num_epoch = 0            # 在停止世代迴圈時，保存最終跑的世代數
best_epoch = 0           # 紀錄最佳驗證準確率時的世代數
best_accuracy_val = 0.0  # 紀錄目前最高的驗證準確率
best_w = w.copy()        # 紀錄最佳驗證準確率時的權重
best_b = b.copy()        # 紀錄最佳驗證準確率時的偏差


# 開始訓練
for epoch in range(maxEpoch):
	
	# 打亂資料
	indices = np.random.permutation(X_train.shape[0])
	X_train_shuffled = X_train[indices]
	Y_train_shuffled = Y_train[indices]

	# 進行 Mini-Batch 迴圈，每次用 batch_size 的資料量更新權重與偏差
	for i in range(0, Num_train, batch_size):
		# 取得這個 batch 的資料
		X_batch = X_train_shuffled[i : i + batch_size]
		Y_batch = Y_train_shuffled[i : i + batch_size]

		n = X_batch @ w + b  # 計算預測值
	
		# axis=1 表示要跨欄 (column) 尋找最大值
		# keepdims=True 讓 shape 始終維持原狀，才能正確廣播相減
		c = np.max(n, axis=1, keepdims=True)   # 對每個樣本各自取最大值
		y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

		error = Y_batch - y_hat                # 計算誤差

		X_T = np.transpose(X_batch)            # 將 X_train 矩陣轉制
		dw = X_T @ error / batch_size
		w = w + lr*dw                          # 更新權重

		db = np.sum(error, axis=0, keepdims=True) / batch_size
		b = b + lr*db                          # 更新偏差值

	# 以 Mini-Batch 更新完權重與偏差之後，針對完整的訓練集重新計算預測值
	n_train = X_train @ w + b
	c_train = np.max(n_train, axis=1, keepdims=True)
	y_hat = np.exp(n_train - c_train) / np.sum(np.exp(n_train - c_train), axis=1, keepdims=True)
	
	# 計算 Cross-Entropy Loss
	loss_train = -np.sum(Y_train*np.log(y_hat)) / Num_train
	lossHistory_train.append(loss_train)   # 將算好的 loss 加入 lossHistory

	# 開始驗證，計算準確率
	n_val = X_val @ w + b                  # 計算預測值
	c_val = np.max(n_val, axis=1, keepdims=True)  # 對每個樣本各自取最大值
	y_hat_val = np.exp(n_val-c_val) / np.sum(np.exp(n_val-c_val), axis=1, keepdims=True)  # 計算 softmax

	# 計算驗證資料的 Loss，用於畫圖
	loss_val = -np.sum(Y_val*np.log(y_hat_val)) / Num_val
	lossHistory_val.append(loss_val)

	# 計算驗證準確率
	max_val = np.argmax(y_hat_val, axis=1)  # 取驗證預測值中最高的
	accuracy_val = np.sum(max_val == labels_val) / Num_val  # 加總分類正確的樣本數並除以驗證資料的總樣本數，得出準確率
	accHistory_val.append(accuracy_val)

	# 計算訓練資料的準確率
	max_train = np.argmax(y_hat, axis=1)
	accuracy_train = np.sum(max_train == labels_train) / Num_train
	accHistory_train.append(accuracy_train)

	print(f"第 {epoch+1:3d} 世代，驗證集的準確率為 {accuracy_val:.4f}, Loss 為 {loss_val:.4f}，訓練集的準確率為 {accuracy_train:.4f}, Loss 為 {loss_train:.4f}")
	Num_epoch = epoch  # 紀錄目前世代數

	# 設定終止條件: 如果目前的驗證準確率比最好的驗證準確率低時，紀錄次數，最多容忍連續 20 次下降就停止
	if accuracy_val > best_accuracy_val:  # 如果目前的驗證準確率比最好的驗證準確率還要高
		best_accuracy_val = accuracy_val  # 更新最好的驗證準確率
		best_epoch = epoch                # 更新最好的世代數
		best_w = w.copy()                 # 記錄在最好的驗證準確率之下的權重
		best_b = b.copy()                 # 記錄最好的偏差
		stop = 0                          # 重置容忍的次數
	else:                  # 驗證準確率比最好的低
		stop += 1          # 目前容忍次數+1
		print("觸發終止條件，目前已觸發次數: " + str(stop))
		if stop >= 20:     # 如果停止條件已經連續觸發 20 次，就正式停止
			print("停止世代迴圈!")
			Num_epoch = epoch  # 記錄跑了多少世代
			break

print("訓練已停止，最終結果:")
print(f"學習率: {lr}")

#print(f"批次大小: {batch_size}")
#print(f"訓練集的準確率為 {accHistory_train[best_epoch]}，損失值為 {lossHistory_train[best_epoch]}")
print(f"驗證集的準確率為 {accHistory_val[best_epoch]}，損失值為 {lossHistory_val[best_epoch]}")
print(f"停止世代數: {Num_epoch+1}")

# 開始畫圖 - Loss
plt.figure(figsize=(6,4))
plt.plot(lossHistory_train, color="blue", label="Train loss")
plt.plot(lossHistory_val, color="orange", label="Validation loss")
plt.xlabel("Epoch")                      # 加上 X 軸標題
plt.ylabel("Loss")                       # 加上 Y 軸標題
plt.title("GroupB_Loss")                 # 圖片標題
plt.legend(loc="upper right")            # 說明框的位置
plt.savefig("./output/output_loss.png")  # 儲存圖片，先儲存再清空
#plt.show()  # 提交時註解 show
plt.clf()    # 清空圖片

# 開始畫圖 - Accuracy
plt.plot(accHistory_train, color="blue", label="Train accuracy")
plt.plot(accHistory_val, color="orange", label="Validation accuracy")
plt.xlabel("Epoch")                          # 加上 X 軸標題
plt.ylabel("Accuracy")                       # 加上 Y 軸標題
plt.title("GroupB_Accuracy")                 # 圖片標題
plt.legend(loc="lower right")                # 說明框的位置
plt.savefig("./output/output_accuracy.png")  # 儲存圖片，先儲存再清空
#plt.show()  # 提交時註解 show
plt.clf()    # 清空圖片

# 輸出成 json 格式
with open("./output/output.json", "w") as file:
	json.dump({
		"Learning rate": lr,
		"Epoch": Num_epoch+1,
		"Batch size": batch_size,
		"Final train accuracy": accHistory_train[best_epoch],
		"Validation accuracy": accHistory_val[best_epoch],
		"Final train loss": lossHistory_train[best_epoch],
		"Final validation loss ": lossHistory_val[best_epoch]
		}, file)


# 驗證 test

# 載入測試資料
test_data = np.loadtxt("Group_B_test.csv", delimiter=',', skiprows=1)
test_data = test_data / 255.0         # 將特徵正規化處理

n = test_data @ best_w + best_b       # 用最好的權重與偏差計算預測值
c = np.max(n, axis=1, keepdims=True)  # 對每個樣本各自取最大值
y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

max_test = np.argmax(y_hat, axis=1)   # 取最高的
testlabel_mapping = {0: 0, 1: 2, 2: 4, 3: 6}  # 對應回原本的標籤名稱
predictions = np.array([testlabel_mapping[i] for i in max_test])

# 將分類結果輸出成 json 格式
with open("./output/test_set_prediction.json", "w") as file:
	json.dump({
		# predictions 為 Numpy array，json 無法輸出，因此加上 tolist()，將其轉為 list 就可以正常輸出了
		"Predictions": predictions.tolist()
		}, file)

