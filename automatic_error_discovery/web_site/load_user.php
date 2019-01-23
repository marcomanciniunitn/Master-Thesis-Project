<?php

  $filename = '/var/www/feedback/setup/users.txt';
  $file = file($filename);
  flock($file, LOCK_EX);
  $output = $file[0];
  unset($file[0]);
  file_put_contents($filename, $file);
  flock($file, LOCK_UN);
  echo str_replace("\n", "", $output);

?>