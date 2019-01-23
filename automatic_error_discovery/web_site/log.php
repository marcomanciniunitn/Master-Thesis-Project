<?php
	$infos = array(
		"tot_hours" => $_POST["hours"],
		"tot_minutes" => $_POST['minutes'],
		"tot_seconds" => $_POST['seconds'],
		"interation_hours" => $_POST['interaction_hours'],
		"interation_minutes" => $_POST['interaction_minutes'],
		"interation_seconds" => $_POST['interaction_seconds'],
		"turn_check_hours" => $_POST['turn_selection_hours'],
		"turn_check_minutes" => $_POST['turn_selection_minutes'],
		"turn_check_seconds" => $_POST['turn_selection_seconds'],
		"error_selection_hours" => $_POST["error_selection_hours"],
		"error_selection_minutes" => $_POST["error_selection_minutes"],
		"error_selection_seconds" => $_POST["error_selection_seconds"],
		"user_id" => $_POST['user_id'],
		"turns" => $_POST['turns'] - 1,
		"outcome" => $_POST['finalized'],
		"error_type" => $_POST['error_type'],
		"task_category" => $_POST['task_category']
	);


	//Encode the array into a JSON string.
	$encodedData = json_encode($infos,JSON_PRETTY_PRINT);
	$user_id = $_POST['user_id'];
	//Save the JSON string to a text file.
	file_put_contents("time_spent/".$user_id.".time", $encodedData);



?>

