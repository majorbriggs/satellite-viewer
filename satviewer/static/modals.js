var modalInfo = document.getElementById('infoModal');
var btnInfo = document.getElementById("btn-ts-vi-info");


btnInfo.onclick = function (){
    modalInfo.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
$(document).on('click', '.close', function() {
    modalInfo.style.display = "none";
}
);

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modalInfo) {
        event.target.style.display = "none";
    }
}