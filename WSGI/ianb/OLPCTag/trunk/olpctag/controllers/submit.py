from olpctag.lib.base import *
from sqlobject import SQLObject
from sqlobject.classregistry import MasterRegistry, registry

class SubmitController(BaseController):
    def index(self):
        c.page_title = request.params.get('title', '')
        c.page_uri = request.params['uri']
        p = model.Page.from_uri(c.page_uri, c.page_title)
        c.default_tags = join_tags(dict(
            (ann.tag.name, ann.rating)
            for ann in
            model.Annotation.select_for_user(self.user, p, self.group)))
        results = list(model.Comments.select_for_user(self.user, p, self.group))
        if results:
            c.comments = '\n'.join(r.comments for r in results)
        else:
            c.comments = ''
        return render_response('submit_form.myt')

    def submit(self):
        uri = request.params['uri']
        title = request.params['title']
        tags = split_tags(request.params['tags'])
        comments = request.params['comments']
        p = model.Page.from_uri(uri, title)
        u = self.user
        destroy_objects(model.Annotation.select_for_user(u, p, self.group))
        for tag_name, rating in tags.items():
            model.Annotation(user=u, page=p,
                             tag=model.Tag.from_name(tag_name, self.group),
                             rating=rating)
        destroy_objects(model.Comments.select_for_user(u, p, self.group))
        if comments:
            model.Comments(user=u, page=p, comments=comments,
                           group=self.group)
        if request.params.get('from_js'):
            return Response('''
            <html><head><script type="text/javascript">
            window.close();
            </script></head><body>
            The page should close
            </body></html>
            ''')
        else:
            h.redirect_to(controller='index')

def split_tags(tag_text):
    tags = []
    for tag_chunk in tag_text.split():
        tags.extend(tag_chunk.split(','))
    tags = [t.strip() for t in tags if t.strip()]
    result = {}
    for t in tags:
        if t.startswith('-'):
            adjust = -1
            t = t[1:]
        else:
            adjust = 1
        try:
            rating = int(t)
            name = t
        except ValueError:
            if ':' in t:
                first, second = t.split(':', 1)
                try:
                    rating = int(second)
                    name = first
                except ValueError:
                    try:
                        rating = int(first)
                        name = second
                    except ValueError:
                        name = first
                        # @@: Discard second :(
            else:
                name = t
                rating = 1
        rating *= adjust
        result[name] = result.get(name, 0) + rating
    return result

def join_tags(tags):
    parts = []
    for name, rating in sorted(tags.items()):
        if name == 'general':
            parts.append(str(rating))
            continue
        if rating == -1:
            parts.append('-'+name)
            continue
        if rating == 1:
            parts.append(name)
            continue
        parts.append('%s:%s' % (name, rating))
    return ' '.join(parts)

def destroy_objects(objs):
    for obj in objs:
        obj.destroySelf()
