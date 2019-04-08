import logging
from zeep import Client
import flask
import sys
import lime_config as lc
import plugin_objektvision.objektvision_rentalobject_factory as rof
import plugin_objektvision.objektvision_estate_factory as ef
import plugin_objektvision.objektvision_helper as oh

logger = logging.getLogger(__name__)

wsdl = lc.config['plugins']['plugin_objektvision'].get('wsdl')
vendorkey = lc.config['plugins']['plugin_objektvision'].get('vendorkey')


def publish_to_ov(idrentalobject, application, public):
    client = Client(wsdl=wsdl)
    rentalobject = rof.get_rentalobject(application, idrentalobject)

    valid_response = oh.validate_rentalobject(rentalobject)
    if not valid_response['valid']:
        return flask.Response(valid_response['errormessage'], 400)
    userid = rentalobject['objects'][0]['coworker']['region']['ovusername']
    password = rentalobject['objects'][0]['coworker']['region']['ovpassword']
    estate = ef.get_estate(client, rentalobject, public)
    client.service.Login(vendorkey, userid, password)

    response = client.service.Update(estate)

    if response.Success:
        try:
            oh.update_lime_objects(rentalobject,
                                   application,
                                   public,
                                   True,
                                   response.ServerID)
            return {'result': response.ServerID}
        except Exception:
            e = sys.exc_info()[0]
            logger.error('Something went wrong when updating Lime, \
                errormessage: ' + str(e))
            return {'result': 'Something went wrong when updating the \
                rentalobject in lime'}
    else:
        return flask.Response(response.Message, 500)


def remove_from_ov(idrentalobject, application):
    client = Client(wsdl=wsdl)
    rentalobject = rof.get_rentalobject(application, idrentalobject)
    userid = rentalobject['objects'][0]['coworker']['region']['ovusername']
    password = rentalobject['objects'][0]['coworker']['region']['ovpassword']

    client.service.Login(vendorkey, userid, password)
    response = client.service.DeleteByServerID(
                    str(rentalobject['objects'][0]['objektvisionserverid']))
    if response:
        try:
            oh.update_lime_objects(rentalobject,
                                   application,
                                   False,
                                   False)
            return {'result': response}
        except Exception:
            e = sys.exc_info()[0]
            logger.error('Something went wrong when updating Lime, \
                errormessage: ' + str(e))
            return {'result': 'Something went wrong when updating the \
                rentalobject in lime'}
    else:
        return flask.Response(response, 500)


def get_leads_from_ov(userid, password, application):
    client = Client(wsdl=wsdl)

    client.service.Login(vendorkey, userid, password)
    response = client.service.GetLeads()
    if response is not None:
        try:
            oh.create_leads_in_lime(response, application)
        except Exception:
            e = sys.exc_info()[0]
            logger.error('Something went wrong when fetchin leads, \
                errormessage: ' + str(e))
