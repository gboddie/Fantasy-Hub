$(document).ready(function(){
  data = $(".nav2").data();
  fill_page(data.url);
});

function fill_page(name) {
  $(".nav-bottom").each(function(){
    if (name == this.dataset.name){
      $(this).css("background-color", "grey");
    }
    else {
      $(this).css("background-color", "");
    }
  });


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

  $("button").click(function(event){
    event.preventDefault();
    var leagueid = this.dataset.leagueid;
    var user = document.getElementById('user');
    var userid = user.dataset.id;
    var user_name = $(user).html();
    var contest = this.dataset.contest;
    var level = this.dataset.level;
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
        if (name == 'Daily'){
          $(`#${leagueid}`).html(data.filled);
        }
        else {
          $(`#${leagueid}`).html(`${data.filled}/${data.teams}`);
        }
      },
      error: function() {
        alert('there was an error');
      }
    });
  });
}
