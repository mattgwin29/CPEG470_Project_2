
let renderLogin = ()=>{
   $("#loginInfo").html(`
<button id="login_button">Login</button>
                  `);
   $("#login_button").on("click", ()=>{
     firebase.auth().signInWithRedirect(google_provider);
   })
}

let globalUser = null;

let startApp = (user)=>{
   $("#loginInfo").html(`<button id="logout">Log out here</button>`);
   $("#loginInfo").css({ 'color': 'white'});
   $("#logout").click(()=>{
     firebase.auth().signOut();
   })
}


  var google_provider = new firebase.auth.GoogleAuthProvider();
  firebase.auth().onAuthStateChanged(user => {
    if (!!user){
      startApp(user);
    } else {
      renderLogin();
    }
    globalUser = user;
  });


  function renderProfile(){
    $('.profile-card').html(`
      <img style="padding-top:100px; padding-right:20px; padding-bottom:0px; padding-left:20px" src="${getProfilePhotoURL()}">
      `);
      console.log(globalUser);
      $("#tourney_title").html(`<span class="w3-text-white" style="font-size:90px">Hello<br>` + globalUser.displayName + `</span>`);
      $("#current_events").html(`<span class="w3-center" style="font-size:50px">My Events</span>`);
    }
    
  function getProfilePhotoURL(){
    console.log(globalUser.photoURL);
    return globalUser.photoURL;
  }
  