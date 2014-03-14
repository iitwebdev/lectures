// Commentary main Javascript
if (typeof Commentary == 'undefined') {
    Commentary = {};
}

Commentary.selectComment = function () {
    document.onclick = Commentary.selectItem;
};

Commentary.selectItem = function (event) {
    event = event || window.event;
    var el = Commentary.findElement(event):
    while (! Commentary.isBlockElement(el)) {
        el = el.parentNode;
    }
    Commentary.showCommentForm(el);
};

Commentary.showCommentForm = function (el) {
    Commentary.highlightElement(el);
    var form = Commentary.makeForm(el);
    el.parentNode.insertBefore(form, el.nextSibling);
};

Commentary.makeForm = function (el) {
    var ce = document.createElement;
    var form = ce('form')
    form.onsubmit = function () {
        Commentary.submitForm(form);
    };
    form.targetElement = el;
    var textarea = ce('textarea');
    textarea.name = 'comment';
    textarea.setAttribute('cols', '60');
    textarea.setAttribute('rows', '10');
    textarea.style.width = '100%';
    form.appendChild(textarea);
    form.appendChild(ce('br'));
    var submit = ce('input');
    submit.setAttribute('type', 'submit');
    submit.setAttribute('value', 'submit');
    form.appendChild(submit);
    return form;
};

Commentary.highlightElement = function (el) {
    el.style.backgroundColor = '#ff9';
};

Commentary.submitForm = function (form) {
    
};