function display_message(data) {
    console.log(data);

    var msgbox = document.createElement('div');
    msgbox.classList.add('message');

    // sender info
    {
        var sender = document.createElement('div');
        sender.classList.add('sender');

        var avatar = document.createElement('img');
        avatar.src = data.avatar; // Assuming data.avatar contains the URL of the avatar
        sender.appendChild(avatar);

        var name = document.createElement('span');
        name.innerText = data.from;
        sender.appendChild(name);

        msgbox.appendChild(sender);
    }

    // message
    {
        var msg = document.createElement('div');
        msg.classList.add('msg');
        msg.innerText = data.msg;
        msgbox.appendChild(msg);
    }

    $('#chat').appendChild(msgbox);
}

window.onload = function () {
    var ws = new WebSocket('ws://localhost:12345');

    ws.onopen = function () {
        display_message({ from: '[INFO]', msg: 'Connected to server' });
    };

    ws.onmessage = function (event) {
        data = JSON.parse(event.data);
        display_message(data);
    };

    ws.onclose = function () {
        display_message({ from: '[INFO]', msg: 'Disconnected from the server' });
    };

    $('#send').onclick = function () {
        var message = $('#input').value;
        ws.send(message);
        display_message({ from: 'Bernie Huang', msg: message });
        $('#input').value = '';
    };
};
