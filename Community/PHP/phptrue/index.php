<?php
    highlight_file(__FILE__);
    $FROM_INCLUDE = true;
    include("flag.php");
    $admin = false;
    extract($_GET);

    if ($admin === "1" || $admin === "true") {
        die("NoNo:)");
    }
    if($admin == true){
        echo "FLAG: " . $flag;
    }
    else{
            echo "You are not admin!";
    }
?>
