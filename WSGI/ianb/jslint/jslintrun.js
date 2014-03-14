/*
 * Usage:
 * js jslintrun.js [--plusplus] "`cat js_file.js`"
 *
 * Uses the spidermonkey command-line Javascript interpreter, and 
 * Douglas Crockford's jslint (see http://jslint.com).
 *
 * If --plusplus is used, then use the ++ operator will cause an error.
 */

load('fulljslint.js');

var body = arguments[0];
if (body == "--plusplus") {
  jslint.plusplus = true;
  body = arguments[1];
}

var result = jslint(body);
if (result) {
    print('All good.');
} else {
    print('Problems:');
    print(jslint.report());
}
