# -*- coding: utf-8 -*-
# https://github.com/ohhal/EasyGrab
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    Username: Optional[str] = 'HSesports'
    Proxy: Optional[str] = None
    Guest_token: str = None
    Cookie: str = None
    Followers_count: int = 50
    User_id: str = None
    Tweet_count: int = 50
    Topic_search:str='China'
    Topic_count: int = 50
    # 方法
    Following = False
    Followers = False
    Profile = False
    Topic_Profile = False
    Tweet = False


_config = Config()
