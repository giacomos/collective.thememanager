import json
from urllib2 import urlopen

from zope import interface

from collective.thememanager import interfaces
from collective.thememanager import theme
from Products.CMFCore.utils import getToolByName

class Provider(object):
    """ Implements a theme provider.
    
    A theme provider have to publish a json file with al infos about
    provided themes.
    """
    interface.implements(interfaces.IThemeProvider)
    def __init__(self, url):
        self.themes = {}
        self.url = url
        self._initialized = False

    def getThemeIds(self):
        """Return a list of all theme ids provided"""
        if not self.themes:
            self._initialize()
        return self.themes.keys()

    def getThemeById(self, id):
        """Return the theme with id=id. If the theme doesn't exist it create
        a new one but doesn't create resources. You must use theme manager
        for that. If id is None return None"""
        if not self.themes:
            self._initialize()
        return self.themes.get(id, None)

    def getThemes(self):
        """Return a list of ITheme objects"""
        if not self.themes:
            self._initialize()
        return self.themes.values()

#TODO: memoize
    def _initialize(self):
        """ Initialize this themes provider by remote fetching its json
        file with all themes infos
        """
        if self._initialized:
            return

        download = urlopen(self.url)
        code = download.getcode()
    
        if code != 200:
            raise Exception, 'Cant download source list' % code
        if download.info().type != 'application/json':
            raise Exception, 'Is not json mimetype'
        content = download.read()
        themesinfos = json.loads(content)
        themeids = []

        for themeinfos in themesinfos:
            if themeinfos['zipurl'] in themeids:
                continue
            themeids.append(themeinfos['zipurl'])
            themeObj = theme.Theme(self, **themeinfos)
            self.themes[themeObj.zipurl] = themeObj
        self._initialized = True


from Products.Five import BrowserView

class ProviderController(BrowserView):
    """A view to create a json input to create a proxy provider"""

    #TODO: memoize
    def getThemes(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type = 'collective.thememanager.theme')
        objs = [brain.getObject() for brain in brains]
        def metadata(ob):
            url = ob.absolute_url()
            return {'title':ob.Title(),
                    'description':ob.Description(),
                    'picture':url+'/@@images/picture',
                    'url':url,
                    'zipurl':url+'/@@download/zip',
                    'author':ob.author,
                    'version':ob.version}
        metadatas = map(metadata, objs)
        return metadatas
