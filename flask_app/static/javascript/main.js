
var session_ID;
var user_ID;
var test_event
vm = new Vue({
  el: '#app',
  data: {
    counter_lookups:0,
    more_than_5_lookups:false,
    active_page:{
      welcome:false,
      lookup:true,
      suggest:true,
      list:true,
      about:true,
      login:true
    },
    global_spinning_wheel:true,
    stats_div:true,
  	landing_page_name:'',
    name_1: '',
  	name_2: '',
    name_1_meaning:'',
    name_2_meaning:'',
    name_1_gelijkaardig:'',
  	suggestion_request_sex:'',
  	region:'',
    returned_suggestion:{
      'name':'',
      'sex':''
    },
    suggestion_sex:{
      male_selected:false,
      female_selected:true,
      icon:"<i class='fa fa-venus' aria-hidden='true'>"
    },
    selection_liked_names:{
      male_selected:false,
      female_selected:true,
      icon:"<i class='fa fa-venus' aria-hidden='true'>"
    },
    lookup_sex_selection:{
      prim_name:{
        male_selected:false,
        female_selected:true,
        icon: "<i class='fa fa-venus' aria-hidden='true'>"
      },
      ref_name:{
        male_selected:false,
        female_selected:true,
        icon: "<i class='fa fa-venus' aria-hidden='true'>"
      },
    },
    name_to_add:'',
    name_to_add_sex:'',
    liked_names:[],
    liked_names_displayed:[],
    user_create_login:{
      email:'',
      password:'',
      repeat_password:''
    },
    user_login:{
      email:'',
      password:''
    },
  	score_original:{
  		name_1:{
  			1:{ full: true, half_empty: false, empty: false },
	  		2:{ full: false, half_empty: true, empty: false },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},name_2:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},
  	},
  	score_vintage:{
  		name_1:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},name_2:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},
  	},
  	score_trend:{
  		name_1:{
  			1:{ full: true, half_empty: false, empty: false },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},name_2:{
  			1:{ full: false, half_empty: true, empty: false },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},
  	},
  	score_classic:{
  		name_1:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},name_2:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},
  	},
  	score_popular:{
  		name_1:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},name_2:{
  			1:{ full: false, half_empty: false, empty: true },
	  		2:{ full: false, half_empty: false, empty: true },
	  		3:{ full: false, half_empty: false, empty: true },
	  		4:{ full: false, half_empty: false, empty: true }
  		},
  	},
    suggest:{
      original:{
        min:{
          1:{ full: false, half_empty: false, empty: true },
          2:{ full: false, half_empty: false, empty: true },
          3:{ full: false, half_empty: false, empty: true },
          4:{ full: false, half_empty: false, empty: true }
        },max:{
          1:{ full: true, half_empty: false, empty: false },
          2:{ full: true, half_empty: false, empty: false },
          3:{ full: true, half_empty: false, empty: false },
          4:{ full: true, half_empty: false, empty: false }
        },
      },
      populair:{
        min:{
          1:{ full: false, half_empty: false, empty: true },
          2:{ full: false, half_empty: false, empty: true },
          3:{ full: false, half_empty: false, empty: true },
          4:{ full: false, half_empty: false, empty: true }
        },max:{
          1:{ full: true, half_empty: false, empty: false },
          2:{ full: true, half_empty: false, empty: false },
          3:{ full: true, half_empty: false, empty: false },
          4:{ full: true, half_empty: false, empty: false }
        },
      },
      classic:{
        min:{
          1:{ full: false, half_empty: false, empty: true },
          2:{ full: false, half_empty: false, empty: true },
          3:{ full: false, half_empty: false, empty: true },
          4:{ full: false, half_empty: false, empty: true }
        },max:{
          1:{ full: true, half_empty: false, empty: false },
          2:{ full: true, half_empty: false, empty: false },
          3:{ full: true, half_empty: false, empty: false },
          4:{ full: true, half_empty: false, empty: false }
        },        
      },
      vintage:{
        min:{
          1:{ full: false, half_empty: false, empty: true },
          2:{ full: false, half_empty: false, empty: true },
          3:{ full: false, half_empty: false, empty: true },
          4:{ full: false, half_empty: false, empty: true }
        },max:{
          1:{ full: true, half_empty: false, empty: false },
          2:{ full: true, half_empty: false, empty: false },
          3:{ full: true, half_empty: false, empty: false },
          4:{ full: true, half_empty: false, empty: false }
        },
      },
      trending:{
        min:{
          1:{ full: false, half_empty: false, empty: true },
          2:{ full: false, half_empty: false, empty: true },
          3:{ full: false, half_empty: false, empty: true },
          4:{ full: false, half_empty: false, empty: true }
        },max:{
          1:{ full: true, half_empty: false, empty: false },
          2:{ full: true, half_empty: false, empty: false },
          3:{ full: true, half_empty: false, empty: false },
          4:{ full: true, half_empty: false, empty: false }
        },
      },
      sex:'',
    } 
  },
  computed: {
    computed_suggest_score_ints: function () {
      var suggest_scores_int={}
      var score_names = ['original','populair','classic','vintage','trending']
      for (var i = 0; i < score_names.length; i++) {
        x = score_names[i]
        suggest_scores_int[x]={}
        suggest_scores_int[x]['min']=0
        suggest_scores_int[x]['max']=0
        for(var j = 1; j < 5; j++){
          suggest_scores_int[x]['min'] += this['suggest'][x]['min'][j]['full']*1+
                                this['suggest'][x]['min'][j]['half_empty']*0.5 
          suggest_scores_int[x]['max'] += this['suggest'][x]['max'][j]['full']*1+
                                this['suggest'][x]['max'][j]['half_empty']*0.5 
        }
      }
      return suggest_scores_int
    }
  },
  methods: {
    create_login:function(){
      console.log(this.user_create_login['email'])
      console.log(this.user_create_login['password'])
      console.log(this.user_create_login['repeat_password'])
      if(!validateEmail(this.user_create_login['email'])){
        console.log('Not a valid email address')
        return null
      }
      if(this.user_create_login['password'] != this.user_create_login['repeat_password'] ){
        console.log('Passwords do not match')
        return null
      }
    },
    login:function(){
      if(!validateEmail(this.user_login['email'])){
        console.log('Not a valid email address')
        return null
      }
    },
    suggestion_change_sex:function(){
      if(this.suggestion_sex['male_selected']){
        this.suggestion_sex['male_selected'] = false
        this.suggestion_sex['female_selected'] = true
        this.suggestion_sex['icon'] = "<i class='fa fa-venus' aria-hidden='true'>"
      }else{
        this.suggestion_sex['male_selected'] = true
        this.suggestion_sex['female_selected'] = false        
        this.suggestion_sex['icon'] = "<i class='fa fa-mars' aria-hidden='true'>"
      }
      stringer_initialize();
    },
    liked_names_change_sex:function(){
      if(this.selection_liked_names['male_selected']){
        this.selection_liked_names['male_selected']=false
        this.selection_liked_names['female_selected']=true
        this.selection_liked_names['icon'] = "<i class='fa fa-venus' aria-hidden='true'>"
      }else{
        this.selection_liked_names['male_selected']=true
        this.selection_liked_names['female_selected']=false
        this.selection_liked_names['icon'] = "<i class='fa fa-mars' aria-hidden='true'>"
      }
      this.display_liked_names()
    },
    lookup_prim_change_sex: function(){
      if(this.lookup_sex_selection['prim_name']['male_selected']){
        this.lookup_sex_selection['prim_name']['male_selected'] = false
        this.lookup_sex_selection['prim_name']['female_selected'] = true
        this.lookup_sex_selection['prim_name']['icon'] = "<i class='fa fa-venus' aria-hidden='true'>"
      }else{
        this.lookup_sex_selection['prim_name']['male_selected'] = true
        this.lookup_sex_selection['prim_name']['female_selected'] = false        
        this.lookup_sex_selection['prim_name']['icon'] = "<i class='fa fa-mars' aria-hidden='true'>"
      }
    },
    lookup_ref_change_sex: function(){
      if(this.lookup_sex_selection['ref_name']['male_selected']){
        this.lookup_sex_selection['ref_name']['male_selected'] = false
        this.lookup_sex_selection['ref_name']['female_selected'] = true
        this.lookup_sex_selection['ref_name']['icon'] = "<i class='fa fa-venus' aria-hidden='true'>"
      }else{
        this.lookup_sex_selection['ref_name']['male_selected'] = true
        this.lookup_sex_selection['ref_name']['female_selected'] = false 
        this.lookup_sex_selection['ref_name']['icon'] = "<i class='fa fa-mars' aria-hidden='true'>"       
      }
    },
    activate_page: function(which_one){
      console.log(which_one)
      this.stats_div = true
      for(page in this.active_page){
        if(page==which_one) this.active_page[page]=false 
        else this.active_page[page]=true 
      }
      //if(which_one=='suggest') this.get_suggestion()
      if(which_one=='suggest') stringer_initialize()
      if(which_one=='list') this.request_liked_names()
      // Anoying method to close the navbar
      $('.navbar-collapse.collapse').collapse('hide')
    },
    set_stars : function (event) {
      // Out of the identifier in the html code we can get which star to set
      star_array_clicked = event['path'][0]['id'].split('_')
      star_clicked = parseInt(star_array_clicked[star_array_clicked.length-1])
      // Set the stars prior to the one clicked active
      for(i=0;i<star_clicked; i++){
        this[star_array_clicked[0]][star_array_clicked[1]][star_array_clicked[2]][i+1]['full']=true
        this[star_array_clicked[0]][star_array_clicked[1]][star_array_clicked[2]][i+1]['empty']=false
      }
      // Set the ones behind the one clicked unactive
      for(i=star_clicked;i<4; i++){
        this[star_array_clicked[0]][star_array_clicked[1]][star_array_clicked[2]][i+1]['full']=false
        this[star_array_clicked[0]][star_array_clicked[1]][star_array_clicked[2]][i+1]['empty']=true
      }
    },
    get_suggestion:function(feedback){
      var pass_this = this
      this.spinning_wheel_suggestions = false
      $.get(
        url='/get_suggestion',
        data={
          'user_ID':user_ID,
          'session_ID':session_ID,
          'suggestion_scores':JSON.stringify(pass_this.computed_suggest_score_ints),
          'requested_sex':pass_this.suggestion_request_sex,
          'previous_suggestion':pass_this.returned_suggestion['name'],
          'previous_suggestion_sex':pass_this.returned_suggestion['sex'],
          'feedback':feedback ? feedback : 'suggestion_initialisation',
          'how_many':10
          //'names_alread_on_frontend':
        },
        callback=function(return_data){
          console.log('Hier')
          console.log(return_data)
          pass_this.returned_suggestion['name'] = return_data['name']
          pass_this.returned_suggestion['sex'] = return_data['sex']
          pass_this.spinning_wheel_suggestions = true
        }
      )
    },
    delete_listed_name:function(name_to_delete, rank){
      this.global_spinning_wheel=false      
      pass_this = this
      sex = this.selection_liked_names['male_selected'] ? 'M' : 'F'
      $.get(
          url='/delete_name',
          data={
            'user_ID':user_ID,
            'name':name_to_delete,
            'sex':sex,
            'rank':rank
          },
          callback=function(return_data){
            pass_this.global_spinning_wheel=true
            pass_this.liked_names = return_data['liked_names']
            pass_this.display_liked_names()
          }
      )
    },
    move_rank_up:function(name_to_change_rank){
      // First get the name object of the name clicked
      pass_this = this
      name_to_change_rank = this.liked_names_displayed.filter(function(liked_name){
        if(pass_this.selection_liked_names['male_selected']){
          return (liked_name['sex'] == 'M') & (liked_name['name'] == name_to_change_rank)
        }else{
          return (liked_name['sex'] == 'F')  & (liked_name['name'] == name_to_change_rank)
        } 
      })
      name_to_change_rank = name_to_change_rank[0]
      // Now get the names above it
      names_above_in_rank = this.liked_names_displayed.filter(function(liked_name){
        if(pass_this.selection_liked_names['male_selected']){
          return (liked_name['sex'] == 'M') & (liked_name['rank'] > name_to_change_rank['rank'])
        }else{
          return (liked_name['sex'] == 'F')  & (liked_name['rank'] > name_to_change_rank['rank'])
        } 
      })
      if(names_above_in_rank.length ==0 ) return null
      // Get the first name above it
      closest_rank = names_above_in_rank.sort(function(a, b){return a['rank'] - b['rank']});
      closest_rank = closest_rank[0]['rank']
      name_to_swap = this.liked_names_displayed.filter(function(liked_name){
        if(pass_this.selection_liked_names['male_selected']){
          return (liked_name['sex'] == 'M') & (liked_name['rank'] == closest_rank)
        }else{
          return (liked_name['sex'] == 'F')  & (liked_name['rank'] == closest_rank)
        } 
      })
      name_to_swap = name_to_swap[0]
      // Send to backend
      pass_this = this
      this.global_spinning_wheel=false
      $.get(
          url='/swap_ranks',
          data={
            'user_ID':user_ID,
            'name_one': name_to_change_rank['name'],
            'name_two': name_to_swap['name'],
            'new_rank_name_one' : name_to_swap['rank'],
            'new_rank_name_two' : name_to_change_rank['rank'],
            'sex': pass_this.selection_liked_names['male_selected'] ? 'M' : 'F'
          },
          callback=function(return_data){
            pass_this.liked_names = return_data['liked_names']
            pass_this.global_spinning_wheel=true
            pass_this.display_liked_names()
      })
    },
    add_name:function(event){
      pass_this = this
      this.global_spinning_wheel=false
      $.get(
          url='/add_name',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'name': pass_this.name_to_add,
            'sex': pass_this.selection_liked_names['male_selected'] ? 'M' : 'F'
          },
          callback=function(return_data){
            pass_this.name_to_add = ''
            pass_this.liked_names = return_data['liked_names']
            pass_this.global_spinning_wheel=true
            pass_this.display_liked_names()
      })
      
    },
    display_liked_names:function(){
      //filter displayed names based on the button
      pass_this = this
      this.liked_names_displayed = this.liked_names.filter(function(liked_name){
        if(pass_this.selection_liked_names['male_selected']){
          return liked_name['sex'] == 'M'  
        }else{
          return liked_name['sex'] == 'F'  
        }  
      })
      // sort based on the rank. Hoe hoger de rank, hoe hoger op de pagina
      this.liked_names_displayed = this.liked_names_displayed.sort(function(a,b){
        return b['rank'] - a['rank']
      })

    },
    request_liked_names:function(){
        var pass_this = this
        this.global_spinning_wheel=false
        $.get(
          url='/request_liked_names',
          data={
            'user_ID':user_ID
          },
          callback=function(return_data){
            pass_this.global_spinning_wheel=true
            pass_this.liked_names = return_data['liked_names']            
            pass_this.display_liked_names()
          })
    },      
    submit_names: function () {
		  var pass_this = this
      this.global_spinning_wheel=false
      	$.get(
      		url='/get_stats',
      		data={
      			'name_1':this.name_1,
            'name_2':this.name_2,
            'sex_name_1':(this.lookup_sex_selection['prim_name']['male_selected'] ? "M" : "F"),
            'sex_name_2':(this.lookup_sex_selection['ref_name']['male_selected'] ? "M" : "F"),
      			'region':this.region,
      			'user_ID':user_ID,
      			'session_ID':session_ID
      		},
      		callback=function(return_data){
            pass_this.stats_div = false
      			// Set stars
            score_names = ['score_classic','score_trend','score_vintage','score_original','score_popular']
            name_numbers = ['name_1','name_2']
      			for(i=0; i<score_names.length;i++ ){
      				score_name = score_names[i]
      				for(j=0; j<name_numbers.length; j++){
                name_number = name_numbers[j]
                for(k=0; k<4; k++ ){
		      				pass_this[score_name][name_number][k+1]['full'] = false
		      				pass_this[score_name][name_number][k+1]['half_empty'] = false
		      				pass_this[score_name][name_number][k+1]['empty'] = false
		      				if(k + 1 - return_data[score_name][name_number]<0.5){
		      					pass_this[score_name][name_number][k+1]['full'] = true
		      				}else if(k + 1 - return_data[score_name][name_number] < 1){
		      					pass_this[score_name][name_number][k+1]['half_empty'] = true
		      				}else{
		      					pass_this[score_name][name_number][k+1]['empty'] = true
		      				}
		      			}
		      		}
      			}
            pass_this.name_1_meaning = return_data['meanings']['name_1']
            pass_this.name_2_meaning = return_data['meanings']['name_2']
            pass_this.lookup_sex_selection.prim_name['female_selected'] = return_data['sexes']['name_1'] == 'F' ? true : false
            pass_this.lookup_sex_selection.prim_name['male_selected'] = return_data['sexes']['name_1'] == 'M' ? true : false
            pass_this.lookup_sex_selection.ref_name['female_selected'] = return_data['sexes']['name_2'] == 'F' ? true : false
            pass_this.lookup_sex_selection.ref_name['male_selected'] = return_data['sexes']['name_2'] == 'M' ? true : false
            pass_this.lookup_sex_selection['ref_name']['icon'] = return_data['sexes']['name_2'] == 'M' ? 
                           "<i class='fa fa-mars' aria-hidden='true'>" : "<i class='fa fa-venus' aria-hidden='true'>"
            pass_this.name_2 = return_data['names']['name_2']
            pass_this.global_spinning_wheel=true
            pass_this.name_1_gelijkaardig = return_data['names']['name_2']
      			// Draw time series
      			draw_timeseries(return_data['ts'],pass_this.name_1, pass_this.name_2 )
            // Increase the counter
            pass_this.counter_lookups  += 1;
            console.log(pass_this.counter_lookups)
            // Check flag
            if(pass_this.counter_lookups > 3) pass_this.more_than_5_lookups = true
        })
    },
    submit_names_landing_page:function(){
      this.activate_page('lookup')
      var pass_this = this
      this.global_spinning_wheel=false
        $.get(
          url='/get_stats',
          data={
            'name_1':this.name_1,
            'name_2':null,
            'sex_name_1':null,
            'sex_name_2':null,
            'region':this.region,
            'user_ID':user_ID,
            'session_ID':session_ID
          },
          callback=function(return_data){
            console.log(return_data)

            pass_this.stats_div = false
            // Set stars
            score_names = ['score_classic','score_trend','score_vintage','score_original','score_popular']
            name_numbers = ['name_1','name_2']
            for(i=0; i<score_names.length;i++ ){
              score_name = score_names[i]
              for(j=0; j<name_numbers.length; j++){
                name_number = name_numbers[j]
                for(k=0; k<4; k++ ){
                  pass_this[score_name][name_number][k+1]['full'] = false
                  pass_this[score_name][name_number][k+1]['half_empty'] = false
                  pass_this[score_name][name_number][k+1]['empty'] = false
                  if(k + 1 - return_data[score_name][name_number]<0.5){
                    pass_this[score_name][name_number][k+1]['full'] = true
                  }else if(k + 1 - return_data[score_name][name_number] < 1){
                    pass_this[score_name][name_number][k+1]['half_empty'] = true
                  }else{
                    pass_this[score_name][name_number][k+1]['empty'] = true
                  }
                }
              }
            }
            pass_this.name_1_meaning = return_data['meanings']['name_1']
            pass_this.name_2_meaning = return_data['meanings']['name_2']
            pass_this.name_1_gelijkaardig = return_data['names']['name_2']
            pass_this.lookup_sex_selection.prim_name['female_selected'] = return_data['sexes']['name_1'] == 'F' ? true : false
            pass_this.lookup_sex_selection.prim_name['male_selected'] = return_data['sexes']['name_1'] == 'M' ? true : false
            pass_this.lookup_sex_selection.ref_name['female_selected'] = return_data['sexes']['name_2'] == 'F' ? true : false
            pass_this.lookup_sex_selection.ref_name['male_selected'] = return_data['sexes']['name_2'] == 'M' ? true : false
            pass_this.lookup_sex_selection['prim_name']['icon'] = return_data['sexes']['name_1'] == 'M' ? 
                           "<i class='fa fa-mars' aria-hidden='true'>" : "<i class='fa fa-venus' aria-hidden='true'>"
            pass_this.name_2 = return_data['names']['name_2']
            pass_this.global_spinning_wheel=true
            
            // Draw time series
            draw_timeseries(return_data['ts'],pass_this.name_1, pass_this.name_2 )

            // Increase the counter
            pass_this.counter_lookups  += 1;
            console.log(pass_this.counter_lookups)
        })
    },
  }
})
function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}


