
var sug_names_ret_backend;
var sug_names_in_frontend;

var pairs_returned_to_backend = [];
var backend_communication_loop_running = false;

var selection;
var active_pair_index;
var number_of_votes = 0;

var man_class_enabled = true

var infinte_loop_enabled = false

var await_return = false

//var width_of_div_sorting_strings = $('#div_sorting_strings').width();
//width_of_div_sorting_strings = 806

// Hulp functies
function key(d){ return d['key'] }
function return_key(d){ return d[0] }

function stringer_initialize(){
	vm._data['global_spinning_wheel'] = false
	$.get(
          url='/get_stringer_suggestion',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'requested_sex':vm._data['suggestion_sex']['female_selected'] ? 'F':'M',
            'how_many':10
            //'names_already_in_frontend':temp_comm_strings_in_frontend
          },
          callback=function(return_data){
				// Initialise, add the first 5 strings on the page. DIT IS NIET CLEAN
          		sug_names_ret_backend = return_data['names']
	          	sug_names_in_frontend = {}
	          	// Remove all the spans from the canvas
				selection = d3.select("#div_sorting_strings").selectAll("span")
					.data(d3.entries(sug_names_in_frontend), key);
				selection.exit()
					.remove()
				// Fill up names array
	          	for(var i=0;i<return_data['names'].length;i++){
	          		sug_names_in_frontend[i] ={}
	          		sug_names_in_frontend[i]['name'] = return_data['names'][i]	
	          	}
	          	// Add the strings in the "to sort div"	
				selection = d3.select('#div_sorting_strings')
								.selectAll("span")
								.data(d3.entries(sug_names_in_frontend), key);

				// Make the active one bigger
				active_pair_index = d3.keys(sug_names_in_frontend)[0]
				selection.enter()
							.append("span")
							.text(function(d){
								return d['value']['name']
							})
							.style("font-weight", function(d){
								if(d['key']==active_pair_index){ return 'bold' }else{ return 'normal'}
							})
							.style("font-size", function(d){
								if(d['key']==active_pair_index){ return '120%' }else{ return '100%' }
							})
							.style("display","block")
							.style("width","100%")
							.attr("class", "text-center");

				vm._data['global_spinning_wheel'] = true
			})				
}
function get_stringer_suggestion(how_many, initialise){

	if(initialise) vm._data['global_spinning_wheel'] = false
	await_return = true
	$.get(
          url='/get_stringer_suggestion',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'requested_sex':vm._data['suggestion_sex']['female_selected'] ? 'F':'M',
            'how_many':how_many
            //'names_already_in_frontend':temp_comm_strings_in_frontend
          },
          callback=function(return_data){

      		max_key = parseInt(d3.keys(sug_names_in_frontend)[d3.keys(sug_names_in_frontend).length-1])

      		for(var i=0;i<return_data['names'].length;i++){
      			new_key = max_key+i+1
      			sug_names_in_frontend[new_key] = {'name':return_data['names'][i]}
      		} 		

      		// When the suggestion are returned, disable wait screen, update table
      		switch_wait_screen('off') 
      		update_d3_string_pairs_table()

      		// And call itself again if there is less than 10 names on the screen:
      		if(10 - d3.keys(sug_names_in_frontend).length > 0){
      			get_stringer_suggestion(20 - d3.keys(sug_names_in_frontend).length,false)
      		}else{
      			// Disable infinite loop until user voted again
      			infinte_loop_enabled = false
      		}
          }
        )
}

function return_vote(name, vote){
	$.ajax({
    	url: '/return_vote',
    	dataType:'json',
		data: {'user_ID':user_ID,
            	'session_ID':session_ID,
				'feedback':vote,
				'name':name,
				'sex':vm._data['suggestion_sex']['female_selected'] ? 'F':'M'},
		success:function(){
		}
	});
}


function actions_after_vote(vote){
	
	// Actions to take:
	// - Return the vote to the backend
	// - Add the new string pair to the list of strings
	// - If it is the infite loop is not enabled, enable it.

	// // Parameter to keep track of votes
	number_of_votes = number_of_votes + 1;

	// //First store vote
	sug_names_in_frontend[active_pair_index]['man_vote'] = vote
	return_vote(sug_names_in_frontend[active_pair_index]['name'], vote)

	// Delete the first votes on top of the page, DANGEROUS
	delete sug_names_in_frontend[d3.keys(sug_names_in_frontend)[0]]

	// Fix the bug, if there are no names any more in the front end, let him wait
	if(d3.keys(sug_names_in_frontend).length == 1){
	 	console.log('He should be waiting')
	 	switch_wait_screen('on')
	}

	// Search for active pair
	var pair_not_found = true
	var i = 0;
	while (pair_not_found){
    	if(sug_names_in_frontend[d3.keys(sug_names_in_frontend)[i]]['man_vote'] == null){
     		active_pair_index = d3.keys(sug_names_in_frontend)[i]
     		console.log( 'Active pair index: '+ active_pair_index)
     		pair_not_found = false
     	}
     	i++;
	}
	// Update the table because a pair is deleted and a new one active
	update_d3_string_pairs_table()

	// If the voting loop is not enabled, start it start infite loop
	if(infinte_loop_enabled == false){
		infinte_loop_enabled = true
		get_stringer_suggestion(20 - d3.keys(sug_names_in_frontend).length,false)
	}
}

function switch_wait_screen(on_off){
	if(on_off == 'on'){
		vm._data['global_spinning_wheel'] = false
	}else{
		vm._data['global_spinning_wheel'] = true
	}
}

function update_d3_string_pairs_table(){

	// Now update the DOM with d3
	selection = d3.select("#div_sorting_strings").selectAll("span")
					.data(d3.entries(sug_names_in_frontend), key);

	selection.enter()
				.append('span')
				.text(function(d){
					return d['value']['name']
				})
				.style("display", "block")
				.style("width","100%")
				.attr("class", "text-center");

	selection.style("font-weight", function(d){
					if(d['key']==active_pair_index){ return 'bold' }else{ return 'normal'}
				})
				.style("font-size", function(d){
					if(d['key']==active_pair_index){ return '120%' }else{ return '100%' }
				})
				.style("display", "block")

	selection.exit()
				.remove()

	// selection.transition()
	//  			.style("top", function(d,i){return i*30})
	// 			// NICE to have, let them go left and right
	// 			// .style("left", function(d,i){
	// 			// 	temp = d['value']['dirty_street'] + " - " + d['value']['kad_street']
	// 			// 	if(d['value']['man_vote'] == null){
	// 			// 		// algin center
	// 			//  		return width_of_div_sorting_strings / 2 - temp.length*7 / 2
	// 			//  	}else{
	// 			//  		if(d['value']['man_vote'] == 'Yes'){
	// 			//  			// Align right
	// 			//  			return width_of_div_sorting_strings - 1 - $(this).width()
	// 			//  		}else{
	// 			//  			// Align left
	// 			//  			return 0
	// 			//  		}
	// 			//  	}
	// 			// })
}

	// temp_comm_strings_in_frontend = []
	// if(sug_names_in_frontend){
	// 	for(i=0; i<d3.keys(sug_names_in_frontend).length;i++){
	// 		console.log(sug_names_in_frontend)
	// 		temp_comm_strings_in_frontend[i] = sug_names_in_frontend[d3.keys(sug_names_in_frontend)[i]]['name']
	// 	}
	// }
