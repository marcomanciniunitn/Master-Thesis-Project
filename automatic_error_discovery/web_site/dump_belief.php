<?php
   $belief = $_POST['belief'];
   $folder  = $_POST['user_id'];

   /* sanity check */
   if (json_decode($belief) != null)
   {
     $file = fopen('users/'.$folder.'.json','w+');
     fwrite($file, $belief);

     fclose($file);

     chmod('users/'.$folder.'.json', 0777);

   }
   else
   {
     // user has posted invalid JSON, handle the error 
   }
?>