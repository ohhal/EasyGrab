# -*- coding: utf-8 -*-
# https://github.com/ohhal/EasyGrab

import re
import time
from json import loads, dumps
from urllib.parse import quote

import requests
from retry import retry

from greb_tw import guest_token
from greb_tw.format import User, _Tweet
from utils.tools import Logger

bearer = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs' \
         '%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'


class RequestException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class TwGrebtException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class TwGreb:
    def __init__(self, config):
        Logger().warning(__name__ + ':TwGreb:__init__')
        self.config = config
        self.token = guest_token.Token(self.config)
        self.token.refresh()
        self.header = {
            'authorization': bearer,
            'x-guest-token': self.config.Guest_token
        }
        self.proxy = {
            'http': self.config.Proxy,
            'https': self.config.Proxy
        }
        self.username = self.config.Username
        self.tweet_count = self.config.Tweet_count
        self.cookie = self.config.Cookie
        self.followers_count = self.config.Followers_count

    @staticmethod
    def dict_to_url(dct):
        return quote(dumps(dct))

    @retry(tries=5, delay=2)
    def following(self, cursor=None):
        '''
        获取正在关注（需要登录cookie）强制等待1s避免封号
        :return:
        '''
        time.sleep(1)
        Logger().warning(__name__ + ':TwGreb:following')
        if cursor:
            params = (
                ('variables',
                 '{"userId":"%s","count":20,"cursor":"%s","withHighlightedLabel":false,"withTweetQuoteCount":false,"includePromotedContent":false,"withTweetResult":false,"withUserResult":false}' % (
                     self.config.User_id, cursor)),
            )
        else:
            params = (
                ('variables',
                 '{"userId":"%s","count":20,"withHighlightedLabel":false,"withTweetQuoteCount":false,"includePromotedContent":false,"withTweetResult":false,"withUserResult":false}' % (
                     self.config.User_id)),
            )
        headers = self.header
        headers[
            'cookie'] = 'personalization_id="v1_a8rI8ElLnTN1/+XCuWaIxw=="; guest_id=v1%3A160516768660954465; _ga=GA1.2.384448571.1605167692; _gid=GA1.2.1834082828.1606979779; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; ads_prefs="HBERAAA="; kdt=zMr0aw1r0mUlIMvb1xjdw0e9yhx2mdzUINDvyZ82; remember_checked_on=1; auth_token=86c1e22406898be2cae58e5c4d7852af2a7b67c9; twid=u%3D1315856555254792192; lang=zh-cn; _twitter_sess=BAh7DCIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCI05c7t1AToMY3NyZl9p%250AZCIlMTgxYWJjZWJhZjgyODkxOGFhZTYxYTYzMzI2YTI0NWQ6B2lkIiVjNTA1%250AYTc0OWFjYjVhYzZmYzVlNzkxZTE2MzRiZTU1MToJdXNlcmwrCQDAVLeQ3EIS%250AOh9sYXN0X3Bhc3N3b3JkX2NvbmZpcm1hdGlvbiIVMTYwNjk4MTgyNjEzOTAw%250AMDoecGFzc3dvcmRfY29uZmlybWF0aW9uX3VpZCIYMTMxNTg1NjU1NTI1NDc5%250AMjE5Mg%253D%253D--045668918785f9047cd9d0c4caf40a18a247c30f; ct0=9dd46cca56ced20fdb94acf4646d09923f6b82c04995e6136653b065af530dee8f5056dbd1e35e6ee1798d1c1a8576491d3ee31cb9ce5a45b384de3d350b1a3371f18314140ac298a89fe17056c15871'
        try:
            headers['x-csrf-token'] = str(re.findall(r'ct0=(.*?);', headers['cookie'])[0]).strip()
        except:
            headers['x-csrf-token'] = headers['cookie'].split('ct0=')[1].strip()
        if headers['x-csrf-token'] == '':
            raise TwGrebtException('Please enter the correct cookie')
        try:
            response = requests.get('https://twitter.com/i/api/graphql/kr_QEk14pqAKwSD8DIWycA/Following',
                                    proxies=self.proxy,
                                    headers=headers, params=params)
        except Exception as e:
            raise RequestException(f'Request url failed:{e}')
        else:
            if 'errors' in response.text:
                msg = f'Error response:{response.text}'
                raise TwGrebtException(msg)
            else:
                users_msg = list()
                if len(response.json()['data']['user']['following_timeline']['timeline']['instructions']) > 1:
                    for usermsg in response.json()['data']['user']['following_timeline']['timeline']['instructions'][2][
                                       'entries'][:20]:
                        users_msg.append(User(usermsg, user_tpye='followers'))
                    cursors = \
                        response.json()['data']['user']['following_timeline']['timeline']['instructions'][2]['entries'][
                            20]['content']['value']
                else:
                    for usermsg in response.json()['data']['user']['following_timeline']['timeline']['instructions'][0][
                                       'entries'][:20]:
                        users_msg.append(User(usermsg, user_tpye='followers'))
                    cursors = \
                        response.json()['data']['user']['following_timeline']['timeline']['instructions'][0]['entries'][
                            20]['content']['value']
                return users_msg, cursors

    @retry(tries=5, delay=2)
    def followers(self):
        Logger().warning(__name__ + ':TwGreb:followers')
        # TODO : future implementation
        pass

    @retry(tries=5, delay=2)
    def get_user_id(self):
        '''
        获取单个用户信息
        :return: 返回User类
        '''
        Logger().warning(__name__ + ':TwGreb:get_user_id')
        params = {'screen_name': self.username, 'withHighlightedLabel': False}
        _url = 'https://api.twitter.com/graphql/jMaTS-_Ea8vh9rpKggJbCQ/UserByScreenName?variables={}' \
            .format(self.dict_to_url(params))
        try:
            response = requests.get(_url, headers=self.header, proxies=self.proxy)
        except Exception as e:
            raise RequestException(f'Request url failed:{e}')
        else:
            if 'errors' in response.text:
                msg = f'Error response:{response.text}'
                raise TwGrebtException(msg)
            return [User(loads(response.text))]

    @retry(tries=5, delay=2)
    def get_topic_user(self):
        '''
        获取某话题下的N个user信息(N代表显示tweet数量，对应返回的用户数通常不等于N)
        :param search:
        :return:User类
        '''
        Logger().warning(__name__ + ':TwGreb:get_topic_user')
        params = (
            ('include_profile_interstitial_type', '1'),
            ('include_blocking', '1'),
            ('include_blocked_by', '1'),
            ('include_followed_by', '1'),
            ('include_want_retweets', '1'),
            ('include_mute_edge', '1'),
            ('include_can_dm', '1'),
            ('include_can_media_tag', '1'),
            ('skip_status', '1'),
            ('cards_platform', 'Web-12'),
            ('include_cards', '1'),
            ('include_ext_alt_text', 'true'),
            ('include_quote_count', 'true'),
            ('include_reply_count', '1'),
            ('tweet_mode', 'extended'),
            ('include_entities', 'true'),
            ('include_user_entities', 'true'),
            ('include_ext_media_color', 'true'),
            ('include_ext_media_availability', 'true'),
            ('send_error_codes', 'true'),
            ('simple_quoted_tweet', 'true'),
            ('q', self.config.Topic_search),
            ('count', f'{self.config.Topic_count}'),
            ('query_source', 'typed_query'),
            ('pc', '1'),
            ('spelling_corrections', '1'),
            ('ext', 'mediaStats,highlightedLabel'),
        )
        try:
            response = loads(
                requests.get('https://twitter.com/i/api/2/search/adaptive.json', headers=self.header, params=params,
                             proxies=self.proxy).text)
        except Exception as e:
            raise RequestException(f'Request url failed:{e}')
        else:
            for user_data in response['globalObjects']['users'].values():
                yield User(ur=user_data, user_tpye='topic')
                # TODO : future implementation

    @retry(tries=5, delay=2)
    def get_tweet(self):
        Logger().warning(__name__ + ':TwGreb:get_tweet')
        params = (
            ('include_profile_interstitial_type', '1'),
            ('include_blocking', '1'),
            ('include_blocked_by', '1'),
            ('include_followed_by', '1'),
            ('include_want_retweets', '1'),
            ('include_mute_edge', '1'),
            ('include_can_dm', '1'),
            ('include_can_media_tag', '1'),
            ('skip_status', '1'),
            ('cards_platform', 'Web-12'),
            ('include_cards', '1'),
            ('include_ext_alt_text', 'true'),
            ('include_quote_count', 'true'),
            ('include_reply_count', '1'),
            ('tweet_mode', 'extended'),
            ('include_entities', 'true'),
            ('include_user_entities', 'true'),
            ('include_ext_media_color', 'true'),
            ('include_ext_media_availability', 'true'),
            ('send_error_codes', 'true'),
            ('simple_quoted_tweet', 'true'),
            ('include_tweet_replies', 'true'),
            ('count', f'{self.tweet_count}'),  # 数量
            ('userId', self.config.User_id),
            ('ext', 'mediaStats,highlightedLabel'),
        )
        try:
            response = loads(
                requests.get(f'https://api.twitter.com/2/timeline/profile/{self.config.User_id}.json',
                             headers=self.header,
                             params=params, proxies=self.proxy).text)
        except Exception as e:
            raise RequestException(f'Request url failed:{e}')
        else:
            Logger().info(
                '共抓取用户{}-{}条tweet'.format(self.username,
                                          len(response['timeline']['instructions'][0]['addEntries']['entries'])))
            for entrryid in response['timeline']['instructions'][0]['addEntries']['entries']:
                try:
                    entrryid = str(entrryid['sortIndex'])
                    tweet_single = response['globalObjects']['tweets'][entrryid]
                    yield _Tweet(tw=tweet_single, username=self.username)
                    # TODO : future implementation
                except:
                    pass

    def get_following(self):
        Logger().warning(__name__ + ':TwGreb:get_following')
        cursor = None
        follower_msg = list()
        if self.followers_count:
            for _ in range(int(self.followers_count / 20) + 1):
                users_msg, cursors = self.following(cursor)
                follower_msg.extend(users_msg)
                cursor = cursors
        if self.followers_count < len(follower_msg):
            return follower_msg
        else:
            return follower_msg[:self.followers_count]

    def run(self):
        if self.config.Username is not None and self.config.User_id is None:
            Logger().warning(__name__ + ':TwGreb:main:username')
            self.config.User_id = self.get_user_id()[0].id
            if self.config.User_id is None:
                raise ValueError("Cannot find twitter account with name = " + self.config.Username)
        # todo
        if self.config.Following:
            Logger().warning(__name__ + ':TwGreb:main:follow')
            return self.get_following()
        elif self.config.Profile:
            Logger().warning(__name__ + ':TwGreb:main:profile')
            return self.get_user_id()
        elif self.config.Topic_Profile:
            Logger().warning(__name__ + ':TwGreb:main:profile')
            return self.get_topic_user()
        elif self.config.Followers:
            return Logger().warning(__name__ + ':TwGreb:main:Followers Not online')
        elif self.config.Tweet:
            Logger().warning(__name__ + ':TwGreb:main:Tweet')
            return self.get_tweet()
        else:
            Logger().warning(__name__ + ':TwGreb:main:no-more-tweets')


def Following(config):
    Logger().warning(__name__ + ':Following')
    config.Following = True
    config.Followers = False
    config.Profile = False
    config.Topic_Profile = False
    config.Tweet = False
    return TwGreb(config).run()


def Profile(config):
    Logger().warning(__name__ + ':Profile')
    config.Following = False
    config.Followers = False
    config.Profile = True
    config.Topic_Profile = False
    config.Tweet = False
    return TwGreb(config).run()


def Topic_Profile(config):
    Logger().warning(__name__ + ':Topic_Profile')
    config.Following = False
    config.Followers = False
    config.Profile = False
    config.Topic_Profile = True
    config.Tweet = False
    return TwGreb(config).run()


def Tweet(config):
    Logger().warning(__name__ + ':Tweet')
    config.Following = False
    config.Followers = False
    config.Profile = False
    config.Topic_Profile = False
    config.Tweet = True
    return TwGreb(config).run()
