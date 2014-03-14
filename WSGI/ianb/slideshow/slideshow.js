/*
 * slideshow.js
 * Copyright (c) Ian Bicking <ianb@colorstudy.com> July 2004
 * (This is an MIT/BSD-style permissive license:)
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

/*

Documentation
=============

This implements a simple slideshow, using Javascript.

To use the slideshow, you must list your images as anchor tags, like:

    <div id="images">
      <a href="image1.jpg">My cat</a>
      <a href="image2.jpg">My cat, eating a mouse, <b>ew!</b></a>
      <a href="image3.jpg">My dog, eating my cat.  So sad...</a>
    </div>

You can also give your links title attributes, which will be used for
the page title, and displayed next to the progress indicator.  Then
you must do:

    <script type="text/javascript" src="slideshow.js"></script>
    <script type="text/javascript">
      Slideshow('images');
    </script>

I.e., you must load this file, then you must start the script and
point it at your images (passing in the ID of the element that
contains your anchors).  You can also give a second argument, which is
a set of options, like:

    <script type="text/javascript">
      slideshow('images'
        {titlePrefix: 'Pet Pictures: ',
         prevText: 'back',
         nextText: 'forward',
         fillStyles: true,
         preloadImages: true,
	 bindKeys: false,
	 useThumbnails: false})
    </script>

That's all the useful options this script takes.


Options
-------

imageHeight, imageWidth:
  The width and height of the images.  You probably don't want to give
  both, as that may cause the images to be distorted.  You may want to
  force all your images to have the same height to be less
  disconcerting as you move through images.  You can also give '100%',
  and then give a specific height to your imageContainer.

titlePrefix:
  If you give title attributes to your anchors, then this will be used
  for the document title.  The titlePrefix is prepended to this.  By
  default it is 'Slideshow: ' (note the trailing space).

prevText, nextText:
  The text in the previous and next link, default '<<prev' and 'next>>'.

fillStyles:
  If true (default false), then styles will be applied to some elements,
  so you don't need to do it yourself in the CSS.  You can view these
  styles at the bottom of this file.

preloadImages:
  If true (default false), then all the images will be preloaded.  This
  causes the slideshow to be a bit more snappy, but at the expense of
  loading a bunch of images to start with.

bindKeys:
  If true (default is true), then there will be keyboard shortcuts.
  This could be confusing if you have more than one slideshow on a
  page.

useThumbnails:
  If thumbnails exist, they will be shown on the page.  But if this
  is false (default true) then they will be suppressed.

linkTables:
  If true (default false) then the prev/next links (and progress) will
  be put in a table (with appropriate alignment).  This seems to work
  better than float in most cases.

Styling
-------

There are a couple default classes that you can use.  The previous and
next links both have the class "prevNextButton", and they also have
the "prevButton" and "nextButton" classes (respectively).  The image
has the class "slideshowImage", the description
"slideshowDescription", and the progress indicator
"slideshowProgress".

Keyboard Shortcuts
------------------

You can use the keyboard to navigate as well.  Keys are:

Space, N(ext), F(orward):           go forward
Backspace, P(revious), B(ackward):  go backward


Browser Compatibility
---------------------

This has been tested in Firefox 0.9.1 and Internet Explorer 6.0
*/

allSlideShows = new Array();

function Slideshow(ns, options) {

  if (typeof this != 'object' || this == window) {
    // In case this isn't invoked as "new Slideshow(...)":
    return new Slideshow(ns, options);
  }
  allSlideShows.push(this);
  this.allSlideShowIndex = allSlideShows.length-1;

  this.expression =
    function () {
      return 'allSlideShows[' + this.allSlideShowIndex + ']';
    }

  this.methodExpression =
    function (methodName, args) {
      if (! args) {
	args = '';
      }
      return this.expression() + '.' + methodName + '(' + args + ')';
    }

  if (! options) {
    options = new Object;
  }
  this.ns = ns;
  this.options = options;
  this.slidePosition = 0;

  // Find the slideshow data:
  this.slideContainerElement = document.getElementById(ns);
  if (! this.slideContainerElement) {
    window.alert('No element with the id ' + id + ' found');
    return;
  }
  this.slideElements = findAll('a', this.slideContainerElement);
  this.slides = new Array();
  if (! this.slideElements.length) {
    window.alert('No anchor elements found in the element ' 
		 + id + ' (' + this.slideContainerElement + ')');
    return;
  }
  this.slideContainerElement.style.display = 'none';
  this.thumbnailSlides = new Array();
  for (var i=0; i<this.slideElements.length; i++) {
    var slide = new Slide(this, this.slideElements[i]);
    slide.slideIndex = i;
    this.slides.push(slide);
    if (slide.thumbImage && 
	(typeof options.useThumbnails == 'undefined'
	 || options.useThumbnails)) {
      this.thumbnailSlides.push(slide);
    }
  }

  // Set up all the containers, for progress indicator, the image,
  // and the image description.
  this.progressContainer =
    document.getElementById(this.ns + '_progress');
  this.descriptionContainer =
    document.getElementById(this.ns + '_description');
  this.imageContainer =
    document.getElementById(this.ns + '_body');
  this.thumbContainer =
    document.getElementById(this.ns + '_thumb');

  if (! this.imageContainer || ! this.descriptionContainer ||
      ! this.progressContainer ||
      (! this.thumbContainer && this.thumbnailSlides.length)) {
    if (document.getElementById(this.ns + '_container')) {
      this.container = document.getElementById(this.ns + '_container');
    } else {
      this.container = document.createElement('P');
      this.slideContainerElement.parentNode.insertBefore(
	this.container,
	this.slideContainerElement);
    }

    if (! this.progressContainer) {
      this.progressContainer = document.createElement('P');
      this.progressContainer.className = 'slideshowProgress';
      if (this.container.childNodes.length) {
	this.container.insertBefore(this.progressContainer,
				    this.container.childNodes[0]);
      } else {
	this.container.appendChild(this.progressContainer);
      }
    }
    if (! this.imageContainer) {
      this.imageContainer = document.createElement('SPAN');
      this.imageContainer.className = 'slideshowImage';
      this.container.appendChild(this.imageContainer);
    }
    if (! this.descriptionContainer) {
      this.descriptionContainer = document.createElement('SPAN');
      this.descriptionContainer.className = 'slideshowDescription';
      this.container.appendChild(document.createElement('BR'));
      this.container.appendChild(this.descriptionContainer);
    }
    if (! this.thumbContainer && this.thumbnailSlides.length) {
      this.thumbContainer = document.createElement('DIV');
      this.thumbContainer.className = 'slideshowThumbnail';
      this.container.appendChild(this.thumbContainer);
    }
  }

  for (var i=0; i<this.thumbnailSlides.length; i++) {
    slide = this.thumbnailSlides[i];
    var thumbEl = slide.thumbImage;
    thumbEl.slideIndex = i;
    thumbEl.slideshow = this;
    addEvent(thumbEl, 'click', setSlide);
    thumbEl.setAttribute('title', slide.title);
    this.thumbContainer.appendChild(thumbEl);
  }

  /***********************************************************
   * Define methods:
   **********************************************************/

  this.getOption =
    function(optionName, defaultValue) {
      if (typeof this.options[optionName] == 'undefined') {
	return defaultValue;
      } else {
	return this.options[optionName];
      }
    }

  this.displaySlide =
    function () {
      var slide;
      if (! (slide = this.slides[this.slidePosition])) {
	slide = new Slide(this, this.slideElements[this.slidePosition]);
      }
      slide.display();
      posText = '';
      if (slide.title) {
	posText = slide.title + ' ';
      }
      posText += (this.slidePosition+1) + '/' + this.slideElements.length;
      var prevLink = document.createElement('A');
      addEvent(prevLink, 'click', backwardSlide);
      prevLink.slideshow = this;
      prevLink.setAttribute('href', '');
      prevLink.appendChild(document.createTextNode(
        this.getOption('prevText', '<<prev')));
      prevLink.className = this.getOption('buttonClass',
					  'prevNextButton')
      + ' ' + this.getOption('prevClass', 'prevButton');
      prevLink.id = this.ns + '_prevLink';
      if (this.options.fillStyles) {
	applyStyles(prevNextLinkStyles, prevLink);
      }
      var nextLink = document.createElement('A');
      addEvent(nextLink, 'click', forwardSlide);
      nextLink.slideshow = this;
      nextLink.setAttribute('href', '');
      nextLink.appendChild(document.createTextNode(
	this.getOption('nextText', 'next>>')));
      nextLink.className = this.getOption('buttonClass',
					  'prevNextButton')
      + ' ' + this.getOption('nextClass', 'nextButton');
      nextLink.id = this.ns + '_nextLink';
      if (this.options.fillStyles) {
	applyStyles(prevNextLinkStyles, nextLink);
      }
      if (this.linkTables) {
	var progress = document.createElement('TABLE');
	progress.className = 'slideshowProgress';
	if (this.options.fillStyles) {
	  progress.styles.width = '500px';
	  progress.styles.border = '1px solid black';
	  window.alert(progress);
	}
	var tr = document.createElement('TR');
	progress.appendChild(tr);
	//var td = document.createElement('TD');
	var td = makeElement('<td align="left" style="border: thin red solid"></td>');
	if (this.options.fillStyles) {
	  td.styles.textAlign = 'left';
	}
	td.appendChild(prevLink);
	tr.appendChild(td);
	window.alert(td);
	td = document.createElement('TD');
	if (this.options.fillStyles) {
	  td.styles.textAlign = 'center';
	}
	td.appendChild(document.createTextNode(posTest));
	tr.appendChild(td);
	td = document.createElement('TD');
	if (this.options.fillStyles) {
	  td.styles.textAlign = 'right';
	}
	tr.appendChild(td)
      } else {
	var progress = document.createElement('DIV');
	progress.className = 'slideshowProgress';
	progress.appendChild(prevLink);
	progress.appendChild(document.createTextNode(
	    ' ' + posText + ' '));
	progress.appendChild(nextLink);
	if (this.options.fillStyles) {
	  applyStyles(progressDivStyles, progress);
	}
      }
      replaceChildren(this.progressContainer, progress);
    }

  this.forwardSlide =
    function () {
      this.slidePosition += 1;
      if (this.slidePosition >= this.slideElements.length) {
	this.slidePosition = 0;
      }
      this.displaySlide();
      return false;
    }

  this.backwardSlide =
    function () {
      this.slidePosition -= 1;
      if (this.slidePosition < 0) {
	this.slidePosition = this.slideElements.length-1;
      }
      this.displaySlide();
      return false;
    }

  this.showSlide = 
    function (index) {
      this.slidePosition = index;
      this.displaySlide();
      return false;
    }

  this.displaySlide();

  // Set up key bindings:
  if (options.bindKeys || options.bindKeys == null) {
    installKeyBindings();
    bindKeys([32, // Space
	      78, // N
	      70, // F
	      ], this.methodExpression('forwardSlide'));
    bindKeys([8,  // backspace
	      80, // P
	      66, // B
	      ], this.methodExpression('backwardSlide'));
  }
}

function Slide(slideShow, el) {
  this.element = el;
  this.slideShow = slideShow;
  if (el.tagName != 'A') {
    window.alert('Expected <a> tag (not ' + el.tagName + ': '
		 + el + ')');
  }
  this.image = document.createElement('IMG');
  if (el.getAttribute('fullsrc')) {
    var imEl = this.imageElement = document.createElement('A');
    imEl.appendChild(this.image);
    imEl.setAttribute('title', 'Click for full-sized version');
    imEl.setAttribute('target', 'blank');
    imEl.setAttribute('href', el.getAttribute('fullsrc'));
  } else {
    this.imageElement = this.image;
  }
  this.imageView = this.image;
  this.image.setAttribute('src', el.getAttribute('href'));
  this.image.className = 'slideshowImage';
  if (slideShow.options.imageHeight) {
    this.image.style.height = slideShow.options.imageHeight;
  }
  if (slideShow.options.imageWidth) {
    this.image.style.width = slideShow.options.imageWidth;
  }
  if (slideShow.options.fillStyles) {
    applyStyles(slideshowImgStyles, this.image);
  }
  this.description = document.createElement('SPAN');
  this.description.className = 'slideshowDescription';
  for (var i=0; i < el.childNodes.length; i++) {
    this.description.appendChild(el.childNodes[i].cloneNode(true));
  }
  this.title = el.getAttribute('title');
  if (slideShow.options.preloadImages) {
    this.imageObject = new Image();
    this.imageObject.src = el.getAttribute('href');
  }
  if (el.getAttribute('thumbsrc')) {
    var imEl = this.thumbImage = document.createElement('IMG');
    imEl.setAttribute('src', el.getAttribute('thumbsrc'));
    imEl.setAttribute('title', this.title);
    if (slideShow.options.fillStyles) {
      applyStyles(slideshowThumbStyles, imEl);
    }
  }

  this.display =
    function () {
      replaceChildren(this.slideShow.imageContainer,
		      this.imageElement);
      replaceChildren(this.slideShow.descriptionContainer,
		      this.description);
      if (this.title) {
	if (document.origTitle == null) {
	  document.origTitle = document.title;
	}
	document.title = slideShow.getOption('titlePrefix', 'Slideshow: ')
	  + this.title;
      } else if (document.origTitle) {
	document.title = document.origTitle;
	document.origTitle = null;
      }
    }
}

// Remove all children of container, and add replacement.
function replaceChildren(container, replacement) {
  while (container.childNodes.length) {
    container.removeChild(container.childNodes[0]);
  }
  container.appendChild(replacement);
}

// Search recursively in element for all elements with the tag
// name tagName, return result as an Array.
function findAll(tagName, element) {
  var result = new Array;
  _findAll(tagName, element, result);
  return result;
}

function _findAll(tagName, element, result) {
  var i, child;
  var children = element.childNodes;
  if (children) {
    for (i=0; i < children.length; i++) {
      child = children[i];
      if (child.tagName && child.tagName.toLowerCase() == tagName) {
	result.push(child);
      }
      _findAll(tagName, child, result);
    }
  }
}

function makeElement(tagString) {
  var container = document.createElement('SPAN');
  container.innerHTML = tagString;
  return container.childNodes[0];
}

function addEvent(obj, eventType, func) {
  if (obj.addEventListener) {
    obj.addEventListener(eventType, func, true);
  } else if (obj.attachEvent) {
    obj.attachEvent('on' + eventType, func);
  } else {
    obj.setAttribute('on' + eventType, func);
  }
}

function cancelEvent(ev) {
  ev.cancelBubble = true;
  if (ev.stopPropagation) {
    ev.stopPropagation();
  }
  if (ev.preventDefault) {
    ev.preventDefault();
  }
  return false;
}

function setSlide(ev) {
  if (document.all) {
    ev = window.event;
  }
  var el = ev.target;
  if (! el) {
    el = ev.srcElement;
  }
  /*window.alert('Element: ' + el + ' slideshow: ' + el.slideshow
    + ' event: ' + event + ' this: ' + this);*/
  el.slideshow.showSlide(el.slideIndex);
  return cancelEvent(ev);
}

function backwardSlide(ev) {
  if (document.all) {
    ev = window.event;
  }
  var el = ev.target;
  if (! el) {
    el = ev.srcElement;
  }
  el.slideshow.forwardSlide();
  return cancelEvent(ev);
}

function forwardSlide(ev) {
  if (document.all) {
    ev = window.event;
  }
  var el = ev.target;
  if (! el) {
    el = ev.srcElement;
  }
  el.slideshow.forwardSlide();
  return cancelEvent(ev);
}


// Key bindings

var bindings = {};

function installKeyBindings() {
  document.onkeydown = keyPressEvent;
}

function bindKeys(keys, func) {
  for (var i=0; i < keys.length; i++) {
    bindings[keys[i]] = composeFunctions(bindings[keys[i]], func);
  }
}

function composeFunctions(f1, f2) {
  // Takes two arguments, and returns a function that runs
  // both of them in turn.  If one of the arguments is false
  // (or null or undefined) then it returns the other argument.
  // Can also deal with string arguments, which are eval'd.
  // It always returns functions, never strings.
  if (! f1) {
    if (typeof f2 == 'string') {
      return function() {
	eval(f2);
      }
    } else {
      return f2;
    }
  } else if (! f2) {
    if (typeof f1 == 'string') {
      return function() {
	eval(f1);
      }
    } else {
      return f1;
    }
  }
  if (typeof f1 == 'string') {
    if (typeof f2 == 'string') {
      return function() {
	eval(f1);
	eval(f2);
      }
    } else {
      return function() {
	eval(f1);
	f2();
      }
    }
  } else if (typeof f2 == 'string') {
    return function() {
      f1();
      eval(f2);
    }
  } else {
    return function() {
      f1();
      f2();
    }
  }
}

function keyPressEvent(event) {
  if (document.all) {
    event = window.event;
  }
  var key;
  if (document.layers) {
    key = event.which;
  } else {
    key = event.keyCode;
  }
  if (! key) {
    return true;
  }
  if (bindings[key]) {
    if (document.all) {
      event.returnValue = false;
    }
    func = bindings[key];
    func();
    return false;
  } else {
    return true;
  }
}


// Styles

function applyStyles(styles, el) {
  for (i in styles) {
    el.style[i] = styles[i];
  }
}


var prevNextLinkStyles = {
  textDecoration: 'none',
  border: 'thin outset black',
  backgroundColor: '#dddddd',
  padding: '3px',
  color: 'black'
};

var progressDivStyles = {
  textAlign: 'center'
};

var slideshowImgStyles = {
  border: '4px solid black'
};

var slideshowThumbStyles = {
  paddingLeft: '5px',
  paddingRight: '5px',
  border: '0'
};
