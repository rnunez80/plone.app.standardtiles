from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.component import getUtility 

from zope import schema
from plone.directives import form as directivesform
from plone.directives import dexterity

from plone.tiles import Tile, PersistentTile
from plone.tiles.interfaces import ITile

from zope.interface import Interface
from zope.component import getMultiAdapter

from five import grok
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager

from zope.browser.interfaces import IBrowserView
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.tiles import Tile
from z3c.form import field

from plone.dexterity.interfaces import IDexterityContent

from plone.dexterity.utils import iterSchemata
from plone.dexterity.interfaces import IDexterityContent

import re
from Products.CMFPlone.utils import log


class TitleTile(Tile):
    """A tile for the content title
    """

    _possible_attributes = ('title', 'Title')
    # BBB: refactor, this needs to be a proper template
    _template = u'<html><body><h1 class="documentFirstHeading">%s</h1></body></html>'
    _default_value = u'Insert the content title here'

    def retrieve_value(self):
        value = None
        for attr_name in self._possible_attributes:
            if hasattr(self.context, attr_name):
                value = getattr(self.context, attr_name)
                if callable(value):
                    value = value()
        return value

    def __call__(self):
        if 'ignore_context' in self.data and self.data['ignore_context'].lower() == 'true':
            value = self._default_value 
        else:
            value = self.retrieve_value()
        return self._template % value

class DescriptionTile(TitleTile):
    """A tile for the content description
    """

    _possible_attributes = ('description', 'Description')
    _template = u'<html><body><div class="documentDescription">%s</div></body></html>'
    _default_value = u'Insert the content description here'

class PonyTile(Tile):
    """A silly transient tile that outputs an ASCII pony.
    """

    def __call__(self):
        return "<html><body><pre>\n        .,,.\n     ,;;*;;;;,\n    .-'``;-');;.\n   /'  .-.  /*;;\n .'    \d    \;;               .;;;,\n/ o      `    \;    ,__.     ,;*;;;*;,\n\__, _.__,'   \_.-') __)--.;;;;;*;;;;,\n `\"\"`;;;\       /-')_) __)  `\' ';;;;;;\n    ;*;;;        -') `)_)  |\ |  ;;;;*;\n    ;;;;|        `---`    O | | ;;*;;;\n    *;*;\|                 O  / ;;;;;*\n   ;;;;;/|    .-------\      / ;*;;;;;\n  ;;;*;/ \    |        '.   (`. ;;;*;;;\n  ;;;;;'. ;   |          )   \ | ;;;;;;\n  ,;*;;;;\/   |.        /   /` | ';;;*;\n   ;;;;;;/    |/       /   /__/   ';;;\n   '*jgs/     |       /    |      ;*;\n        `\"\"\"\"`        `\"\"\"\"`     ;'\n</pre></body></html>"


class HelloWorldTile(Tile):
    """A simple tile that outputs the text "Hello World".
    """
    
    def __call__(self):
        return "<html><body>Hello World</body></html>"


class IHelloNameTile(Interface):
    name = schema.TextLine(title=u"Name of the person to greet.",
                           required=True)

class HelloNameTile(Tile):
    """A tile that greets someone.
    """
    
    def __call__(self):
        return "<html><body>Hello %s!</body></html>" % self.data.get('name')
    

class IYoutubeTile(directivesform.Schema):
    
    youtubeURL = schema.TextLine(title=u"Youtube URL", required=True)
    


class YoutubeTile(PersistentTile):
    """A tile that displays a youtube movie. Purely as a proof of concept and to showcase possibilities of Deco
    """
    
    def __call__(self):
        youtubeURL = self.data.get('youtubeURL')
        
        youtubeID = re.split('v=([A-Za-z00-9_\-]+)', youtubeURL)[1]
        
        # Not for production use - this should be in a template!
        return '<object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/%s&hl=en_GB&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%s&hl=en_GB&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>' % (youtubeID, youtubeID)



class IViewletManagerTile(Interface):
    manager = schema.TextLine(title=u"Name of the viewlet manager to render.",
                           required=True)


class ViewletManagerTile(Tile):
    """A tile that renders a viewlet manager."""

    implements(IViewletManagerTile)

    def __call__(self):
        """Return the rendered contents of the viewlet manager specified."""
        manager = self.data.get('manager')
        managerObj = queryMultiAdapter((self.context, self.request, self), IViewletManager, manager)
        managerObj.update()
        return "<html><body>%s</body></html>" % managerObj.render()


class IPortletManagerTile(Interface):
    manager = schema.TextLine(title=u"Name of the portlet manager to render.",
                           required=True)


class PortletManagerTile(Tile):
    """A tile that renders a portlet manager."""

    implements(IPortletManagerTile)

    def __call__(self):
        """Return the rendered contents of the portlet manager specified."""
        manager = self.data.get('manager')
        managerObj = getUtility(IPortletManager, name=manager)
        rendererObj = managerObj(self.context, self.request, self)
        rendererObj.update()
        return "<html><body>%s</body></html>" % rendererObj.render()