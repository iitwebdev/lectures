/* twill.js */

/* The main namespace: */
twill = {};

twill.activate = function() {
    twill.loadScript(_twill_script);
};

twill.loadScript = function(scriptHref) {
    var d = MochiKit.Async.doSimpleXMLHttpRequest(scriptHref);
    d.addCallback(function (data) {
        var pre = MochiKit.DOM.PRE();
        var lines = data.responseText.split('\n');
        var domLines = [];
        for (var i=0; i<lines.length; i++) {
            var line = lines[i];
            var domLine = MochiKit.DOM.SPAN({}, line);
            domLine.text = line;
            domLine.lineIndex = i;
            domLines.push(domLine);
            pre.appendChild(domLine);
            pre.appendChild(MochiKit.DOM.BR());
        }
        var container = $('script');
        container.appendChild(pre);
        container.lines = lines;
        container.domLines = domLines;
    });
};

twill.Runner = function (lines, domLines) {
    if (this === window) {
        throw('you must use new');
    }
    this.lines = lines;
    this.domLines = domLines;
    this.currentIndex = 0;
    this.frame = $('test-frame');
    this.variables = {};
};

_runner = null;

twill.runner = function () {
    if (! _runner) {
        var container = $('script');
        _runner = new twill.Runner(container.lines, container.domLines);
    }
    return _runner;
}

twill.run = function () {
    twill.runner().run();
};

twill.step = function () {
    twill.runner().step();
}

twill.restart = function () {
    twill.runner().restart();
}

_waitCondition = null;

twill.Runner.prototype.run = function () {
    this._runSome(true);
}

twill.Runner.prototype.step = function () {
    this._runSome(false);
}

twill.Runner.prototype._runSome = function (many) {
    while (this.currentIndex < this.lines.length) {
        if (_waitCondition) {
            if (_waitCondition.apply(this)) {
                _waitCondition = null;
            } else {
                setTimeout(MochiKit.Base.bind(this.run, this), 100);
                break;
            }
        }
        var domLine = this.domLines[this.currentIndex];
        try {
            var result = this.runLine(this.currentIndex);
        } catch (e) {
            domLine.style.backgroundColor = '#f99';
            this.log(e, '#f99');
            break;
        }
        if (result) {
            domLine.style.backgroundColor = '#ff9';
            this.log(result, '#9f9');
        } else {
            domLine.style.backgroundColor = '#9f9';
        }
        this.currentIndex++;
        if (! many) {
            break;
        }
    }
};

twill.Runner.prototype.runLine = function (index) {
    var line = this.lines[index];
    line = MochiKit.Format.strip(line);
    if (! line || line.substr(0, 1) == '#') {
        return;
    }
    var parts = line.split(' ');
    var command = this.commands[parts[0]];
    if (! command) {
        throw('Command not known: "'+parts[0]+'"');
    }
    command.apply(this, extend(null, parts, 1));
};

twill.Runner.prototype.restart = function () {
    for (var i=0; i < this.domLines.length; i++) {
        var el = this.domLines[i];
        el.style.backgroundColor = '';
    }
    $('log').innerHTML = '';
    this.doc().location.href = 'blank.html';
    this.currentIndex = 0;
    this.variables = {};
}

twill.Runner.prototype.doc = function () {
    return this.frame.contentDocument;
};

twill.Runner.prototype.log = function(msg, bgcolor) {
    var div = $('log');
    var v = MochiKit.DOM.SPAN({});
    msg = msg.toString();
    msg = msg.replace('<', '&lt;');
    msg = msg.replace('\n', '<br>\n');
    v.innerHTML = msg;
    if (bgcolor) {
        v.style.backgroundColor = bgcolor;
    }
    div.appendChild(v);
    div.appendChild(MochiKit.DOM.BR());
};

twill.Runner.prototype.form = function (n) {
    var index = parseInt(n);
    if (index === NaN) {
        index = n;
    }
    var forms = this.doc().forms;
    var form = forms[index];
    if (! form) {
        throw('No form by index: '+repr(index)
              + '\nForms: '+stringJoin(keys(forms), ', ')
              + '; indexes: '+ forms.length);
    }
    return form;
}

twill.Runner.prototype.go = function (uri) {
    var doc = this.doc();
    var orig = doc.location.href;
    if (orig == uri) {
        doc.location.reload();
        return;
    }
    doc.location.href = uri;
    _waitCondition = function () {
        return doc.location.href != orig;
    }
}

/* Commands: */

twill.Runner.prototype.commands = {};

twill.Runner.prototype.commands['go'] = function (uri) {
    this.go(uri);
};

twill.Runner.prototype.commands['back'] = function () {
    this.doc().history.go(-1);
};

twill.Runner.prototype.commands['reload'] = function () {
    this.doc().reload();
};

twill.Runner.prototype.commands['follow'] = function (pattern) {
    var regex = RegExp(pattern);
    var els = this.doc().getElementsByTagName('a');
    for (var i=0; i<els.length; i++) {
        if (els[i].getAttribute('href').match(regex)
            || els[i].innerHTML.match(regex)) {
            this.go(els[i].getAttribute('href'));
            return;
        }
    }
    throw('No link found matching '+regex+' from '+els.length+' links');
};

twill.Runner.prototype.commands['code'] = function (code) {
    return "can't do codes yet";
};

twill.Runner.prototype.commands['find'] = function (pattern) {
    var doc = this.doc().innerHTML;
    if (! doc.match(RegExp(pattern))) {
        return 'Pattern not found in document: ' + pattern;
    }
    return;
};

twill.Runner.prototype.commands['notfind'] = function (pattern) {
    var doc = this.doc().getElementsByTagName('html')[0].innerHTML;
    if (doc.match(RegExp(pattern))) {
        return 'Pattern found in document (not expected): ' + pattern;
    }
    return;
};

twill.Runner.prototype.commands['url'] = function (pattern) {
    var href = this.doc().location.href;
    if (! href.match(RegExp(pattern))) {
        return 'URL (' + href + ') does not match pattern: ' + pattern;
    }
    return;
};

twill.Runner.prototype.commands['url'] = function (pattern) {
    var title = this.doc().getElementsByTagName('TITLE')[0].innerHTML;
    if (! title.match(RegExp(pattern))) {
        return 'Title (' + title + ') does not match pattern: ' + pattern;
    }
    return;
};

twill.Runner.prototype.commands['submit'] = function (n) {
    var form = this.form(n);
    var action = form.getAttribute('action');
    var doc = this.doc();
    var origHref = doc.location.href.toString();
    form.submit();
    _waitCondition = function () {
        return doc.location.href != origHref;
    }
};

twill.Runner.prototype.commands['formvalue'] = function (n, fieldname, value) {
    var form = this.form(n);
    var el = form.elements[fieldname];
    if (! el) {
        throw('No field '+fieldname+' in form '+n);
    }
    el.value = value;
};

twill.Runner.prototype.commands['fv'] = twill.Runner.prototype.commands['formvalue'];

twill.Runner.prototype.commands['echo'] = function (message/*optional*/) {
    this.log(stringJoin(arguments, ' '));
}

twill.Runner.prototype.commands['formclear'] = function (n) {
    var form = this.form(n);
    for (var i=0; i<form.elements.length; i++) {
        var el = form.elements[i];
        el.value = '';
    }
}

twill.Runner.prototype.commands['setglobal'] = function (name, value) {
    this.variables[name] = value;
}

twill.Runner.prototype.commands['reset_browser'] = function () {
    this.restart();
}

/* Utility functions: */

function inspect(obj, brief) {
    result = '';
    for (var i in obj) {
        if (brief && typeof(obj[i]) == 'function') {
            break;
        } else {
            result += i + '=' + repr(obj[i]) + '\n';
        }
    }
    return result;
}

function stringJoin(array, joinChar) {
    var result = '';
    for (var i=0; i<array.length; i++) {
        if (result) {
            result += joinChar;
        }
        result += array[i];
    }
    return result;
}

function keys(obj) {
    var result = [];
    for (var i in obj) {
        if (obj.prototype && obj.prototype[i] === obj[i]) {
            continue;
        }
        result.push(i);
    }
    return result;
}
