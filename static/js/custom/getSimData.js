let altitude;
let fuel_percentage;
let vertical_speed;
let compass;
let airspeed;
let latitude;
let longitude;
let groundspeed;


window.setInterval(function(){
    getSimulatorData();
    displayData()
    updateMap()
}, 2000);


function getSimulatorData() {
    $.getJSON($SCRIPT_ROOT + '/ui', {}, function(data) {

        //Navigation
        altitude = data.ALTITUDE;
        vertical_speed = data.VERTICAL_SPEED;
        compass = data.MAGNETIC_COMPASS;
        airspeed = data.AIRSPEED_INDICATE;
        latitude = data.LATITUDE;
        longitude = data.LONGITUDE;
        groundspeed = data.GROUND_VELOCITY;

    });
    return false;
}


function displayData() {
    //Navigation
    $("#altitude").text(altitude);
    $("#compass").text(compass);
    $("#vertical-speed").text(vertical_speed);
    $("#airspeed").text(airspeed);
    $("#GroundSpeed").text(groundspeed);

}


function updateMap() {
    var pos = L.latLng(latitude, longitude);

    marker.slideTo(	pos, {
        duration: 1500,
    });
    marker.setRotationAngle(compass);

    if (followPlane === true) {
        map.panTo(pos);
    }
}

function setSimDatapoint(datapointToSet, valueToUse) {
    url_to_call = "/datapoint/"+datapointToSet+"/set";
    $.post( url_to_call, { value_to_use: valueToUse } );
}



function triggerSimEventFromField(eventToTrigger, fieldToUse, messageToDisplay = null){
    // Get the field and the value in there
    fieldToUse = "#" + fieldToUse
    valueToUse = $(fieldToUse).val();

    // Pass it to the API
    url_to_call = "/event/"+eventToTrigger+"/trigger";
    $.post( url_to_call, { value_to_use: valueToUse } );

    // Clear the field so it can be repopulated with the placeholder
    $(fieldToUse).val("")

    if (messageToDisplay) {
        temporaryAlert('', messageToDisplay + " to " + valueToUse, "success")
    }

}


function temporaryAlert(title, message, icon) {
    let timerInterval

    Swal.fire({
        title: title,
        html: message,
        icon: icon,
        timer: 2000,
        timerProgressBar: true,
        onBeforeOpen: () => {
            Swal.showLoading()
            timerInterval = setInterval(() => {
                const content = Swal.getContent()
                if (content) {
                    const b = content.querySelector('b')
                    if (b) {
                        b.textContent = Swal.getTimerLeft()
                    }
                }
            }, 100)
        },
        onClose: () => {
            clearInterval(timerInterval)
        }
    }).then((result) => {
        /* Read more about handling dismissals below */
        if (result.dismiss === Swal.DismissReason.timer) {
            console.log('I was closed by the timer')
        }
    })
}