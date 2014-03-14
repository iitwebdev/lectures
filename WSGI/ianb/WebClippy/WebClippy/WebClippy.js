/* TODO

* If you have one screen with no scrollbar, then the next screen has a
  scrollbar, the location of the buttons on the right shifts.  It would
  be nice to make them more absolutely positioned (e.g., to screen width
  -20px), so they don't move.

* Maybe we should use fragments instead of cookies to remember
  location.  This would also make a location bookmarkable.

* Should even the base loading be done with fragments instead of
  parameters?  I'm not sure about this.

* It would be nice if there was a way to have asides of some sort.
  Like when you want more detail about some particular operation, but
  you don't want to force people to step through the steps if they don't
  want to.  I'm not sure what the UI would look like.

*/

if (typeof WebClippy == 'undefined') {
    WebClippy = {};
}

/* Catch errors from a function, and regardless of error
   always return the same thing (default false) */
WebClippy.catcher = function (func, returnValue, skip) {
    if (skip) {
        return func;
    }
    return function () {
        try {
            func.apply(this, arguments);
        } catch (e) {
            if (typeof log != 'undefined') {
                log('Error: '+e);
            } else if (typeof console != 'undefined') {
                console.log('Error: '+e);
            }
        }
        return returnValue || false;
    }
}

/* You can use this in a document like:
   <a href="help-document.html"
    onclick="return WebClippy.launch(this)">Show with help</a> */
WebClippy.launch = WebClippy.catcher(
    function (link) {
        link = link || this;
        var href = link.href;
        if (! href) {
            throw("I can't figure out where the help is (did you forget to pass in 'this'?)");
        }
        var oldHref = location.href;
        document.location.href = WebClippy.getScriptLocation() + 'frame.html?doc='+escape(oldHref)+'&help='+escape(href);
    });

/* Returns the location of WebClippy itself (by looking at the script tags) */
WebClippy.getScriptLocation = function () {
    if (typeof WebClippy._scriptLocation == 'undefined') {
        var els = document.getElementsByTagName('script');
        for (var i=0; i<els.length; i++) {
            var el = els[i];
            if (el.src && el.src.indexOf('WebClippy.js') != -1){
                var parts = el.src.split('/');
                parts.length--;
                WebClippy._scriptLocation = parts.join('/') + '/';
                break;
            }
        }
        if (typeof WebClippy._scriptLocation == 'undefined') {
            throw('Cannot find any scripts with WebClippy.js');
        }
    }
    return WebClippy._scriptLocation;
};

/* Used in frame.html to load up the documents from query string parameters
   and initialize the help */
WebClippy.startFrame = function () {
    var vars = WebClippy._parseQueryString();
    if (! vars.doc || ! vars.help) {
        throw('Both the doc and help variables are required in the link ("' + location.href + '")');
    }
    WebClippy.frameWindow = window;
    WebClippy.helpWindow = open(vars.help, 'helpFrame');
    WebClippy.docWindow = open(vars.doc, 'docFrame');
    WebClippy._aLittleLater(function () {
                                WebClippy._fixupHelpWindow(WebClippy.helpWindow);
                            });
};

/* Do something in a little while, typically used when DOM stuff needs
   a moment to update itself */
WebClippy._aLittleLater = function (callback, timeout) {
    timeout = timeout || 1000;
    setTimeout(callback, timeout);
};

/* Adds the CSS and functionality for the help window */
WebClippy._fixupHelpWindow = function (w) {
    
    var doc = w.document;
    try {
        w.WebClippy = WebClippy;
    } catch (e) {
        if (typeof console != 'undefined') {
            console.log('Error setting helpWindow.WebClippy: '+e);
        }
        alert('Cannot initialize help frame, probably because it is on a separate domain');
        return;
    }
    var cssLink = WebClippy.getScriptLocation() + 'help.css';
    WebClippy._fixupHTML();
    WebClippy._addStyleSheet(doc, cssLink);
    WebClippy._addHeader(doc);
    WebClippy.setSlideIndex(WebClippy.readIndexCookie());
    WebClippy.showSlide();
};

/* Adds the little bar at the top of the help window */
WebClippy._addHeader = function (doc) {
    var body = doc.getElementsByTagName('body')[0];
    var div = doc.createElement('div');
    div.setAttribute('id', 'WebClippy_nav');
    var base = WebClippy.getScriptLocation();
    div.innerHTML = 
        '<span id="WebClippy_sizing">'
        + '<a href="#" onclick="return WebClippy.close()">'
        + '<img src="'+base+'x.gif" alt="close help"></a> '
        + '<a href="#" onclick="return WebClippy.collapse()">'
        + '<img src="'+base+'arrow-up.gif" alt="collapse"></a> '
        + '<a href="#" onclick="return WebClippy.expand()">'
        + '<img src="'+base+'arrow-down.gif" alt="expand"></a>'
        + '<span id="WebClippy_title">'
        + doc.title 
        + '</span></span> &nbsp; '
        + '<span id="WebClippy_controls">'
        + '<span id="WebClippy_position"></span> '
        + '<a href="#" onclick="return WebClippy.prevSlide()">'
        + '<img src="'+base+'arrow-left.gif" alt="previous"></a> '
        + '<a href="#" onclick="return WebClippy.nextSlide()">'
        + '<img src="'+base+'arrow-right.gif" alt="next"></a></span>';
    body.insertBefore(div, body.childNodes[0]);
};

/* Go to next slide in help frame */
WebClippy.nextSlide = WebClippy.catcher(
    function () {
        WebClippy._moveSlide(1);
    }, false, true);

/* Go to previous slide in help frame */
WebClippy.prevSlide = WebClippy.catcher(
    function () {
        WebClippy._moveSlide(-1);
    });

/* close help frame */
WebClippy.close = WebClippy.catcher(
    function () {
        var docWindow = WebClippy.docWindow;
        parent.location.href = docWindow.location.href;
    });

/* Make the help frame smaller */
WebClippy.collapse = WebClippy.catcher(
    function () {
        var current = WebClippy._getHelpHeight();
        if (current > 40) {
            WebClippy._expandedHeight = current;
        }
        WebClippy._setHelpHeight(20);
    });

/* Make the help frame bigger again */
WebClippy.expand = WebClippy.catcher(
    function () {
        var previous = WebClippy._expandedHeight || 200;
        var current = WebClippy._getHelpHeight();
        if (current == previous && current < 350) {
            previous += 20;
            WebClippy._expandedHeight = previous;
        }
        WebClippy._setHelpHeight(previous);
    });

WebClippy._setHelpHeight = function (height) {
    var frameWindow = WebClippy.frameWindow;
    var frameset = frameWindow.document.getElementsByTagName('frameset')[0];
    frameset.setAttribute('rows', ''+height+',*');
};

WebClippy._getHelpHeight = function () {
    return WebClippy.helpWindow.innerHeight;
}

WebClippy._moveSlide = function (direction) {
    var index = WebClippy.slideIndex();
    WebClippy.hideSlide();
    index += direction;
    WebClippy.setSlideIndex(index);
    WebClippy.showSlide();
};

/* Return a list of all the <div class="slide"> elements in the help */
WebClippy.slideEls = function () {
    var doc = WebClippy.helpWindow.document;
    if (! WebClippy._slideEls) {
        var els = doc.getElementsByTagName('div');
        var slideEls = WebClippy._slideEls = [];
        for (var i=0; i<els.length; i++) {
            if (WebClippy._hasClass(els[i], 'slide')
                || WebClippy._hasClass(els[i], 'shownSlide')) {
                slideEls.push(els[i]);
            }
        }
    }
    return WebClippy._slideEls;
};

/* Show the current slide */
WebClippy.showSlide = function () {
    var slide = WebClippy.currentSlide();
    if (slide) {
        WebClippy._swapClass(slide, 'slide', 'shownSlide');
    }
    var title = WebClippy.docWindow.document.title + ': ' + WebClippy.helpWindow.document.title;
    try {
        document.title = title;
    } catch (e) {
        // ignore
    }
};

/* Hide the current slide */
WebClippy.hideSlide = function () {
    var slide = WebClippy.currentSlide();
    if (slide) {
        WebClippy._swapClass(slide, 'shownSlide', 'slide');
    }
};

/* Return the slide index (the index of the current slide being shown) */
WebClippy.slideIndex = function () {
    if (typeof WebClippy._slideIndex == 'undefined') {
        return -1;
    } else {
        return WebClippy._slideIndex;
    }
};

WebClippy.setSlideIndex = function (value) {
    var slideEls = WebClippy.slideEls();
    if (value < 0) {
        value = 0;
    }
    if (value >= slideEls.length) {
        value = slideEls.length - 1;
    }
    WebClippy._slideIndex = value;
    WebClippy.writeIndexCookie(value);
    var doc = WebClippy.helpWindow.document;
    var position = '' + (value+1) + '/' + (slideEls.length);
    WebClippy.$('WebClippy_position', doc).innerHTML = position;
};

WebClippy.currentSlide = function () {
    var index = WebClippy.slideIndex();
    var slides = WebClippy.slideEls();
    if (index >= 0 && index < slides.length) {
        return slides[index];
    } else {
        return null;
    }
};

WebClippy._fixupHTML = function () {
    var doc = WebClippy.helpWindow.document;
    var base = WebClippy.getScriptLocation();

    var slides = [];
    var els = WebClippy._copyArray(doc.getElementsByTagName('hr'));
    for (var i=0; i<els.length; i++) {
        var el = els[i];
        var slide = doc.createElement('div');
        slide.className = 'slide';
        WebClippy._popBeforeElement(el, slide, true);
        slides.push(slide);
    }
    /* Get the most trailing slide */
    var body = WebClippy._getBody(doc);
    var slide = doc.createElement('div');
    slide.className = 'slide';
    while (body.childNodes.length) {
        slide.appendChild(body.childNodes[0]);
    }
    slides.push(slide);
    for (var i=0; i<slides.length; i++) {
        var slide = slides[i];
        body.appendChild(slide);
    }

    var els = doc.getElementsByTagName('a');
    for (var i=0; i<els.length; i++) {
        var el = els[i];
        var href = el.getAttribute('href');
        if (href == '#next') {
            el.onclick = WebClippy.nextSlide;
        } else if (href == '#prev') {
            el.onclick = WebClippy.prevSlide;
        } else if (href == '#close') {
            el.onclick = WebClippy.close;
        } else if (href == '#collapse') {
            el.onclick = WebClippy.collapse;
        } else if (href == '#expand') {
            el.onclick = WebClippy.expand;
        } else if (href.charAt(0) == '#') {
            var rest = parseInt(href.substring(1));
            if (rest) {
                el.onclick = function (index) {
                    return function () {
                        WebClippy.hideSlide();
                        WebClippy.setSlideIndex(index-1);
                        WebClippy.showSlide();
                        return false;
                    };
                }(rest);
            }
        }
    }
    els = doc.getElementsByTagName('img');
    for (var i=0; i<els.length; i++) {
        el = els[i];
        var src = el.getAttribute('src');
        if (src == '#prev') {
            el.src = base + 'arrow-left.gif';
            el.style.border = 0;
        } else if (src == '#next') {
            el.src = base + 'arrow-right.gif';
            el.style.border = 0;
        }
    }
};

/* The slide index is also kept in a cookie, so that we can return to the
   old location when you revisit */
WebClippy.readIndexCookie = function () {
    var index = WebClippy.readCookie('WebClippy_index');
    if (! index) {
        index = 0;
    } else {
        index = parseInt(index);
    }
    return index;
};

WebClippy.writeIndexCookie = function (index) {
    WebClippy.createCookie('WebClippy_index', ''+index, 365*10);
}

/* Test if the given element has the given class */
WebClippy._hasClass = function (el, className) {
    if (! el) {
        throw("You cannot test if "+el+" has a class");
    }
    if (! el.className) {
        return false;
    } else if (el.className == className) {
        return true;
    }
    var parts = el.className.split();
    for (var i=0; i<parts.length; i++) {
        if (parts[i] == className) {
            return true;
        }
    }
    return false;
};

WebClippy._getBody = function (doc) {
    return doc.getElementsByTagName('body')[0];
};

WebClippy._copyArray = function (arrayLike) {
    var result = [];
    for (var i=0; i<arrayLike.length; i++) {
        result.push(arrayLike[i]);
    }
    return result;
};

WebClippy._popBeforeElement = function (el, container, removeElement) {
    if (el.parentNode.nodeName.toLowerCase() == 'body') {
        /* We don't have to look up any further */
        WebClippy._movePreviousSiblings(el, container);
        if (removeElement) {
            el.parentNode.removeChild(el);
        }
        /* the container takes any split elements */
        return container;
    }
    var trailing = WebClippy._popBeforeElement(el.parentNode, container, false);
    var newParent = el.parentNode.cloneNode();
    WebClippy._clearNode(newParent);
    WebClippy._movePreviousSiblings(el, newParent);
    trailing.appendChild(newParent);
    if (removeElement) {
        el.parentNode.removeChild(el);
    }
    return newParent;
};

WebClippy._movePreviousSiblings = function (el, container) {
    var parent = el.parentNode;
    while (parent.childNodes[0] !== el) {
        container.appendChild(parent.childNodes[0]);
    }
};

WebClippy._clearNode = function (el) {
    while (el.childNodes.length) {
        el.removeChild(el.childNodes[0]);
    }
};

/* Swap one class for another */
WebClippy._swapClass = function (el, oldClass, newClass) {
    if (! el) {
        throw("You cannot swap the class of "+el);
    }
    if (el.className == oldClass) {
        el.className = newClass;
        return;
    }
    var parts = el.className.split();
    var somethingSet = false;
    for (var i=0; i<parts.length; i++) {
        if (parts[i] == oldClass) {
            parts[i] = newClass;
            somethingSet = true;
        }
    }
    if (! somethingSet) {
        parts.push(newClass);
    }
    el.className = parts.join(' ');
};

/* Add a stylesheet to a document */
WebClippy._addStyleSheet = function (doc, href) {
    // From http://cse-mjmcl.cse.bris.ac.uk/blog/2005/08/18/1124396539593.html
    if (doc.createStyleSheet) {
        doc.createStyleSheet(href);
    } else {
        var style = "@import url('"+href+"');";
        var link = doc.createElement('link');
        link.setAttribute('rel', 'stylesheet');
        link.setAttribute('href', 'data:text/css,'+escape(style));
        doc.getElementsByTagName('head')[0].appendChild(link);
    }
};

/* Like document.getElementById */
WebClippy.$ = function (elId, doc) {
    doc = doc || document;
    var result = doc.getElementById(elId);
    if (result === null) {
        throw('No element with the id "'+elId+'" found');
    }
    return result;
};

/* Parse the query string into an object;
   FIXME: use unicode alternative to escape/unescape */
WebClippy._parseQueryString = function (href) {
    href = href || location.href
    var parts = href.split('?');
    if (! parts[1]) {
        return {};
    }
    parts = parts[1].split('&');
    var variables = {}
    for (var i=0; i<parts.length; i++) {
        var nameValue = parts[i].split('=');
        var name = nameValue[0];
        var value = unescape(nameValue[1]);
        variables[name] = value;
    }
    return variables;
};

// From http://www.quirksmode.org/js/cookies.html

WebClippy.createCookie = function (name, value, days) {
    if (days) {
	var date = new Date();
	date.setTime(date.getTime()+(days*24*60*60*1000));
	var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
};

WebClippy.readCookie = function (name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i < ca.length; i++) {
	var c = ca[i];
	while (c.charAt(0)==' ') c = c.substring(1,c.length);
	if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
};

WebClippy.eraseCookie = function (name) {
	createCookie(name, "", -1);
};
