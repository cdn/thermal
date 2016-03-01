TOKEN = open('.token').readlines()[0].strip()
#POST = '10208075829630848_10208076327923305'
POST = '10208075829630848_10208083405100230'
LIMIT = 10
SKIP_INIT = False

from imageprinter import *

import requests, urllib
import time, os
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

#font_main = ImageFont.truetype('/home/lacop/.fonts/Helvetica.ttf', 20)
font_san_big = ImageFont.truetype('/home/lacop/.fonts/RobotoSlab-Bold.ttf', 36)
font_san_med = ImageFont.truetype('/home/lacop/.fonts/RobotoSlab-Regular.ttf', 32)
font_san_small = ImageFont.truetype('/home/lacop/.fonts/RobotoSlab-Thin.ttf', 20)
font_ser = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 32)

def fb_get(url):
    time.sleep(1) # Avoid getting rate-limited
    print('Fetching ' + url)
    return requests.get(url).json()
def fb_url(object, args):
    url = 'https://graph.facebook.com/v2.5/' + object
    args['access_token'] = TOKEN
    url += '?' + urllib.parse.urlencode(args)
    return url

def cached_resource(url, key):
    path = 'cache/' + key
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return f.read()
    res = requests.get(url)
    if res.status_code != 200:
        return None
    with open(path, 'wb') as f:
        f.write(res.content)
    return res.content

def get_user_picture(id):
    #pic = fb_get(fb_url(id + '/picture', {'type': 'large'}))
    #return cached_resource(pic['data']['url'], 'profile-' + id)
    return cached_resource(fb_url(id + '/picture', {'type': 'large'}), 'profile-' + id)

def render_thing(profilepic, name, desc, datetime=None, text=None, attachpic=None):
    #img = Image.new('L', (576, 2048), 255)
    img = Image.new('L', (576, 2000), 255)
    draw = ImageDraw.Draw(img)

    pic = Image.open(BytesIO(profilepic))
    pic.thumbnail((180, 180))
    img.paste(pic.convert('1'), (8, 8))

    draw.text((196+8, 8), name, font=font_san_big)
    draw.text((196+8, 50), desc, font=font_san_med)
    if datetime:
        draw.text((196+8, 150), datetime[:10] + ' at ' + datetime[11:19], font=font_san_med)

    yoff = 196+16
    if text:
        lines = textwrap.wrap(text, 42)
        for i in range(len(lines)):
            if i >= 5 and len(lines) > i+1:
                draw.text((8, yoff), lines[i][:35] + ' ...', font=font_ser)
                yoff += 32
                break
            else:
                draw.text((8, yoff), lines[i], font=font_ser)
            yoff += 32
    if attachpic:
        yoff += 24
        attpic = Image.open(BytesIO(attachpic))
        attpic.thumbnail((576-32, 576-32))
        try:
            img.paste(attpic.convert('1'), (576//2-attpic.size[0]//2, yoff), mask=attpic)
        except ValueError:
            img.paste(attpic.convert('1'), (576//2-attpic.size[0]//2, yoff))
        yoff += attpic.size[1]

    yoff += 24
    draw.line([(64, 1), (576-64, 1)], fill=0, width=1)
    queue_bitmap(img.crop((0, 0, 576, yoff+8)).rotate(180))
    #queue_bitmap(img.crop((0, 0, 576, yoff+8)))

def render_post(post):
    print('[POST]\t\tFrom: {} ({})'.format(post['from']['name'], post['from']['id']))
    pic_bytes = get_user_picture(post['from']['id'])
    print('\t\tTime: {}'.format(post['created_time']))
    print('\t\tMsg: {}'.format(post['message']))
    print(post)

    render_thing(pic_bytes, post['from']['name'], 'created a post.', post['created_time'], post['message'])

def render_comment(comment):
    print('[COMMENT]\tFrom: {} ({})'.format(comment['from']['name'], comment['from']['id']))
    pic_bytes = get_user_picture(comment['from']['id'])
    print('\t\tTime: {}'.format(comment['created_time']))
    print('\t\tMsg: {}'.format(comment['message']))
    attach_bytes = None
    if 'attachment' in comment:
        if comment['attachment']['type'] == 'sticker' or comment['attachment']['type'] == 'photo':
            attach_bytes = cached_resource(comment['attachment']['media']['image']['src'], 'attach-'+comment['attachment']['target']['id'])
            print('\t\tAttachment: {} -> {}'.format(comment['attachment']['type'], comment['attachment']['target']['id']))
        else:
            print('\t\tUnknown attachment type: {}'.format(comment['attachment']['type']))
    print(comment)

    render_thing(pic_bytes, comment['from']['name'], 'postead a comment.', comment['created_time'], comment['message'], attach_bytes)

def render_like(user):
    print('[LIKE]\t\tFrom: {} ({})'.format(user['name'], user['id']))
    pic_bytes = get_user_picture(user['id'])
    print(user)

    render_thing(pic_bytes, user['name'], 'likes this post.')

if not SKIP_INIT:
    post = fb_get(fb_url(POST, {'fields': 'from,message,created_time'}))
    post = {'id': '10208075829630848_10208076327923305', 'created_time': '2016-02-20T20:05:20+0000', 'from': {'id': '10208075829630848', 'name': 'Laco Pápay'}, 'message': 'Test post, please ignore. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ullamcorper vitae odio vel blandit. Maecenas aliquam lectus vitae neque vestibulum luctus. Pellentesque aliquet massa mi, eu ultricies libero auctor sit amet. Donec imperdiet cursus ex sed posuere. Nullam vel hendrerit nunc, et egestas sapien.'}
    render_post(post)
    pass

comment_ids = set()
like_ids = set()
comments_req = fb_url(POST, {'fields': 'comments.order(chronological).limit('+ str(LIMIT) + '){from{id,name},id,message,created_time,attachment}'})
likes_req = fb_url(POST, {'fields': 'likes.order(chronological).limit('+ str(LIMIT) + '){id,name}'})


#render_comment({'id': '10208076327923305_10208076853256438', 'created_time': '2016-02-20T21:15:03+0000', 'message': 'Third comment!', 'from': {'id': '10208075829630848', 'name': 'Laco Pápay'}})
#render_comment({'id': '10208076327923305_10208076957899054', 'created_time': '2016-02-20T21:22:36+0000', 'message': '', 'attachment': {'target': {'id': '150916231762632', 'url': 'https://scontent.xx.fbcdn.net/hphotos-xta1/t39.1997-6/851565_150916235095965_597077506_n.png'}, 'media': {'image': {'height': 496, 'src': 'https://scontent.xx.fbcdn.net/hphotos-xta1/t39.1997-6/851565_150916235095965_597077506_n.png', 'width': 445}}, 'type': 'sticker', 'url': 'https://scontent.xx.fbcdn.net/hphotos-xta1/t39.1997-6/851565_150916235095965_597077506_n.png', 'title': ''}, 'from': {'id': '10208075829630848', 'name': 'Laco Pápay'}})
#render_comment({'id': '10208076327923305_10208077044941230', 'created_time': '2016-02-20T21:30:39+0000', 'attachment': {'url': 'https://www.facebook.com/photo.php?fbid=10208077043781201&set=p.10208077043781201&type=3', 'type': 'photo', 'target': {'id': '10208077043781201', 'url': 'https://www.facebook.com/photo.php?fbid=10208077043781201&set=p.10208077043781201&type=3'}, 'media': {'image': {'height': 552, 'width': 552, 'src': 'https://scontent.xx.fbcdn.net/hphotos-xpl1/v/t1.0-9/12705793_10208077043781201_8800308936961125052_n.jpg?oh=bcb9c08ed81c83a6f5b2f5c896bd540d&oe=57690073'}}, 'title': ''}, 'message': 'Picture test', 'from': {'id': '10208075829630848', 'name': 'Laco Pápay'}})
#render_comment({'id': '10208076327923305_10208077072501919', 'created_time': '2016-02-20T21:33:03+0000', 'attachment': {'url': 'https://scontent.xx.fbcdn.net/hphotos-xpa1/t39.1997-6/10734316_1601168500115068_914428519_n.png', 'type': 'sticker', 'target': {'id': '1601168493448402', 'url': 'https://scontent.xx.fbcdn.net/hphotos-xpa1/t39.1997-6/10734316_1601168500115068_914428519_n.png'}, 'media': {'image': {'height': 240, 'width': 240, 'src': 'https://scontent.xx.fbcdn.net/hphotos-xpa1/t39.1997-6/10734316_1601168500115068_914428519_n.png'}}, 'title': ''}, 'message': 'Same sticker now', 'from': {'id': '10208075829630848', 'name': 'Laco Pápay'}})
#render_like({'id': '10208075829630848', 'name': 'Laco Pápay'})
#render_comment({'created_time': '2016-02-21T19:11:39+0000', 'from': {'name': 'Viktor Seč', 'id': '10208676909299945'}, 'attachment': {'target': {'url': 'https://www.facebook.com/photo.php?fbid=10208676957101140&set=p.10208676957101140&type=3', 'id': '10208676957101140'}, 'media': {'image': {'width': 220, 'src': 'https://scontent.xx.fbcdn.net/hphotos-xtf1/v/t1.0-9/12729260_10208676957101140_7306138789373152768_n.jpg?oh=af21b0f324d3b1c389a6eddf004ccf9c&oe=5762B462', 'height': 200}}, 'url': 'https://www.facebook.com/photo.php?fbid=10208676957101140&set=p.10208676957101140&type=3', 'title': '', 'type': 'photo'}, 'message': '', 'id': '10208083405100230_10208083938353561'})

first = True
while True:
#while False:
    # Fetch comments until pagination stops
    while True:
        comments = fb_get(comments_req)
        if 'comments' in comments:
            comments = comments['comments']
        if 'data' in comments:
            for comment in comments['data']:
                if comment['id'] in comment_ids:
                    continue
                comment_ids.add(comment['id'])
                if not SKIP_INIT or not first:
                    render_comment(comment)
        if 'paging' in comments and 'next' in comments['paging']:
            comments_req = comments['paging']['next']
        else:
            break
    # Same for likes
    while True:
        likes = fb_get(likes_req)
        if 'likes' in likes:
            likes = likes['likes']
        if 'data' in likes:
            for like in likes['data']:
                if like['id'] in like_ids:
                    continue
                like_ids.add(like['id'])
                if not SKIP_INIT or not first:
                    render_like(like)
        if 'paging' in likes and 'next' in likes['paging']:
            likes_req = likes['paging']['next']
        else:
            break

    # Wait before next pagination round
    #break
    print('Seen a total of {} items ({} likes and {} comments)'.format(len(comment_ids)+len(like_ids), len(like_ids), len(comment_ids)))
    time.sleep(5)
    first = False
