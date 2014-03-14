/*

    Interpreter: JavaScript Interactive Interpreter

*/
InterpreterManager = function () {
    bindMethods(this);
};

InterpreterManager.prototype.initialize = function () {
    updateNodeAttributes(currentDocument().body, {
        "onbeforepaste": this.beforePaste,
        "onpaste": this.paste
    });
    updateNodeAttributes("interpreter_text", {
        "onkeyup": this.keyUp
    });
    updateNodeAttributes("interpreter_form", {
        "onsubmit": this.submit
    });
    this.banner();
    this.lines = [];
    this.history = [];
    this.currentHistory = "";
    this.historyPos = -1;
    this.blockingOn = null;
    if (typeof(this.doEval) == "undefined") {
        // detect broken eval, warn at some point if a namespace ever gets used
        this.doEval = EvalFunctions.evalWith;
    }
};

InterpreterManager.prototype.banner = function () {
    var _ua = window.navigator.userAgent;
    var ua = _ua.replace(/^Mozilla\/.*?\(.*?\)\s*/, "");
    if (ua == "") {
        // MSIE
        ua = _ua.replace(/^Mozilla\/4\.0 \(compatible; MS(IE .*?);.*$/, "$1");
    }
    appendChildNodes("interpreter_output",
        SPAN({"class": "banner"},
            "MochiKit v" + MochiKit.Base.VERSION + " [" + ua + "]",
            BR(),
            "Type your expression in the input box below and press return, or see the notes below for more information."
        ),
        BR()
    );
};

InterpreterManager.prototype.submit = function () {
    if (this.blockingOn) {
        try {
            this.blockingOn.cancel();
        } catch (e) {
            this.showError(e);
        }
        this.blockingOn = null;
    }
    this.doSubmit();
    this.doScroll();
    return false;
};

InterpreterManager.prototype.doScroll = function () {
    var p = getElement("interpreter_output").lastChild;
    if (typeof(p) == "undefined" || p == null) {
        return;
    }
    var area = getElement("interpreter_area");
    if (area.offsetHeight > area.scrollHeight) {
        area.scrollTop = 0;
    } else {
        area.scrollTop = area.scrollHeight;
    }
};

InterpreterManager.prototype.moveHistory = function (dir) {
    // totally bogus value
    if (dir == 0 || this.history.length == 0) {
        return;
    }
    var elem = getElement("interpreter_text");
    if (this.historyPos == -1) {
        this.currentHistory = elem.value;
        if (dir > 0) {
            return;
        }
        this.historyPos = this.history.length - 1;
        elem.value = this.history[this.historyPos];
        return;
    }
    if (this.historyPos == 0 && dir < 0) {
        return;
    }
    if (this.historyPos == this.history.length - 1 && dir > 0) {
        this.historyPos = -1;
        elem.value = this.currentHistory;
        return;
    } 
    this.historyPos += dir;
    elem.value = this.history[this.historyPos];
}

InterpreterManager.prototype.beforePaste = function (e) {
    e.preventDefault();
};


InterpreterManager.prototype.doPaste = function (text) {
    var lines = rstrip(text).split(/\n/);
    appendChildNodes("interpreter_output",
        SPAN({"class": "code"}, ">>> ", izip(lines, imap(BR, cycle([null]))))
    );
    this.runCode(text);
}

InterpreterManager.prototype.paste = function (e) {
    var text = e.clipboardData.getData("text/plain");
    if (text) {
        e.preventDefault();
        callLater(0.0, this.doPaste, text);
    }
};

InterpreterManager.prototype.keyUp = function (e) {
    e = e || window.event;
    switch (e.keyCode) {
        case 38: this.moveHistory(-1); break;
        case 40: this.moveHistory(1); break;
        default: return true;
    }
    e.cancelBubble = true;
    return false;
};

InterpreterManager.prototype.blockOn = function (d) {
    var node = SPAN({"class": "banner"}, "blocking on " + repr(d) + "...");
    this.blockingOn = d;
    appendChildNodes("interpreter_output", node);
    this.doScroll();
    d.addBoth(function (res) {
        swapDOM(node);
        this.blockingOn = null;
        if (res instanceof CancelledError) {
            window.writeln(SPAN({"class": "error"}, repr(d) + " cancelled!"));
            return undefined;
        }
        return res;
    });
    d.addCallbacks(this.showResult, this.showError);
};

InterpreterManager.prototype.showError = function (e) {
    if (typeof(e) != "object") {
        e = new Error(e);
    }
    appendChildNodes("interpreter_output",
        SPAN({"class": "error"}, "Error:"),
        TABLE({"class": "error"},
            THEAD({"class": "invisible"}, TD({"colspan": 2})),
            TFOOT({"class": "invisible"}, TD({"colspan": 2})),
            TBODY(null,
                map(function (kv) {
                    var v = kv[1];
                    if (typeof(v) == "function") {
                        return;
                    }
                    if (typeof(v) == "object") {
                        v = repr(v);
                    }
                    return TR(null,
                        TD({"class": "error"}, kv[0]),
                        TD({"class": "data"}, v)
                    );
                }, sorted(items(e)))
            )
        )
    );
    window.last_exc = e;
    this.doScroll();
};

EvalFunctions = {
    evalWith: function () {
        with (arguments[1] || window) { return eval(arguments[0]); };
    },
    evalCall: function () {
        return eval.call(arguments[1] || window, arguments[0]);
    },
    choose: function () {
        var ns = {__test__: this};
        var e;
        try {
            if (this.evalWith("return __test__", ns) === this) {
                return this.evalWith;
            }
        } catch (e) {
            // pass
        }
        try {
            if (this.evalCall("return __test__", ns) === this) {
                return this.evalCall;
            }
        } catch (e) {
            // pass
        }
        return undefined;
    }
};
        
InterpreterManager.prototype.doEval = EvalFunctions.choose();

InterpreterManager.prototype.doSubmit = function () {
    var elem = getElement("interpreter_text");
    var code = elem.value;
    elem.value = "";
    var isContinuation = false;
    if (code.length >= 2 && code.lastIndexOf("//") == code.length - 2) {
        isContinuation = true;
        code = code.substr(0, code.length - 2);
    }
    appendChildNodes("interpreter_output",
        SPAN({"class": "code"}, ">>> ", code),
        BR()
    );
    this.lines.push(code);
    this.history.push(code);
    this.historyPos = -1;
    this.currentHistory = "";
    if (isContinuation) {
        return;
    }
    var allCode = this.lines.join("\n");
    this.lines = [];
    this.runCode(allCode);
    return;
};

InterpreterManager.prototype.runCode = function (allCode) {
    var res;
    try {
        res = this.doEval(allCode);
    } catch (e) {
        // mozilla shows some keys more than once!
        this.showError(e);
        return;
    }
    this.showResult(res);
};

InterpreterManager.prototype.showResult = function (res) {
    if (typeof(res) != "undefined") {
        window._ = res;
    }
    if (typeof(res) != "undefined") {
        appendChildNodes("interpreter_output",
            SPAN({"class": "data"}, repr(res)),
            BR()
        );
        this.doScroll();
    }
};

window.writeln = function () {
    appendChildNodes("interpreter_output",
        SPAN({"class": "data"}, arguments),
        BR()
    );
    interpreterManager.doScroll();
};

window.clear = function () {
    replaceChildNodes("interpreter_output");
    getElement("interpreter_area").scrollTop = 0;
};

window.blockOn = function (d) {
    if (!(d instanceof Deferred)) {
        throw new TypeError(repr(d) + " is not a Deferred!");
    }
    interpreterManager.blockOn(d);
};

window.dir = function (o) {
    // Python muscle memory!
    return sorted(keys(o));
};

window.inspect = function (o) {
    window._ = o;
    if ((typeof(o) != "function" && typeof(o) != "object") || o == null) {
        window.writeln(repr(o));
        return;
    }
    var pairs = items(o);
    if (pairs.length == 0) {
        window.writeln(repr(o));
        return;
    }
    window.writeln(TABLE({"border": "1"},
        THEAD({"class": "invisible"}, TR(null, TD(), TD())),
        TFOOT({"class": "invisible"}, TR(null, TD(), TD())),
        TBODY(null,
            map(
                function (kv) {
                    var click = function () {
                        try {
                            window.inspect(kv[1]);
                        } catch (e) {
                            interpreterManager.showError(e);
                        }
                        return false;
                    }
                    return TR(null,
                        TD(null, A({href: "#", onclick: click}, kv[0])),
                        TD(null, repr(kv[1]))
                    );
                },
                pairs
            )
        )
    ));
};
    
interpreterManager = new InterpreterManager();
addLoadEvent(interpreterManager.initialize);

// rewrite the view-source links
addLoadEvent(function () {
    var elems = getElementsByTagAndClassName("A", "view-source");
    var page = "interpreter/";
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var href = elem.href.split(/\//).pop();
        elem.target = "_blank";
        elem.href = "../view-source/view-source.html#" + page + href;
    }
});