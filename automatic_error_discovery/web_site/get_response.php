<?php

	

	$message = $_POST['data'];

	$url = 'http://127.0.0.1:5000/';
	//$data = array('key1' => 'value1', 'key2' => 'value2');

	// use key 'http' even if you send the request to https://...
	$options = array(
	    'http' => array(
	        'header'  => "application/json\r\n",
	        'method'  => 'POST',
	        'content' => $message
	    )
	);
	$context  = stream_context_create($options);
	$result = file_get_contents($url, false, $context);
	if ($result === FALSE) { /* Handle error */ }

	
	echo $result;
		 
	

?>
