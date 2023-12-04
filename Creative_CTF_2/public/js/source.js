function displaySource(){
    console.log("Function is called");
    remove();
    document.body.innerHTML = 'deez nuts';
}


function remove(){
    console.log("Removing fake iframe");
    var frame = document.getElementById("fakegoogle");
    if (!!frame) {
        frame.parentNode.removeChild(frame);
    }
   }

function isAuthorized(){
    localStorage.getItem("authorized")
}