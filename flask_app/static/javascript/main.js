

var session_ID;
var user_ID;
var test_event
vm = new Vue({
  el: '#app',
  data: {
    active_page:{
      welcome:false,
      lookup:true,
      suggest:true,
      list:true,
      about:true,
    },
    global_spinning_wheel:true,
    stats_div:true,
  	name_1: '',
  	name_2: '',
    name_1_meaning:'',
    name_2_meaning:'',
  	suggestion_request_sex:'',
  	region:'',
    returned_suggestion:{
      'name':'',
      'sex':''
    },
    suggestion_sex:{
      male_selected:false,
      female_selected:true
    },
    lookup_sex_selection:{
      prim_name:{
        male_selected:false,
        female_selected:true
      },
      ref_name:{
        male_selected:false,
        female_selected:true
      },
    },
    name_to_add:'',
    name_to_add_sex:'',
    liked_names:[],
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
    suggestion_change_sex_to:function(change_to){
      this.suggestion_request_sex = change_to
      if(change_to =='M'){
        this.suggestion_sex['male_selected']=true
        this.suggestion_sex['female_selected']=false
      }else{
        this.suggestion_sex['male_selected']=false
        this.suggestion_sex['female_selected']=true
      }
      stringer_initialize()
    },
    lookup_prim_change_sex_to: function(change_to){
      if(change_to == 'M'){
          this.lookup_sex_selection['prim_name']['male_selected']=true
          this.lookup_sex_selection['prim_name']['female_selected']=false
      }else if(change_to == 'F') {
          this.lookup_sex_selection['prim_name']['male_selected']=false
          this.lookup_sex_selection['prim_name']['female_selected']=true
      }
    },
    lookup_ref_change_sex_to: function(change_to){
      if(change_to == 'M'){          
          this.lookup_sex_selection['ref_name']['male_selected']=true
          this.lookup_sex_selection['ref_name']['female_selected']=false
      }else if(change_to == 'F') {
          this.lookup_sex_selection['ref_name']['male_selected']=false
          this.lookup_sex_selection['ref_name']['female_selected']=true
      }
    },
    activate_page: function(which_one){
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
      if(feedback){
        $.get(
          url='/get_suggestion',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'suggestion_scores':JSON.stringify(pass_this.computed_suggest_score_ints),
            'requested_sex':pass_this.suggestion_request_sex,
            'previous_suggestion':pass_this.returned_suggestion['name'],
            'previous_suggestion_sex':pass_this.returned_suggestion['sex'],
            'feedback':feedback,
            'how_many':5
          },
          callback=function(return_data){
            pass_this.returned_suggestion['name'] = return_data['name']
            pass_this.returned_suggestion['sex'] = return_data['sex']
            pass_this.spinning_wheel_suggestions = true
          }
        )
      }else{
        $.get(
          url='/get_suggestion',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'suggestion_scores':JSON.stringify(pass_this.computed_suggest_score_ints),
            'requested_sex':'suggestion_initialisation',
            'previous_suggestion':'suggestion_initialisation',
            'previous_suggestion_sex':'suggestion_initialisation',
            'feedback':'suggestion_initialisation'
          },
          callback=function(return_data){
            pass_this.returned_suggestion['name'] = return_data['name']
            pass_this.returned_suggestion['sex'] = return_data['sex']
            pass_this.spinning_wheel_suggestions = true
          }
        )
      }
    },
    delete_listed_name:function(event){
      pass_this = this
      name_to_delete = event['path'][1]['innerText']
      $.get(
          url='/delete_name',
          data={
            'user_ID':user_ID,
            'name':name_to_delete
          },
          callback=function(return_data){
            pass_this.liked_names = return_data['liked_names']
          }
      )
    },
    add_name:function(event){
      console.log(this.name_to_add)
      pass_this = this
      $.get(
          url='/add_name',
          data={
            'user_ID':user_ID,
            'session_ID':session_ID,
            'name': pass_this.name_to_add,
            'sex':pass_this.name_to_add_sex
          },
          callback=function(return_data){
            console.log(return_data)
            pass_this.name_to_add = ''
            pass_this.liked_names = return_data['liked_names']
      })
      
    },
    request_liked_names:function(){
        var pass_this = this
        $.get(
          url='/request_liked_names',
          data={
            'user_ID':user_ID
          },
          callback=function(return_data){
            pass_this.liked_names = return_data['liked_names']
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
              console.log(score_name)
              console.log(return_data[score_name])
      				for(j=0; j<name_numbers.length; j++){
                name_number = name_numbers[j]
                console.log(name_number)
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
            console.log(return_data)
            console.log(return_data['meanings']['name_1'])
            pass_this.name_1_meaning = return_data['meanings']['name_1']
            pass_this.name_2_meaning = return_data['meanings']['name_2']
            pass_this.global_spinning_wheel=true
      			// Draw time series
      			draw_timeseries(return_data['ts'],pass_this.name_1, pass_this.name_2 )
      	})
    }
  }
})


