#include <Python.h>

static PyObject *
html_escape(PyObject *self, PyObject *args)
{
    char *input;
    PyObject *input_obj = NULL;
    int input_length;
    int convert_quote;
    PyObject *convert_quote_obj = NULL;
    char *input_converted;
    int input_converted_length;
    int i;
    char *pos;
    char c;
    int conv_chars;

    if (!PyArg_ParseTuple(args, "O|O", &input_obj, &convert_quote_obj)) {
        return NULL;
    }
    if (! convert_quote_obj) {
        convert_quote = 0;
    } else {
        convert_quote = PyObject_IsTrue(convert_quote_obj);
    }
    if (convert_quote == -1) {
        return NULL;
    }
    if (PyString_AsStringAndSize(input_obj, &input, &input_length) == -1) {
        return NULL;
    }
    conv_chars = 0;
    for (i=0; i<input_length; i++) {
        c = input[i];
        // &amp; &lt; &gt; &quot;
        switch (c) {
        case '&':
            conv_chars += 4;
            break;
        case '<':
        case '>':
            conv_chars += 3;
            break;
        case '"':
            if (convert_quote) {
                conv_chars += 5;
            }
            break;
        }
    }
    if (! conv_chars) {
        Py_INCREF(input_obj);
        return input_obj;
    }
    input_converted_length = input_length + conv_chars;
    input_converted = malloc(sizeof(char) * input_converted_length);
    pos = input_converted;
    for (i=0; i<input_length; i++) {
        c = input[i];
        switch (c) {
        case '&':
            pos[0] = '&';
            pos[1] = 'a';
            pos[2] = 'm';
            pos[3] = 'p';
            pos[4] = ';';
            pos += 5;
            break;
        case '<':
            pos[0] = '&';
            pos[1] = 'l';
            pos[2] = 't';
            pos[3] = ';';
            pos += 4;
            break;
        case '>':
            pos[0] = '&';
            pos[1] = 'g';
            pos[2] = 't';
            pos[3] = ';';
            pos += 4;
            break;
        case '"':
            if (convert_quote) {
                pos[0] = '&';
                pos[1] = 'q';
                pos[2] = 'u';
                pos[3] = 'o';
                pos[4] = 't';
                pos[5] = ';';
                pos += 6;
            } else {
                pos[0] = '"';
                pos += 1;
            }
            break;
        default:
            pos[0] = c;
            pos += 1;
        }
    }
    return Py_BuildValue("s#", input_converted, input_converted_length);
}

static PyMethodDef HtmlMethods[] = {
    {"escape",  html_escape, METH_VARARGS,
     "HTML-Escape a string."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_html(void)
{
    (void) Py_InitModule("_html", HtmlMethods);
}
