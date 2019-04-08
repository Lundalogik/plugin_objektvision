import datetime


def get_estate(client, rentalobject, public):
    properties = rentalobject['objects'][0]
    factory = client.type_factory('ns0')

    attachmentlist = get_attachment_list(properties, client, factory)
    return factory.Estate(
        ClientID=properties['id'],
        DisplayedClientID=198000005,
        Modified=datetime.datetime.now(),
        Contact=get_contact(properties, client, factory),
        InternetDisplay=get_internetdisplay_array(properties,
                                                  client,
                                                  factory,
                                                  public),
        Address=get_address(properties, client, factory),
        Attachments=factory.ArrayOfAbstractAttachment(attachmentlist))


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


def get_attachment_list(rentalobject, client, factory):
    attachment_list = []
    for picture in rentalobject['pictures']:
        if picture['published_to_ov'] == 0:
            content = factory.AttachmentBase64Content(
                Base64EncodedContent=picture['content'])
        else:
            content = factory.AttachmentKeepContent()
        categories = get_image_category(picture['category'])
        image = factory.AttachmentImage(
            Category=categories,
            ClientID='{}.{}'.format(picture['id'], picture['fileextension']),
            Description=picture['description'],
            Content=content)
        attachment_list.append(image)

    for document in rentalobject['documents']:
        if document['fileextension'] == 'pdf':
            content = factory.AttachmentBase64Content(
                Base64EncodedContent=document['content'])
            doc = factory.AttachmentFile(
                Type='PDF',
                ClientID='{}.{}'.format(document['id'],
                                        document['fileextension']),
                Description=document['description'],
                Content=content)
            attachment_list.append(doc)

    return attachment_list


def get_address(properties, client, factory):
    return factory.Address(
        StreetAddress=properties['streetaddress'],
        PostalCode=properties['zipcode'],
        City=properties['postalcity'],
        MunicipalityCode=properties['municipality']['code'])


def get_contact(properties, client, factory):
    if properties['coworker']['picture'] is None:
        contact = factory.Contact(
            Name=properties['coworker']['name'],
            Email=properties['coworker']['email'],
            Phone=properties['coworker']['phone'])
    else:
        contact_image_content = factory.AttachmentBase64Content(
            Base64EncodedContent=properties['coworker']['picture']['content'])
        contact_image = factory.ContactImage(
            Content=contact_image_content,
            ClientID=properties['coworker']['picture']['clientid'])
        contact = factory.Contact(
            Name=properties['coworker']['name'],
            Email=properties['coworker']['email'],
            Phone=properties['coworker']['phone'],
            Image=contact_image)

    return contact


def get_internetdisplay_array(properties, client, factory, public):
    leadFormMode = factory.LeadFormMode("Off")
    if public:
        displayMode = factory.DisplayMode("Public")
    else:
        displayMode = factory.DisplayMode("Private")

    premiseTypes = get_premise_type(properties['premisestypes'])
    surroundings = factory.CommercialSurroundings(
        Nature=properties['environment'],
        ParkingAndGarage=properties['parking'],
        ServiceInNeighbourhood=properties['service'],
        Transportation=properties['communication'])
    premise = factory.Premise(
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

    return factory.ArrayOfInternetDisplay([premise])
