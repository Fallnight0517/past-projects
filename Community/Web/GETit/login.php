<!DOCTYPE html>
<html lang="zh-Hant-TW">

    <head>
        <meta charset="UTF-8">
        <title>Response</title>
        <style>
            body {
                background-color: #E2FEF7;
                font-family: monospace, sans-serif;
                color: #333;
            }
            .response {
                font-family: monospace, sans-serif;
                font-color: #964CBA;
                font-size: 25px;
            }
        </style>
    </head>

    <body>
        <?php
            //在本地端執行測試，使用cmd打以下指令
            //php -S localhost:8000
            //再去瀏覽器用以下網址打開index.html
            //http://localhost:8000/index.html

            $say = $_GET['say'];
            $page = $_GET['page'];
            $filename = 'random_number.txt';
            $response = "";

            $old_num = file_get_contents($filename);
            //echo "上次的隨機數是：$odd_num";

            $num = rand(0, 9999); // 生成0~9999的隨機數字
            file_put_contents($filename, $num); // 儲存到檔案random_number.txt
            //echo "新生成的隨機數是：$num";
            
            //只有page的數字是上次拿到的secret number，才能拿到flag
            if ($page == $old_num)
            {
                echo "<h3 style=\"font-family: monospace; font-size: 20px;\">Of course!   Our secret is FLAG!<br>NISRA{y0u_\$GET_s3cReT}</h3><br><br>";
            }
            elseif ($page > 0 && $page < 10000){
                echo "<h1 style=\"font-family: monospace;\">Welcome to page ",$page," !</h1><br><br>";
            }

            //預設一些單字跟常見的大小寫排列組合，只要有輸入以下這些就回應特定的話語，如果都沒有就說can't understand
            if (strpos($say, 'flag') !== false) {
                $response = "<p>Maybe you can try to ask for <b>admin</b>?</p>";
            } 
            elseif (strpos($say, 'admin') !== false) {
                $response = "<p>Welcome back! My admin!</p>";
                $response .= "<p>Hope you not forget our secret number:  <b>".$num."</b></p>";
            }
            elseif (strpos($say, 'hint') !== false) {
                $response = "<h3>Attention! The numbers are always changing randomly.</h3>";
                $response .= "<h3>Don't forget to check the URL.</h3>";
            }
            elseif (strpos($say, 'Hint') !== false) {
                $response = "<h3>Attention! The numbers are always changing randomly.</h3>";
                $response .= "<h3>Don't forget to check the URL.</h3>";
            }
            elseif (strpos($say, 'hi') !== false) {
                $response = "<h1>Hello! Nice to meet u!</h1>";
            } 
            elseif (strpos($say, 'Hi') !== false) {
                $response = "<h1>Hello! Nice to meet u!</h1>";
            } 
            elseif (strpos($say, 'Hello') !== false) {
                $response = "<h1>Hello! Nice to meet u!</h1>";
            } 
            elseif (strpos($say, 'hello') !== false) {
                $response = "<h1>Hello! Nice to meet u!</h1>";
            }
            elseif (strpos($say, 'money') !== false) {
                $response = "<h1>I am poor, too. （；´д｀）ゞ</h1>";
            }
            elseif (strpos($say, 'score') !== false) {
                $response = "<h1>All Pass!!!</h1>";
            }
            else
            {
                $response = "<p>Sorry, I only know a few words in English.</p>";
                $response .= "<p>So I can't understand what u say. QAQ</p>";
                
            }
            echo "<div class=response>$response</div>";
            echo  "<a href=\"index.html\" target=\"_self\"> <input type=\"submit\" value=\"Go Back\" style=\"font-family: monospace; font-size:20px;\"></a>";

            //解題需要先輸入admin，拿到secret number
            //由於secret number每次都會更新成新的數字，所以在拿到sectet number後，下一步就一定要去修改網址的page參數

        ?>
    </body>

</html>