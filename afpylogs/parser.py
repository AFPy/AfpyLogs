from __future__ import unicode_literals
import re
import codecs
from collections import namedtuple
from datetime import time
from cgi import escape

IRCLine = namedtuple('IRCLine', ['timestamp', 'nick', 'message'])

# Auto-linkification
_re_link = re.compile(r'.*(https?://\S+).*') # detect URLs
_tpl_link = '<a href="{link}" rel="nofollow">{link}</a>' # Template used to render them

# IRSSI log format
_re_line = re.compile(r'''^
(?P<hour>\d{2}):(?P<minute>\d{2})\s+
((<(?P<nick>[^>]+)>)|(\[\#\]))\s+
(?P<message>.*)
$
''', re.VERBOSE)


_tpl_action_message = '<span class="action">[#] {message}</span>'
_tpl_normal_message = (
    '<span class="barket">&lt;</span>'
    '<span class="nick">{nick}</span>'
    '<span class="barket">&gt;</span>'
    ' {message}'
)
_tpl_line = (
    '<div>'
    '<a id="{line_number}" href="#{line_number}">{timestamp:%H}:{timestamp:%M}</a>'
    ' {message}'
    '</div>'
)

def get_lines(path, encoding='utf-8'):
    """Yield IRCLine tuples from the given path to an irssi log file.
    Lines beginning with '---' will be omitted.
    All lines are stripped from whitespace before being returned."""
    with codecs.open(path, encoding=encoding) as f:
        for line in f:
            if line.startswith('---'):
                continue
            try:
                yield parse_line(line.strip())
            except ValueError:
                continue # TODO: log failure?

def linkify(message):
    """Make <a> tags for URLs in the given message. Return the HTML."""
    for link in set(_re_link.findall(message)):
        message = message.replace(link, _tpl_link.format(link=link))
    return message

def render_line(**context):
    """Render a line to HTML.
    Depending on whether the message is a normal or an "action" one, use
    a different template."""
    message_tpl = _tpl_normal_message if context['nick'] else _tpl_action_message
    context['message'] = message_tpl.format(**context)
    return _tpl_line.format(**context)

def parse_line(line):
    """Parse a line from the log and return an IRCLine tuple."""
    match = _re_line.search(line)
    if not match:
        raise ValueError('Unhandled line %r' % line)
    data = match.groupdict()
    data['timestamp'] = time(hour=int(data.pop('hour')), minute=int(data.pop('minute')))
    return IRCLine(**data)

def parse(channel, path, encoding='utf-8'):
    """Turn an irssi log line into HTML, URLs are converted to <a>.
    
    Normal lines look like this:
    09:42 < bmispelon> this is the message
    
    Some lines are "action" ones (usually, the result of a "/me ... command")
    and look like this:
    09:42 [#] this is the message
    """
    stdout = []
    for i, line_tuple in enumerate(get_lines(path, encoding), start=1):
        message = linkify(escape(line_tuple.message))
        line_tuple = line_tuple._replace(message=message)
        stdout.append(render_line(
            line_number=i,
            **line_tuple._asdict()
        ))
    return '\n'.join(stdout)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
