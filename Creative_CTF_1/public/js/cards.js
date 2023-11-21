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

function get_current_events(){
    $.ajax({
        async: false,
        method: "GET",
        url: "https://mattgwin-tournament-builder-default-rtdb.firebaseio.com/.json",
        contentType: "application/json",
        success: (data) => {tourney_data = {...data}}
    })
}



function load_current_events(){

    firebase.database().ref("/").on("value", ss=>{
        //console.log(ss);
        document.querySelector(".cards-list").innerHTML = ss;
      });
}

get_current_events();

console.log("Deez Nuts");
console.log(tourney_data.tournaments);


function load_cards_from_tourney(data){
    var keys = Object.keys(data.tournaments);

    for (var i = 0; i < keys.length; i++){
        let current_k = keys[i];
        let current_tourney = JSON.parse(data.tournaments[current_k]);
        console.log("*******");
        console.log(current_tourney.name);
        console.log(current_tourney.date);
        $(".cards-list").append(create_cards("card " + current_k, current_tourney.name, current_tourney.date, null))
        console.log(current_tourney);
    }
    /*.forEach(element => {
        console.log(element);
    });*/

}

load_cards_from_tourney(tourney_data);


//load_current_events();

/*for (var i = 0; i < 5; i++){
    $(".cards-list").append(create_cards("card " + i, "deez nuts", null, null));
}*/