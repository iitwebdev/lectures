var foo= 'bar';

function tokenize(s) {
    var result = [];
    while (s) {
        //logDebug('match '+repr(result)+' with '+repr(s));
        var char1 = s.charAt(0);
        s = s.substr(1);

        if (char1 == ' ' || char1 == '\t') {
            /* Whitespace; ignore */
            continue;
        }

        if (char1.match( RegExp('[\\n[()\*+-/\\:\\]]') ) || char1 == '"') {
            /* literal character */
            result.push(char1);
            continue;
        }

        if (char1.match(/[<>=]/)) {
            /* possible two-char operator */
            if (s.match(/^[<>=]/)) {
                char1 += s.charAt(0);
                s = s.substr(1);
            }
            result.push(char1);
            continue;
        }

        if (char1.match(/[\d.]/)) {
            num = char1;
            while (s) {
                char1 = s.charAt(0);
                if (char1.match(/^[\d.]/)) {
                    num += char1;
                    s = s.substr(1);
                } else {
                    break;
                }
            }
            result.push(parseInt(num))
            continue;
        }

        if (char1.match(/[a-zA-Z]/)) {
            name = char1;
            while (s) {
                char1 = s.charAt(0);
                if (char1.match(/[a-zA-Z0-9._]/)) {
                    name += char1;
                    s = s.substr(1);
                } else {
                    break;
                }
            }
            result.push(name);
            continue;
        }

        logDebug('Bad character: '+repr(char1));

    }
    return result;
}

