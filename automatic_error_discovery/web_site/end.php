<?php
	$user_id = $_POST["user_id"];
	$type = $_POST['type'];


	#echo file_get_contents( 'interactions/'.$user_id.'.json'); 
	$handle = fopen('interactions/'.$user_id.'.json', "r");

	if ($type == "false") {
		$turn = $_POST['turn_id'];

		$i = 0;
		$index = 0;
		$found = 0;
		while (($line = fgets($handle)) !== false) {
			if ($line[0] == "*") {
				if($i == $turn){
					$found = $index;
				}
				$i = $i + 1;
			}
	    	$index = $index + 1;
	    }

	    fclose($handle);


	    $data = file('interactions/'.$user_id.'.json'); // reads an array of lines
	    $tmp = $data[$found];
		$data[$found] = "!!!".$tmp;

		file_put_contents ('interactions/'.$user_id.'.json', implode("", $data));

		copy("interactions/".$user_id.".json", "interactions/bad/".$user_id.".json");
		unlink("interactions/".$user_id.".json");

		copy("beliefs/".$user_id, "beliefs/bad/".$user_id);
		unlink("beliefs/".$user_id);

		copy("goals/".$user_id, "goals/bad/".$user_id);
		unlink("goals/".$user_id);

	   

	}else{
		copy("interactions/".$user_id.".json", "interactions/good/".$user_id.".json");
		unlink("interactions/".$user_id.".json");

		copy("beliefs/".$user_id, "beliefs/good/".$user_id);
		unlink("beliefs/".$user_id);

		copy("goals/".$user_id, "goals/good/".$user_id);
		unlink("goals/".$user_id);
	}



?>

<!DOCTYPE html>
<html>
<head>
<title>Experiment finished!</title>
</head>
<body>

<h1 style="margin: auto; text-align: center;">EXPERIMENT FINISHED!</h1>
<h1 style="margin: auto; text-align: center;">Re-start if needed</h1>
<form  style="margin: auto; margin-top: 2%; text-align: center; " action="task.php" method="post">
  <select style="font-size: 130%;" name="exp_type">
	  <option value="BL">Baseline experiment</option>
	  <option value="FULL">Advanced experiment</option>
  </select>
  <button style="font-size: 130%;" type="submit" value="Submit">START!</button>
</form>



</body>
</html>