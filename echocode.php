<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
#main { padding-top: 70px; margin: 0px auto; width: 700px; }
p { font-size: 14px; }
h5 { font-size: 16px; font-weight: normal; }
</style>
</head>
<body>
<div id="main">
<p><a href="https://anilist.co/api/auth/authorize?grant_type=authorization_code&client_id=sirtetris-eky4q&redirect_uri=http%3A%2F%2Fmoc.sirtetris.com%2Fanihilist%2Fechocode.php&response_type=code">request auth_code</a></p>
<h5>code:<h5>
<p>
<?php
if(strlen($_GET['code'])!=0)
    echo $_GET['code'];
?>
</p>
</div>
</body>
</html>
