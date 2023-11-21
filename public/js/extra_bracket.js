//https://codepen.io/meriawep/pen/ExaqNvd

var dataTemplate = {teams: [], results: [[]], name: "", date: "", notes: ""}

  function openCreateEventMenu(){
    console.log("Got in here");
    $("#event_creator").html(`
    <div class="w3-container" id="where" style="padding-bottom:32px;">
      <div class="w3-content" style="max-width:700px">
        <h5 class="w3-center w3-padding-48"><span class="w3-tag w3-wide">Create an event</span></h5>
        <form action="/" target="_blank">
          <p><input class="w3-input w3-padding-16 w3-border" id="tournament_name" type="text" placeholder="Name" required name="Name"></p>
          <p><input class="w3-input w3-padding-16 w3-border" id="tourney_people_count" type="number" placeholder="How many people" required name="People"></p>
          <p><input class="w3-input w3-padding-16 w3-border" id="tournament_date" type="datetime-local" placeholder="Date and time" required name="date" ></p>
          <p><input class="w3-input w3-padding-16 w3-border" id="tournament_notes" type="text" placeholder="Message \ Special requirements" required name="Message"></p>
        </form>
      </div>
      <p><button class="w3-button w3-black" onclick="createInputForNames();">Next</button></p>
    </div>`);
    $("#current_events").hide()
    
    }

    function createInputForNames(){
        let amount = $('#tourney_people_count').val();
        if ((amount/2) % 2 !=0) {
          alert("The amount of people must be a power of 2.");
          return;
        }
        console.log("Creating " + amount + " input boxes"); //<label class="inline-label">Name</label><label class="inline-label">Seed</label>
        document.getElementById('bracket_creator').innerHTML += (`<div id="names_list"></div>`);
    
        let htmlstring = ``;
        htmlstring+=`<h5 class="w3-center w3-padding-48"><span class="w3-tag w3-wide">Name and Seed</span></h5>`;
        for (var i = 0; i < amount; i++){
            htmlstring += `<div><p class="w3-center"><input type="text" placeholder="Name" id="Name_` + i + `"><input type="number" placeholder="seed"  id="Seed_` + i + `"></p>
          `;
          //htmlstring += `<div><p class="w3-center"><input type="text" placeholder="Name" id="Name_` + i + `"><input type="email" placeholder="Email"  id="Email_` + i + `"></p>
          }
          $("#Seed_" + i).val(i);
          htmlstring += `<div class="w3-center"><button class="w3-button w3-black" onclick="loadBracket(false)">Generate Perfect Bracket</button>
          <button class="w3-button w3-black" onclick="loadBracket(true)">Generate Random Bracket</button>
          <button class="w3-button w3-black" onclick="clearBracket()">Clear Current</button></div> `;
          

        document.getElementById('names_list').innerHTML = htmlstring;
    
        for (var j = 0; j < amount; j++){
          $("#Name_" + j).val("Person " + (j+1));
    
          $("#Seed_" + j).val((j+1));
        }
        window.location.href = '#names_list';
      }

    
function loadBracket(random){
    clearBracket();
    let amount = $('#tourney_people_count').val();
    console.log("Got in here?");
    $("#bracket_holder").html(`<span id="matchCallback"></span>
    <div id="matches">
      <div class="demo">
      </div>
    </div>
    `);

    data = {...dataTemplate};
    if (random){
        setResults(data, amount, true);
    }
    else{
        setResults(data, amount, false);
    }
    setResults(data, amount);
    data.results[0] = [...data.results[0], [1,0]];

    var count = 0;
    for (var j = 0; j < amount/2; j++){
        var teamX = []
        for (var k = 0; k < 2; k++){
            if (k==0){
                teamX = [...teamX ,($("#Name_" + (count)).val())];
            }
            else { //k=1
                teamX = [...teamX ,($("#Name_" + (amount - count)).val())];
            }
            count++;
        }
        data.teams = [...data.teams, teamX];
        data.name = $("#tournament_name").val();
        data.date = moment(new Date($("#tournament_date").val())).format('dddd MMMM D Y');
        data.notes = $("#tournament_notes").val();
        setBracketData(data);
    }
    //window.location.href= "#finalize_event";

    $("#finalize_event").html(`<div class="w3-center"><button class="w3-button w3-black" onclick="pushTournamentToFirebase(data)">Create Event</button></div>`);
  }

  function pushTournamentToFirebase(json_data){
    var data = JSON.stringify(json_data);
    console.log(data);
    firebase.database().ref("/tournaments").push(data);
    alert("Successfully Created Event!");
    //window.location.reload();
    //window.location.href = "/";

  }

  function setResults(data, amount, random){
    console.log("ARGH ME MATEY " + amount);
    if ( Number.isNaN(amount)) return;

    for (var k1 = 0; k1 < Math.ceil(getBaseLog(2, amount)); k1++){
        data.results = [...data.results, []];
        for (var i = 0; i < amount / 2; i++){
            if (random){
                var firstScore = Math.floor(Math.random() * 10);
                var secondScore = Math.floor(Math.random() * 10);
                if (firstScore === secondScore){
                    console.log("Uh oh, collision!");
                    while(firstScore === secondScore){
                        console.log("first score " + firstScore);
                        console.log("second score " + secondScore);
                        secondScore = Math.floor(Math.random() * 10);
                    }
                }
                data.results[k1] = [...data.results[k1], [firstScore, secondScore]];
            }
            else {
                data.results[k1] = [...data.results[k1], [10,0]];
            }
        }
    }
  }

  function clearBracket(){
    setBracketData(dataTemplate);
  }

  function setBracketData(data){
    $(function() {
        $('#matches .demo').bracket({
          init: data
          /*onMatchClick: onclick,
          onMatchHover: onhover*/
        })
      })
  }

  function getPeopleInTourney(){
    var items = [];
    //var item = document.getElementById("tourney_people_count");
    var amount = $("#tourney_people_count").val();

    var newArr =[[]];

    console.log("Running the loop until " + amount/2);
    var count = 0;
    if (amount > 50){
      alert("The maximum allowed number of people in a tournament is 50 ");
      return;
    }
    for (var i=1; i<(amount/2)+1; i++){
      for (var j = 0; j < 2; j++)
      {
        var current_name = $("#Name_" + count).val();
        console.log(current_name);
        count++;
      } 
    }
  }

  function createRounds(){
    let htmlstring = ``;
    let numRounds = $('#tourney_people_count').val();
    for (var i = 1; i <= getBaseLog(2, numRounds); i++){
        htmlstring += `<h5 class="w3-center w3-padding-48"><span class="w3-tag w3-wide">Round ` + i + ` </span></h5>`;
    }
    $("#round_holder").html(htmlstring);
}

  function getBaseLog(base, y) {
    return Math.log(y) / Math.log(base);
  }

  function onclick(data) {
    $('#matchCallback').text("onclick(data: '" + data + "')")
  }
   
  function onhover(data, hover) {
    $('#matchCallback').text("onhover(data: '" + data + "', hover: " + hover + ")")
  }
   
  