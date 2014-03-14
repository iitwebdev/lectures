from sqlobject import *
from pylons.database import PackageHub
hub = PackageHub("olpctag")
__connection__ = hub
from datetime import datetime

class Group(SQLObject):

    class sqlmeta:
        table = 'tag_group'

    slug = StringCol(alternateID=True, length=255)
    name = StringCol(default=None)
    description = StringCol(default=None)
    uri = StringCol(default=None)

    def _get_display_title(self):
        return self.name or self.slug.title()

class Page(SQLObject):

    uri = StringCol(unique=True, alternateID=True, notNull=True,
                    length=1000)
    title = StringCol()
    added = DateTimeCol(default=datetime.now)
    annotations = MultipleJoin('Annotation')

    @classmethod
    def from_uri(cls, uri, title=None):
        try:
            return cls.byUri(uri)
        except LookupError:
            return cls(uri=uri, title=title)

    def _get_display_title(self):
        return self.title or self.uri

class Tag(SQLObject):

    name = StringCol(notNull=True)
    group = ForeignKey('Group', notNull=True)
    description = StringCol(default=None)
    added = DateTimeCol(default=datetime.now)
    annotations = MultipleJoin('Annotation')

    @classmethod
    def from_name(cls, name, group):
        results = list(cls.selectBy(name=name, groupID=group.id))
        if results:
            assert len(results) == 1
            return results[0]
        else:
            return cls(name=name, group=group)

    @classmethod
    def select_for_user(cls, user, page, group):
        return cls.select(
            (cls.q.id == Annotation.q.tagID)
            & (Annotation.q.userID == user.id)
            & (Annotation.q.pageID == page.id)
            & (cls.q.groupID == group.id))

    def pages_by_rating(self, limit=1):
        """
        Return a list of (rating, page) ordered by the pages' rating, then
        title.  No page with a rating of less than limit will be returned.
        """
        pages = {}
        for ann in Annotation.selectBy(tagID=self.id):
            page = ann.page
            pages[page] = pages.get(page, 0) + ann.rating
        pages = sorted(
            ((rating, page) for (page, rating) in pages.iteritems()
             if rating >= limit),
            key=lambda (r, p): (r, p.title))
        return pages

class Comments(SQLObject):
    user = ForeignKey('User')
    page = ForeignKey('Page')
    group = ForeignKey('Group')
    comments = StringCol()
    added = DateTimeCol(default=datetime.now)

    @classmethod
    def select_for_user(cls, user, page, group):
        return cls.select(
            (cls.q.userID == user.id)
            & (cls.q.pageID == page.id)
            & (cls.q.groupID == group.id))

class User(SQLObject):

    username = StringCol(alternateID=True, length=255)
    name = StringCol(default=None)
    added = DateTimeCol(default=datetime.now)
    annotations = MultipleJoin('Annotation')

    @classmethod
    def from_username(cls, username):
        try:
            return cls.byUsername(username)
        except LookupError:
            return User(username=username)

class Annotation(SQLObject):

    user = ForeignKey('User')
    tag = ForeignKey('Tag')
    page = ForeignKey('Page')
    rating = IntCol(default=0)
    added = DateTimeCol(default=datetime.now)

    @classmethod
    def select_for_user(cls, user, page, group):
        return cls.select(
            (cls.q.userID == user.id)
            & (cls.q.pageID == page.id)
            & (cls.q.tagID == Tag.q.id)
            & (Tag.q.groupID == group.id))


soClasses = [Group, User, Page, Tag, Comments, Annotation]

def setup_classes():
    all_extra = []
    for cls in soClasses:
        print 'Handling table', cls.sqlmeta.table
        cls.dropTable(ifExists=True)
        sql, extra = cls.createTableSQL()
        all_extra.extend(extra)
        print sql
        cls.createTable(ifNotExists=True)
    print '\n'.join(all_extra)

if __name__ == '__main__':
    import sys
    import os
    from paste.deploy import CONFIG, appconfig
    if not sys.argv[1:]:
        print 'usage: ... conf_file'
        sys.exit(2)
    conf_filename = sys.argv[1]
    if not conf_filename.startswith('config:'):
        conf_filename = 'config:' + conf_filename
    conf = appconfig(conf_filename, relative_to=os.getcwd())
    conf = {'global_conf': conf.global_conf,
            'app_conf': conf.local_conf}
    CONFIG.push_process_config(conf)
    setup_classes()
    
