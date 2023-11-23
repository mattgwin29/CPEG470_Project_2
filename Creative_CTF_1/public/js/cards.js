let options = ["test1", "test2", "test3", "test4"];

function create_cards(c,  name, date, img){
    return `<div class="` + c + `">
                <div class="card_image"> <img src="assets/comp.avif" /> </div>
                <div class="card_title title-white">
                <p>` + name+ `</p>
                </div>
                <div class="title-black">
                <p>` + date + `</p>
                </div>
            </div>`;
}

var tourney_data = {};

function get_current_events(uid){

    console.log("UID -> " + uid);
    url = "https://mattgwin-web-ctf-default-rtdb.firebaseio.com/Users/"  + uid + "/.json";
    console.log("Querying " + url);

    $.ajax({
        async: false,
        method: "GET",
        url: "https://mattgwin-web-ctf-default-rtdb.firebaseio.com/Users/"  + uid + "/.json",
        contentType: "application/json",
        success: (data) => {load_cards_from_tourney(data)}
    })
}



function load_current_events(){

    firebase.database().ref("/").on("value", ss=>{
        document.querySelector(".cards-list").innerHTML = ss;
      });
}

function load_cards_from_tourney(data){
    var keys = Object.keys(data.tournaments);
    for (var i = 0; i < keys.length; i++){
        let current_k = keys[i];
        let current_tourney = JSON.parse(data.tournaments[current_k]);
        $(".cards-list").append(create_cards("card " + current_k, current_tourney.name, current_tourney.date, null))
    }
    
}


