from sanic.response import json
from sanic import Blueprint

import requests

from html.parser import HTMLParser
from bs4 import BeautifulSoup

from io import BytesIO

from PIL import Image

from base64 import b64encode, standard_b64encode

v1 = Blueprint('v1')

@v1.route('/v1')
async def get_article(request):
    article_url = request.args.get('a',None)
    if not article_url:
        return json({'status':'error', 'message':'missing article'})
    else:
        req = requests.get(article_url)

        soup = BeautifulSoup(req.text, 'html.parser')

        info = {
            'url':article_url,
            'extra':{},
            'authors':[]
        }

        authorOne = None
        authorTwo = None
        authorThree = None

        for meta in soup.find_all('meta'):
            type = meta.get('name', None)
            if type == None:
                type = meta.get('property')

            # HTML standards
            if type=="title":info['title']=meta.get('content','_')
            if type=="og:title":info['title']=meta.get('content','_')
            if type=="twitter:title":info['title']=meta.get('content','_')

            if type=="description":info['description']=meta.get('content','_')
            if type=="og:description":info['description']=meta.get('content','_')
            if type=="twitter:description":info['description']=meta.get('content','_')

            if type=="image":info['image_url']=meta.get('content','_')
            if type=="og:image":info['image_url']=meta.get('content','_')
            if type=="twitter:image":info['image_url']=meta.get('content','_')

            # Article specific
            if type=="author":info['author']=meta.get('content','_')

            if type=="article:kicker":info['extra']['kicker']=meta.get('content','_')
            if type=="topo:kicker":info['extra']['kicker']=meta.get('content','_')

            # TOPO specific
            if type=="article:author:1:image":
                if not authorOne:
                    authorOne = {}
                authorOne['image']= image_url_to_data_url(meta.get('content','_'))
            if type=="article:author:1:name":
                if not authorOne:
                    authorOne = {}
                authorOne['name']= meta.get('content','_')
            if type=="article:author:2:image":
                if not authorTwo:
                    authorTwo = {}
                authorTwo['image']= image_url_to_data_url(meta.get('content','_'))
            if type=="article:author:2:name":
                if not authorTwo:
                    authorTwo = {}
                authorTwo['name']= meta.get('content','_')
            if type=="article:author:3:image":
                if not authorThree:
                    authorThree = {}
                authorThree['image']= image_url_to_data_url(meta.get('content','_'))
            if type=="article:author:3:name":
                if not authorThree:
                    authorThree = {}
                authorThree['name']= meta.get('content','_')


        if authorOne: info['authors'].append(authorOne)
        if authorTwo: info['authors'].append(authorTwo)
        if authorThree: info['authors'].append(authorThree)

        # image as data
        if info.get('image_url') :
            im_url = info.get('image_url')
            info['image_data'] = image_url_to_data_url(im_url)

        return json({
            'status':'ok',
            'data': info
        })


def image_url_to_data_url(image_url):
    im_req = requests.get(image_url)
    img = Image.open(BytesIO(im_req.content))
    output = BytesIO()
    img.save(output, format='PNG')
    hex_data = output.getvalue()
    return "data:image/png;base64,"+str(standard_b64encode(hex_data), 'utf-8')
