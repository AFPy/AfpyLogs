"""
We do it this way so that we can re-use the afpy stylesheets and navigation menu
that plone generates.
We use a global variable as the document as a poor man's cache.
"""
from pyquery import PyQuery


document = PyQuery(url='https://www.afpy.org')
# Remove some stuff we don't want
document('#portal-searchbox, #portal-personaltools-wrapper').remove()

def as_absolute(html):
    for attr in 'href', 'src':
        html = html.replace(f'{attr}="/', f'{attr}="https://afpy.org/')
    return html

def get_stylesheets():
    """
    All the stylesheets used in the <head>, as a string.
    """
    global document
    STYLESHEET_SELECTOR = 'head style, head link[@rel=stylesheet]'
    return as_absolute('\n'.join(str(elt) for elt in document(STYLESHEET_SELECTOR).items()))

def get_header():
    """
    The navigation menu as a string.
    """
    global document
    HEADER_SELECTOR = 'nav.menu'
    return as_absolute(str(document(HEADER_SELECTOR)))
