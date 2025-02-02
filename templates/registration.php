<?php
$sever="localhost";
$username="root";
$passwor="";
$bdname="shipathon";
$con= mysqli_connect($sever,$username,$passwor,$bdname);

if(!$con)
{
    echo "not connected";
}
else
{
    echo "connected";
}
$name = $_POST['name'];
$email = $_POST['email'];
$password = $_POST['password'];
$role = $_POST['role'];

$sql="INSERT INTO `registration`(`name`, `email`, `password`, `role`) VALUES ('$name','$email','$password','$role')";

$result= mysqli_query($con, $sql);
if($result)
{
    echo "data submited...";
}
else
{
    echo "error";
}
?>