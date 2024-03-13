function changeLoginButtonText(buttons) {
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].innerText === 'Continue with Azure-ad-b2c') {
            buttons[i].innerHTML = '<img class="MuiButton-startIcon MuiButton-iconSizeMedium css-6xugel MuiSvgIcon-root login-logo" ' +
                'src="../public/b2c_logo.png" ' +
                'alt="Log in on Client SSO" ' +
                'role="presentation" >' +
                'Login with Client Portal';
            }
    }
}

function mutationObserverCallback(mutationsList, observer) {
    var buttons = document.querySelectorAll('button');
    if (buttons.length === 1) {
        changeLoginButtonText(buttons);
        observer.disconnect();
    }
}

if (window.location.href.includes('login')) {
    const observer = new MutationObserver(mutationObserverCallback);
    const config = { childList: true, subtree: true };
    observer.observe(document.body, config);
}