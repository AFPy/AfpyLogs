import datetime
import os
from operator import itemgetter
from collections import defaultdict
import codecs

from webob import Request, Response
from webob.exc import HTTPFound
from paste.fileapp import FileApp
from paste.deploy.config import ConfigMiddleware
from paste.deploy.config import CONFIG

from afpylogs.parser import parse
from afpylogs.utils import get_stylesheets, get_header

dirname = os.path.dirname(os.path.abspath(__file__))

def path_from_here(*args):
    return os.path.join(dirname, *args)

MONTH_TPL = u"""
<dt class="portletHeader {active}"><a href="#">{date:%Y %m}</a></dt>
<dd class="portletItem">{rendered_days}</dd>
"""
DAY_TPL = u'<a class="{active}" href="/archives/{date:%Y/%m/%d}/">{date:%d}</a> '

def render_archives(archives, active):
    """Given an archive dict, return the corresponding HTML."""
    rendered = ['<dl class="portlet">']
    for year, months in sorted(archives.items(), key=itemgetter(0),
                               reverse=True):
        for month, days in sorted(months.items(), key=itemgetter(0),
                                  reverse=True):
            is_active_month = (active.year, active.month) == (year, month)
            rendered.append(MONTH_TPL.format(
                active='active' if is_active_month else '',
                date=datetime.date(year, month, 1), # first day of the current month
                rendered_days=render_days(year, month, days, active)
            ))

    rendered.append('</dl>')
    return u'\n'.join(rendered)

def render_days(year, month, days, active):
    """Return the HTML corresponding to all the available days of a given month."""
    rendered = []
    for day in sorted(days):
        current_date = datetime.date(year, month, day)
        is_active_day = active == current_date
        rendered.append(DAY_TPL.format(
            date=current_date,
            active='active' if is_active_day else '',
        ))
    
    return u'\n'.join(rendered)

def get_archives(path, active):
    """Return HTML with links corresponding to all available days.
    The list is reversed chronologically, with most recent days appearing at
    the top."""
    archives = defaultdict(lambda: defaultdict(list))
    for filename in os.listdir(path):
        if not filename.endswith('.txt'):
            continue
        _, year, month, day = filename.replace('.txt','').split('-')
        archives[int(year)][int(month)].append(int(day))

    return render_archives(archives, active)

def serve_static(filepath):
    return FileApp(filepath)

def r404(environ, start_response, text=u"File not found"):
    resp = Response(status=404, text=text)
    return resp(environ, start_response)

def redirect(environ, start_response, location):
    resp = HTTPFound(location=location)
    return resp(environ, start_response)

def application(environ, start_response):
    logfile_encoding = CONFIG.get('charset', 'utf-8') # XXX: actually depends on the date (see below)
    response_encoding = 'utf-8'
    template_encoding = 'utf-8'
    STATIC = ['jquery.js', 'transcript.js']
    template = CONFIG.get('template', path_from_here('template.html'))
    channel = CONFIG.get('channel', '')
    path = CONFIG.get('path', '')
    
    path_info = Request(environ).path_info[1:] # remove leading /

    if path_info in STATIC:
        app = serve_static(path_from_here(path_info))
        return app(environ, start_response)
    
    if not path_info:
        date = datetime.date.today()
        location = 'archives/{:%Y/%m/%d/}'.format(date)
        return redirect(environ, start_response, location)
    else:
        try:
            date = datetime.datetime.strptime(path_info, 'archives/%Y/%m/%d/').date()
        except ValueError:
            return r404(environ, start_response)

    # XXX: logfiles changed encoding at some point
    if date <= datetime.date(2011, 6, 5):
        logfile_encoding = 'latin1'
    
    filename = 'log-{:%Y-%m-%d}.txt'.format(date)
    filepath = os.path.join(path, filename)

    if not os.path.isfile(filepath):
        return r404(environ, start_response)

    output = parse('#%s' % channel, filepath, logfile_encoding)
    archives = get_archives(path, active=date)
    with codecs.open(template, encoding=template_encoding) as fd:
        tpl = fd.read()
    
    body = tpl % {
        'channel': channel,
        'body': output,
        'archives': archives,
        'stylesheets': get_stylesheets(),
        'header': get_header(),
        'date': date.strftime('%Y/%m/%d'),
    }

    resp = Response(
        content_type="text/html",
        charset=response_encoding,
    )
    resp.text = body

    return resp(environ, start_response)

def factory(global_config, **local_config):
    """Aplication factory to expand configs"""
    conf = global_config.copy()
    conf.update(**local_config)
    return ConfigMiddleware(application, conf)
