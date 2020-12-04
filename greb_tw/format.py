# -*- coding: utf-8 -*-
# https://github.com/ohhal/EasyGrab
import datetime


class user:
    type = "user"

    def __init__(self):
        pass


User_formats = {
    'join_date': '%Y-%m-%d',
    'join_time': '%H:%M:%S %Z'
}


def User(ur, user_tpye='user',):
    _usr = user()
    if user_tpye == 'topic':
        _usr.id = ur['id_str']
        _usr.name = ur['name']
        _usr.username = ur['screen_name']
        _usr.bio = ur['description']
        _usr.location = ur['location']
        _dt = ur['created_at']
        _dt = datetime.datetime.strptime(_dt, '%a %b %d %H:%M:%S %z %Y')
        _usr.join_date = _dt.strftime(User_formats['join_date'])
        _usr.join_time = _dt.strftime(User_formats['join_time'])
        _usr.tweets = int(ur['statuses_count'])
        _usr.following = int(ur['friends_count'])
        _usr.followers = int(ur['followers_count'])
        _usr.likes = int(ur['favourites_count'])
        _usr.media_count = int(ur['media_count'])

    elif user_tpye == 'user':
        if 'data' not in ur:
            raise Exception('账号查询错误')
        if 'data' not in ur and 'user' not in ur['data']:
            raise Exception('账号查询错误')
        if 'legacy' not in ur['data']['user']:
            raise Exception('账号查询错误')
        _usr.id = ur['data']['user']['rest_id']
        _usr.name = ur['data']['user']['legacy']['name']
        _usr.username = ur['data']['user']['legacy']['screen_name']
        _usr.bio = ur['data']['user']['legacy']['description']
        _usr.location = ur['data']['user']['legacy']['location']
        _dt = ur['data']['user']['legacy']['created_at']
        _dt = datetime.datetime.strptime(_dt, '%a %b %d %H:%M:%S %z %Y')
        _usr.join_date = _dt.strftime(User_formats['join_date'])
        _usr.join_time = _dt.strftime(User_formats['join_time'])
        _usr.tweets = int(ur['data']['user']['legacy']['statuses_count'])
        _usr.following = int(ur['data']['user']['legacy']['friends_count'])
        _usr.followers = int(ur['data']['user']['legacy']['followers_count'])
        _usr.likes = int(ur['data']['user']['legacy']['favourites_count'])
        _usr.media_count = int(ur['data']['user']['legacy']['media_count'])
    elif user_tpye == 'followers':
        _usr.id = ur['content']['itemContent']['user']['rest_id']
        _usr.name=ur['content']['itemContent']['user']['legacy']['name']
        _usr.username = ur['content']['itemContent']['user']['legacy']['screen_name']
    # TODO : future implementation
    return _usr


class tweet:
    type = "tweet"

    def __init__(self):
        pass


Tweet_formats = {
    'datestamp': '%Y-%m-%d',
    'timestamp': '%H:%M:%S'
}

def _Tweet(tw, username):
    t = tweet()
    _dt = tw['created_at']

    t.id = tw['id_str']
    t.user_id = tw["user_id_str"]
    t.username = username
    t.conversation_id = tw["conversation_id_str"]
    t.quote_url = ''
    t.quoted_status_id = ''
    t.tweet = tw['full_text']  # 帖子内容
    if 'RT @' in t.tweet:
        t.behavior = 'repost'  # 转发
    elif 'is_quote_status' in tw and tw['is_quote_status'] is True:
        t.behavior = 'comment'  # 评论
        t.quoted_status_id = tw['quoted_status_id_str']  # 评论帖子id
        t.quote_url = tw['quoted_status_permalink']['expanded']  # 评论帖子url
    else:
        t.behavior = 'post'  # 发帖
    t.lang = tw['lang']
    _dt = tw['created_at']
    _dt = datetime.datetime.strptime(_dt, '%a %b %d %H:%M:%S %z %Y')
    t.datetime = str(_dt)
    t.datestamp= _dt.strftime(Tweet_formats['datestamp'])
    t.timestamp = _dt.strftime(Tweet_formats['timestamp'])
    t.replies_count = tw['reply_count']  # 回复数
    t.retweets_count = tw['retweet_count']  # 转发数
    t.likes_count = tw['favorite_count']  # 点赞数
    t.link = f"https://twitter.com/{t.username}/status/{t.id}"
    t.platform = 'twitter'
    # TODO : future implementation
    return t


class nurture:
    type = "plan"

    def __init__(self):
        pass