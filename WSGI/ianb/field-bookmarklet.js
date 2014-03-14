// Using this bookmarklet: 
// Copy the (function ()...) into a bookmark, typically a bookmark on
// your bookmark toolbar.  Make sure the bookmark starts with
// javascript: When you use this bookmarklet, all the forms on a page
// will be framed out with information on the form, and all input
// elements will have their name and id (if they have one) displayed.
// Also elements with hidden values (like submit buttons) will have
// their value shown.

(function () {
     forms = document.forms;
     for (var i=0; i<forms.length; i++) {
         form = forms[i];
         form.style.border = '2px dashed #00f';
         text = 'form ' + (form.getAttribute('method') || 'GET')
             + ' ' + form.action;
         if (form.name) {
             text += ' name="'+form.name+'"';
         }
         text += ' ';
         form.insertBefore(document.createTextNode(text),
                           form.childNodes[0]);
         for (var j=0; j<form.elements.length; j++) {
             el = form.elements[j];
             if (el.nodeName == 'FIELDSET') {
                 continue;
             }
             container = document.createElement('span');
             container.style.border = '1px dashed #060';
             el.parentNode.insertBefore(container, el);
             text = el.name || '(no name)';
             if (el.id) {
                 text += ' id="'+el.id+'"';
             }
             if ((el.type == 'submit' || el.type == 'checkbox' || el.type == 'radio')
                 && el.value) {
                 text += ' value="'+el.value+'"';
             }
             if (el.type == 'select') {
                 for (var k=0; k<el.options.length; k++) {
                     option = el.options[k];
                     option.innerHTML += ' value="'+option.value+'"';
                 }
             }
             if (el.type == 'hidden') {
                 el.type = 'text';
             }
             container.appendChild(document.createTextNode(text+' '));
             container.appendChild(el);
         }
     }
 }());
