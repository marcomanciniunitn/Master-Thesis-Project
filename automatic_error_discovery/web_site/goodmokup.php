<?php
	session_start();
	$n_paraphrases = 2;
	$dialog_id = isset($_SESSION['dialog_id']) ? $_SESSION['dialog_id'] : "-1";
	if (isset($_SESSION['done'])) {
		header("Location: http://localhost/submit.php");
	}
	$EXPTYPE = $_POST['exp_type'];
?>

<html>
<head>
<script src="alertify.min.js"></script>
<!-- include the style -->
<link rel="stylesheet" href="alertify.min.css" />
<!-- include a theme -->
<link rel="stylesheet" href="themes/default.min.css" />
<script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js'></script>
<link href="https://fonts.googleapis.com/css?family=Fjalla+One" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
<meta name="viewport" content="width=device-width, initial-scale=1">
	<style>

	* {border-style: solid; border-width: 0px; border-color: red; font-family: 'Montserrat', sans-serif;}

	body {
		margin-left: 3%; 
		margin-right: 3%; 
		margin-top: 5%;
		margin-bottom: 5%;
		
		background-image: linear-gradient(to top right, #4ecdc4, #556270);
	}

	#white {
		background: white;

	}

	#container{
		margin-left: -5%;
		
	}

	::placeholder {opacity: 0.4;}

	.slotval {color: red; background: none;}
	.error {color: blue; background: none;}
	.bold {font-weight: bold; font-style: normal; font-family: arial; background: none;}

	.green {font-weight: bold; font-style: normal; font-family: 'Roboto', sans-serif; background: none; color: green;}

	#belief_instr{ background: none ;  text-align: center; }

	.red {font-weight: bold; font-style: normal; font-family: 'Roboto', sans-serif; background: none; color: red;}

	.orange {font-weight: bold; font-style: normal; font-family: arial; background: none; color: #EE7600;}

	

	.guidelines {
		margin-left: 10%;
		margin-right: 10%;
		font-family: 'Roboto', sans-serif;
		font-weight: normal;
		font-size: 190%;
	}

	

	.title {
		margin-left: 10%;
		margin-right: 10%;
		font-family: 'Roboto', sans-serif;
		font-weight: bold;
		font-size: 270%;

		padding-top:4%;
	}

	#chat {
		
		margin-left: -5%;
		

		border-radius: 5px 5px 0 0;
		border-style: solid;
		border-width: 2px;
		border-color: black;

		background-image: url("images/chat.jpeg");
		background-repeat: no-repeat;
		background-size: cover;

		overflow-y: auto;
		height: 90%;
		width: 115%;

	}


	#done {
		margin: 45%;
		margin-top: 3%;
		margin-bottom: 0;
		padding: 1.5% 3.5%;

		text-align: center;
		font-size: 120%;
		font-weight: bold;
		text-shadow:1px 1px 0px #07526e;
		font-family: Arial, "Helvetica";
		
		color: #fff;
		display: none;

		cursor: pointer;
		outline: none;
		border-style: solid;
		border-radius: 15px;
		border-width: 1px;
		border-color: #3e8e41;
		box-shadow: 0 9px #CCC;
		background-color: #4CAF50;
	}

	#done:hover {background-color: #3e8e41}

	#done:active {
		background-color: #3e8e41;
		box-shadow: 0 5px #666;
		font-size: 110%;
		padding: 1.4% 3.8%;
	}


	.div_agent{
		width: 100%;
		display: inline-block;
	}

	.agent {

 
		width: 450px;
	
		display: table;
		overflow: auto;

	
		
		
		background: #adeebe;
		border-radius: .8em;
		
		box-shadow: .5px 1.5px 1.5px #aaa;

		padding: 1.5%;

		color: black;
		font-family: arial;
		font-size: 180%;
		
		text-align: left;
		float: right;
		margin-right: 2%;
	}

	.agent:hover {
		box-shadow: 0 2px 2px 1px #999;
	}


	.div_user{
		width: 100%;
		display: inline-block;
	}

	.user {
		
		padding: 1%;
		min-width: 350px;
		
		
		display: inline-block;

		
		position: inline-block;
		background: white;
		border-radius: .8em;

		box-shadow: -.5px 1.5px 1.5px #aaa;


		font-size: 180%;
		text-align: left;
		float: left;
		margin-left: 2%;
	}

	.user:hover {
		box-shadow: 0 2px 2px 1px #999;
	}

	.turk {
		text-transform: lowercase;
		overflow: hidden;
		display: block;
		resize: none;

		width: 100%;
		color: black;
		font-family: arial;
		font-size: 125%;
	}

	#hint-box {
		padding: 2% 1%;

		border-width: 2px;
		border-style: solid;
		border-color: black;
		background: #ffffba;

		font-size: 130%;
	}

	.popup-hints {
		padding: 1%;
		margin-bottom: 9%;
		border-width: 1px;
		border-style: solid;
		border-color: black;
		background: #ffffba;
		display: none;

		font-size: 130%;
	}

	



	.paraphrases_list {
		background: #ffffba;
		border-style: solid;
		border-width: .5px;
		border-radius: 2px;
		border-color: black;

		margin-right: 1%;
		margin-top: -4%;
		float: right;
	}
	.paraphrases_list:hover {
		background: #fff000;
		border-color: red;
		color: red;
	}

	#info_box{
		margin-left: 10%;
		display: flex;
		flex-wrap: wrap;
		
		padding: 2px;
		margin-right: 10%;
		margin-bottom: 3%;
	}

	#table_box{
		text-align: center;
		
		float: left;
		display: flex;
		flex: 1 0 30%;
		margin: auto;
		

	}

	#table_container{
		width: 100%;
		    column-count:2;
    -moz-column-count:2;
    -webkit-column-count:2;
    
	}


	
	.on_top{
		text-align: center;
		height: auto;

		display: flex;
		flex: 1 0 40%;
		
	

    	
	}

	.information_table{
			font-size: 160%;
			
		}

		#info_box_2{
			font-size: 90%;
			margin:auto;
		}

	



	.info_infos{

		text-align: center;
		margin-right: 0.5%;


		font-weight: bold;
		


		
	}

	.info_infos_val{
		margin-left: 22.5%;
		display: inline;
		text-align: center;
		font-weight: normal;
			 

	}

	#what{
		.info_infos_val;
		margin-left: 25%;
	}

	.attention{
		
		display: inline-block;
		
		border: 4px solid gray;
		
		padding: 7px;
    	background-color: #f44336; /* Red */
    	color: white;
    

	}

	.info_spot{
		width: 157.5%;
		margin-top: 1%;
		text-align: center;


		
		font-weight: bold;
		font-size: 120%;\

	    color: #00529b;
	    background-color: #bde5f8;
	    
	}


	.instr{font-style: normal; font-family: arial; background: none; font-size: 110%; margin-left: 25%}

	#goal_title{
			
			margin-left: 22%;
			margin-right: 22%;
			border-color: black;
			font-size: 230%;
			border: 2px solid black;
			text-align: center;
			padding-top: 0.6%;
			padding-bottom: 0.6%;

			border-radius: 84px 34px 85px 34px;
-moz-border-radius: 84px 34px 85px 34px;
-webkit-border-radius: 84px 34px 85px 34px;
border: 2px solid #000000;

-webkit-box-shadow: inset 0px 0px 99px -13px rgba(0,0,0,0.78);
-moz-box-shadow: inset 0px 0px 99px -13px rgba(0,0,0,0.78);
box-shadow: inset 0px 0px 99px -13px rgba(0,0,0,0.78);
		}



			table {
				padding: 2%;
	  border-spacing: 0.1rem;
	 

	}

	#info_box_2 tr{
		border:2px solid black;
		padding: 10rem;

		
		 border: 1px solid black;

	}

	th {
		border:2px solid black;
		padding: 0.5rem;

	}
	td {
	  padding: 0.5rem;
	   border:1.2px solid black;

	  
	}
	tr{
		
		 border: 1px solid black;
		

	}

	td:nth-child(1) { 
	 background-color: 	#D3D3D3;  border:none;  font-weight: bold;}
	td:nth-child(2,3) { background-color: white, border:2px solid black; }
	
	

	form {
    position: relative;

  }

	/*For text+submit*/
	input[type=text] {
		margin-left: 1.6%	;

		border: 1px solid black;
	 	width: 90%;
	 	height: 30px;	
	 	font-size: 20px;
	  	
	}

	#send {

		font-size: 100%;
		color: #333;
		margin-top: 2px;
		
		background-image: url("images/send.png");
		background-repeat: no-repeat;
		/*
		background-position: center;
		background-size: 50%;
		*/
		border-radius: 5px;
		border-style: solid;
		border-width: 1px;
		border-color: black;
		width: 7.7%;
		height: 4%;
	}



	#send:hover {
		background: #53a4c3;
		/*
		background-image: url("images/send_active.png");
		background-repeat: no-repeat;
		background-position: center;
		background-size: 50%;
		*/
		color: white;
	}

	#send:active {
		background: #53b8c3;
		/*
		background-image: url("images/send_active.png");
		background-repeat: no-repeat;
		background-position: center;
		background-size: 40%;
		*/
		color: white;
	}

	.float-left{
		float:left;
		display: inline-block;

	}

	#chat-box {
		/*margin-bottom: 22%;*/
		height: 100%;


	}

	.example_b {
		color: #fff !important;
		text-transform: uppercase;
		font-weight: bold;

		background-image: linear-gradient(to right top, #b3e7ae, #94d88c, #74c86a, #52b845, #24a817);
		padding: 6%;
		border-radius: 25%;
		border-radius: 50px;
		font-size: 120%;
		border: none;
		margin-left: 10%;
		width:50%;
		margin-top: 280%;


	}
	#ok_button {
		margin-left: 0%;

	}


	.attention_big{
		color: white;
		background: none;
		font-size: 120%;
	}

	.example_c {
		color: #fff !important;
		text-transform: uppercase;
		font-weight: bold;

		/*background: #8B0000;*/
		padding: 6%;
		border-radius: 50px;
		font-size: 150%;
		border: none;
		margin-left: ;

		width:50%;
		margin-left: 17%;
		background-image: linear-gradient(to left top, #a61111, #b63731, #c3544f, #cd6f6c, #d58989);
		margin-top: 265%;

	}

	.button_stop{
		margin-top: 94%;


	}

	

	input[type='checkbox'] {
	    -webkit-appearance:none;
	    width:30px;
	    height:30px;
	    background:white;
	    border-radius:5px;
	    border:2px solid #555;
	}
	input[type='checkbox']:checked {
	    background: red;
	}

	.custom-alert {
  display: inline-block;
  visibility: hidden;
  background-color: #666;
  color: #fff;
  text-align: enter;
  margin: 5% auto;
  padding: 12px 48px;
}

		

		#belief_box{

			-webkit-border-radius: 40px 0px 40px 0px;
-moz-border-radius: 40px 0px 40px 0px;
border-radius: 40px 0px 40px 0px;

		}

		#errorForm ul{
  list-style: none;
  margin: 0;
  padding: 0;
	overflow: auto;
}

#errorForm ul li{
  color: 	#000000;
  display: block;
  position: relative;

  font-weight: bold;
  font-size: 150%;
  height: 100px;
  padding-bottom: 1%;
	border-bottom: 2px solid #333;
}

#errorForm ul li input[type=radio]{
  position: absolute;
  visibility: hidden;
}

#errorForm ul li label{
  display: block;
  position: relative;
  font-weight: 300;
  font-weight: bold;
  font-size: 1.35em;
  padding: 25px 25px 25px 80px;
  margin: 10px auto;
  height: 30px;
  z-index: 9;
  cursor: pointer;
  -webkit-transition: all 0.25s linear;
}

#errorForm ul li:hover label{
	color: #6495ED;
}

#errorForm ul li .check{
  display: block;
  position: absolute;
  border: 5px solid #AAAAAA;
  border-radius: 100%;
  height: 25px;
  width: 25px;
  top: 30px;
  left: 20px;
	z-index: 5;
	transition: border .25s linear;
	-webkit-transition: border .25s linear;
}

#errorForm ul li:hover .check {
  border: 5px solid #FFFFFF;
}

#errorForm ul li .check::before {
  display: block;
  position: absolute;
	content: '';
  border-radius: 100%;
  height: 15px;
  width: 15px;
  top: 5px;
	left: 5px;
  margin: auto;
	transition: background 0.25s linear;
	-webkit-transition: background 0.25s linear;
}

#errorForm input[type=radio]:checked ~ .check {
  border: 5px solid #6495ED;
}

#errorForm input[type=radio]:checked ~ .check::before{
  background: #6495ED;
}

#errorForm input[type=radio]:checked ~ label{
  color: #6495ED;
}

.signature {
	margin: 10px auto;
	padding: 10px 0;
	width: 100%;
}

.signature p{
	text-align: center;
	font-family: Helvetica, Arial, Sans-Serif;
	font-size: 0.85em;
	color: #AAAAAA;
}

.signature .much-heart{
	display: inline-block;
	position: relative;
	margin: 0 4px;
	height: 10px;
	width: 10px;
	background: #AC1D3F;
	border-radius: 4px;
	-ms-transform: rotate(45deg);
    -webkit-transform: rotate(45deg);
    transform: rotate(45deg);
}

.signature .much-heart::before, 
.signature .much-heart::after {
	  display: block;
  content: '';
  position: absolute;
  margin: auto;
  height: 10px;
  width: 10px;
  border-radius: 5px;
  background: #AC1D3F;
  top: -4px;
}

.signature .much-heart::after {
	bottom: 0;
	top: auto;
	left: -4px;
}

.signature a {
	color: #AAAAAA;
	text-decoration: none;
	font-weight: bold;
}

#errorForm{
	display: inline-block;
	margin-left: 5%;
}

	#next{
		display: block;
	}

	.mainselection select {
   border: 0;
   color: white;

   background: transparent;
   font-size: 20px;
   font-weight: bold;
   padding: 2px 10px;
   width: 378px;
   *width: 350px;
   *background: #58B14C;
   -webkit-appearance: none;
}

.mainselection option{
	background-image: linear-gradient(to right top, #f68f09, #f4a61d, #f1bc33, #eed14c, #ebe566);
	font-weight: bold;

}

.mainselection {
   overflow:hidden;
   
   -moz-border-radius: 9px 9px 9px 9px;
   -webkit-border-radius: 9px 9px 9px 9px;
   border-radius: 9px 9px 9px 9px;
   box-shadow: 1px 1px 11px #330033;
   background-image: linear-gradient(to left top, #a61111, #b63731, #c3544f, #cd6f6c, #d58989);
   color: white;
   text-align: center;
   font-size: 130%;

}


	</style>
</head>
<body>

	<header></header>
	

	<div id="white">

		<div id="goal_form" >
				<h1 class="title" id="title_2">Goal</h1>
				<div> 
					<h2 id="goal_title"> You want to make a restaurant reservation</h2>

				</div>
	          	<h3 class="guidelines"> 
	          	<!-- 
	          	<ul>
		          	  <mark class="instr" > <mark  class="green"> Green values </mark> must be communicated <mark class="bold"> exactly  </mark> as you read them. </mark> 
	          	</ul>
	          	-->

	          	</h3>
	         </div>

	        <div id="info_box">
		        <div class="live_infos" id="table_box">

		        	<div class="live_infos" id="table_container">


		         	
		       		 </div>
		         	
		        </div>
		        


				<br>
			</div>


			<h1 class="title">Good Interaction Example!</h1>
	        <div id="info_box">
		       
			</div>
			<div id="chat-box"> 
				
			<div id="no_button" align="center" class="float-left" style="width: 20%;">
							
								<div class="button_cont"  onclick="somethingWrong()" ><button class="example_c" style=""> YOU GOT ME <br> <mark class="attention_big"> WRONG! </mark></button> </div>
				</div>
				<div align="center" class="float-left" style="width: 60%;">
					<form id="submit-form" action="submit.php" method="POST" style="margin-bottom: -.1%;">
						<div id="chat">
								<div class="div_user">
									<p class="user"> Hi!</p>>
								</div>

								<div class="div_agent">
									<p class="agent"> Hello, how can I help you?</p>
								</div>

								<div class="div_user">
									<p class="user"> I want to buy a movie ticket!</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Alright. So you want to insert a ticket purchase. Which movie's title?</p>
								</div>

								<div class="div_user">
									<p class="user">Schindler's List</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Is this movie what you were looking for?[1. title: Schindler's List, genre: Biography, director: Steven Spielberg, actor: Liam Neeson, rating: r]</p>
								</div>

								<div class="div_user">
									<p class="user"> yes!</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Ok! You have selected the following movie: [title: Schindler's List, genre: Biography, director: Steven Spielberg, actor: Liam Neeson, rating: r] . Please tell me the theater's name</p>
								</div>

								<div class="div_user">
									<p class="user"> We usually go to Multicinema Padova</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Mm-mmh . Is this theater what you were looking for? [1. name: MultiCinema Padova, chain: MultiCinema circuit, city: Padova]</p>
								</div>

								<div class="div_user">
									<p class="user"> yes, that one</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Ok! You have selected the following theater: [name: MultiCinema Padova, chain: MultiCinema circuit, city: Padova] . Please tell me the screening's date</p>
								</div>

								<div class="div_user">
									<p class="user"> November 07 at 10 pm</p>>
								</div>

								<div class="div_agent">
									<p class="agent">Mm-mmh . Is this screening what you were looking for? [1. time: 10 pm, date: November 07]</p>
								</div>

								<div class="div_user">
									<p class="user"> Yes!</p>>
								</div>

								<div class="div_agent">
									<p class="agent"> ok! Which ticket purchase's number of tickets?</p>
								</div>

								<div class="div_user">
									<p class="user"> 1 ticket</p>>
								</div>

								<div class="div_agent">
									<p class="agent"> Which ticket purchase's customer name?</p>
								</div>

								<div class="div_user">
									<p class="user"> I'm Marco Mancini</p>>
								</div>

								<div class="div_agent">
									<p class="agent"> Ok. As requested by you, I have registered your ticket purchase for [ticket purchase number of tickets: 1, ticket purchase customer name: Marco
									Mancini, screening time: 10 pm, screening date: November 07, movie title: Schindler's List, movie genre: Biography, movie cast: Liam Neeson, Ben Kingsley, Ralph Fiennes, Caroline Goodall, Jonathan Sagall, theater name: MultiCinema Padova, theater address: Via Giuseppe Rossi 34] . Now, is there anything else I can help you with or should I finalize?</p>
								</div>

								<div class="div_user">
									<p class="user"> I'm ok! Bye!</p>>
								</div>

								<div class="div_agent">
									<p class="agent"> 
									Goodbye</p>
								</div>



								
						</div>
					</form>
			
				   
				</div>

				<div id="ok_button" align="center" style="width: 20%;" class="float-left">
					<div class="button_cont" align="center"><button class="example_b" onclick="end_f(true)" style="" > SUCCESFULLY <br>  <mark class="attention_big"> COMPLETED! </mark>  </button>  </div>
				</div>

				
				</div>

			<div id="next_2" style="margin-left: 15%; margin-top: -20%; display: none;">
				<div id="next" align="center" style="width: 20%; display:none; margin-left: 30%;">
								
						<div class="button_cont" align="center" ><button class="example_c" onclick="end_f(false)" style="background: #1a75ff;"  > NEXT </button> </div>

						

					
				</div>

			
				</div>


		</div>
		


		</div>

		



	<script>	


		var baseline = false
		var display_only_lasts = true;
		var dates_for_cbs = {};
		var start_wrong = null;

		var end = false
		var slots = []
		var to_check_slots = []
		var goal = ""
		var belief = {}
		var alerted = 1
		var user = ""
		var beliefs = {}
		var n_turn_passed = 4
		var to_upd = true
		var finalized = "None"

		var bl_post = <?php echo '"'.$EXPTYPE.'"';?>

		if (bl_post == "BL"){
			baseline = true;
		}
		$.ajax({
	              type: "POST",
	              cache: false,
	              url: "lol.php",//url to file
	              success: function(data){
	           			//user = data
	           			user = "user_good"  


	           			$.getJSON('goals/' + user, function(data) {
	           

			              		goal_struct = data
			           			goal = goal_struct['goal']  
			           			slots = goal_struct['slots']
			           			for (var sl in slots){
			           				belief[sl] = "?"
			           			}
			           			document.getElementById("goal_title").innerHTML = goal;
			           			$.getJSON('beliefs/' + user, function(sl) {
						        	new_bel = {}
						        	new_slots = {}

						        	for (s in slots){
						        		if (slots[s] != "ANY VALUE YOU WANT"){
						        			new_slots[s] = slots[s]
						        			new_bel[s] = sl[s]
						        		}
						        	}
						           
						           
							        tableCreate(new_slots, new_bel)
				           			to_check_slots = slots
	            					to_check_slots = Object.assign({}, slots);

						            //document.getElementById("belief_ta").appendChild(h4)

						        });
			           			

				          

				            //document.getElementById("belief_ta").appendChild(h4)

				        });

	           			    
	                }

              });
		$(document).ready(function() {
			  $.ajaxSetup({ cache: false });
			  var start = new Date();
			  $(window).unload(function() {
			      var end = new Date();
			      var e = document.getElementById("error_picker");
			      if (start_wrong != null){
			      	var err_type = e.options[e.selectedIndex].value;
			      	var interaction_time = Math.abs(start_wrong - start) / 1000;

			      }else{
			      	var err_type = "NONE";
			      	if (n_turn_passed + 1 > 0){
			      		var interaction_time = Math.abs(end - start) / 1000;
			      	}else{
			      		var interaction_time = Math.abs(end - end) / 1000;
			      	}
			      				      
			      }
				  
			        var interaction_hours = Math.floor(interaction_time / 3600) % 24
			      	var interaction_minutes = Math.floor(interaction_time / 60) % 60
			      	var interaction_seconds = interaction_time % 60

			      if(baseline){
			      	var turn_selection_hours = 0
			      	var turn_selection_minutes = 0
			      	var turn_selection_seconds = 0

			      	if (start_wrong != null){
			      		var res_error_find = Math.abs(end - start_wrong )/ 1000
			      		var res_error_hours = Math.floor(res_error_find/3600) % 24
			      		var res_error_minutes = Math.floor(res_error_find / 60) % 60;
			      		var res_error_seconds = res_error_find % 60;
			      	}else{
			      		var res_error_hours = 0
			      		var res_error_minutes = 0
			      		var res_error_seconds = 0
			      	}

			      }else{
			      	if (start_wrong != null){
			      		var inputs = document.querySelectorAll("input[type='checkbox']");
				
						for(var i = 0; i < inputs.length; i++) {
						    if(inputs[i].checked){
						    	inputs[i].getAttribute("turn_id");
						    	turn = inputs[i].getAttribute("turn_id");
						    }
						}
						last_check_time = dates_for_cbs[turn][dates_for_cbs[turn].length - 1]
			      		var turn_selection_find = Math.abs(start_wrong - last_check_time) / 1000
			      		var turn_selection_hours = Math.floor(turn_selection_find/3600) % 24
			      		var turn_selection_minutes = Math.floor(turn_selection_find/60) % 60
			      		var turn_selection_seconds = turn_selection_find % 60

			      		var res_error_find = Math.abs(end - last_check_time) / 1000
			      		var res_error_hours = Math.floor(res_error_find / 3600) % 24
			      		var res_error_minutes = Math.floor(res_error_find / 60) % 60
			      		var res_error_seconds = res_error_find % 60
			      	}else{
			      		var res_error_hours = 0
			      		var res_error_minutes = 0
			      		var res_error_seconds = 0

			      		var turn_selection_hours = 0
				      	var turn_selection_minutes = 0
				      	var turn_selection_seconds = 0

			      	}
			      }
			      

			     
				 var res = Math.abs(end - start) / 1000;
				 var hours = Math.floor(res / 3600) % 24;   
				 var minutes = Math.floor(res / 60) % 60;  
				 var seconds = res % 60;

				 console.log({'seconds': seconds,
			        		'hours': hours,
			        		"minutes": minutes,
			        		"turns": n_turn_passed +1,
			        		"finalized": finalized,
			    			"user_id": user,
			    			"task_category": bl_post,
			    			"turn_selection_hours": turn_selection_hours,
			    			"turn_selection_minutes": turn_selection_minutes,
			    			"turn_selection_seconds": turn_selection_seconds,
			    			"error_selection_hours": res_error_hours,
			    			"error_selection_minutes": res_error_minutes,
			    			"error_selection_seconds": res_error_seconds,
			    			"interaction_hours": interaction_hours,
			    			"interaction_minutes": interaction_minutes,
			    			"interaction_seconds": interaction_seconds,
			    			"error_type": err_type})


			      $.ajax({ 
			      	type: "POST",
			        url: "log.php",
			        data: {'seconds': seconds,
			        		'hours': hours,
			        		"minutes": minutes,
			        		"turns": n_turn_passed +1,
			        		"finalized": finalized,
			    			"user_id": user,
			    			"task_category": bl_post,
			    			"turn_selection_hours": turn_selection_hours,
			    			"turn_selection_minutes": turn_selection_minutes,
			    			"turn_selection_seconds": turn_selection_seconds,
			    			"error_selection_hours": res_error_hours,
			    			"error_selection_minutes": res_error_minutes,
			    			"error_selection_seconds": res_error_seconds,
			    			"interaction_hours": interaction_hours,
			    			"interaction_minutes": interaction_minutes,
			    			"interaction_seconds": interaction_seconds,
			    			"error_type": err_type},
			        async: false
			      })
			   });

			  $(".drop .option").click(function() {
			    var val = $(this).attr("data-value"),
			        $drop = $(".drop"),
			        prevActive = $(".drop .option.active").attr("data-value"),
			        options = $(".drop .option").length;
			    $drop.find(".option.active").addClass("mini-hack");
			    $drop.toggleClass("visible");
			    $drop.removeClass("withBG");
			    $(this).css("top");
			    $drop.toggleClass("opacity");
			    $(".mini-hack").removeClass("mini-hack");
			    if ($drop.hasClass("visible")) {
			      setTimeout(function() {
			        $drop.addClass("withBG");
			      }, 400 + options*100); 
			    }
			    triggerAnimation();
			    if (val !== "placeholder" || prevActive === "placeholder") {
			      $(".drop .option").removeClass("active");
			      $(this).addClass("active");
			    };
			  });
			  
			  function triggerAnimation() {
			    var finalWidth = $(".drop").hasClass("visible") ? 22 : 20;
			    $(".drop").css("width", "24em");
			    setTimeout(function() {
			      $(".drop").css("width", finalWidth + "em");
			    }, 400);
			  }
			  $('#message_txt').keypress(function(e){
			      if(e.keyCode==13)
			      $('#send').click();
			    });

		});
		function sendFinalMessage(good, turn_id, error_type){
			exp_t = "ADVANCEDTASK";
			if (baseline){
				exp_t = "BASELINETASK"

			}
			if (good == true){
				msg = "[[[ENDTASK_TRUE_" + exp_t + "]]]"
			}else{
				msg = "[[[ENDTASK_FALSE_" + turn_id + "_" + error_type + "_" + exp_t + "]]]"
			}

		
			sendMessageClient(msg, user, show=false, finalize=true, good=good, turn=turn_id)

		    

		}
		function updateScroll(){
		    var element = document.getElementById("chat");
		    element.scrollTop = element.scrollHeight;
		}

	
        function end_f(good){
			var url = 'end.php';
			if (good == true){
				finalized = "SUCCESS"
				sendFinalMessage(true, 0, "yolo")
				
			}else{
				t = null
				var inputs = document.querySelectorAll("input[type='checkbox']");
				
						for(var i = 0; i < inputs.length; i++) {
						    if(inputs[i].checked){
						    	inputs[i].getAttribute("turn_id");
						    	t = inputs[i].getAttribute("turn_id");
						    }
						}
				if (t == null){
					alert("YOU MUST CHECK THE TURN!")
				}else{
					finalized = "ERRONEOUS"
				

					var checkboxes = document.getElementsByTagName("checkbox");
					var turn = 0;
					for (var item in checkboxes){
						if(item.checked){
					    	turn = item.getAttribute("turn_id");
					    }
					}

					var inputs = document.querySelectorAll("input[type='checkbox']");
					
					for(var i = 0; i < inputs.length; i++) {
					    if(inputs[i].checked){
					    	inputs[i].getAttribute("turn_id");
					    	turn = inputs[i].getAttribute("turn_id");
					    }
					}

					var e = document.getElementById("error_picker");
					var error_v = e.options[e.selectedIndex].value;


				    sendFinalMessage(false, turn,error_v)
				}
			}
			

	    }



        setInterval(function() {
	       	//scrollToBottom();
	        $.getJSON('beliefs/' + user, function(sl) {
	        	new_bel = {}
	        	new_slots = {}

	        	for (s in slots){
	        		if (slots[s] != "ANY VALUE YOU WANT"){
	        			new_slots[s] = slots[s]
	        			new_bel[s] = sl[s]
	        		}
	        	}
	           
	           updateBelief(new_bel, new_slots)
	          

	            //document.getElementById("belief_ta").appendChild(h4)

	        });
	    }, 1);

	    function checkOneBox(cbox){
	    	var checkboxes = document.getElementsByTagName("checkbox");

	    	index = 0;
	    	checkboxes.forEach(function(item){
			    item.checked = false;
			    item.setAttribute("turn_id", index);
			    index = index + 1;
			});

			cbox.checked = true;


	    }



	function updateBelief(belief, slots){
		if (to_upd == true){

			for (var b in belief){
			belief_td = document.getElementById("belief_" + b)
			slot_td = document.getElementById("slotval_" + b)

			belief_td.removeChild(belief_td.childNodes[0]);
			belief_td.appendChild(document.createTextNode(belief[b]))

			

			if (belief[b] != slots[b] && slots[b] != "?"){
				belief_td.classList = ["red"]
			}
			else{
				belief_td.classList = ["green"]
			}

			if (belief[b] == slots[b] && belief[b] == "?"){
				belief_td.classList = ["red"]

			}

			if (belief[b].toLowerCase() != slots[b].toLowerCase() && belief[b] != "?" ){
				belief_td.classList = ["orange"]
			
				if (slots[b] != "?"){
					alerted -= 1;
					if (alerted == 0){
						 alertify.dialog('alert').set({transition:'pulse',message: 'ATTENTION!<br> Maybe the system mysunderstood something you typed!<br>Or you did not follow the goal!'}).show();
					}
				}
				
			} 


		}

		}
		
	}

	

	function tableCreate(slots, belief, after_wrong=false) {

      var tbl = document.createElement('table');

      
      var tbdy = document.createElement('tbody');

      //slots head
      	var tr_head = document.createElement('tr');
      	var th_head = document.createElement('th');
      	th_head.colSpan = 2;



        var tr_head_slots = document.createElement('tr');
      	var th_head_slotname = document.createElement('th');
      	var th_head_slotval = document.createElement('th');
      	var th_head_belief = document.createElement('th');

        th_head_slotname.appendChild(document.createTextNode("Information"));
        th_head_slotval.appendChild(document.createTextNode("You say"));
        th_head_belief.appendChild(document.createTextNode("System Understood"));
      	
      	tr_head_slots.appendChild(th_head_slotname);
      	tr_head_slots.appendChild(th_head_slotval);
      	tr_head_slots.appendChild(th_head_belief);
      	tbdy.appendChild(tr_head_slots);

        for (var slot in slots){
        	
	        	var tr_slot = document.createElement('tr');
	        	var td_slotname = document.createElement('td');
	        	var td_slotval = document.createElement('td');
	        	var td_belief = document.createElement('td');


	        	slot_value = String(slot).split("::");

	        	if (slot_value.length > 1){
	        		s_v = slot_value[1]
	        		s_v = slot_value[0] + "' " + slot_value[1]
	        	}else{
	        		s_v = slot_value[0]
	        	}	

	        	val_towrite = slots[slot]
	        	td_slotname.appendChild(document.createTextNode(s_v))
	        	slot_val = document.createTextNode(slots[slot])
	        	if (after_wrong == false){
	        		td_belief.appendChild(document.createTextNode("?"))
	        	}else{
	        		td_belief.appendChild(document.createTextNode(belief[slot]))
	        	}
	        	
	        	td_belief.id = "belief_" + slot

	        	

	        	td_slotval.appendChild(slot_val)
	        	td_slotval.style.fontWeight="bold";
	        	if (val_towrite == "ANY VALUE YOU WANT"){
	        		td_slotval.style.fontSize="50%";
	        		td_slotval.style.fontWeight = "normal";
	        		td_slotval.style.color = "black";
	        	}

	        	td_slotval.id = "slotval_" + slot
	        	if (slots[slot] == "?"){
	        		
	        		td_slotval.classList = ["red"]
	        		
	        		
	        	}else{
	        		
	        		if(val_towrite != "ANY VALUE YOU WANT"){
						td_slotval.style.color = "green"
	        		}
	        		
	        	}

	        	if (belief[slot] == "?"){
	        		

	        		td_belief.classList = ["red"]
	        		
	        	}else{
	        		

	        		if(val_towrite != "ANY VALUE YOU WANT"){
						td_slotval.style.color = "green"
	        		}
	        		
	        	}



	        	tr_slot.appendChild(td_slotname)
	        	tr_slot.appendChild(td_slotval)
	        	tr_slot.appendChild(td_belief)


	        	tbdy.appendChild(tr_slot)

        	
        	


        }

      tbl.appendChild(tbdy);
      tbl.classList = ["information_table"]
      div = document.getElementById("table_container")


      div.appendChild(tbl)
      return tbl
    }

    
    function getErrorSelect(){
		var array = ["ERROR: COMPRENSION ERROR","ERROR: INTERACTION ERROR","ERROR: BOTH","ERROR: I DON'T KNOW"];
					var elementExists = document.getElementById("error_picker");
					if (elementExists){
						elementExists.remove()

					}
					//Create and append select list
					var selectList = document.createElement("select");
					selectList.id = "error_picker";
					selectList.classList = ["mainselection"]
					selectList.style.fontWeight = "bold";
					selectList.style.height = "90px"
					selectList.style.margin = "auto"
					selectList.style.fontSize = "130%"
					//selectList.style.backgroundImage = "linear-gradient(to left top, #a61111, #b63731, #c3544f, #cd6f6c, #d58989)"
					
					errors = {0: "NLU", 1:"DM", 2:"BOTH", 3: "DONTKNOW"}
					//Create and append the options
					for (var i = 0; i < array.length; i++) {
					    var option = document.createElement("option");
					    option.style.backgroundImage = "linear-gradient(to right top, #f68f09, #f4a61d, #f1bc33, #eed14c, #ebe566)";
					    option.style.color = "black";
					    option.style.fontWeight = "bold";
					    option.value = errors[i];
					    option.text = array[i];
					    selectList.appendChild(option);
					}
					return selectList
    }

    function somethingWrong(){
    	if (n_turn_passed > 0){
    		start_wrong = new Date();
    		console.log(start_wrong)

    		

    		to_upd = false
    	document.getElementById("message_txt").remove()
    	document.getElementById("send").remove()
    	document.getElementById("goal_title").remove()
    	document.getElementById("title_2").innerHTML = "Belief of the system at the MARKED turn"



    	if (end === false){
    		var index =  0

    		
    		alertify.dialog('alert').set({transition:'pulse',message: '<div class="guidelines">From now you have to check the <mark class="bold"> FIRST </mark> turn where you encountered problems, also providing the category of error!<br><br> When marking a turn we help you understanding the problem also providing what the system understood at that step! </div>'}).show();

    		
    		
	    	textareas = document.getElementById("chat").childNodes;

	    	t = 0
	    	z = 0
	    	textareas.forEach(function(item){
			    radio = document.createElement("input");
			    radio.type = "checkbox"

			    radio.classList = ["wherewrong"]
			    radio.addEventListener("change", function(cbox){
				    var checkboxes = document.getElementsByTagName("checkbox");
				    var tab = document.getElementsByClassName("information_table")[0];
				    tab.remove()

				    tableCreate(slots, beliefs[this.getAttribute("turn_id")], true)

				    $('input[type=checkbox]').each(function () {
					    this.checked = false

					});

					selectList = getErrorSelect()

			    	document.getElementById("user_div_"+this.getAttribute("turn_id")).appendChild(selectList)
			    	
				

					this.checked = true;

					dates_for_cbs[this.getAttribute("turn_id")].push(new Date())
				});
	    		radio.style.float = "left";

	    		if (item.classList[0] == ['div_user']){

	    			item.appendChild(radio)
	    			if (baseline){
	    				if (t != textareas.length - 2 && t != textareas.length - 1){
	    				item.childNodes[1].style.display = "none"
	    				}
	    			}
	    			
	    		}
	    		if (baseline && display_only_lasts){
	    			if (t != textareas.length - 2 && t != textareas.length - 1){
	    				item.style.display = "none"
	    				}
	    			

	    		}
	    		t+= 1

	    		
			});

			var inputs = document.querySelectorAll("input[type='checkbox']");
			for(var i = 0; i < inputs.length; i++) {
			    inputs[i].checked = false;   
			    inputs[i].setAttribute("turn_id", index);
	    		index = index + 1;
			}

			if (baseline){
				first_cb = document.getElementsByClassName("wherewrong")[document.getElementsByClassName("wherewrong").length - 1]
			}else{
				first_cb = document.getElementsByClassName("wherewrong")[0]
			}
			if(baseline){
				first_cb.checked = true
			}
    		//;
    		var tab = document.getElementsByClassName("information_table")[0];
			tab.remove()
    		tableCreate(slots, beliefs[first_cb.getAttribute("turn_id")], true)
    		selectList = getErrorSelect()
    		
    		if (baseline){
    			document.getElementById("user_div_" + String(document.getElementsByClassName("wherewrong").length - 1)).appendChild(selectList)
    		}
    		
		    

			wr = document.getElementById("no_button")
    		ri = document.getElementById("ok_button")
    		next = document.getElementById("next")
    		next2 = document.getElementById("next_2")
    	

    		
    		

    		wr.style.visibility = "hidden";
    		ri.style.visibility = "hidden";



    		next.style.display = "block";
    		next2.style.display = "block";
    	} else {

    		end_f();

    	}
    	end = true;


    	}else{
    		alert("YOU NEED TO INTERACT WITH THE BOT!")
    	}
    	
    }

    function sleep(milliseconds) {
	  var start_1 = new Date().getTime();
	  for (var i = 0; i < 1e7; i++) {
	    if ((new Date().getTime() - start_1) > milliseconds){
	      break;
	    }
	  }
	}

	function dumpBeliefState(){

    	$.getJSON('beliefs/' + user, function(belief) {
    		beliefs[n_turn_passed] = belief;	
    		dates_for_cbs[n_turn_passed] =  [];   
    		n_turn_passed += 1   


	    });

	}

    function checkBelief(){

    	sleep(200)
    	$.getJSON('beliefs/' + user, function(belief) {
	           
	           for (var sl in slots){
	           		if (belief[sl] != "?"){
	           			if (slots[sl] != "?"){
	           				if (sl in to_check_slots){
	           					if (belief[sl].toLowerCase() == to_check_slots[sl].toLowerCase()){
		           					alertify.success('The system got the slot ' + sl); 
		           					td_green = document.getElementById("belief_"+sl)
		           					td_green.classList.remove("red")
		           					td_green.classList.add("green")
		           					td_green.style.color = "green"

		           					delete to_check_slots[sl]
		           				}
	           				else {
	           					if (sl in to_check_slots){
	           						if (belief[sl].toLowerCase() != to_check_slots[sl].toLowerCase() && to_check_slots[sl].toLowerCase() != "any value you want" ){
			           					alertify.error('Maybe the system misunderstood a slot! '); 
			           					td_red = document.getElementById("belief_"+sl)
			           					td_red.style.color = "red"
			           					delete to_check_slots[sl]
		           					}
	           					}
	           					
	           				}
	           					
	           				}
	           				
	           			}
	           		}
	           }
	            //document.getElementById("belief_ta").appendChild(h4)

	       
	    });

    }

    function sendMessage(){
    	msg = document.getElementById("message_txt").value

    	
    	if (msg != "") {

    		$.ajax({
	              type: "POST",
	              cache: false,
	              url: "dump_message.php",//url to file
	              data: { msg: msg,
	              		user_id: user
	                },
	              success: function(data){
	           			textH = document.createTextNode(msg)
	           			divuser = document.createElement("div")
	           			divuser.classList = ["div_user"]
	           			divuser.id="user_div_" + n_turn_passed 

				    	p = document.createElement("p")
				    	p.appendChild(textH)
						p.classList = ["user"]
						p.readOnly = true

						divuser.appendChild(p)
				    	document.getElementById("chat").appendChild(divuser)
				    	

				    	document.getElementById("message_txt").value = ""
				    	//scrollToBottom()
				    	sendMessageClient(msg, user)
				    	elem = document.getElementById("chat")
				    	elem.scrollTop = elem.scrollHeight;
				    	
			                  
	                }

              });

	    	
	    	
	    }else{
	    	alertify.dialog('alert').set({transition:'pulse',message: 'You MUST insert a message!'}).show();
	    }
    	

    }

    

    function sendMessageClient(string, user, show=true, finalize=false, good=true, turn=0){

    	headers = { 'Content-Type': 'application/json'}


   
           data = { "version" : "1.0",
       				"sessionId" : "1",
       				"application" : {"applicationId": "api.vui.appId.1234"},
       				"user" : {"userId": user , "accessToken": "abc123", "telephoneNumber":"+11112345678"},
       				"request": {"utterance":  string },
       				"turnId" : "api.vui.session.abc-123",
       				"customerId" :"api.vui.session-abc-123"
       			}


       			$.ajax({
	              type: "POST",
	              cache: false,
	              url: "get_response.php",//url to file
	              data: { data:JSON.stringify(data),
	                },
	              success: function(data){
	              	if (show == true){
	              		dumpBeliefState()


	              		resp = JSON.parse(data)
		              	msg = resp['response']['outputSpeech']['text']

		              	divagent = document.createElement("div")
		           		divagent.classList = ["div_agent"]

				        text_agent = document.createTextNode(msg)
				    	p = document.createElement("p")
				    	p.appendChild(text_agent)
				    	p.classList = ["agent"]
				    	p.readOnly = true

				    	divagent.appendChild(p)
			

				    	document.getElementById("chat").appendChild(divagent)
				    	checkBelief()
				    	updateScroll()

	              	}
	              	if (finalize == true){
	
	              		url = "end.php"
	              		if (good == true){
				            var form = $('<form action="' + url + '" method="post">' +
						  '<input type="text" name="user_id" value="' + user + '" />' +
						  '<input type="text" name="type" value="' + good + '" />' +
						  '</form>');
							$('body').append(form);
							form.submit();
	              		}else{
	              			

							var form = $('<form action="' + url + '" method="post">' +
						  '<input type="text" name="user_id" value="' + user + '" />' +
						  '<input type="text" name="type" value="' + good + '" />' +
						  '<input type="text" name="turn_id" value="' + turn + '" />' +
						  '</form>');
							$('body').append(form);
							form.submit();

	              		}

	              	}
	              	
			    	
			    	
			                  
	                }

              });

    }

	</script>

</body>
</html>