from zope import component

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer 

SiteLayer = layer.PloneSite

class StickyStatusMessagesLayer(SiteLayer):

    @classmethod
    def setUp(cls):
        """ Set up the additional products required for the 
            DubletteFinder.
        """
        PRODUCTS = [
                'slc.stickystatusmessages',
                ]
        ptc.setupPloneSite(products=PRODUCTS)

        fiveconfigure.debug_mode = True
        import slc.stickystatusmessages
        zcml.load_config('configure.zcml', slc.stickystatusmessages)
        fiveconfigure.debug_mode = False
        
        component.provideAdapter(instanceSchemaFactory)
        SiteLayer.setUp()
    

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = StickyStatusMessagesLayer 

