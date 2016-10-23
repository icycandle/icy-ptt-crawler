"""telnet bbs crawler engine
Usage:
    mission01.py getindex <id>
    mission01.py <site> <id> <passwd>
"""
from docopt import docopt
from pttcrawler import PttRobot
from .settings import LOGIN_INFO
import sys
import re

class MissionRobot(PttRobot):

    def toboard(self):
        # enter Board
        self.keyin("f").enter().keyin("5").enter(2).keyin("15").enter(3)
        self.wait()
        return self

    def mission1(self, _range):
        for i in _range:
            print('+', end='')
            sys.stdout.flush()
            if i % 10 == 0:
                print(i, end='')
            # into article
            ptt_robot.keyin(str(i)).enter(2).CtrlL()
            # read first page
            content = self.wait_until(lambda c: c and ('【徵求中】' not in c[:100]))

            if_flyllis = re.findall('flyllis', content, re.IGNORECASE)

            if if_flyllis:
                with open(self.output_file_name, 'a') as f:
                    f.write("%s\n" % i)

            self.wait()
            ptt_robot.left()

            if '★ 這份文件是可播放的文字動畫，要開始播放嗎？ [Y/n]' in content[-70:]:
                ptt_robot.left()

            content = self.wait_until(lambda c: '【徵求中】' in c[:100])

    def mission2(self, target_ids):
        for aid in target_ids:
            # into article
            ptt_robot.keyin(str(aid)).enter().CtrlL().wait().refresh_buffer(
                ).get_current_line()
            # read first page


if __name__ == '__main__':
    args = docopt(__doc__, version='pttcrawler-2014.02.22')

    ptt_robot = MissionRobot(site='ptt2.cc', wait_time=0.3, **LOGIN_INFO)
    ptt_robot.login().toboard()
    board_index_content = ptt_robot.CtrlL().safe_content()
    assert '看板《Segawar》' in board_index_content

    if args['getindex']:
        print(args['getindex'])
        aid = args['<id>']
        ptt_robot.keyin(aid).enter().wait().download_article()
    else:
        pass

    # mission 1: scan all post have flyllis name (in first page)
    # ptt_robot.mission1(range(1900,2200))  # from 2200 ~ 2700
    # 求快沒有意義，因為良率重於一切。理想的良率是 90%，重複驗證一次以後即可降至 1% miss。第二次是 100%!!
    # target_ids = []
    # mission 2: print titles
    # ptt_robot.mission2(target_ids)
    # mission 3: download articles


"""
    article = BBSArticle()
    for i in range(7):
        c = ptt_robot.right().CtrlL().safe_content()
        c = c.split('\x1b[H\x1b[2J')[-1]  # CtrlL will keep response, just append new content
        article.devsave('a-ctrl-%s.txt' % (i+1), c)
        print(i)


from pttcrawer import PttRobot, BBSArticle, BBSPage, re
article = BBSArticle()
for i in range(7):
    print(i+1);
    article.page[i+1] = article.devload('a-ctrl-%s.txt' % (i+1))
    article.feedpage( article.page[i+1] )
bbspage = BBSPage( article.page[1] )
article.save()

ptt_robot = PttRobot(wait_time=0.3, **LOGIN_INFO)
ptt_robot.login().toboard()
board_index_content = ptt_robot.safe_content()
assert '看板《Segawar》' in board_index_content
ptt_robot.enter()
ptt_robot.wait().download_article()

"""
