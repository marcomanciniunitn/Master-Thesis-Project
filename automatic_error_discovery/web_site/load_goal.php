<?php
	
  $user = $_POST['user_id'];

  $filename = '/var/www/feedback/goals/'.$user;

  // Read JSON file
	$json = file_get_contents($filename);

	//Decode JSON
	$json_data = json_decode($json,true);

	//Print data
	echo $json;


?>