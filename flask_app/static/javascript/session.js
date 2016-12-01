
create_session_info()

function create_session_info(){
    // First check if user ID was created before, and is stored in a cookie
    user_ID_from_cookie = find_cookie('user_ID')
    if(user_ID_from_cookie != ''){
        set_user_ID(user_ID_from_cookie)
        window.console && console.log('User id already found, pick up session ID:')
        // User ID found in cookie, just create session ID in backend
        set_session_ID(get_session_ID(user_ID))
        return null
    }
    height = window.innerHeight || $(window).height();
    width = window.innerWidth || $(window).width();

    // No user ID found in cookie, get a new one, and store in coockie. Session ID is also created in backend
    $.get(
        url='/request_user_ID',
        data={
            'window_width': width,
            'window_height':height          
        },     
        callback=function(return_data){
            set_user_ID(return_data['user_ID'])
            set_session_ID(return_data['session_ID'])
            window.console && console.log('New user ID: ' + user_ID + ' Session ID: ' + session_ID) 
            //setCookie('user_ID', user_ID, 100)
    })
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}


function find_cookie(cname){
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            cookie_value = c.substring(name.length, c.length);
            window.console && console.log('Cookie ' + cname + ' found, value: ' + cookie_value)
            return cookie_value
        }
    }
    return ''
}

function get_session_ID(user_ID){
    height = window.innerHeight || $(window).height();
    width = window.innerWidth || $(window).width();
    // Request session ID from the back end
    $.get(
        url='/create_session_ID',
        data={
            'user_ID':user_ID,
            'window_width': width,
            'window_height':height
        },
        callback=function(return_data){
            window.console && console.log('New session ID: ' + return_data['session_ID']) 
            set_session_ID(return_data['session_ID'])
    })
}

function set_session_ID(session_ID){
    this.session_ID = session_ID
}
function set_user_ID(user_ID){
    this.user_ID = user_ID
}
