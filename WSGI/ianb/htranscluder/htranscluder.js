/*
hinclude.js -- HTML Includes (version 0.9)

Copyright (c) 2005-2006 Mark Nottingham <mnot@pobox.com>
Additions and changes made by Ian Bicking <ianb@openplans.org>, Open Planning Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

--------------------------------------------------------------------------------

See http://www.mnot.net/javascript/hinclude/ for documentation.

TODO:
 - check navigator property to see if browser will handle this without javascript

--------------------------------------------------------------------------------
*/

var htransclude = {
    makeElement: function (text, fragment) {
        var match = text.match(/<body.*?>/i);
        if (match !== null) {
            text = text.substring(match.index+match[0].length);
        }
        match = text.match(/<\/body.*?>/i);
        if (match !== null) {
            text = text.substring(0, match.index);
        }
        var newEl = document.createElement('span');
        newEl.innerHTML = text;
        if (fragment !== null) {
            newEl = htransclude.findElementById(newEl, fragment) || newEl;
        } else {
            if (newEl.childNodes.length == 1) {
                newEl = newEl.childNodes[0];
            }
        }
        return newEl;
    },

    findElementById: function (el, elementId) {
        if (el.getAttribute('id') == elementId) {
            return el;
        }
        for (var i=0; i<el.childNodes.length; i++) {
            var child = el.childNodes[i];
            if (child.nodeType != 1) {
                continue;
            }
            var newEl = htransclude.findElementById(child, elementId);
            if (newEl !== null) {
                return newEl;
            }
        }
        return null;
    },

    setContentAsync: function (element, req, fragment) {
        if (req.readyState == 4) {
            // this should look for a fragment or something
            if (req.status == 200 || req.status == 304 || req.status === 0) {
                var newEl = htransclude.makeElement(req.responseText, fragment);
                element.parentNode.insertBefore(newEl, element);
                element.parentNode.removeChild(element);
            }
        }
    },

    buffer: [],
    setContentBuffered: function (element, req, fragment) {
        if (req.readyState == 4) {
            htransclude.buffer.push([element, req, fragment]);
            htransclude.outstanding--;
            if (htransclude.outstanding === 0) {
                htransclude.showBufferedContent();
            }
        }
    },
    showBufferedContent: function () {
        while (htransclude.buffer.length > 0) {
           var include = htransclude.buffer.pop();
           if (include[1].status == 200 | include[1].status == 304 || include[1].status === 0) {
               var newEl = htransclude.makeElement(include[1].responseText, include[2]);
               include[0].parentNode.insertBefore(newEl, include[0]);
               include[0].parentNode.removeChild(include[0]);
           }
        }
    },

    outstanding: 0,
    run: function () {
        var mode = this.getMeta("include_mode", "buffered"); 
        var callback = function(element, req) {};
        var includes = document.getElementsByTagName("a");
        if (mode == "async") {
            callback = this.setContentAsync;
        } else if (mode == "buffered") {
            callback = this.setContentBuffered;
            var timeout = this.getMeta("include_timeout", 2.5) * 1000;
            setTimeout(htransclude.showBufferedContent, timeout);
        }
        for (var i=0; i < includes.length; i++) {
            if (includes[i].getAttribute('rel') == 'include') {
                this.include(includes[i], includes[i].href, callback);
            }
        }
    },
    
    include: function (element, url, incl_cb) {
        var fragment = null;
        if (url.indexOf('#') != -1) {
            fragment = url.substring(url.indexOf('#')+1);
            url = url.substring(0, url.indexOf('#'));
        }
        var scheme = url.substring(0, url.indexOf(":"));
        if (scheme.toLowerCase() == "data") { // just text/plain for now
           var data = unescape(url.substring(url.indexOf(",") + 1, url.length));
           element.innerHTML = data;
        } else {
            var req = false;
            if(window.XMLHttpRequest) {
                try {
                    req = new XMLHttpRequest();
                } catch(e) {
                    req = false;
                }
            } else if(window.ActiveXObject) {
                try {
                    req = new ActiveXObject("Microsoft.XMLHTTP");
                } catch(e) {
                    req = false;
                }
            }
            if(req) {
                this.outstanding++;
                req.onreadystatechange = function() {
                    incl_cb(element, req, fragment);
                };
                try {
                    req.open("GET", url, true);
                    req.send("");
                } catch (e) {
                    this.outstanding--;
                    alert("Include error: " + url + " (" + e + ")");
                }
            }    
        }
    },

    getMeta: function (name, value_default) {
        var metas = document.getElementsByTagName("meta");
        for (var m=0; m < metas.length; m++) {
            var meta_name = metas[m].getAttribute("name");
            if (meta_name == name) {
                return metas[m].getAttribute("content");
            }
        }
        return value_default;
    },
    
    /*
     * (c)2006 Dean Edwards/Matthias Miller/John Resig
     * Special thanks to Dan Webb's domready.js Prototype extension
     * and Simon Willison's addLoadEvent
     *
     * For more info, see:
     * http://dean.edwards.name/weblog/2006/06/again/
     * http://www.vivabit.com/bollocks/2006/06/21/a-dom-ready-extension-for-prototype
     * http://simon.incutio.com/archive/2004/05/26/addLoadEvent
     * 
     * Thrown together by Jesse Skinner (http://www.thefutureoftheweb.com/)
     *
     *
     * To use: call addDOMLoadEvent one or more times with functions, ie:
     *
     *    function something() {
     *       // do something
     *    }
     *    addDOMLoadEvent(something);
     *
     *    addDOMLoadEvent(function() {
     *        // do other stuff
     *    });
     *
     */ 
    addDOMLoadEvent: function(func) {
       if (!window.__load_events) {
          var init = function () {
              // quit if this function has already been called
              if (arguments.callee.done) {
                  return;
              }
          
              // flag this function so we don't do the same thing twice
              arguments.callee.done = true;
          
              // kill the timer
              if (window.__load_timer) {
                  clearInterval(window.__load_timer);
                  window.__load_timer = null;
              }
              
              // execute each function in the stack in the order they were added
              for (var i=0;i < window.__load_events.length;i++) {
                  window.__load_events[i]();
              }
              window.__load_events = null;
              
              // clean up the __ie_onload event
              /*@cc_on @*/
              /*@if (@_win32)
                  document.getElementById("__ie_onload").onreadystatechange = "";@*/
              /*@end @*/
          };
       
          // for Mozilla/Opera9
          if (document.addEventListener) {
              document.addEventListener("DOMContentLoaded", init, false);
          }
          
          // for Internet Explorer
          /*@cc_on @*/
          /*@if (@_win32)
              document.write("<scr"+"ipt id=__ie_onload defer src=javascript:void(0)><\/scr"+"ipt>");
              var script = document.getElementById("__ie_onload");
              script.onreadystatechange = function() {
                  if (this.readyState == "complete") {
                      init(); // call the onload handler
                  }
              }; @*/
          /*@end @*/
          
          // for Safari
          if (/WebKit/i.test(navigator.userAgent)) { // sniff
              window.__load_timer = setInterval(function() {
                  if (/loaded|complete/.test(document.readyState)) {
                      init(); // call the onload handler
                  }
              }, 10);
          }
          
          // for other browsers
          window.onload = init;
          
          // create event function stack
          window.__load_events = [];
       }
       
       // add function to event stack
       window.__load_events.push(func);
    }
}

htransclude.addDOMLoadEvent(function() { htransclude.run(); });
