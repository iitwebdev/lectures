import re
from lxml.etree import tostring
from dateutil.parser import parse as dateutil_parse
import datetime
from hreviewparser.model import HReview, Tag, Rating, Item, URL, Photo
from hreviewparser.parselog import dummy
from hreviewparser.elquery import *

class NoDefault:
    """
    Used when there's no default argument
    """

def filter_none(seq):
    return [i for i in seq if i is not None]

def parse_hreviews(root, log=dummy):
    """
    Returns a list of all hreviews found in the given element.
    """
    return filter_none([
        parse_hreview(el, log=log)
        for el in get_elements_by_class(root, 'hreview')])

def parse_hreview(el, log=dummy):
    """
    Parses a single hreview out of the given element, returning an
    `HReview` object.  The element should have ``class="hreview"``.
    """
    try:
        version, version_el = get_single_item(el, 'version', log=log)
    except ElementNotFound:
        version = version_el = None
    try:
        summary, summary_el = get_single_item(el, 'summary', log=log)
    except ElementNotFound:
        summary = summary_el = None
    try:
        type, type_el = get_single_item(el, 'type', log=log)
    except ElementNotFound:
        type = type_el = None
    try:
        item_el = get_single_el(el, 'item', log=log)
    except ElementNotFound:
        log.fatal(
            "Required element with class fn not found in %s",
            tostring(el))
        return None
    item = parse_item(item_el, log=log)
    try:
        reviewer_el = get_single_el(el, 'reviewer', log=log)
    except ElementNotFound:
        reviewer_el = reviewer = None
    else:
        reviewer = parse_hcard(reviewer_el)
    try:
        dtreviewed, dtreviewed_el = get_single_item(el, 'dtreviewed', log=log)
    except ElementNotFound:
        dtreviewed_el = dtreviewed = None
    else:
        dtreviewed = parse_date(dtreviewed, log=log)
        if dtreviewed is None:
            dtreviewed_el = None
    try:
        rating = get_plain_rating_item(el, log=log)
    except ElementNotFound:
        rating = None
    try:
        description_el = get_single_el(el, 'description', log=log)
    except ElementNotFound:
        description = description_el = None
    else:
        description = get_contents(description_el).strip()
    tags = get_tags(el, log=log)
    try:
        permalink, permalink_el = get_rel_link(el, 'bookmark', log=log)
    except ElementNotFound:
        permalink = permalink_el = None
    try:
        license, license_el = get_rel_link(el, 'license', log=log)
    except ElementNotFound:
        license = license_el = None

    return HReview(
        el=el,
        item=item, item_el=item_el,
        version=version, version_el=version_el,
        summary=summary, summary_el=summary_el,
        type=type, type_el=type_el,
        reviewer=reviewer, reviewer_el=reviewer_el,
        dtreviewed=dtreviewed, dtreviewed_el=dtreviewed_el,
        rating=rating,
        tags=tags,
        permalink=permalink, permalink_el=permalink_el,
        license=license, license_el=license_el,
        description=description, description_el=description_el)

def parse_hcard(el, log=dummy):
    """
    Parse an hCard element.
    """
    # @@: I don't feel like doing this now!
    return el

def parse_item(el, log=dummy):
    urls = [
        URL(url_el.attrib['href'], url_el)
        for url_el in get_elements_by_class(el, 'url')]
    photos = [
        Photo(photo_el.attrib['src'], photo_el)
        for photo_el in get_elements_by_class(el, 'photo')]
    fn, fn_el = get_single_item(el, 'fn', log=log)
    fn = strip_tags(fn)
    item = Item(fn=fn,
                fn_el=fn_el,
                el=el,
                urls=urls,
                photos=photos)
    return item

def get_tags(el, log=dummy):
    return filter_none([
        parse_tag(tag_el, log=log)
        for tag_el in get_rel_links(el, 'tag')])

def parse_tag(el, log=dummy):
    if not el.attrib.get('href'):
        log.warn(
            "Bad tag link (no href): %s"
            % tostring(el))
    url = el.attrib['href']
    rating = None
    try:
        rating_el = get_single_el(el, 'rating', log=log)
    except ElementNotFound:
        try:
            rating_el = get_parent_with_class(el, 'rating', log=log)
        except ElementNotFound:
            rating_el = None
    if rating_el is not None:
        rating = parse_rating(rating_el)
    return Tag(el=el, url=url, rating=rating)

def get_plain_rating_item(el, log=dummy):
    """
    Returns any rating that doesn't have a tag child or tag parent.
    Raises `ElementNotFound` if none found, or couldn't parse any.
    """
    results = []
    for rating_el in get_elements_by_class(el, 'rating'):
        # First see if there's a contained rating...
        if get_rel_links(rating_el, 'tag'):
            continue
        parent = rating_el
        while parent:
            # Check if the object is a tag
            if parent.tag == 'a' and parent.attrib.get('rel') == 'tag':
                break
            parent = parent.getparent()
        if not parent:
            # Nothing found
            results.append(rating_el)
    if not results:
        raise ElementNotFound()
    if len(results) > 1:
        log.warn(
            "Multiple ratings found with no related tags: %s"
            % ", ".join(map(tostring, results)))
    for el in results:
        rating = parse_rating(rating_el)
        if rating is not None:
            return rating
    raise ElementNotFound("Could not parse rating")

def parse_rating(el, log=dummy):
    """
    Parses a rating element, that may have a ``class="value"``,
    ``class="best"``, ``class="worst"``, or may just have a ``title``
    that contains a singular rating.
    """
    try:
        value, value_el = get_single_item(el, 'value', log=log)
    except ElementNotFound:
        value = None
        if el.attrib.get('title'):
            try:
                value = float(el.attrib['title'])
            except ValueError:
                log.warn(
                    "Cannot convert rating title to number: %r"
                    % el.attrib['title'])
        else:
            value = get_contents(el)
    value = parse_float(value, default=None, log=log)
    if value is None:
        return None
    try:
        best, best_el = get_single_item(el, 'best', log=log)
    except ElementNotFound:
        best = None
    else:
        best = parse_float(best, default=None, log=log)
    try:
        worst, worst_el = get_single_item(el, 'worst', log=log)
    except ElementNotFound:
        worst = None
    else:
        worst = parse_float(best, default=None, log=log)
    return Rating(value, best=best, worst=worst, el=el)
    
############################################################
## Value parsing
############################################################

def parse_float(text, name='value', default=NoDefault, log=dummy):
    """
    Parse text to a float value.  Use name in log message.  If
    default is not given, can raise ValueError.
    """
    if text is None:
        if default is not NoDefault:
            log.info('Got None for text; expected number')
            return default
        raise TypeError(
            "Value expected (got None)")
    try:
        return float(text)
    except ValueError:
        log.warn(
            "Cannot convert %s to number: %r"
            % (name, text))
        if default is not NoDefault:
            return default
        raise

def parse_date(text, log=dummy):
    if re.search(r'^200\d\d\d$', text):
        # YYYYMM form:
        text += '01'
        ambiguous_day = True
    else:
        ambiguous_day = False
    try:
        value = dateutil_parse(text)
    except ValueError:
        try:
            value = dateutil_parse(text, fuzzy=True)
            log.info(
                "Date contains extra characters: %r" % text)
        except ValueError:
            log.warn(
                "Date cannot be parsed: %r" % text)
            return None
    if ambiguous_day:
        value = YearMonthDate.from_date(value)
    return value
    
class YearMonthDate(datetime.date):
    ambiguous_day = True
    def __new__(cls, year, month, day=None):
        if day is None:
            day = 1
        return datetime.date.__new__(cls, year, month, day)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.year, self.month)
    
    @classmethod
    def from_date(cls, date):
        return cls(date.year, date.month, date.day)
