$(document).ready(function(){
  //get name of the requested data
  data = $(".nav2").data();
  //fill page based on requested data
  fill_page(data.url);
});

function fill_page(name) {
  //give selected page grey background displace all other
  $(".nav-bottom").each(function(){
    if (name == this.dataset.name){
      $(this).css("background-color", "grey");
    }
    else {
      $(this).css("background-color", "");
    }
  });

  //fill page with text variable from index.html equal to requested data
  switch (name) {
    case 'Daily':
    document.querySelector(".main-body").innerHTML = daily_page;
        break;
    case 'Redraft':
        document.querySelector(".main-body").innerHTML = redraft_page;
        break;
    case 'Dynasty':
        document.querySelector(".main-body").innerHTML = dynasty_page;
        break;
    case 'Best_Ball':
        document.querySelector(".main-body").innerHTML = bb_page;
        break;
  }
  //on button click run this function
  $("button").click(function(event){
    event.preventDefault();
    var leagueid = this.dataset.leagueid;
    var user = document.getElementById('user');
    var userid = user.dataset.id;
    var user_name = $(user).html();
    var contest = this.dataset.contest;
    var level = this.dataset.level;
    //send data on league and user to server
    $.ajax({
      url: "/new_league_user",
      dataType: 'json',
      type: 'GET',
      data: {
        'leagueId': leagueid,
        'userId': userid,
        'username': user_name,
        'contest': contest,
        'level': level
      },
      success: function(data){
        //update available leagues on page
        if (name == 'Daily'){
          $(`#${leagueid}`).html(data.filled);
        }
        else {
          $(`#${leagueid}`).html(`${data.filled}/${data.teams}`);
        }
      },
      error: function() {
        //alert if server could not process data
        alert('there was an error');
      }
    });
  });
}
