import logging
import zeep
from zeep import Client
from zeep.plugins import HistoryPlugin
import flask
import datetime
from lime_type.unit_of_work import create_unit_of_work
import sys
import lime_config as lc
import plugin_objektvision.objektvision_rentalobject_factory as rof
import plugin_objektvision.objektvision_estate_factory as ef

logger = logging.getLogger(__name__)

wsdl = lc.config['plugins']['plugin_objektvision'].get('wsdl')
vendorkey = lc.config['plugins']['plugin_objektvision'].get('vendorkey')


def publish_to_ov(idrentalobject, application, public):
    ###############################################
    history = HistoryPlugin()

    client = Client(wsdl=wsdl, plugins=[history])
    rentalobject = rof.get_rentalobject(application, idrentalobject)
    estate = ef.get_estate(client, rentalobject, public)
    client.service.Login(vendorkey, 15162, "lundalogik")
    # for attachment in estate['Attachments']:
    #     print(attachment['ClientID'])
    #     print(attachment['Description'])
    #     print(attachment['Category'])

    response = client.service.Update(estate)
    print('--------------------------')
    print(history.last_sent)
    print('--------------------------')
    print(history.last_received)
    print('--------------------------')
    print(response)
    print('--------------------------')
    # return response
    ###############################################
    if response.Success:
        try:
            ro = application.limetypes.rentalobject.get(idrentalobject)
            ro.properties.published_objektvision.value = True
            ro.properties.date_obj.value = datetime.datetime.now()
            ro.properties.objektvisionserverid.value = response.ServerID
            uow = application.unit_of_work()
            uow.add(ro)
            uow.commit()
            return {'result': response.ServerID}
        except Exception:
            e = sys.exc_info()[0]
            print(e)
            return {'result': 'Something went wrong when updating the \
                    rentalobject in lime'}
    else:
        return flask.Response(response.Message, 500)


def remove_from_ov(idrentalobject, application):
    ro = application.limetypes.rentalobject.get(idrentalobject)

    client = zeep.Client(wsdl=wsdl)

    client.service.Login(vendorkey, 15162, "lundalogik")
    response = client.service.DeleteByServerID(
                    str(ro.properties.objektvisionserverid.value))

    if response:
        try:
            ro.properties.published_objektvision.value = False
            ro.properties.date_obj.value = None
            ro.properties.removedobjektvision.value = datetime.datetime.now()
            ro.properties.objektvisionserverid.value = None
            uow = create_unit_of_work(application)
            uow.add(ro)
            uow.commit()
            return {'result': response}
        except Exception:
            e = sys.exc_info()[0]
            print(e)
    else:
        return flask.Response(response, 500)


def get_leads_from_ov(application):
    client = zeep.Client(wsdl=wsdl)

    client.service.Login(vendorkey, 15162, "lundalogik")
    response = client.service.GetLeads()
    # import ipdb;ipdb.set_trace()
    if response is not None:
        uow = create_unit_of_work(application)
        for resp in response:
            # print(resp)
            # print(resp.ClientID)
            ro = application.limetypes.rentalobject.get(int(resp.ClientID))
            lead = application.limetypes.objectneed(
                responsablename=resp.ProspectFullName)
            lead.properties.rentalobject.attach(ro)
            uow.add(ro)
            uow.add(lead)
        uow.commit()