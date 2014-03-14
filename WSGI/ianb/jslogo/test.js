function assertEqual(x, y, desc) {
    try {
        var result = compare(x, y);
    } catch (e) {
        logError('Error: ' + (desc || '(unnamed)') + ' failed '
                 + repr(x) + ' and ' + repr(y) + ' give: '
                 + e);
        return;
    }
    if (result) {
        logError('Error: ' + (desc || '(unnamed)') + ' failed '
                 + repr(x) + ' != ' + repr(y));
    } else {
        logDebug('Success ' + (desc || (x + ' == ' + y)));
    }
}

var tokenTests = [
                  'this is a test', ['this', 'is', 'a', 'test'],
                  '1 + 2', [1, '+', 2],
                  '[and then+1]', ['[', 'and', 'then', '+', 1, ']'],
                  '(:this + :that)*5', ['(', ':', 'this', '+', ':', 'that',
                                        ')', '*', 5],
                  'first "that', ['first', '"', 'that']
                  ];

for (var i=0; i<tokenTests.length; i+=2) {
    var tokenResult = tokenize(tokenTests[i]);
    assertEqual(tokenResult, tokenTests[i+1]);
}
