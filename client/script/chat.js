function display_message(data) {
    switch (data.type) {
        case 'message':
            message();
            break;
    }

    function message() {
        var msgbox = document.createElement('div');
        msgbox.classList.add('message');

        // sender info
        {
            var sender = document.createElement('div');
            sender.classList.add('sender');

            var avatar = document.createElement('img');
            avatar.src = data.avatar;
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
}

window.onload = function () {
    window.ws = new WebSocket('ws://localhost:12345');
    window.bkws = {};   // backup websocket functions

    ws.onopen = function () {
        display_message({ type: 'message', from: '[INFO]', msg: 'Connected to server' });
    };

    bkws.onmessage = ws.onmessage = function (event) {
        data = JSON.parse(event.data);
        display_message(data);
    };

    ws.onclose = function () {
        display_message({ type: 'message', from: '[INFO]', msg: 'Disconnected from the server' });
    };

    ws.wait1 = function (func) {
        // wait for message 1 times
        ws.onmessage = function (event) {
            func(event);
            ws.onmessage = bkws.onmessage;
        }
    };

    $('#send').onclick = function () {
        var message = $('#input').value;
        ws.send(message);
        display_message({ type: 'message', from: MY_INFO.username, msg: message });
        $('#input').value = '';
    };

    $('#login_btn').onclick = async function () {
        var uname = $('#username').value;
        var pwd = $('#password').value;
        await auth(uname, pwd);
    };
};

async function auth(uname, pwd) {
    async function hashPassword(pwd, salt) {
        const encoder = new TextEncoder();
        const data = encoder.encode(pwd + salt);
        const hash = await window.crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
    }

    salt = Math.random().toString();
    pwd = await hashPassword(pwd + salt);

    var data = {
        type: 'auth',
        authmethod: 'password',
        username: uname,
        password: pwd,
        salt: salt
    };
    ws.send(JSON.stringify(data));

    ws.wait1(function (e) {
        var data = JSON.parse(e.data);

        if (data.type == 'auth') {
            if (data.code == 0) {
                display_message({ type: 'message', from: '[INFO]', msg: 'Authentication success' });
                MY_INFO.username = uname;
                MY_INFO.avatar = data.avatar;
                $('#login').style.display = 'none';
                $('#chat').style.display = 'block';
            } else {
                display_message({ type: 'message', from: '[INFO]', msg: 'Authentication failed' });
            }
        }
    })
}
