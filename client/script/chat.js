function display_message(data) {
    switch (data.type) {
        case 'message':
            m_message();
            break;
        case 'info':
            m_info();
            break;
        case 'alert':
            m_alert();
            break;
    }

    function m_message() {
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

    function m_info() {
        var msgbox = document.createElement('div');
        msgbox.classList.add('info');

        var msg = document.createElement('div');
        msg.classList.add('msg');
        msg.innerText = data.msg;
        msgbox.appendChild(msg);

        $('#chat').appendChild(msgbox);
    }

    function m_alert() {
        var msgbox = document.createElement('div');
        msgbox.classList.add('info', 'alert');

        var msg = document.createElement('div');
        msg.classList.add('msg');
        msg.innerText = data.msg;
        msgbox.appendChild(msg);

        $('#chat').appendChild(msgbox);
    }
}

window.onload = function () {
    window.ws = new WebSocket('ws://localhost:12345');
    window.bkws = {};   // backup websocket functions

    ws.onopen = function () {
        display_message({ type: 'info', msg: 'Connected' });
        auto_auth();
    };

    bkws.onmessage = ws.onmessage = function (event) {
        data = JSON.parse(event.data);
        display_message(data);
    };

    ws.onclose = function () {
        display_message({ type: 'alert', msg: '⚠ Disconnected' });
    };

    ws.wait1 = async function (func) {
        // wait for message 1 times
        return new Promise(function (resolve, reject) {
            ws.onmessage = function (event) {
                func(event);
                ws.onmessage = bkws.onmessage;
                resolve();
            }
        });
    };

    $('#send').onclick = function () {
        var message = $('#input').value;
        var data = {
            type: 'message',
            from: ME.username,
            msg: message
        };
        ws.send(JSON.stringify(data));
        display_message(data);
        $('#input').value = '';
    };

    $('#login_btn').onclick = async function () {
        var uname = $('#username').value;
        var pwd = $('#password').value;
        await auth_pwd(uname, pwd);
    };
};

/* === Tool Functions === */

async function sha256(message) {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const hash = await window.crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function set_cookie(name, value, expiry) {
    var d = new Date();
    d.setTime(d.getTime() + expiry);
    var expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";";
}

function get_cookie(name) {
    var cname = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(cname) == 0) {
            return c.substring(cname.length, c.length);
        }
    }
    return "";
}

/* === Auth === */

async function auto_auth() {
    // Step 1: Try cookie
    var token = get_cookie('otchat-login-token');
    if (token) {
        var result = await auth_token(token);
        if (result.code == 0) {
            auth_success(result);
            return;
        }
    }

    // Step Final: Failed
    $('#login').style.display = 'block';
    $('#ui').style.display = 'none';
}

async function auth_token(token) {
    var salt = Math.random().toString();
    var token_1 = token.substring(0, 64);
    var token_2 = token.substring(64);
    var token = token_1 + await sha256(token_2 + salt);

    var data = {
        type: 'auth',
        authmethod: 'token',
        token: token,
        salt: salt
    }
    ws.send(JSON.stringify(data));

    var auth_result = { code: -1 };   // default: waiting

    await ws.wait1(function (e) {
        var data = JSON.parse(e.data);

        if (data.type == 'auth') {
            auth_result = data;
        }
    })

    return auth_result;
}

async function auth_pwd(uname, pwd) {
    var salt = Math.random().toString();
    var pwd = await sha256(await sha256(pwd) + salt);

    var data = {
        type: 'auth',
        authmethod: 'password',
        username: uname,
        password: pwd,
        salt: salt,
        AuthNeedToken: true
    };
    ws.send(JSON.stringify(data));

    ws.wait1(function (e) {
        var data = JSON.parse(e.data);

        if (data.type == 'auth') {
            console.log(data)
            if (data.code == 0) {
                auth_success(data);
                set_cookie('otchat-login-token', data.token, 3600 * 24 * 30);
            } else {
                display_message({ type: 'info', msg: 'Authentication failed' });
            }
        }
    })
}

function auth_success(data) {
    display_message({ type: 'info', msg: `Logged in as '${data.id}'` });
    ME.username = data.id;
    ME.avatar = data.avatar;
    $('#login').style.display = 'none';
    $('#ui').style.display = 'block';
}
