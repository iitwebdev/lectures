/***********************************************************************
 *
 * Copyright (c) 2005 Imaginary Landscape LLC and Contributors.
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 **********************************************************************/

/*
This follows the WHAT-WG spec roughly, with the intention of following
it more closely in the future.

Its primary feature at the moment is the repeating field model from:
http://www.whatwg.org/specs/web-forms/current-work/#repeatingFormControls

You do this like:

  <form validate="1">

  <fieldset repeat="template" id="address">
  Address: <textarea name="addr-[address]"></textarea><br>
  <button type="remove">Remove this address</button>
  </fieldset>

  <button type="add" template="address">Add an address</button>

  </form>

The validate="1" attribute enables this library on that form.
repeat="template" marks something as a template, the id names the
template.  Fields inside the template have [id] substituted with an
integer.  Two kinds of buttons -- add and remove -- add a new
instance of the template, or remove the containing instance.

There's other stuff in here -- like validation and filling in the
templates -- but it's rough and probably will change to better
fit what WHAT-WG defines.

This library will move in the future, this is just a temporary
location for it.

*/


/* Utility functions */

DOM = MochiKit.DOM;
logFatal = MochiKit.Logging.logFatal;
logError = MochiKit.Logging.logError;
logWarning = MochiKit.Logging.logWarning;
logDebug = MochiKit.Logging.logDebug;



function all_inputs(node) {
    return MochiKit.Base.filter(
        function (el) {
            return (el.tagName == 'INPUT' || el.tagName == 'TEXTAREA'
                    || el.tagName == 'SELECT');
    }, DOM.getElementsByTagAndClassName('*', null, node));
}

function all_child_tags(node) {
    return DOM.getElementsByTagAndClassName('*', null, node);
}

function strip(s) {
    s = s.replace(/^\s*/, '');
    s = s.replace(/\s*$/, '');
    return s;
}

function assert(v, msg, allowWindow) {
    if (! v || (! allowWindow && v === this)) {
        throw ('Assertion failed (' 
               + (v === this ? 'got window object' : v) + ')'
               + (msg ? ': '+msg : ''));
    }
}

function replaceAll(pat, sub, src) {
    /* String.replace only replaces one occurance of a string, this
       replaces all */
    while (src.indexOf(pat) >= 0) {
        src = src.replace(pat, sub);
    }
    return src;
}



/*****************************************
 * Templates (repeating forms)
 *****************************************/

function _scanDocument() {
    _enableTemplates(document.getElementsByTagName('BODY')[0]);
}

function _enableTemplates(node) {
    var templates = [];
    _scanForTemplates(node, templates);
    for (var i=0; i < templates.length; i++) {
        _setupTemplate(templates[i]);
    }
}

function _scanForTemplates(node, templates) {
    if (node.getAttribute('repeat') == 'template') {
        templates[templates.length] = node;
        return
    }
    if (node.tagName == 'BUTTON') {
        var type = node.getAttribute('type');
        if (type == 'add') {
            node.onclick = addButtonOnClick;
        } else if (type == 'remove') {
            node.onclick = removeButtonOnClick;
        } else if (type == 'move-up') {
            node.onclick = moveUpButtonOnClick;
        } else if (type == 'move-down') {
            node.onclick = moveDownButtonOnClick;
        }
    }
    var children = node.childNodes;
    if (children) {
        var length = children.length;
        for (var i=0; i < length; i++) {
            if (children[i].nodeType == 1) {
                _scanForTemplates(children[i], templates);
            }
        }
    }
}

function addRepetitionBlock(insertAfter) {
    return _addRepetition(this, insertAfter, null);
}

function addRepetitionBlockByIndex(index) {
    return _addRepetition(this, null, index);
}

function _addRepetition(template, insertAfter, setIndex) {
    // insertAfter is null when called by an add button from outside
    // the template; when an add button is inside a repetition block
    // then that block is the argument.  This is always null when this
    // is invoked via addRepetitionBlockByIndex.
    //
    // setIndex is non-null if this was invoked via 
    // addRepetitionBlockByIndex.

    assert(template, 'template (in addRepetitionBlock)');
    logDebug('adding repetition block of template ' + template.id
             + (insertAfter ? ' after ' + insertAfter.getAttribute('repeat')
                            : ' at beginning'));
    if (! template.parentNode) {
        return null;
    }
    var templateIndex = parseInt(template.getAttribute('index'));
    var previousBlocks = 0;
    var previous = template.previousSibling;
    while (previous) {
        if (previous.getAttribute && 
            previous.getAttribute('repeat-template') == template.id) {
            previousBlocks++;
            previousIndex = parseInt(previous.getAttribute('repeat'));
            if (previousIndex >= templateIndex) {
                template.setAttribute(
                    'index', templateIndex = previousIndex+1);
            }
        }
        previous = previous.previousSibling;
    }
    if (template.getAttribute('repeat-max')
        && parseInt(template.getAttribute('repeat-max')) <= previousBlocks) {
        return null;
    }
    if (setIndex !== null && setIndex > templateIndex) {
        template.setAttribute(
            'index', templateIndex = setIndex);
    }
    var block = template.cloneNode(true);
    var blockIndex = setIndex === null ? templateIndex : setIndex;
    block.setAttribute('repeat', blockIndex);
    block.removeAttribute('repeat-min');
    block.removeAttribute('repeat-max');
    block.removeAttribute('repeat-start');
    var templateVar = '[' + template.id + ']';
    _substituteChildrenAttributes(block, templateVar, blockIndex);
    block.setAttribute('repeat-template', template.id);
    // Not in spec, but I like to keep an ID of some sort:
    block.setAttribute('id', template.id + '_' + blockIndex);
    if (! insertAfter) {
        var insertAfter = this.previousSibling;
        while (insertAfter) {
            if (insertAfter.getAttribute('repeat-template')
                || ! insertAfter.previousSibling) {
                break;
            }
            insertAfter = insertAfter.previousSibling;
        }
    }
    if (insertAfter && insertAfter.nextSibling) {
        insertAfter.parentNode.insertBefore(block, insertAfter.nextSibling);
    } else if (insertAfter) {
        insertAfter.parentNode.appendChild(block);
    } else {
        template.parentNode.insertBefore(block, template);
    }
    templateIndex++;
    template.setAttribute('index', templateIndex);
    block.removeRepetitionBlock = removeRepetitionBlock;
    block.moveRepetitionBlock = moveRepetitionBlock;
    _enableTemplates(block);
    DOM.showElement(block);
    return block;
}

function _substituteChildrenAttributes(node, sub, repl) {
    var attrs = node.attributes;
    if (attrs) {
        var length = attrs.length;
        for (var i=0; i < length; i++) {
            var attr = attrs[i];
            var current = attr.nodeValue;
            if (!current || typeof(current) != 'string') {
                continue;
            }
            var newValue = replaceAll(sub, repl, current);
            if (current != newValue) {
                node.setAttribute(attr.nodeName, newValue);
            }
        }
    }
    var children = node.childNodes;
    if (children) {
        var length = children.length;
        for (i=0; i < length; i++) {
            _substituteChildrenAttributes(children[i], sub, repl);
        }
    }
}

function removeRepetitionBlock() {
    var block = this;
    if (block.parentNode) {
        block.parentNode.removeChild(block);
    }
    var template = document.getElementById(
        block.getAttribute('repeat-template'));
    if (template) {
        _ensureRepeatMin(template);
    }
}

function _ensureRepeatMin(template) {
    var repeat_min = parseInt(template.getAttribute('repeat-min'));
    if (repeat_min) {
        logDebug('ensuring minimum of ' + repeat_min
                 + ' blocks in template ' + template.id);
        while (_countRepetitionBlocks(template) < repeat_min) {
            logDebug('adding block to ' + template.id 
                     + ' to maintain repeat-min');
            template.addRepetitionBlock();
        }
    }
}

function _countRepetitionBlocks(template) {
    // This will assume that all blocks are siblings
    var children = template.parentNode.childNodes;
    var blocks = 0;
    for (var i = 0; i < children.length; i++) {
        var el = children[i];
        if (el.getAttribute('repeat-template') == template.id
            && el !== template) {
            blocks++;
        }
    }
    return blocks;
}

function moveRepetitionBlock(distance) {
    var block = this;
    var target = block;
    if (! block.parentNode) {
        return null;
    }
    if (distance < 0) {
        while (distance) {
            var prev = target.previousSibling;
            if (! prev) {
                break;
            }
            if (prev.getAttribute && prev.getAttribute('repeat-template')) {
                distance++;
            }
            target = prev;
        }
    } else {
        while (distance) {
            var next = target.nextSibling;
            if (! next) {
                break;
            }
            if (next.getAttribute && next.getAttribute('repeat-template')) {
                distance--;
            }
            target = next;
        }
        target = target.nextSibling;
    }
    block.parentNode.insertBefore(block, target);
}

function _setupTemplate(template) {
    DOM.hideElement(template);
    template.setAttribute('index', 0);
    template.addRepetitionBlock = addRepetitionBlock;
    template.addRepetitionBlockByIndex = addRepetitionBlockByIndex;
    if (! template.getAttribute('repeat-start')) {
        var repeat_start = 1;
    } else {
        var repeat_start = parseInt(template.getAttribute('repeat-start'));
    }
    for (var i=0; i < repeat_start; i++) {
        logDebug('Adding repeat-start block to ' + template.id);
        template.addRepetitionBlock();
    }
    _ensureRepeatMin(template);
}

function _findBlock(node) {
    while (node) {
        if (node.getAttribute && node.getAttribute('repeat-template')) {
            return node;
        }
        node = node.parentNode;
    }
    return null;
}

function removeButtonOnClick() {
    try {
        var block = _findBlock(this);
        if (block) {
            block.removeRepetitionBlock();
        }
    } catch (e) {
        logError(e);
        alert('Error removing block: ' + (e.message ? e.message : e));
    }
    return false;
}

function addButtonOnClick() {
    try {
        var templateId = this.getAttribute('template');
        if (! templateId) {
            var block = _findBlock(this);
            if (block) {
                template = document.getElementById(block.getAttribute('repeat-template'));
                if (template) {
                    template.addRepetitionBlock(block);
                }
            }
        } else {
            var template = document.getElementById(templateId);
            template.addRepetitionBlock();
        }
    } catch (e) {
        logError(e);
        alert('Error adding block: ' + (e.message ? e.message : e));
    }
    return false;
}

function moveUpButtonOnClick() {
    try {
        var block = _findBlock(this);
        block.moveRepetitionBlock(-1);
    } catch (e) {
        logError(e);
        alert('Error moving block up: ' + (e.message ? e.message : e));
    }
    return false;
}

function moveDownButtonOnClick() {
    try {
        var block = _findBlock(this);
        block.moveRepetitionBlock(1);
    } catch (e) {
        logError(e);
        alert('Error moving block down: ' + (e.message ? e.message : e));
    }
    return false;
}






/*****************************************
 * Validation
 *****************************************/

/* This stuff is rough, doesn't follow WHAT-WG, and maybe is broken
   at the moment.  */


function process_required(input) {
    var types = input.getAttribute('form-required').split(',');
    var value;
    if (input.errorNode) {
        input.parentNode.removeChild(input.errorNode);
        input.errorNode = null;
    }
    MochiKit.DOM.removeElementClass(input, 'error');
    for (var i=0; i<types.length; i++) {
        var validator = validators[types[i]];
        if (! validator) {
            throw ('Unknown validation type: ' + types[i]);
        }
        result = validator(get_input_value(input), input, types[i]);
        if (result) {
            var err = MochiKit.DOM.DIV({'class': 'error'}, result);
            input.parentNode.insertBefore(err, input);
            MochiKit.DOM.addElementClass(input, 'error');
            input.errorNode = err;
            return false;
        }
    }
    return true;
}

function get_input_value(input) {
    if (input.tagName == 'INPUT' || input.tagName == 'TEXTAREA') {
        return input.value;
    } else if (input.tagName == 'SELECT') {
        return input.options[input.selectedIndex].value;
    } else {
        throw ('Unknown input tag: ' + input.tagName);
    }
}    

function set_input_value(input, value) {
    if (input.tagName == 'INPUT' || input.tagName == 'TEXTAREA') {
        input.value = value;
    } else if (input.tagName == 'SELECT') {
        for (var i=0; i < input.options.length; i++) {
            if (input.options[i].value == value) {
                input.selectedIndex = i;
                return;
            }
        }
        throw ('Value not found in select list ' 
               + input.getAttribute('name') + ': "'
               + value + '"');
    } else {
        throw ('Unknown input tag: ' + input.tagName);
    }
}

var validators = {
    present: function (value) {
        if (! value) {
            return 'Please enter something';
        }
    },
    url: function (value, input) {
        value = strip(value);
        if (value && value.search(/^https?:\/\//) == -1) {
            value = 'http://' + value;
        }
        input.value = value;
    },
    'path-dir': function (value, input) {
        value = strip(value);
        if (value && value.search(/\/$/) == -1) {
            value = value + '/';
        }
    }
};

//MochiKit.DOM.addLoadEvent(
//    function () {
//        MochiKit.Iter.forEach(
//            document.getElementsByTagName('form'),
//            function (el) {new Form(el)});
//    });

MochiKit.DOM.addLoadEvent(_scanDocument);
        
