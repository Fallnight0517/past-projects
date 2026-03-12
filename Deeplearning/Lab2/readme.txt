以下 README 的完整內容也可以在我的共筆上審閱：
https://hackmd.io/@gqTNOr7LQHqF73eJwwWLNA/ryAIZ2egWe



# 使用 Claude、Gemini 的對話紀錄

##### 上次作業是只有一行的 json ，現在變 n x 784 的資料量，如何引入資料進 python?

## 如何引入 .csv 內的 784 維的影像像素數據? with Claude
- ### 完整 promt
```
我在嘗試利用 Fashion-MNIST 數據集，用 Python 實作 Multinomial Logistic Regression 與 Softmax Regression，以此完成作業任務，其作業說明請參考附件檔案(深度學習Lab2_作業要求.pdf 與 DL2025_Lab2.pdf)
而附件檔案(Group_A_train.csv)是我預計使用的測資，其影像為大小 28*28  的灰階圖像(即 784 維輸入屬性)，檔案內含4種類別(label)的物品，分別為 0: Tshirt/top、1: Trouser、8: Bag、9: Ankle boot 首先我想先實作引入測資檔案內容的部分，在每一筆樣本被分成了784維的情況下，我該如何引入樣本，進行後續的計算?
```

- 整理過的回答
    - 使用 ```np.loadtxt()``` 讀取 CSV 檔案
        ```data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)```
        - delimiter 為 分隔符號
        - skiprows 為 跳過幾行再開始讀取
            - 設定為 1，跳過標籤那行
    - 分別存取 標籤 與 像素(特徵)
        ```
        labels = data[:, 0].astype(int)
        features = data[:, 1:]
        ```
        - data[:, 0] 存取 data (CSV 檔案的資料)
            - `:` 表示 所有行 與 第 0 列 (label 那列)
            - ```.astype(int)``` c會將資料型態都轉為 int 再存進 label
        - data[:, 1:] 存取 data 的 `:` 所有行 與 `1:` 從第一列到最後一列

### 接下來需要 one-hot encoding，如何在 python 實現?
- 透過這篇文章理解了 one-hot encoding 
- 文章連結:
https://axk51013.medium.com/%E4%B8%8D%E8%A6%81%E5%86%8D%E5%81%9Aone-hot-encoding-b5126d3f8a63
- 所以如何實現?
    - 已知運算時應該是
    ```y_hat = XW + b```
        - X 大小為 10000x784
        - W 大小為 784x4
        - 這樣 XW 矩陣相乘完的大小是 10000x4
    - 所以可以得知 one-hot encoding 後，需要拿來用的矩陣大小是 10000x4
        - 也就是將本來的 4 種 label，```0, 1, 8, 9``` 改成:
        ```
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]]
        ```

    - 對應的樣子

        | 一筆筆的樣本↓，類別名稱-> | 0 | 1 | 8 | 9|
        | --- | --- | --- | --- | --- |
        | 0 | 1 | 0 | 0 | 0 |
        | 1 | 1 | 0 | 0 | 0 |
        | 2 | 0 | 0 | 1 | 0 |
        | 3 | 0 | 0 | 0 | 1 |
        | 4 | 0 | 1 | 0 | 0 |
        | 5 | 0 | 1 | 0 | 0 |
        | ... | ... | ... | ... | ... |
        | n 筆樣本 | ... | ... | ... | ... |

## 如何實作將 label 做 one-hot encoding? with Claude
- ### 完整 promt
```
我在嘗試利用 Fashion-MNIST 數據集，用 Python 實作 Multinomial Logistic Regression 與 Softmax Regression，以此完成作業任務，其作業說明請參考附件檔案(深度學習Lab2_作業要求.pdf 與 DL2025_Lab2.pdf)
而附件檔案(Group_A_train.csv)是我預計使用的測資，其影像為大小 28*28  的灰階圖像(即 784 維輸入屬性)，檔案內含4種類別(label)的物品，分別為 0: Tshirt/top、1: Trouser、8: Bag、9: Ankle boot 
我將使用以下程式碼引入測資
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)
labels = data[:, 0].astype(int)
features = data[:, 1:]
然後將特徵做正規化處理
features = features / 255.0
接下來我想時做 one-hot encoding ，將 label 本來的資料內容，0, 1, 8, 9，轉成大小為 10000*4 的陣列，請參考上述的前提說明，告訴我應該怎麼讓 label 做 one-hot encoding
```

- 收到的回覆
    - 步驟 1: Label Encoding（標籤編碼）
        - 建立映射字典：原始label -> 編碼後label
            ```label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}```
        -  將原始labels轉換為編碼後的labels
            ```encoded_labels = np.array([label_mapping[label] for label in labels])```
    - 步驟 2: One-Hot Encoding
        - 建立 one-hot encoding
            ``` 
            num_classes = 4
            one_hot_labels = np.zeros((len(encoded_labels), num_classes))

            for i, label in enumerate(encoded_labels):
                one_hot_labels[i, label] = 1
            ```
            
## 執行遇到錯誤，如何解決? with Gimini
- ### 完整 promt
```
我要實作Multinomial Logistic Regression，以下是我的程式碼
import numpy as np
import math 

# 載入訓練資料
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 將 label 做 one-hot encoding
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}
encoded_labels = np.array([label_mapping[i] for i in labels])

one_hot_labels = np.zeros((len(encoded_labels), 4))

index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1

# 開始計算
np.random.seed(seed=42)               #設定亂數種子
w = np.random.uniform(-1,1, (784, ))     #隨機取 -1 ~ 1 之間的權重 w
b = np.random.uniform(-1,1, (1,))     #隨機取 -1 ~ 1 之間的偏差 b
lr = 0.01

n = features@w + b
c = max(n)

softmax = np.exp(n-c) / sum(np.exp(n-c))

tri = one_hot_labels - softmax
tri在計算誤差
但此時卻遇到錯誤訊息
tri = one_hot_labels - softmax
          ~~~~~~~~~~~~~~~^~~~~~~~~
ValueError: operands could not be broadcast together with shapes (10000,4) (10000,)
如何解決?
```
- 收到的回覆
    - 發現是 權重w 與 偏差b 在初始化時的 shape 沒有設定好
        - 應該改成
        ```python
        w = np.random.uniform(-1,1, (784, 4))  # shape = (784, 4)
        b = np.random.uniform(-1,1, (1, 4))    # shape = (1, 4)
        ```
    - 以及使用 ```np.max(), nm.sum()``` 時，應該加上參數，避免出錯
        - 因為 w 和 b 的形狀改變了，n 的計算結果也會改變
        - softmax 必須沿著「類別」的維度 ( axis=1 ) 進行計算
            - 沿著 axis=1 (類別的維度) 尋找最大值
            - keepdims=True 讓 shape 始終維持原狀，才能正確廣播相減
::: spoiler Gimini 回覆的完整版
這是一個非常經典的問題！你遇到的錯誤是 Multinomial Logistic Regression (多項式邏輯迴歸) 與 Binary Logistic Regression (二元邏輯迴歸) 在實作上的關鍵差異。

錯誤訊息 `ValueError: operands could not be broadcast together with shapes (10000,4) (10000,)` 告訴你：

  * `one_hot_labels` 的形狀是 `(10000, 4)` -\> (10000 筆資料, 4 個類別)，這是**正確**的。
  * `softmax` 的形狀是 `(10000,)` -\> (10000 筆資料, 每個資料只有 1 個值)，這是**錯誤**的。

**問題的根源：**
你的模型權重 `w` 和 `b` 被設定為二元分類（只有一組權重）。對於多項式（多類別）迴歸，你**需要為每一個類別 (Class) 都設定一組獨立的權重**。

你有 4 個類別 (0, 1, 2, 3)，所以你需要 4 組權重和 4 個偏差值。

-----

### 🚀 如何修正

你需要調整 `w` 和 `b` 的形狀，以及 `softmax` 的計算方式。

#### 1\. 修正 `w` 和 `b` 的初始化

`w` 應該從 `(784,)` 變成 `(784, 4)`，因為 784 個特徵中的每一個都要對 4 個類別產生一個分數。
`b` 應該從 `(1,)` 變成 `(1, 4)` 或 `(4,)`，為 4 個類別各提供一個偏差值。

```python
# (原來的程式碼)
# np.random.seed(seed=42)
# w = np.random.uniform(-1,1, (784, ))  # <--- 錯誤的形狀
# b = np.random.uniform(-1,1, (1,))    # <--- 錯誤的形狀
# lr = 0.01

# (修正後的程式碼)
np.random.seed(seed=42)
num_features = 784
num_classes = 4  # 你有 4 個類別

# w 的形狀應為 (特徵數量, 類別數量)
w = np.random.uniform(-1, 1, (num_features, num_classes))

# b 的形狀應為 (1, 類別數量)，這樣便於廣播(broadcasting)
b = np.random.uniform(-1, 1, (1, num_classes)) 
lr = 0.01
```

#### 2\. 修正 `n` (Logits) 和 `softmax` 的計算

因為 `w` 和 `b` 的形狀改變了，`n` 的計算結果也會改變。接著 `softmax` 必須沿著「類別」的維度 ( `axis=1` ) 進行計算。

```python
# (原來的程式碼)
# n = features@w + b
# c = max(n)
# softmax = np.exp(n-c) / sum(np.exp(n-c))

# (修正後的程式碼)

# --- 1. 計算 Logits (n) ---
# features (10000, 784) @ w (784, 4) -> (10000, 4)
# (10000, 4) + b (1, 4) -> (10000, 4) (廣播)
n = features @ w + b
# 現在 n 的形狀是 (10000, 4)，代表每筆資料對 4 個類別的分數

# --- 2. 計算穩定的 Softmax (Stable Softmax) ---
# 這是為了避免 exp() 溢位 (overflow)
# 我們沿著 axis=1 (類別的維度) 尋找最大值
# keepdims=True 讓 c 的形狀保持 (10000, 1)，才能正確廣播相減
c = np.max(n, axis=1, keepdims=True)

# (10000, 4) - (10000, 1) -> (10000, 4)
n_stable = n - c

# (10000, 4)
exp_n = np.exp(n_stable)

# 沿著 axis=1 (類別維度) 加總
# sum_exp_n 的形狀會是 (10000, 1)
sum_exp_n = np.sum(exp_n, axis=1, keepdims=True)

# (10000, 4) / (10000, 1) -> (10000, 4) (廣播)
softmax = exp_n / sum_exp_n

# 現在 softmax 的形狀是 (10000, 4)，代表每筆資料的機率分佈
```

#### 3\. 計算誤差 (Gradient)

現在你的 `tri` 計算式可以正常運作了！

```python
# one_hot_labels (10000, 4) - softmax (10000, 4)
tri = one_hot_labels - softmax

# tri 的形狀將會是 (10000, 4)，這是正確的
print("one_hot_labels shape:", one_hot_labels.shape)
print("softmax shape:", softmax.shape)
print("tri (gradient) shape:", tri.shape)
```

-----

### 總結：修改後的完整計算區塊

把你的「開始計算」區塊換成下面這樣即可：

```python
# 開始計算
np.random.seed(seed=42) # 設定亂數種子

num_features = features.shape[1] # 應為 784
num_classes = one_hot_labels.shape[1] # 應為 4

# 1. 初始化 w 和 b (使用正確的形狀)
w = np.random.uniform(-1, 1, (num_features, num_classes))
b = np.random.uniform(-1, 1, (1, num_classes))
lr = 0.01

# 2. 計算 Logits (n)
# n 的形狀將是 (10000, 4)
n = features @ w + b

# 3. 計算穩定的 Softmax
# c 的形狀 (10000, 1)
c = np.max(n, axis=1, keepdims=True)
exp_n = np.exp(n - c)
# sum_exp_n 的形狀 (10000, 1)
sum_exp_n = np.sum(exp_n, axis=1, keepdims=True)
# softmax 的形狀 (10000, 4)
softmax = exp_n / sum_exp_n

# 4. 計算誤差
# tri (誤差梯度) 的形狀 (10000, 4)
tri = one_hot_labels - softmax

print(f"Softmax 陣列的形狀: {softmax.shape}")
print(f"誤差 tri 陣列的形狀: {tri.shape}")
```

這個 `tri` 變數 (通常稱為梯度 `grad`) 接下來就可以用來更新你的 `w` 和 `b` 了。

這樣修改後，你的程式碼就可以順利計算誤差了。這個 `tri` 是計算 Loss 對 `n` 的偏微分，你的下一步就是利用它來計算 `w` 和 `b` 的梯度並更新它們。

需要我接著說明如何使用 `tri` 來更新 `w` 和 `b` (即梯度下降的下一步) 嗎？
:::

            
### 此時已完成資料引入、one-hot 編碼，也計算了 1 個世代的預測值，權重、偏差也已更新 1 個世代

## 下一步該怎麼做? with Gimini
- ### 完整 promt
```
我正在撰寫python完成附件的作業要求，我想先完成 Group A
Group_A_train.csv 與 Group_A_test.csv 是作業提供的樣本
請你參考兩份作業要求的檔案(深度學習Lab2_作業要求.pdf、DL2025_Lab2.pdf)
告訴我，以下我撰寫的程式碼下一步應該做什麼，怎麼做?

import numpy as np

# 載入訓練資料
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 將 label 做 one-hot encoding
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}
encoded_labels = np.array([label_mapping[i] for i in labels])

one_hot_labels = np.zeros((len(encoded_labels), 4))

index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1

# 開始計算
np.random.seed(seed=42)               #設定亂數種子
w = np.random.uniform(-1,1, (784, 4))     #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (1,)
b = np.random.uniform(-1,1, (1, 4))     #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1,)
lr = 0.01
N = 10000 # 有一萬筆訓練資料


n = features@w + b
c = np.max(n)

softmax = np.exp(n-c) / np.sum(np.exp(n-c))

tri = one_hot_labels - softmax



features = np.transpose(features)



dw = features@tri / N
w = w + lr*dw

db = np.sum(tri) / N
b = b + lr*db
```

- 收到的回答
    - 得知接下來應該完成
        - 打亂資料
        ```python
        # 取得資料總筆數
        total_samples = features.shape[0] # 應該是 10000

        # 產生一個打亂的索引
        # np.random.seed(42) 已經在後面設定了，您也可以在這裡設定一次
        np.random.seed(42)
        indices = np.random.permutation(total_samples)

        # 使用打亂的索引來重排 features 和 labels
        features_shuffled = features[indices]
        labels_shuffled = one_hot_labels[indices]
        ```
        - 分割資料
        ```python
        # 決定分割點
        split_idx = int(total_samples * 0.8) # 8000

        # 分割為訓練集和驗證集
        X_train = features_shuffled[:split_idx]
        y_train = labels_shuffled[:split_idx]

        X_val = features_shuffled[split_idx:]
        y_val = labels_shuffled[split_idx:]

        # 更新 N (訓練資料筆數)
        N = X_train.shape[0] # N 現在應該是 8000
        ```
        - 建立「Epoch」訓練迴圈
        ```python
        maxEpoch = 500
        for epoch in range(maxEpoch):
            # 這邊再開始計算預測值、更新權重與偏差
        ```
        - 設定用於存放每個世代的結果之列表，方便後續畫圖
        ```python
        lossHistory_train = []
        lossHistory_val = []
        accHistory_train = []
        accHistory_val = []
        ```
        - 設定停止條件
            - 參考作業說明: "驗證準確率下降而訓練準確率上升 (出現 overfitting)"
            ```python
            # 設定終止條件: 當驗證準確率下降時終止
            if accuracy_val < accHistory_val[epoch-1]:
                break  # 最終會在第 258 世代停止
            ```
        - 計算 Loss 與 Accuracy
            - Loss
            ```python
            # 計算 Cross-Entropy Loss
            loss_train = -np.sum(Y_train*np.log(y_hat)) / N_train
            lossHistory_train.append(loss_train)   # 將算好的 loss 加入 lossHistory 
            
            # 計算驗證資料的 Loss，用於畫圖
            loss_val = -np.sum(Y_val*np.log(y_hat_val)) / N_val
            lossHistory_val.append(loss_val)
            ```
            - Accuracy
            ```python
            # 開始驗證，計算準確率
            n_val = X_val @ w + b                  # 計算預測值
            c_val = np.max(n_val, axis=1, keepdims=True)  # 對每個樣本各自取最大值
            y_hat_val = np.exp(n_val-c_val) / np.sum(np.exp(n_val-c_val), axis=1, keepdims=True)  # 計算 softmax
            
            
            # 計算驗證準確率
            max_val = np.argmax(y_hat_val, axis=1)  # 取驗證預測值中最高的
            accuracy_val = np.sum(max_val == labels_val) / N_val  # 加總分類正確的樣本數並除以驗證資料的總樣本數，得出準確率
            accHistory_val.append(accuracy_val)

            # 計算訓練資料的準確率
            max_train = np.argmax(y_hat, axis=1)
            accuracy_train = np.sum(max_train == labels_train) / N_train
            accHistory_train.append(accuracy_train)
            ```
            
            
:::spoiler Gimini 回覆的完整版
您好！我分析了您的程式碼以及兩份作業要求文件（`深度學習Lab2_作業要求.pdf` 與 `DL2025_Lab2.pdf`）。

您目前已經成功完成了**資料前處理**（載入、正規化、Label Encoding、One-Hot Encoding）以及**梯度下降的單一步驟**（Forward pass、計算梯度、更新權重）。

不過，您的程式碼目前只執行了**一次**更新，使用的是**所有**的訓練資料（這稱為 Batch Gradient Descent）。

根據作業要求，您需要進行以下幾項關鍵調整，才能建構出一個完整的訓練流程：

-----

### 1\. 建立「訓練集」與「驗證集」

作業要求明確提到，`_train.csv` 檔案需要**自行切分**為訓練集（train set）和驗證集（validation set），建議的比例是 80% 訓練集和 20% 驗證集。

此外，原始資料**沒有打亂**，您必須**自行打亂** 。

**下一步行動：**

在您計算完 `one_hot_labels` 之後，但在初始化 `w` 和 `b` 之前，您需要：

1.  **打亂資料：** 建立一個隨機的索引，並同時用這個索引去重排 `features` 和 `one_hot_labels`，確保特徵和標籤能對應起來。

    ```python
    # 取得資料總筆數
    total_samples = features.shape[0] # 應該是 10000

    # 產生一個打亂的索引
    # np.random.seed(42) 已經在後面設定了，您也可以在這裡設定一次
    np.random.seed(42)
    indices = np.random.permutation(total_samples)

    # 使用打亂的索引來重排 features 和 labels
    features_shuffled = features[indices]
    labels_shuffled = one_hot_labels[indices]
    ```

2.  **分割資料：** 按照 80/20 的比例分割。

    ```python
    # 決定分割點
    split_idx = int(total_samples * 0.8) # 8000

    # 分割為訓練集和驗證集
    X_train = features_shuffled[:split_idx]
    y_train = labels_shuffled[:split_idx]

    X_val = features_shuffled[split_idx:]
    y_val = labels_shuffled[split_idx:]

    # 更新 N (訓練資料筆數)
    N = X_train.shape[0] # N 現在應該是 8000
    ```

### 2\. 建立「Epoch」訓練迴圈

作業要求您繪製**每個 epoch** 的 loss 和 accuracy，這代表您需要一個外層迴圈來跑好幾輪（Epochs）的訓練。

**下一步行動：**

將您的梯度下降計算（Forward、Backward、Update）包在一個 `for` 迴圈裡。

```python
# ... (初始化 w, b, lr 之後) ...

# 設定超參數
max_epochs = 50 # 範例，您需要自行調整
batch_size = 64 # 範例，您需要自行調整

# 用來儲存每個 epoch 的結果，為繪圖做準備
train_losses = []
val_losses = []
train_accuracies = []
val_accuracies = []

for epoch in range(max_epochs):
    # (您目前的計算邏輯要放在這裡，並調整為 Mini-Batch)
    # ...
    # ...
```

### 3\. 實現「Mini-Batch」梯度下降

您的程式碼目前是「Batch」梯度下降（一次處理全部 10000 筆資料），這在計算上非常慢。作業要求中的 `output.json` 提到了 `Batch size`，且提示中也建議 batch size 可設定於 32\~128 之間。這強烈暗示您應該使用「Mini-Batch 梯度下降」。

**下一步行動：**

在 `epoch` 迴圈**內部**，再建立一個迴圈，用來遍歷所有 mini-batches。

```python
for epoch in range(max_epochs):
    
    # 每個 epoch 開始時，重新打亂一次"訓練集"
    indices = np.random.permutation(X_train.shape[0])
    X_train_shuffled = X_train[indices]
    y_train_shuffled = y_train[indices]
    
    # Mini-Batch 迴圈
    for i in range(0, N, batch_size): # N 是 X_train.shape[0]
        # 取得這個 batch 的資料
        X_batch = X_train_shuffled[i : i + batch_size]
        y_batch = y_train_shuffled[i : i + batch_size]
        
        # --- 以下是您的計算邏輯，但要改用 X_batch 和 y_batch ---
        
        # 1. Forward Pass
        n = X_batch @ w + b
        
        # [cite_start]2. Softmax (您已使用穩定版，很好) [cite: 203]
        #    注意：要沿著 "列" (axis=1) 進行 max 和 sum
        c = np.max(n, axis=1, keepdims=True)
        stable_exp = np.exp(n - c)
        softmax = stable_exp / np.sum(stable_exp, axis=1, keepdims=True)
        
        # 3. Backward Pass (計算梯度)
        # 誤差 (gradient of cross-entropy w.r.t. n)
        grad_n = y_batch - softmax 
        
        # 計算 dw 和 db
        # 您的 features 轉置 (features = np.transpose(features)) 應該在這裡做
        # 並且是對 X_batch 做
        dw = X_batch.T @ grad_n / batch_size # 除以 batch_size
        db = np.sum(grad_n, axis=0, keepdims=True) / batch_size
        
        # 4. Update Weights (權重更新)
        w = w + lr * dw
        b = b + lr * db
    
    # --- Mini-Batch 迴圈結束 (即一個 Epoch 結束) ---
    # 在這裡計算 "整個" 訓練集和驗證集的 Loss & Accuracy
    # ... (請見下一步)
```

### 4\. 計算 Loss 與 Accuracy

作業要求您記錄**訓練**和**驗證**的準確率與 Loss。您需要實作 Cross-Entropy Loss 和 Accuracy 的計算函式。

**下一步行動：**

在 `epoch` 迴圈的**結尾**（即 Mini-Batch 迴圈之外），加入計算。

1.  **Loss (Cross-Entropy):** $Loss = -\Sigma_{j=1}^{k}y_{j}log~a_{j}$。

      * `train_loss = calculate_loss(X_train, y_train, w, b)`
      * `val_loss = calculate_loss(X_val, y_val, w, b)`
      * 將結果存入 `train_losses.append(train_loss)` 和 `val_losses.append(val_loss)`

2.  **Accuracy:**

      * `train_acc = calculate_accuracy(X_train, y_train, w, b)`
      * `val_acc = calculate_accuracy(X_val, y_val, w, b)`
      * 將結果存入 `train_accuracies.append(train_acc)` 和 `val_accuracies.append(val_acc)`

3.  **印出進度：**
    `print(f"Epoch {epoch+1}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}")`

### 5\. 實作停止條件

作業**不允許**只使用最大世代數作為停止條件。您必須加入其他條件，例如 overfitting 或 loss 不再改善。

**下一步行動：**

這比較進階，您可以在迴圈中加入「Early Stopping」邏輯。
例如：如果 `val_loss` 連續 10 個 epochs 都沒有下降，就 `break` 迴圈。

-----

### 總結您的下一步

1.  **分割資料：** 在 `np.random.seed(42)` 之前，先打亂 `features` 和 `one_hot_labels`，然後將它們分割成 `X_train`, `y_train`, `X_val`, `y_val`。
2.  **建立迴圈：** 建立一個 `for epoch in range(max_epochs):` 的外層迴圈。
3.  **Mini-Batch：** 在 Epoch 迴圈內，建立一個 `for i in range(0, N, batch_size):` 的內層迴圈。
4.  **修正計算：** 將您的 Forward/Backward/Update 邏輯移入 Mini-Batch 迴圈，並確保 Softmax 的 `axis=1` 和梯度的平均值（除以 `batch_size`）是正確的。
5.  **計算指標：** 在 Epoch 迴圈的結尾（Mini-Batch 迴圈外），計算**整個** `X_train` 和 `X_val` 的 Loss 和 Accuracy，並將它們儲存在 List 中，以便最後繪圖。
6.  **(重要)** `readme.txt`：作業要求，如果有使用 AI 查詢（例如我們的對話），務必寫入 `readme.txt` 中。

完成這些步驟後，您將擁有一個完整的訓練腳本。下一步就是使用 `matplotlib` 繪圖並將結果寫入 `.json` 檔案。

請問您需要我針對「如何計算 Cross-Entropy Loss 和 Accuracy」提供更詳細的程式碼範例嗎？
:::


## 如何計算驗證準確率? with Gimini
-  完整 promt
:::spoiler
參考附件的訓練資料(Group_A_train.csv)以及下方依照附件訓練資料實作 Multinomial Logistic Regression / Softmax Regression 的 Python 程式碼
告訴我該如何實作計算驗證準確率(accuracy)?
import numpy as np

# 載入訓練資料
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 將 label 做 one-hot encoding
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}
encoded_labels = np.array([label_mapping[i] for i in labels])

one_hot_labels = np.zeros((len(encoded_labels), 4))

index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1

np.random.seed(seed=42)               # 設定亂數種子
N = 10000                             # 有一萬筆訓練資料

# 打亂資料

# 產生亂數排序的 0 ~ 10000，當作已經打亂的索引值
random_index = np.random.permutation(N) # np.random.permutation 會產生一個 0 ~ N-1 的隨機序列

# 用打亂的索引值，重新調整資料排序
X = features[random_index]         # 經過正規化並打亂的特徵 (features)，也就是待會要拿去計算的 X
Y = one_hot_labels[random_index]   # 經過打亂的標籤 (labels)，也就是待會要拿去計算的 Y

# 分割資料，將一萬筆的訓練資料分成 80% 的訓練集 (train) 與 20% 的驗證集 (val)
N_train = int(N * 0.8)
N_val = N - N_train

X_train = X[:N_train]
Y_train = Y[:N_train]

X_val = X[N_train:]
Y_val = Y[N_train:]


# 開始訓練
w = np.random.uniform(-1,1, (784, 4))        #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (1,)
b = np.random.uniform(-1,1, (1, 4))          #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1,)
lr = 0.01          # 設定學習率

maxEpoch = 50     # 設定最大世代數

# 用來存放每一次 epoch 的結果
lossHistory = []

for epoch in range(maxEpoch):
    n = X_train @ w + b                  # 計算預測值
    
    c = np.max(n, axis=1, keepdims=True) # 對每個樣本各自取最大值
    y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

    error = Y_train - y_hat              # 計算誤差

    X_T = np.transpose(X_train)          # 將 X_train 矩陣轉制
    dw = X_T @ error / N_train
    w = w + lr*dw                        # 更新權重

    db = np.sum(error, axis=0, keepdims=True) / N_train
    b = b + lr*db                        # 更新偏差值

    # 計算 Cross-Entropy Loss
    loss = -np.sum(Y_train*np.log(y_hat)) / N
    lossHistory.append(loss)             # 將算好的 loss 加入 lossHistory
:::

- 收到的回覆
    - 有參考的部分
    ```python
    # --- 驗證階段 (Validation) ---           # <--- 以下為新增的驗證準確率計算區塊 ---

    # 1. 對驗證集 (X_val) 進行預測 (Forward pass)
    n_val = X_val @ w + b
    c_val = np.max(n_val, axis=1, keepdims=True)
    y_hat_val = np.exp(n_val - c_val) / np.sum(np.exp(n_val - c_val), axis=1, keepdims=True)

    # 2. 取得預測的類別 (機率最高的索引)
    # y_hat_val 的 shape 是 (2000, 4)，argmax 後的 shape 是 (2000,)
    preds_val = np.argmax(y_hat_val, axis=1)

    # 3. 取得真實的類別 (將 one-hot 的 Y_val 轉回 0, 1, 2, 3)
    # Y_val 的 shape 是 (2000, 4)，argmax 後的 shape 是 (2000,)
    true_labels_val = np.argmax(Y_val, axis=1)

    # 4. 比較預測與真實標籤，計算正確的數量
    correct_count = np.sum(preds_val == true_labels_val)

    # 5. 計算準確率 (正確數 / 驗證集總數)
    val_accuracy = correct_count / N_val

    # 6. 儲存準確率
    accHistory.append(val_accuracy)
    ```
:::spoiler Gimini 回覆的完整版
這很清楚了，您希望在每個 `epoch` 訓練完成後，計算模型在「驗證集」(`X_val`, `Y_val`) 上的準確率 (Accuracy)，並將其儲存起來，以便像 Figure 1 那樣繪製圖表。

準確率的計算公式為：**`正確預測的樣本數 / 驗證集的總樣本數`**

您需要在訓練迴圈中加入這個計算過程。

### 📌 如何實作驗證準確率 (Validation Accuracy)

您需要在 `for` 迴圈的**結尾**（計算完 `loss` 之後）加入以下步驟：

1.  **初始化 (迴圈外):** 在 `lossHistory = []` 旁邊，新增一個 `accHistory = []` 來儲存準確率。
2.  **預測 (迴圈內):** 使用當前 epoch 訓練好的 `w` 和 `b`，對**驗證資料 `X_val`** 進行預測。
3.  **取最大值:** 預測結果 `y_hat_val` 是一個 (N\_val, 4) 的機率矩陣。我們要使用 `np.argmax` 找出每個樣本機率最高的索引 (0, 1, 2, or 3)，這就是模型的預測標籤。
4.  **取得真實標籤:** `Y_val` 是 one-hot 編碼。我們同樣使用 `np.argmax` 找出真實標籤的索引。
5.  **比較:** 比較「預測標籤」和「真實標籤」，計算有多少個是相等的。
6.  **計算準確率:** 將相等的數量除以驗證集的總數 `N_val`。
7.  **儲存:** 將計算出的準確率 `append` 到 `accHistory`。

-----

### 💻 修改後的 Python 程式碼

我將您原本的程式碼修改如下。請注意標記為「**`# <--- 新增`**」和「**`# <--- 修改`**」的部分。

```python
import numpy as np
# 為了繪圖，您需要 matplotlib
import matplotlib.pyplot as plt

# 載入訓練資料
data = np.loadtxt("Group_A_train.csv", delimiter=',', skiprows=1)

# 分別存取第一行的標籤 與 其餘的 784 維的像素
labels = data[:, 0].astype(int)
features = data[:, 1:]

# 將特徵正規化處理
features = features / 255.0


# 將 label 做 one-hot encoding
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}
encoded_labels = np.array([label_mapping[i] for i in labels])

one_hot_labels = np.zeros((len(encoded_labels), 4))

index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1

np.random.seed(seed=42)              # 設定亂數種子
N = 10000                            # 有一萬筆訓練資料

# 打亂資料

# 產生亂數排序的 0 ~ 10000，當作已經打亂的索引值
random_index = np.random.permutation(N) # np.random.permutation 會產生一個 0 ~ N-1 的隨機序列

# 用打亂的索引值，重新調整資料排序
X = features[random_index]          # 經過正規化並打亂的特徵 (features)，也就是待會要拿去計算的 X
Y = one_hot_labels[random_index]    # 經過打亂的標籤 (labels)，也就是待會要拿去計算的 Y

# 分割資料，將一萬筆的訓練資料分成 80% 的訓練集 (train) 與 20% 的驗證集 (val)
N_train = int(N * 0.8)
N_val = N - N_train

X_train = X[:N_train]
Y_train = Y[:N_train]

X_val = X[N_train:]
Y_val = Y[N_train:]


# 開始訓練
w = np.random.uniform(-1,1, (784, 4))      # 隨機取 -1 ~ 1 之間的一個神經元參數 w
b = np.random.uniform(-1,1, (1, 4))        # 隨機取 -1 ~ 1 之間的一個神經元參數 b
lr = 0.01                                  # 設定學習率

maxEpoch = 50                              # 設定最大世代數

# 用來存放每一次 epoch 的結果
lossHistory = []
accHistory = []                            # <--- 新增: 用來存放每一次 epoch 的驗證準確率

for epoch in range(maxEpoch):
    # --- 訓練階段 (Training) ---
    n_train = X_train @ w + b                  # <--- 修改: 變數改為 n_train
    
    c_train = np.max(n_train, axis=1, keepdims=True) # <--- 修改: 變數改為 c_train
    y_hat = np.exp(n_train - c_train) / np.sum(np.exp(n_train - c_train), axis=1, keepdims=True) # 計算 softmax

    error = Y_train - y_hat                    # 計算誤差

    X_T = np.transpose(X_train)                # 將 X_train 矩陣轉制
    dw = X_T @ error / N_train
    w = w + lr*dw                              # 更新權重

    db = np.sum(error, axis=0, keepdims=True) / N_train
    b = b + lr*db                              # 更新偏差值

    # 計算 Cross-Entropy Loss (使用訓練集)
    # 注意：您的原始碼 loss 是除以 N (10000)，這裡保持一致
    loss = -np.sum(Y_train*np.log(y_hat)) / N
    lossHistory.append(loss)                   # 將算好的 loss 加入 lossHistory

    # --- 驗證階段 (Validation) ---           # <--- 以下為新增的驗證準確率計算區塊 ---
    
    # 1. 對驗證集 (X_val) 進行預測 (Forward pass)
    n_val = X_val @ w + b
    c_val = np.max(n_val, axis=1, keepdims=True)
    y_hat_val = np.exp(n_val - c_val) / np.sum(np.exp(n_val - c_val), axis=1, keepdims=True)
    
    # 2. 取得預測的類別 (機率最高的索引)
    # y_hat_val 的 shape 是 (2000, 4)，argmax 後的 shape 是 (2000,)
    preds_val = np.argmax(y_hat_val, axis=1)
    
    # 3. 取得真實的類別 (將 one-hot 的 Y_val 轉回 0, 1, 2, 3)
    # Y_val 的 shape 是 (2000, 4)，argmax 後的 shape 是 (2000,)
    true_labels_val = np.argmax(Y_val, axis=1)
    
    # 4. 比較預測與真實標籤，計算正確的數量
    correct_count = np.sum(preds_val == true_labels_val)
    
    # 5. 計算準確率 (正確數 / 驗證集總數)
    val_accuracy = correct_count / N_val
    
    # 6. 儲存準確率
    accHistory.append(val_accuracy)
    
    # (可選) 印出每個 epoch 的結果
    print(f"Epoch {epoch+1}/{maxEpoch}, Loss: {loss:.4f}, Val Accuracy: {val_accuracy:.4f}")

# --- 訓練結束 ---

# --- 繪製 Figure 1 ---
# 建立 x 軸 (Epochs)
epochs = range(1, maxEpoch + 1)

# 建立圖表和兩個 y 軸
fig, ax1 = plt.subplots()

# 繪製 Training Loss (y 軸 1)
color = 'tab:red'
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Training Loss', color=color)
ax1.plot(epochs, lossHistory, color=color, label='Training Loss')
ax1.tick_params(axis='y', labelcolor=color)

# 建立第 2 個 y 軸，共享 x 軸
ax2 = ax1.twinx()  
color = 'tab:blue'
ax2.set_ylabel('Validation Accuracy', color=color)  # <--- y 軸 2
ax2.plot(epochs, accHistory, color=color, label='Validation Accuracy') # <--- 繪製準確率
ax2.tick_params(axis='y', labelcolor=color)

# 標題與圖例
fig.suptitle('Figure 1: Training Loss and Validation Accuracy')
fig.tight_layout()  # 調整佈局
plt.show()
```

### 重點說明

1.  **`accHistory = []`**: 在迴圈外建立空列表，用來收集每個 epoch 的準確率。
2.  **`n_val = X_val @ w + b`**: 關鍵步驟。這裡使用 `X_val` 和**當前 epoch 更新過的 `w` 和 `b`** 來產生預測。
3.  **`np.argmax(..., axis=1)`**: 這是將 one-hot 編碼或機率分佈轉回單一類別標籤 (0, 1, 2, 3) 的核心函數。`axis=1` 表示沿著「行」的方向找出最大值的「索引」。
4.  **`correct_count = np.sum(preds_val == true_labels_val)`**: NumPy 會逐一比較兩個陣列，`==` 會產生一個布林值陣列 (`True`, `False`, `True`, ...)。`np.sum()` 會將 `True` 視為 1、`False` 視為 0 進行加總，從而得到猜對的總數。
5.  **`val_accuracy = correct_count / N_val`**: 計算準確率。
6.  **繪圖**: 最後，我附上了使用 `matplotlib` 繪製雙 Y 軸圖表的程式碼，您可以直接使用 `lossHistory` 和 `accHistory` 來重現 Figure 1。
:::


## 執行遇到錯誤，好像與 json 有關，但我確定語法應該正確，如何解決? with Gimini
- ### 完整 promt
```
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
label_mapping = {0: 0, 1: 1, 8: 2, 9: 3}
encoded_labels = np.array([label_mapping[i] for i in labels])

one_hot_labels = np.zeros((len(encoded_labels), 4))

index = 0
for i in encoded_labels:
    one_hot_labels[index, i] = 1
    index += 1

np.random.seed(seed=42)               # 設定亂數種子
N = 10000                             # 有一萬筆訓練資料

# 打亂資料

# 產生亂數排序的 0 ~ 10000，當作已經打亂的索引值
random_index = np.random.permutation(N) # np.random.permutation 會產生一個 0 ~ N-1 的隨機序列

# 用打亂的索引值，重新調整資料排序
X = features[random_index]         # 經過正規化並打亂的特徵 (features)，也就是待會要拿去計算的 X
Y = one_hot_labels[random_index]   # 經過打亂的標籤 (labels)，也就是待會要拿去計算的 Y

# 分割資料，將一萬筆的訓練資料分成 80% 的訓練集 (train) 與 20% 的驗證集 (val)
N_train = int(N * 0.8)
N_val = N - N_train

X_train = X[:N_train]
Y_train = Y[:N_train]

X_val = X[N_train:]
Y_val = Y[N_train:]

# 提前計算訓練與驗證的 Y 在 one-hot encoding 前的 0,1,2,3 ，用於驗證
labels_train = np.argmax(Y_train, axis=1)
labels_val = np.argmax(Y_val, axis=1)

# 開始訓練
w = np.random.uniform(-1,1, (784, 4))        #隨機取 -1 ~ 1 之間的一個神經元參數 w ，shape = (1,)
b = np.random.uniform(-1,1, (1, 4))          #隨機取 -1 ~ 1 之間的一個神經元參數 b ，shape = (1,)
lr = 0.15          # 設定學習率

maxEpoch = 500     # 設定最大世代數

# 用來存放每一次 epoch 的結果，用於畫圖
lossHistory_train = []
lossHistory_val = []
accHistory_train = []
accHistory_val = []

for epoch in range(maxEpoch):
    n = X_train @ w + b                  # 計算預測值
    
    c = np.max(n, axis=1, keepdims=True) # 對每個樣本各自取最大值
    y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

    error = Y_train - y_hat              # 計算誤差

    X_T = np.transpose(X_train)          # 將 X_train 矩陣轉制
    dw = X_T @ error / N_train
    w = w + lr*dw                        # 更新權重

    db = np.sum(error, axis=0, keepdims=True) / N_train
    b = b + lr*db                        # 更新偏差值

    # 計算 Cross-Entropy Loss
    loss_train = -np.sum(Y_train*np.log(y_hat)) / N_train
    lossHistory_train.append(loss_train)             # 將算好的 loss 加入 lossHistory

    # 開始驗證，計算準確率
    n_val = X_val @ w + b                  # 計算預測值
    c_val = np.max(n_val, axis=1, keepdims=True) # 對每個樣本各自取最大值
    y_hat_val = np.exp(n_val-c_val) / np.sum(np.exp(n_val-c_val), axis=1, keepdims=True)  # 計算 softmax

    # 計算驗證資料的 Loss，用於畫圖
    loss_val = -np.sum(Y_val*np.log(y_hat_val)) / N_val
    lossHistory_val.append(loss_val)

    # 計算驗證準確率
    max_val = np.argmax(y_hat_val, axis=1) # 取驗證預測值中最高的
    accuracy_val = np.sum(max_val == labels_val) / N_val
    accHistory_val.append(accuracy_val)

    # 計算訓練資料的準確率
    max_train = np.argmax(y_hat, axis=1)
    accuracy_train = np.sum(max_train == labels_train) / N_train
    accHistory_train.append(accuracy_train)

    # 設定終止條件: 當驗證準確率下降時終止
    if accuracy_val < accHistory_val[epoch-1]:
        print("stop!!")
        print("Epoch is "+str(epoch))
        break

# 開始畫圖 - Loss
plt.figure(figsize=(6,4))
plt.plot(lossHistory_train, color="blue", label="Train loss")
plt.plot(lossHistory_val, color="orange", label="Validation loss")
plt.xlabel("Epoch")  # 加上 X 軸標題
plt.ylabel("Loss")   # 加上 Y 軸標題
plt.title("GroupA_Loss")               #圖片標題
plt.legend(loc="upper right")   #說明框的位置
plt.savefig("./output/output_loss.png")    #儲存圖片，先儲存再清空
#plt.show() #提交時註解show
plt.clf()  #清空圖片

# 開始畫圖 - Accuracy
plt.plot(accHistory_train, color="blue", label="Train accuracy")
plt.plot(accHistory_val, color="orange", label="Validation accuracy")
plt.xlabel("Epoch")  # 加上 X 軸標題
plt.ylabel("Accuracy")   # 加上 Y 軸標題
plt.title("GroupA_Accuracy")               #圖片標題
plt.legend(loc="lower right")   #說明框的位置
plt.savefig("./output/output_accuracy.png")    #儲存圖片，先儲存再清空
#plt.show() #提交時註解show
plt.clf()  #清空圖片

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


# 輸出成 json 格式 - 驗證 test
# 載入測試資料
test_data = np.loadtxt("Group_A_test.csv", delimiter=',', skiprows=1)
test_data = test_data / 255.0    # 將特徵正規化處理

n = test_data @ w + b                  # 計算預測值
c = np.max(n, axis=1, keepdims=True) # 對每個樣本各自取最大值
y_hat = np.exp(n-c) / np.sum(np.exp(n-c), axis=1, keepdims=True)  # 計算 softmax

max_test = np.argmax(y_hat, axis=1)   # 取最高的
testlabel_mapping = {0: 0, 1: 1, 2: 8, 3: 9}  # 對應回原本的標籤名稱
predictions = np.array([testlabel_mapping[i] for i in max_test])

# 將分類結果輸出成 json 格式
with open("./output/test_set_prediction.json", "w") as file:
    json.dump({
        "Predictions": predictions
        }, file)
        
我使用kali終端機的vim編輯Python程式碼並執行，卻遇到以下錯誤訊息

  File "/home/kali/Desktop/testDL/aitest.py", line 161, in <module>
    json.dump({
    ~~~~~~~~~^^
        "Predictions": predictions
     ^^^^^^^^^^^^^^^^^^^^^^^^^^
        }, file)
     ^^^^^^^^
  File "/usr/lib/python3.13/json/__init__.py", line 179, in dump
    for chunk in iterable:
                 ^^^^^^^^
  File "/usr/lib/python3.13/json/encoder.py", line 433, in _iterencode
    yield from _iterencode_dict(o, _current_indent_level)
  File "/usr/lib/python3.13/json/encoder.py", line 407, in _iterencode_dict
    yield from chunks
  File "/usr/lib/python3.13/json/encoder.py", line 440, in _iterencode
    o = _default(o)
  File "/usr/lib/python3.13/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
                    f'is not JSON serializable')
TypeError: Object of type ndarray is not JSON serializable
```

- 收到的回覆
    - 原來是 json 無法輸出 Numpy array
    - 之前輸出的都是 list，有使用 append() 新增元素
    - 使用 ```.tolist()``` 可以將 NumPy 陣列轉換為 Python 列表

:::spoiler Gimini 回覆的完整版
你好！我看到你遇到的 `TypeError` 錯誤了。這是一個很常見的問題。

### 🚀 錯誤原因分析

這個錯誤訊息 `TypeError: Object of type ndarray is not JSON serializable` 說得非常清楚：Python 內建的 `json` 函式庫不知道如何將一個 **NumPy 陣列**（`ndarray`）物件轉換成 JSON 格式。

JSON 格式只能理解 Python 內建的資料型態，例如：

  * `dict` (物件)
  * `list`, `tuple` (陣列)
  * `str` (字串)
  * `int`, `float` (數字)
  * `True`, `False` (布林值)
  * `None` (null)

在你的程式碼中，倒數第六行：

```python
predictions = np.array([testlabel_mapping[i] for i in max_test])
```

你明確地將 `predictions` 轉換成了一個 NumPy 陣列。當你嘗試將它存入 `test_set_prediction.json` 時，`json.dump` 函式就「愣住」了，不知道該如何處理這個 `ndarray` 物件。

-----

### 🛠️ 解決方案

解決方法很簡單：在將它存入 JSON 之前，你只需要把這個 NumPy 陣列轉換成一個**標準的 Python 列表（list）**。

請將你程式碼的最後一個區塊修改如下：

**你原本的程式碼（會出錯）：**

```python
# 將分類結果輸出成 json 格式
with open("./output/test_set_prediction.json", "w") as file:
    json.dump({
        "Predictions": predictions
        }, file)
```

**修正後的程式碼：**

```python
# 將分類結果輸出成 json 格式
with open("./output/test_set_prediction.json", "w") as file:
    json.dump({
        "Predictions": predictions.tolist()  # <-- 關鍵在這裡
        }, file)
```

`predictions.tolist()` 會將 NumPy 陣列轉換為 Python 列表，這樣 `json.dump` 就能夠正確處理它了。

### 💡 額外說明

你可能會注意到，你在前面儲存 `output.json` 時（儲存 `accHistory_train` 等變數）沒有遇到這個問題。

這是因為 `accHistory_train`、`lossHistory_train` 這些變數是 Python 的**列表（list）**（你使用 `.append()` 加入元素），`json` 函式庫可以處理列表。即使列表裡面裝的是 NumPy 的數字類型（例如 `np.float64`），`json` 函式庫通常也能正確轉換它們。

而 `predictions` 是一個完整的 NumPy \*\*陣列（ndarray）\*\*物件，這才是 `json` 函式庫無法處理的。

你只需要修改最後一個 `json.dump` 區塊，將 `predictions` 改成 `predictions.tolist()` 就可以解決這個錯誤。

請問你還需要我協助你解釋程式碼中其他的部分嗎？
:::