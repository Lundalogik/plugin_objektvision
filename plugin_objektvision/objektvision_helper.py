import datetime
from lime_type.unit_of_work import create_unit_of_work
import lime_config as lc

baseurl = lc.config['plugins']['plugin_objektvision'].get('baseurl')


def validate_rentalobject(ro):
    error_string = ''
    valid = True
    if ro['objects'][0]['ingress'] is None:
        error_string += 'Kort lokalbeskrivning saknas\n'
    if ro['objects'][0]['localdescription'] is None:
        error_string += '"Beskrivning" saknas\n'
    if ro['objects'][0]['localdescription'] is None:
        error_string += '"Beskrivning" saknas\n'
    if ro['objects'][0]['area_from'] is None:
        error_string += '"Area från" saknas\n'
    if ro['objects'][0]['area_to'] is None:
        error_string += '"Area tom" saknas\n'
    # TODO Den här valideringen fungerar inte på set-fields
    if not ro['objects'][0]['premisestypes']:
        error_string += '"Objekttyper publicering" saknas\n'
    if ro['objects'][0]['streetaddress'] is None:
        error_string += '"Gatuadress" saknas\n'
    if ro['objects'][0]['zipcode'] is None:
        error_string += '"Postnummer" saknas\n'

    if ro['objects'][0]['property']['id'] is None:
        error_string += '"Fastighet" saknas\n'
    if ro['objects'][0]['municipality']['code'] is None:
        error_string += '"Kommun" saknas\n'
    if ro['objects'][0]['coworker']['id'] is None:
        error_string += '"Ansvarig uthyrare" saknas\n'
    if ro['objects'][0]['coworker']['email'] is None:
        error_string += 'Ansvarig uthyrare saknar "E-post"\n'
    if ro['objects'][0]['coworker']['phone'] is None:
        error_string += 'Ansvarig uthyrare saknar "Telefonnummer"\n'
    if ro['objects'][0]['coworker']['region']['id'] is None:
        error_string += 'Ansvarig uthyrare saknar kopplad "Region"\n'
    if ro['objects'][0]['coworker']['region']['ovusername'] is None:
        error_string += 'Ansvarig uthyrares region saknar ' + \
                            '"Objektvision användarnamn"\n'
    if ro['objects'][0]['coworker']['region']['ovpassword'] is None:
        error_string += 'Ansvarig uthyrares region saknar ' + \
                            '"Objektvision lösenord"\n'

    if error_string != '':
        valid = False
        error_string = 'Följande information saknas ' + \
            'för publicering till Objektvision: ' + error_string

    result = {'valid': valid,
              'errormessage': error_string}

    return result


def update_lime_objects(rentalobject, application, public, add, serverid=0):
    ro = application.limetypes.rentalobject.get(
                                            rentalobject['objects'][0]['id'])
    uow = application.unit_of_work()
    if add:
        ro.properties.objektvisionserverid.value = serverid
        ro.properties.publishedbyuser.value = \
            str(rentalobject['objects'][0]['coworker']['region']['ovusername'])
        ro.properties.publishedbypassword.value = \
            rentalobject['objects'][0]['coworker']['region']['ovpassword']
        if public:
            ro.properties.date_obj.value = datetime.datetime.now()
            ro.properties.published_objektvision.value = True
            ro.properties.objektvisionurl.value = baseurl + str(serverid)
            ro.properties.removedobjektvision.value = None
        else:
            ro.properties.date_obj.value = None
            if ro.properties.published_objektvision.value:
                ro.properties.removedobjektvision.value = \
                    datetime.datetime.now()
            ro.properties.published_objektvision.value = False
            ro.properties.objektvisionurl.value = baseurl + str(serverid) + \
                '?ShowInActive=True'
        uow.add(ro)
        for mp in rentalobject['objects'][0]['pictures']:
            middle_pic = application.limetypes.middle_picture.get(mp['mp_id'])
            middle_pic.properties.published_to_ov.value = True
            uow.add(middle_pic)
    else:
        ro.properties.published_objektvision.value = False
        ro.properties.date_obj.value = None
        ro.properties.removedobjektvision.value = datetime.datetime.now()
        ro.properties.objektvisionserverid.value = None
        ro.properties.publishedbyuser.value = ''
        ro.properties.publishedbypassword.value = ''
        ro.properties.objektvisionurl.value = ''
        uow.add(ro)
        for mp in rentalobject['objects'][0]['pictures']:
            middle_pic = application.limetypes.middle_picture.get(mp['mp_id'])
            middle_pic.properties.published_to_ov.value = False
            uow.add(middle_pic)

    uow.commit()


def create_leads_in_lime(leads, application):
    uow = create_unit_of_work(application)
    for lead in leads:
        ro = application.limetypes.rentalobject.get(int(lead.ClientID))
        lead = application.limetypes.lead(
            leadid=lead.LeadID,
            serverid=lead.ServerID,
            clientid=lead.ClientID,
            agentid=lead.AgentID,
            prospectfullname=lead.ProspectFullName.strip(),
            prospectcompany=lead.ProspectCompany.strip(),
            prospectemail=lead.ProspectEmail.strip(),
            prospectphone=lead.Phone.strip(),
            prospectaddress=lead.ProspectAddress.strip(),
            prospectcity=lead.ProspectCity.strip(),
            prospectzipcode=lead.ZipCode.strip(),
            errand=lead.Errand.strip(),
            message=lead.Message.strip())
        lead.properties.rentalobject.attach(ro)
        uow.add(ro)
        uow.add(lead)
    uow.commit()
