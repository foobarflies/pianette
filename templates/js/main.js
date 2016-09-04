function constructUrl(namespace, command) {
    return url_root + namespace + "/" + command;
}

function sendCommand(namespace, command, args, needs_reload) {
    callAPI(constructUrl(namespace, command), args, needs_reload);
}

function sendRawSequence(sequence, needs_reload) {
    callAPI(url_root, sequence, needs_reload);
}

function callAPI(url, data, needs_reload) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE ) {
            if (xmlhttp.status == 200) {
                if (needs_reload) {
                    document.location.reload(true);
                }
                console.log("-> Done sending " + url + " " + data);
            }
        }
    };

    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xmlhttp.send('data=' + encodeURIComponent(data));
}

var buttons = document.getElementsByTagName("button");

for(var i =0; i < buttons.length; i++){
    var elem = buttons[i];   
    elem.onclick = (function(){
        if (external_id = elem.getAttribute('data-external-sequence')) {
            var external_value_container = document.getElementById(external_id);
            var needs_reload = (elem.getAttribute('data-needs-reload') == 'true');
            return function() { 
                sendRawSequence(external_value_container.value, needs_reload);
                return false;
            }
        } else {
            var namespace = elem.getAttribute('data-namespace');
            var command = elem.getAttribute('data-command');
            var args = elem.getAttribute('data-args');
            var needs_reload = (elem.getAttribute('data-needs-reload') == 'true');
            return function() { 
                sendCommand(namespace, command, args, needs_reload);
                return false;
            }
        }
        
    })();
}

console.log("Done registering buttons");