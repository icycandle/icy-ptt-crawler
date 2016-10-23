"""telnet bbs crawler engine
Usage:
    mission_pigwar.py getindex <id>
    mission_pigwar.py <site> <id> <passwd>
"""
# from docopt import docopt
import os
import re
from pttcrawler import PttRobot, PlainTxtMixin
from settings import LOGIN_INFO
from ptt_ids import gc, bc
import json
from time import sleep

NAME_REGEXP = r'《ＩＤ暱稱》(\w+) \((.{,20})\)'
MONEY_REGEXP = r'《經濟狀況》.{2,4}\s+\(\$(\d+)\)'
LOGINTIMES_REGEXP = r'《登入次數》\s*(\d+)\s*次'
POST_REGEXP = r'《有效文章》(\d+) 篇 \(退:0\)'
IP_REGEXP = r'《上次故鄉》([\d\.]+)'
INFO_TEMPLATE = r"""
《目前動態》查詢 icycandle              《私人信箱》最近無新信件
《上次上站》10/23/2016 11:17:08 Sun     
"""

get_fname = lambda x: 'userinfo/{0}.json'.format(x)

class MissionRobot(PttRobot):
    def to_query_page(self):
        """ 到使用者查詢介面 """
        self.login().wait().keyin("t").enter().keyin("q").enter()
        content = self.CtrlL().safe_content()
        assert '請輸入使用者代號:' in content
        return self

    def get_user_info(self, user_id):
        """ 下載查詢結果 """
        self.keyin(user_id).enter().wait()

    def parse_info(self):

        content = self.CtrlL().safe_content()

        content = PlainTxtMixin().plaintxt(content)

        name = re.findall(NAME_REGEXP, content)
        money = re.findall(MONEY_REGEXP, content)
        logintimes = re.findall(LOGINTIMES_REGEXP, content)
        post = re.findall(POST_REGEXP, content)
        ip = re.findall(IP_REGEXP, content)

        name =  name[0] if name else None
        money =  money[0] if money else None
        logintimes =  logintimes[0] if logintimes else None
        post =  post[0] if post else None
        ip =  ip[0] if ip else None

        # print("name: {0}".format(name))
        # print("money: {0}".format(money))
        # print("logintimes: {0}".format(logintimes))
        # print("post: {0}".format(post))
        # print("ip: {0}".format(ip))

        return {
            'name': name,
            'money': money,
            'logintimes': logintimes,
            'post': post,
            'ip': ip,
        }

    def main(self):
        self.to_query_page().wait()
        for user in list(gc.keys()) + list(bc.keys()):
            fname = get_fname(user)
            
            if os.path.isfile(fname):
                continue
            self.get_user_info(user)
            data = self.parse_info()
            if not data.get('ip'):
                raise Exception("abort fname: %s" % fname)
                continue
            with open(fname, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False))
                print("save fname: %s" % fname)
            self.enter().wait().keyin('q').wait().enter().wait()
        return True



if __name__ == '__main__':
    while 1:
        try:
            ptt_robot = MissionRobot(site='ptt.cc', wait_time=0.3, **LOGIN_INFO)
            r = ptt_robot.main()
        except Exception as e:
            # 通常是順序亂了，只能乾脆重來 XD
            print(e)
        else:
            break


    # board_index_content = ptt_robot.CtrlL().safe_content()
    # assert '看板《Segawar》' in board_index_content

    # if args['getindex']:
    #     print(args['getindex'])
    #     aid = args['<id>']
    #     ptt_robot.keyin(aid).enter().wait().download_article()
    # else:
    #     pass
