class SessionError(Exception):
    pass

class InvalidSession(SessionError):
    """
    Raised when an invalid session ID is used.
    """

class SessionNotFound(SessionError, LookupError):
    """
    Raised when a session can't be found.
    """

class ConflictError(SessionError):
    """
    Raised when the ``locking_policy`` is ``optimistic``, and a
    session being saved is stale.
    """

def create_session_id():
    """Return a unique session ID (an ASCII string).

    This string must be made up of a-zA-Z0-9_-.

    ???: Should we allow hints, like ``REMOTE_ADDR``?
    """

class ISessionListener:

    """
    Objects with this interface can be appended to the ``listener`` attribute of a
    session manager or session.
    """

    def create_session(session_store, new_session):
        """Called when a new session is created.
        """

    def delete_session(session_store, session_id):
        """Called before a session is deleted.

        This can load the session; this will not affect the ultimate
        deletion of the session.
        """

    def rollback(session_store, session):
        """Called before a session is abandoned via .rollback()"""

class ISessionManager:
    
    """
    The session manager represents policy related to sessions;
    expiration, collection, locking.  It also typically belongs to one
    'application', and ties together the session store with the
    session objects.
    """

    id = """The string-identifier for this session manager.

    All applications that share this session manager need to use the
    same id when creating the session manager.

    This string should be made up of a-zA-Z0-9_.-
    """

    locking_policy = """The lock policy.

    This is one of these strings:

    ``'optimistic'``:
      Optimistic locking; concurrent sessions may be opened for writing;
      however, if a session is saved that was loaded before the last save
      of the session, a ConflictError will be raised.

    ``'lossy'``:
      First-come-first-serve.  No locking is done; if a session is written
      it overwrites any other session data that was written.

    ``'serialized`'':
      All sessions opened for writing are serialized; the request is
      blocked until session is available to be opened.
    """

    session_factory = """A callable to produce sessions

    This should be a class or object like ``ISession``.
    """

    listeners = """A list of ISessionListeners.

    When certain events happen, a method on every object in this list
    will be called.
    """

    store = """A ISessionStore"""

    def __init__(id, store, session_factory, locking_policy='lossy'):
        """Initialize the variables

        ???: Does ``__init__`` need to be standardized?
        """

    
    def load_session(id):
        """Return the session from the given ID.

        This method may block if ``locking_policy`` is ``'serialized'``.

        ???: Does this always return a new session object?  I think it
        shouldn't.
        """

    def load_session_read_only(id):
        """Return a read-only version of the session.

        Read-only sessions do not need to be locked as aggressively.
        Also, loading a read-only session will not update its
        last-accessed time, so you may use this to peek at sessions.

        This cannot ensure that the values stored in the session are
        immutable, so it is very possible that you could make implicit
        changes to the session object and then they will be thrown
        away.
        """

    def create_session(id=None):
        """Create a new session object for the given id.

        If ``id`` is None then a new id will be generated.

        This will call ``session_listener.create(session_store, new_session)``
        """

    def save_session(session):
        """Save the given session.

        This may raise a ``ConflictError``
        """

    def unlock_session(session):
        """If the session store is locked for any reason, unlock it.

        It is not an error if no lock exists on the session.
        ``save_session()`` implies ``unlock_session()``.

        This method makes the session obsolete.
        """

    def delete_session(id):
        """Delete the given session.

        This is given the id of the session, not the session object
        itself.

        This calls ``session_listener.delete(session_store,
        session_id)``.
        """

    def delete_expired_sessions():
        """Scan for and delete any expired sessions.

        ???: How are sessions defined to be expired?  Should listeners
        participate?  Should they be able to cancel an expiration?
        """

    def session_ids():
        """Return a list of session IDs.

        ???: Should this return other metadata, like last accessed
        time?
        """

    def last_accessed(id):
        """The integer timestamp when the identified session was last
        accessed.

        Loading the session read-only does not update this value, only
        writing or calling ``touch()``
        """

    def last_written(id):
        """The integer timestamp when the session was last written to
        """

    def touch(id):
        """Update the session's last_accessed time.
        """

class ISession:

    id = """The string (str, not unicode) ID of this session"""

    manager = """Reference to parent ISessionManager object"""

    read_only = """Boolean, if this session was loaded read-only"""

    last_accessed = """Last access integer timestamp"""

    creation_time = """Creation integer timestamp"""

    loaded_timestamp = """Integer timestamp when session was loaded

    If the session manager's ``locking_policy`` is ``optimistic``, when the
    session is saved if the ``last_written`` time is later than this time
    a ``ConflictError`` will be raised.
    """

    obsolete = """
    Boolean; true if this session object has been deleted.  All
    other methods should fail once this is true.  This attribute
    is writable."""

    listeners = """A list of ISessionListener instances"""

    data = """The data being stored.

    This should be pickleable.  The other instance variables are metadata, and
    are not saved as the 'body' of the session; only this data is.

    Typically this is a dictionary-like object; however, if you want
    application-specific storage this object could have a specific interface,
    so long as your session store understands how to save it.

    ???: Should there be some way to identify this kind of
    tightly-bound-to-storage session data from free-form (like a dictionary)
    session data?  If there was, then application-specific storage could use
    something custom for its sessions, but fall on something more generic
    (e.g., pickle and stuff the string somewhere) for other sessions.
    """

    # ???: Should the expire time be overloadable on a per-session
    # basis?  If listeners can cancel the expiration, then this can be
    # done in an ad hoc way

    # ???: Should there be a way of marking the session "dirty"?  Maybe
    # some soft version of a hash should be kept to detect changes?  (a
    # hash that could hash mutable objects)

    def __init__(id, manager, read_only, last_accessed, creation_time, data):
        """Create the session object

        If the session is new, then ``data`` will be none; otherwise it will contain
        the unpickled data.
        """

    def __getitem__(name):
        """Return the object by the given name."""

    def __setitem__(name, value):
        """Add or overwrite the named object.

        The object should be pickleable.
        """

    def __delitem__(name, value):
        """Delete the named object."""

    def touch():
        """Update the session's last_accessed time.

        Typically just calls ``self.manager.touch(self.id)``
        """

    def commit():
        """Calls ``self.manager.save_session(self)``
        """

    def rollback():
        """Calls ``self.manager.unlock_session(self)``.

        Also calls ``session_listener.rollback(self)``.
        """

class ISessionStore:

    """
    This is responsible for storing sessions.  
    """

    def save_session(session):
        """Save the session

        This uses both ``session.id`` and ``session.manager.id`` to save the session.
        """

    def load_session(session_manager_id, session_id, read_only, session_factory):
        """Load the session"""

    def session_ids(session_manager_id):
        """Returns a list of session IDs

        ???: Plus other metadata?
        """

    def delete_session(session_manager_id, session_id):
        """Delete the session"""

    def touch(session_manager_id, session_id):
        """Update the last accessed time for the session"""
        
    def write_lock_session(session_manager_id, session_id):
        """Lock the session for writing

        ???: Should there be a way of loading a session without
        blocking on a lock (e.g., getting an exception when trying to
        load a locked exception)?
        """



"""
Example usage::

    session_store = (create or identify from configuration)

    # This is in a typical web framework...

    def get_session(request):
        session_id = request.get_cookie('session_id')
        if session_id is None:
            session_id = create_session_id()
            request.response.set_cookie('session_id', session_id)
        session_manager = get_session_manager(request)
        session = session_manager.load_session(session_id)
        # A callback to be run when the request has been finished:
        request.run_when_done(session_store.save_session, session)
        return session

    def get_session_store(request):
        # The application id should be unique to this instance of the
        # application.  But if you don't mind being a little sloppy
        # you could use the framework name here (that would make it
        # possible for an application to clobber the session variables
        # from another application).
        appid = get_app_id(request)
        session_store = SessionManager(appid, get_session_store(request), MySessionClass)
        return session_store

    def get_session_store(request):
        return request.environ['session.store']

    class MySessionClass(UserDict):
        def __init__(self, id, manager, read_only, last_accessed, creation_time, data):
            self.id = id
            self.manager = manager
            self.read_only = read_only
            self.last_accessed = last_accessed
            self.creation_time = creation_time
            if data is None:
                data = {}
            self.data = data

"""
