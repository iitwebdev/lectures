"""
A generalized activity log for SQLObject classes.  Use::

    class MyClass(SQLObject):

        activity = activitylog.Activity()

    inst = MyClass.get(1)
    for logitem in MyClass.activity:
        print 'On', logitem.event_date, logitem.user, 'did', \
              logitem.action
    inst.activity.add('delete', 'This thing was deleted')
    

"""
from sqlobject import *
import datetime

# Set this externally to make automatic user getting work:
appcontext = None

__all__ = ['ActivityLog', 'Activity']

class ActivityLog(SQLObject):

    """
    This represents some activity in the system.
    """

    class sqlmeta:
        defaultOrderBy = 'event_date'

    # When this happened:
    event_date = DateTimeCol(default=datetime.datetime.now)
    # Who did it:
    username = StringCol(notNull=True)
    # What they did (usually a constrained string!):
    action = StringCol(notNull=True)
    # A free text description:
    description = StringCol(default=None)
    # General data, that can be used for action-specific, formal
    # content:
    data = StringCol(default=None)
    # What kind of item was acted upon:
    table_name = StringCol(default=None)
    # And its ID:
    object_id = IntCol(default=None)

class Activity(object):

    def __init__(self, table=None):
        if table is None:
            table = ActivityLog
        self.table = table

    def __get__(self, obj, type=None):
        if obj:
            return ActivityInstance(self, obj)
        else:
            return ActivityClass(self, type)

class ActivityInstance(object):

    def __init__(self, activity, obj):
        self.activity = activity
        self.obj = obj

    def add(self, action, description=None, data=None,
            username='<auto>', date=None):
        if date is None:
            date = datetime.datetime.now()
        if username == '<auto>':
            if appcontext is None:
                username = None
            else:
                username = appcontext.servlet._username or 'Anonymous'
        ActivityLog(
            event_date=date,
            action=action,
            username=username,
            description=description,
            data=data,
            table_name=self.obj.sqlmeta.table,
            object_id=self._get_id())

    def _get_id(self):
        return self.obj.id

    def __repr__(self):
        return '<Activity for: %s>' % (
            repr(self.obj).strip('<').strip('>'))
    
    def __iter__(self):
        table = self.activity.table
        return table.select(
            (table.q.table_name==self.obj.sqlmeta.table)
            & (table.q.object_id==self.obj.id))
    
class ActivityClass(ActivityInstance):

    def __iter__(self):
        table = self.activity.table
        return table.select(
            (table.q.table_name==self.type.sqlmeta.table))
    
    def _get_id(self):
        return None
