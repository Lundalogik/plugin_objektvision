import lime_webserver.webserver as webserver
import logging
import webargs.fields as fields
from webargs.flaskparser import use_args
from ..endpoints import api
import plugin_objektvision.objektvision as o
import json

logger = logging.getLogger(__name__)


class PublishRentalobject(webserver.LimeResource):
    """Summarize your resource's functionality here"""
    args = {
        "rentalobjectid": fields.String(required=True)
    }

    @use_args(args)
    def get(self, args):
        """Get the current number of objects of the given type in the system.
        """
        response = o.publish_to_ov(args['rentalobjectid'],
                                   self.application,
                                   True)
        return json.dumps(response)


class RemoveRentalobject(webserver.LimeResource):
    """Summarize your resource's functionality here"""
    args = {
        "rentalobjectid": fields.String(required=True)
    }

    @use_args(args)
    def get(self, args):
        """Get the current number of objects of the given type in the system.
        """

        response = o.remove_from_ov(args['rentalobjectid'])
        return response


class GetLeads(webserver.LimeResource):
    """Summarize your resource's functionality here"""
    args = {
        "rentalobjectid": fields.String(required=True)
        }

    def get(self, args):
        """Get the current number of objects of the given type in the system.
        """

        # response = oe.get_leads_from_ov()
        response = o.get_rentalobject(self.application, args['rentalobjectid'])
        return response


api.add_resource(PublishRentalobject, '/publishro/')
api.add_resource(RemoveRentalobject, '/removero/')
api.add_resource(GetLeads, '/getleads/')