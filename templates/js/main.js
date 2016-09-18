function constructUrls(player, namespace, command) {
    // Compute path
    if (namespace && command) {
        path = namespace + "/" + command;
    } else {
        path = "";
    }
    // Construct urls
    if (player === "*") {
        return  Object.keys(hosts).map(function(player) {
          return "//" + hosts[player] + ":" + port + "/" + path;
        });
    } else {
        return ["//" + hosts[player] + ":" + port + "/" + path];
    }
}

function sendCommand(player, namespace, command, args, needs_reload) {
    callAPI(constructUrls(player, namespace, command), args, needs_reload);
}

function sendRawSequence(player, sequence, needs_reload) {
    callAPI(constructUrls(player), sequence, needs_reload);
}

function doRequest(url, data, needs_reload) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, true);
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
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xmlhttp.send('data=' + encodeURIComponent(data));  
}

function callAPI(urls, data, needs_reload) {
    for (var i = 0; i < urls.length; i++) {
        doRequest(urls[i], data, needs_reload) 
    }
}

var buttons = document.getElementsByTagName("button");

for(var i =0; i < buttons.length; i++){
    var elem = buttons[i];   
    elem.onclick = (function(){

        var player = elem.getAttribute('data-player');
        var needs_reload = (elem.getAttribute('data-needs-reload') == 'true');

        if (external_id = elem.getAttribute('data-external-sequence')) {
            var external_value_container = document.getElementById(external_id);
            return function() { 
                sendRawSequence(player, external_value_container.value, needs_reload);
                return false;
            }
        } else {
            var namespace = elem.getAttribute('data-namespace');
            var command = elem.getAttribute('data-command');
            var args = elem.getAttribute('data-args');
            return function() { 
                sendCommand(player, namespace, command, args, needs_reload);
                return false;
            }
        }
        
    })();
}

console.log("Done registering buttons");