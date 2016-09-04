function constructUrl(namespace, command) {
    return url_root + namespace + "/" + command;
}

function sendCommand(namespace, command, args) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE ) {
            if (xmlhttp.status == 200) {
                console.log("-> Done sending " + namespace + "/" + command + " " + args);
            }
        }
    };

    xmlhttp.open("POST", constructUrl(namespace, command), true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xmlhttp.send('args=' + encodeURIComponent(args));
}

var buttons = document.getElementsByTagName("button");

for(var i =0; i < buttons.length; i++){
    var elem = buttons[i];   
    elem.onclick = (function(){
        var namespace = elem.getAttribute('data-namespace');
        var command = elem.getAttribute('data-command');
        var args = elem.getAttribute('data-args');
        return function() { 
            sendCommand(namespace, command, args);
            return false;
        }
    })();
}

console.log("Done registering buttons");