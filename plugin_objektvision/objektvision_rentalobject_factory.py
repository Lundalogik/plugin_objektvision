import lime_query as lq
import base64 as b64


def get_rentalobject(app, idrentalobject):
    ro = lq.execute_query(rentalobject_query(idrentalobject),
                          app.connection,
                          app.limetypes,
                          app.acl,
                          app.user)

    pictures = lq.execute_query(
                        middlepicture_query(idrentalobject),
                        app.connection,
                        app.limetypes,
                        app.acl,
                        app.user)

    documents = lq.execute_query(
                        document_query(idrentalobject),
                        app.connection,
                        app.limetypes,
                        app.acl,
                        app.user)

    ro['objects'][0]['pictures'] = fetch_pictures_and_metadata(
                                                        pictures['objects'],
                                                        app)
    ro['objects'][0]['documents'] = fetch_documents_and_metadata(
                                                        documents['objects'],
                                                        app)
    if ro['objects'][0]['coworker']['id'] is not None:
        ro['objects'][0]['coworker']['picture'] = fetch_contact_image(
                                            ro['objects'][0]['coworker'],
                                            app)

    return ro


def rentalobject_query(idrentalobject):
    return {
        'limetype': 'rentalobject',
        'responseFormat': {
            'object': {
                'id': None,
                'property': {
                    'id': None,
                    'name': None
                },
                'streetaddress': None,
                'zipcode': None,
                'postalcity': None,
                'municipality': {
                    'code': None
                },
                'area': {
                    'mainarea': None
                },
                'coworker': {
                    'id': None,
                    'name': None,
                    'email': None,
                    'phone': None,
                    'cellphone': None,
                    'picture': None,
                    'region': {
                        'id': None,
                        'ovusername': None,
                        'ovpassword': None
                    }
                },
                'ingress': None,
                'floor': None,
                'fromdate': None,
                'floorplan': None,
                'localdescription': None,
                'premisestypes': None,
                'area_from': None,
                'area_to': None,
                'environment': None,
                'communication': None,
                'parking': None,
                'service': None,
                'other': None,
                'built': None,
                'objektvisionserverid': None
            }
        },
        'filter': {
            'op': 'AND',
            'exp': [
                {
                    'key': '_id',
                    'op': '=',
                    'exp': idrentalobject
                }
            ]
        }
    }


def middlepicture_query(idrentalobject):
    return {
        'limetype': 'middle_picture',
        'responseFormat': {
            'object': {
                'id': None,
                'picturename': None,
                'picturetype': None,
                'comment': None,
                'pictures': None,
                'publishon': None,
                'published_to_ov': None
            }
        },
        'orderby': [
            {'order': 'ASC'}
        ],
        'filter': {
            'op': 'AND',
            'exp': [
                {
                    'key': 'rentalobject',
                    'op': '=',
                    'exp': idrentalobject
                },
                {
                    'key': 'publishon',
                    'op': '!',
                    'exp': ''
                }
            ]
        }
    }


def document_query(idrentalobject):
    return {
        'limetype': 'document',
        'responseFormat': {
            'object': {
                'id': None,
                'comment': None,
                'type': None,
                'publishon': None
            }
        },
        'filter': {
            'op': 'AND',
            'exp': [
                {
                    'key': 'rentalobject',
                    'op': '=',
                    'exp': idrentalobject
                },
                {
                    'key': 'publishon',
                    'op': '!',
                    'exp': ''
                }
            ]
        }
    }


def fetch_pictures_and_metadata(middle_pictures, app):
    pictures = []
    for pic in middle_pictures:
        picture = {}
        lime_pictures = app.limetypes.pictures.get(pic['pictures'])
        picture_file = lime_pictures.properties.picture.fetch()
        stream = picture_file.stream
        stream.seek(0)
        b64file = b64.b64encode(stream.read())
        picture['fileextension'] = picture_file.extension
        picture['content'] = b64file.decode('utf-8')
        picture['description'] = pic['comment']
        picture['mp_id'] = pic['id']
        picture['id'] = pic['pictures']
        picture['category'] = pic['picturetype']
        picture['publishon'] = pic['publishon']
        picture['published_to_ov'] = pic['published_to_ov']
        pictures.append(picture)

    return pictures


def fetch_documents_and_metadata(docs, app):
    documents = []
    for doc in docs:
        document = {}
        lime_documents = app.limetypes.document.get(doc['id'])
        document_file = lime_documents.properties.document.fetch()
        stream = document_file.stream
        stream.seek(0)
        b64file = b64.b64encode(stream.read())
        document['fileextension'] = document_file.extension
        document['content'] = b64file.decode('utf-8')
        document['description'] = doc['comment']
        document['id'] = doc['id']
        document['publishon'] = doc['publishon']
        documents.append(document)

    return documents


def fetch_contact_image(coworker, app):
    image = {}
    lime_coworker = app.limetypes.coworker.get(coworker['id'])
    image_file = lime_coworker.properties.picture.fetch()
    stream = image_file.stream
    stream.seek(0)
    b64file = b64.b64encode(stream.read())
    content = b64file.decode('utf-8')

    image['description'] = 'testar'
    image['content'] = content
    image['clientid'] = lime_coworker.properties.name.value.replace(' ', '.') \
        + '.' + image_file.extension

    return image
