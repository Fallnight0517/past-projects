import numpy as np
import json
import matplotlib.pyplot as plt

n = 5       #mod 5
fibN = 60   #要計算 Fibonacci 數列的前 fibN 項

A = np.array([[1,1],[1,0]])   #設定矩陣運算所需的矩陣
Fib_array = np.array([1,0])

fib = [0,1] #存放 Fibonacci 數列
pisano = [] #存放 皮薩諾週期

for i in range(fibN):
	fib.append(int(Fib_array[1]))          #將算出的 Fib 的第 n+1 項加入 array
	pisano.append((int(Fib_array[1]%n)))   #將算出的 Fib 的第 n+1 項，經過 mod 5 後，加入 array
	Fib_array = A @ Fib_array              #利用矩陣運算，算出 Fibonacci 數列的下一項數值，計算後 Fib_array[0] 會是 Fib 的第 n+1 項

#輸出成 json 格式
with open("./output/lab1.1_output.json", "w") as file:
	json.dump({
		"mod": n,
		"pisano_period": pisano
		}, file)


#用 matplotlib 畫圖
plt.figure(figsize=(6,4))

plt.plot(pisano, color="blue", label="Pisano periods")

plt.title("Fib mod5")                  #圖片標題
plt.legend(loc="lower right")          #說明框的位置

plt.savefig("./output/lab1.1.png")     #儲存圖片，先儲存再清空
#plt.show()  #顯示圖片(提交作業時要註解
plt.clf()    #清空圖片