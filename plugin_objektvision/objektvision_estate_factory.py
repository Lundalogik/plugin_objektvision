import datetime


def get_estate(client, rentalobject, public):
    properties = rentalobject['objects'][0]

    estate_type = client.get_type('ns0:Estate')
    estate = estate_type(
        ClientID=properties['id'],
        DisplayedClientID=198000005,
        Modified=datetime.datetime.now(),
        Contact=get_contact(properties, client),
        InternetDisplay=get_internetdisplay_array(properties,
                                                  client,
                                                  public),
        Address=get_address(properties, client),
        Attachments=get_attachment_list(properties, client))

    return estate


def get_premise_type(premise_types_from_lime):
    premise_type_to_ov = []
    for type in premise_types_from_lime:
        if 'office' in type.lower():
            premise_type_to_ov.append('Office')
        elif 'shop' in type.lower():
            premise_type_to_ov.append('Shop')
        elif 'storage' in type.lower():
            premise_type_to_ov.append('Storage')
        elif 'industry' in type.lower():
            premise_type_to_ov.append('Industry')
        elif 'officehotel' in type.lower():
            premise_type_to_ov.append('Officehotel')
        elif 'other' in type.lower():
            premise_type_to_ov.append('Other')
        else:
            premise_type_to_ov.append('Other')

    return {'PremiseTypes': premise_type_to_ov}


def get_image_category(category):
    if 'interior' in category.lower():
        cat = 'Enterior'
    elif 'exterior' in category.lower():
        cat = 'Exterior'
    elif 'floorplan' in category.lower():
        cat = 'Plan'
    else:
        cat = 'Exterior'

    return cat


def get_attachment_list(rentalobject, client):
    image_type = client.get_type('ns0:AttachmentImage')
    file_type = client.get_type('ns0:AttachmentFile')
    b64_content_type = client.get_type('ns0:AttachmentBase64Content')
    keep_content_type = client.get_type('ns0:AttachmentKeepContent')
    attachment_list = []
    for picture in rentalobject['pictures']:
        if picture['published_to_ov'] == 0:
            content = b64_content_type(
                Base64EncodedContent=picture['content'])
        else:
            content = keep_content_type()
        categories = get_image_category(picture['category'])
        image = image_type(
            Category=categories,
            ClientID='{}.{}'.format(picture['id'], picture['fileextension']),
            Description=picture['description'],
            Content=content)
        attachment_list.append({'AbstractAttachment': image})

    for document in rentalobject['documents']:
        if document['fileextension'] == '.pdf':
            content = b64_content_type(
                Base64EncodedContent=document['content'])
            doc = file_type(
                Type={'Type': 'Undefined'},
                ClientID='{}.{}'.format(document['id'],
                                        document['fileextension']),
                Description=document['description'],
                Content=content)
            attachment_list.append({'AbstractAttachment': doc})

    return attachment_list


def get_address(properties, client):
    address_type = client.get_type('ns0:Address')

    return address_type(
            StreetAddress=properties['streetaddress'],
            PostalCode=properties['zipcode'],
            City=properties['postalcity'],
            MunicipalityCode=properties['municipality']['code'])


def get_contact(properties, client):
    contact_type = client.get_type('ns0:Contact')
    contact_image_type = client.get_type('ns0:ContactImage')
    b64_content_type = client.get_type('ns0:AttachmentBase64Content')

    if properties['coworker']['picture'] is None:
        contact = contact_type(
            Name=properties['coworker']['name'],
            Email=properties['coworker']['email'],
            CellPhone=properties['coworker']['cellphone'],
            Phone=properties['coworker']['phone'])
    else:
        contact_image_content = b64_content_type(
            Base64EncodedContent=properties['coworker']['picture']['content'])
        contact_image = contact_image_type(
            Content=contact_image_content,
            ClientID=properties['coworker']['picture']['clientid'])
        contact = contact_type(
            Name=properties['coworker']['name'],
            Email=properties['coworker']['email'],
            CellPhone=properties['coworker']['cellphone'],
            Phone=properties['coworker']['phone'],
            Image=contact_image)

    return contact


def get_internetdisplay_array(properties, client, public):
    premise_type = client.get_type('ns0:Premise')
    displayMode_type = client.get_type('ns0:DisplayMode')
    surrounding_type = client.get_type('ns0:CommercialSurroundings')
    internetDisplayArray_type = client.get_type('ns0:ArrayOfInternetDisplay')
    leadFormMode_type = client.get_type('ns0:LeadFormMode')
    leadFormMode = leadFormMode_type("Off")

    if public:
        displayMode = displayMode_type("Public")
    else:
        displayMode = displayMode_type("Private")

    premiseTypes = get_premise_type(properties['premisestypes'])
    surroundings = surrounding_type(
        Nature=properties['environment'],
        ParkingAndGarage=properties['parking'],
        ServiceInNeighbourhood=properties['service'],
        Transportation=properties['communication'])
    premise = premise_type(
        Types=premiseTypes,
        AdjustablePlan=False,
        SwapDemand=False,
        Status=displayMode,
        Description=properties['ingress'],
        ExtendedDescription=properties['localdescription'],
        Floor=properties['floor'] if properties['floor'] is not None else 0,
        Design=properties['floorplan'],
        BuildYear=properties['built'] if properties['built'] != '' else 0,
        OtherInfo=properties['other'],
        SurroundingInfo=surroundings,
        LeadFormSetting=leadFormMode,
        FloorsInBuilding=0,
        Rooms=0,
        RebuildYear=0)

    return internetDisplayArray_type([premise])
