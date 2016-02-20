TOKEN = open('.token').readlines()[0].strip()
POST = '10208075829630848_10208076327923305'
LIMIT = 10

# TODO print existing? cmdline switch

import requests, urllib
import time, os

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

def render_post(post):
    print('[POST]\t\tFrom: {} ({})'.format(post['from']['name'], post['from']['id']))
    get_user_picture(post['from']['id'])
    print('\t\tTime: {}'.format(post['created_time']))
    print('\t\tMsg: {}'.format(post['message']))

def render_comment(comment):
    print('[COMMENT]\tFrom: {} ({})'.format(comment['from']['name'], comment['from']['id']))
    get_user_picture(comment['from']['id'])
    print('\t\tTime: {}'.format(comment['created_time']))
    print('\t\tMsg: {}'.format(comment['message']))
    print(comment)
    if 'attachment' in comment:
        if comment['attachment']['type'] == 'sticker' or comment['attachment']['type'] == 'photo':
            cached_resource(comment['attachment']['media']['image']['src'], 'attach-'+comment['attachment']['target']['id'])
            print('\t\tAttachment: {} -> {}'.format(comment['attachment']['type'], comment['attachment']['target']['id']))
        else:
            print('\t\tUnknown attachment type: {}'.format(comment['attachment']['type']))
def render_like(user):
    print('[LIKE]\t\tFrom: {} ({})'.format(like['name'], like['id']))
    get_user_picture(like['id'])


post = fb_get(fb_url(POST, {'fields': 'from,message,created_time'}))
render_post(post)

comment_ids = set()
like_ids = set()
comments_req = fb_url(POST, {'fields': 'comments.order(chronological).limit('+ str(LIMIT) + '){from{id,name},id,message,created_time,attachment}'})
likes_req = fb_url(POST, {'fields': 'likes.order(chronological).limit('+ str(LIMIT) + '){id,name}'})

#while True:
while False:
    # Fetch comments until pagination stops
    while True:
        comments = fb_get(comments_req)
        if 'comments' in comments:
            comments = comments['comments']
        for comment in comments['data']:
            if comment['id'] in comment_ids:
                continue
            comment_ids.add(comment['id'])
            render_comment(comment)
        if 'next' in comments['paging']:
            comments_req = comments['paging']['next']
        else:
            break
    # Same for likes
    while True:
        likes = fb_get(likes_req)
        if 'likes' in likes:
            likes = likes['likes']
        for like in likes['data']:
            if like['id'] in like_ids:
                continue
            like_ids.add(like['id'])
            render_like(like)
        if 'next' in likes['paging']:
            likes_req = likes['paging']['next']
        else:
            break

    # Wait before next pagination round
    #break
    print('Seen a total of {} items ({} likes and {} comments)'.format(len(comment_ids)+len(like_ids), len(like_ids), len(comment_ids)))
    time.sleep(5)
