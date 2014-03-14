"""A reaction to Jacob's post: http://jacobian.org/writing/dynamic-form-generation/
"""

from webob.dec import wsgify
from webob import exc
from webob import Response
from tempita import HTMLTemplate
from formencode import htmlfill

page_template = HTMLTemplate('''
<html>
<head>
<title>Register</title>
<style type="text/css">
.error-message {
  background-color: #600;
  color: #fff;
  border: 2px solid #000;
}
.error {
  border: 2px solid #f00;
th {
  vertical-align: top;
}
</style>
</head>
<body>

<form action="{{action}}" method="POST">
<table>
  <tr>
    <th><label for="username">New Username:</label></th>
    <td><input id="username" type="text" name="username"></td>
  </tr>
  <tr>
    <th><label for="password">Password:</label></th>
    <td><input id="password" type="password" name="password"></td>
  </tr>
  <tr>
    <th><label for="password_confirm">Repeat Password:</label></th>
    <td><input id="password_confirm" type="password" name="password_confirm"></td>
  </tr>
  {{for index, question in enumerate(questions)}}
  <tr>
    <th><label for="field-{{index}}">{{question}}</label></th>
    <td><input id="field-{{index}}" type="text" name="{{question}}"></td>
  </tr>
  {{endfor}}
</table>

<button type="submit">Submit</button>
</form>

</body></html>
''', name='page')

def get_questions(req):
    return ['how old are you?'] + req.GET.getall('question')

def save_answer(req, question, value):
    print 'Answer %s: %s' % (question, value)

@wsgify
def questioner(req):
    if req.path_info == '/thanks':
        return Response('Thanks!')
    questions = get_questions(req)
    errors = {}
    if req.method == 'POST':
        errors = validate(req, questions)
        if not errors:
            for question in questions:
                save_answer(req, question, req.POST[question])
            raise exc.HTTPFound(location='/thanks')
    page = page_template.substitute(
        action=req.url,
        questions=questions)
    page = htmlfill.render(
        page,
        defaults=req.params,
        errors=errors)
    return Response(page)

def validate(req, questions):
    errors = {}
    form = req.POST
    if (form.get('password')
        and form['password'] != form.get('password_confirm')):
        errors['password_confirm'] = 'Passwords do not match'
    fields = questions + ['username', 'password']
    for field in fields:
        if not form.get(field):
            errors[field] = 'Please enter a value'
    return errors

if __name__ == '__main__':
    from paste.httpserver import serve
    serve(questioner)
