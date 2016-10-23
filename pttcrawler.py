import telnetlib
import sys
import time
import re
import dateutil.parser

# 搞懂了，bbs 根據 command return 的資料是針對前一畫面的局部更新，所以         

class PlainTxtMixin:
    """docstring for PlainTxtMixin"""
    def __init__(self, raw_content=''):
        self.raw_content = raw_content
        self.HTagPattern = re.escape(chr(27)) + r'\[[\d\;]*H'
        self.ColorTagPattern = re.escape(chr(27)) + r'\[[\d\;]*m'
        self.CleanToEndlineTag = re.escape(chr(27)) + r'\[K'
        
    def plaintxt(self, c):
        c = re.sub(self.HTagPattern, '', c)
        c = re.sub(self.ColorTagPattern, '', c)
        c = re.sub(self.CleanToEndlineTag, '', c)
        # if chr(27) in c:
        #     c_index = c.index(chr(27))
        #     print("c.index(chr(27)): %s" % c_index)
        #     print('>>>{0}<<<'.format(c[c_index-10:c_index+10]))
        #     raise Exception('plaintxt is not clean yet.')
        return c


class BBSPage(PlainTxtMixin):
    def __init__(self, raw_content=''):

        super(BBSPage, self).__init__()

        self.current_page = None
        self.total_page = None
        self.percentage = None
        self.line_start = None
        self.line_end = None

        self.author = None
        self.nickname = None
        self.title = None
        self.post_time = None
        self.board = None

        self.linedict = {}

        self.is_tailpage = False
        self.is_headpage = False

        self.status_bar_pattern = (
            re.escape('\x1b[') + r'[\d\;]*m\s*瀏覽\s*第' +
            r'\s*(\d+)/(\d+)\s*頁\s*\(\s*(\d+)%\)\s*' +
            re.escape('\x1b[') + r'[\d\;]*m 目前顯示: 第' +
            r'\s*(\d+)~(\d+)\s*行'
            )

        if raw_content:
            self.parsepage()

    def parsepage(self):
        lines = re.split(r'\r?\n', self.raw_content)
        lastline = lines[-1]
        self.get_status(lastline)
        lines = lines[:-1]

        if re.match( r'\x1b\[0;36m─{30,}', lines[3]) and len(lines[4]) == 0:
            self.is_headpage = True
            lines.pop(4)

            # print(lines[0])
            result = re.findall(
                r'作者 \x1b\[0;44m\s+([\w\d]+)\s+\((.*)\)'
                + r'\s+\x1b\[34;47m 看板 \x1b\[0;44m\s+(.*)\s+$'
                , lines[0])
            if result:
                self.author, self.nickname, self.board = result[0]
            
            result = re.findall(r'標題 \x1b\[0;44m\s(.+)\s*$', lines[1])
            if result:
                # print(result)
                self.title = result[0].strip()

            result = re.findall(r'時間 \x1b\[0;44m\s(.+)\s*$', lines[2])
            if result:
                # print(result)
                self.post_time = result[0].strip()
                self.post_time = dateutil.parser.parse(result[0].strip(), fuzzy=True)
        
        current_lines_len = len(lines)
        while len(lines) != (self.line_end - self.line_start + 1):
            # padding_info = []
            for i in range(len(lines)):
                maybe_H_tag = re.findall(r'\x1b\[(\d+);\d+H', lines[i])
                # print(maybe_H_tag)
                if maybe_H_tag and int(maybe_H_tag[0]) != (i+1):
                    # 其實不應該直接修改 source code 的，但處理起來真的太麻煩，todo: space insert
                    lines[i] = re.sub(r'\x1b\[(\d+);\d+H', '', lines[i])
                    empty_lines_num = int(maybe_H_tag[0]) - (i+1)
                    new_lines = lines[:i] + [''] * empty_lines_num + lines[i:]
                    lines = new_lines
                    break
            #         padding_info.append([i, empty_lines_num])
            # if padding_info:
            #     for o in reversed(padding_info):
            if current_lines_len == len(lines):
                # print(lines)
                break
            else:
                current_lines_len = len(lines)


        assert len(lines) == (self.line_end - self.line_start + 1)


        for i in range(len(lines)):
            self.linedict[self.line_start + i] = lines[i]

    def get_status(self, lastline):
        try:
            result = re.findall(self.status_bar_pattern, lastline)[0]
        except IndexError as e:
            print(lastline)
            raise e
        current_page, total_page, percentage, line_start, line_end = result
        self.current_page = int(current_page)
        self.total_page = int(total_page)
        self.percentage = int(percentage)
        self.line_start = int(line_start)
        self.line_end = int(line_end)
        if current_page == total_page:
            self.is_tailpage = True



class BBSIndexPage(BBSPage):
    """docstring for BBSIndexPage"""
    def __init__(self, boardname=''):
        self.boardname = boardname
        super(BBSIndexPage, self).__init__()

    def get_current_line(self):
        content = self.raw_content
        d = content.split('文章選讀')[0]
        current_title = re.split(self.line_start, d[d.rfind('●'):])[0]
        assert len(current_title) < 120
        return self


class BBSArticle(BBSPage):

    def __init__(self, filename='bbs_article.txt'):
        super(BBSArticle, self).__init__()
        self.page = {}
        self.percentage = 0
        self.linedict = {}
        self.lastpage_end_line_index = 0
        self.finish = False
        self.filename = filename
        self.index_in_board = None

    def feedpage(self, content):
        bbspage = BBSPage(content)
        self.linedict.update(bbspage.linedict)

        # 事實上這行為不太好，應該從 index 頁來決定 title
        if bbspage.is_headpage:
            if bbspage.author:
                self.author = bbspage.author.strip()
            if bbspage.nickname:
                self.nickname = bbspage.nickname.strip()
            if bbspage.board:
                self.board = bbspage.board.strip()
            if bbspage.title:
                self.title = bbspage.title.strip()
            if bbspage.post_time:
                self.post_time = bbspage.post_time

            self.filename = '-'.join(filter(bool, [
                self.index_in_board,
                self.board,
                str(self.post_time),
                self.title,
            ]))

        if bbspage.is_tailpage:
            self.finish = True

    def export(self):
        return '\n'.join(self.linedict.values())

    def devsave(self, name, content):
        with open(name, 'w') as f:
            f.write(content)

    def devload(self, name):
        with open(name, 'r') as f:
            c = f.read()
        return c

    def save(self, filetype='txt'):
        if filetype == 'txt':
            filename = self.filename + '.txt'
            doc = self.plaintxt(self.export())
        elif filetype == 'ansi':
            filename = self.filename + '.ansi.txt'
            doc = self.export()
            
        with open(filename, 'w') as f:
            f.write(doc)


class PttRobot:

    def __init__(self, user, passwd, site, wait_time=0.5, index_range=[1,100]):
        self.site = site
        self.index_range = index_range
        self.tn = telnetlib.Telnet(self.site)
        self.current_percentage = 0
        self.content_buffer = ''
        self.wait_time = wait_time
        self.output_file_name = site + '.txt'
        self.user = user
        self.passwd = passwd

    # Keyin methods
    def keyin(self, v):
        self.tn.write(v.encode('big5'))
        return self

    def enter(self, t=1):
        self.keyin('\r\n' * t)
        return self

    def CtrlL(self):
        self.tn.write(b'\x0c')
        self.wait()
        return self

    def up(self):
        self.tn.write((chr(27)+chr(91)+chr(65)).encode('ascii'))
        return self

    def down(self):
        self.tn.write((chr(27)+chr(91)+chr(66)).encode('ascii'))
        return self

    def right(self):
        self.tn.write((chr(27)+chr(91)+chr(67)).encode('ascii'))
        return self

    def left(self):
        self.tn.write((chr(27)+chr(91)+chr(68)).encode('ascii'))
        return self

    # get site response
    def get_content(self):
        return self.tn.read_very_eager().decode('big5','ignore')

    def safe_content(self):
        """
            '' -> s1 -> s2 -> ''
            return s1 + s2
        """
        c_buffer = self.get_content()
        while not c_buffer:
            time.sleep(0.1)
            c_buffer = self.get_content()

        content = c_buffer

        c_buffer = self.get_content()
        while c_buffer:
            time.sleep(0.1)
            content += c_buffer
            c_buffer = self.get_content()

        print('content'*10)
        print(content)
        print('content'*10)
        return content

    def wait(self, d=1):
        time.sleep(self.wait_time*d)
        return self

    def show(self):
        self.wait().CtrlL()
        self.content_buffer = self.safe_content()
        print(self.content_buffer)
        return self

    def refresh_buffer(self):
        self.content_buffer = self.wait_until(lambda c: c)
        return self

    def wait_until(self, content_condition):
        content = self.safe_content()
        while not content_condition(content):
            print('-', end='')
            sys.stdout.flush()
            self.CtrlL()
            content = self.safe_content()
        return content
        # raise Exception("still in Index, not in article yet %s" % i)        

    # parse site response (?)
    def get_current_line(self):
        esc = '\x1b'
        line_start = re.escape(esc) + r'\[\d{1,2};\dH'
        # line_end = re.escape(esc) + r'\[K'
        content = self.content_buffer
        d = content.split('文章選讀')[0]
        current_title = re.split(line_start, d[d.rfind('●'):])[0]
        assert len(current_title) < 120
        print(current_title)
        return self

    # robot behavior
    def login(self):
        self.wait()
        content = self.safe_content()

        while not '請輸入代號' in content:
            self.wait()
            content = self.safe_content()

        print("首頁顯示...")
        if "請輸入代號" in content:
            print("輸入帳號...")
            self.keyin(self.user).enter()
            # self.wait()
            content = self.safe_content()

            print("輸入密碼...")
            self.keyin(self.passwd).enter()
            # time.sleep(2)
            content = self.safe_content()
            
            if "密碼不對" in content:
                print("密碼不對或無此帳號。程式結束")
                sys.exit()

            assert '密碼正確！ 開始登入系統...' in content
            content = self.safe_content()

            if "您想刪除其他重複登入的連線嗎" in content:
                print("發現重複連線,刪除他...")
                self.keyin("y").enter()
                # time.sleep(7)
                content = self.safe_content()

            while "任意鍵" in content:
                print("資訊頁面，按任意鍵繼續...")
                self.enter()
                self.wait(3)
                content = self.CtrlL().safe_content()
                
            if "要刪除以上錯誤嘗試" in content:
                print("發現嘗試登入卻失敗資訊，是否刪除?(Y/N)：")
                anser = input("")
                self.keyin(anser).enter()
                self.wait()

            print("----------------------------------------------")
            print("----------- 登入完成，顯示操作介面--------------")
            print("----------------------------------------------")

        else:
            print("沒有可輸入帳號的欄位，網站可能掛了")

        content = self.CtrlL().safe_content()

        assert '【主功能表】'in content

        return self

    def logout(self):
        print("----------------------------------------------")
        print("------------------- 登出----------------------")
        print("----------------------------------------------")
        self.keyin("qqqqqqqqqg\r\ny\r\n")
        return self

    def download_article(self):
        # pre-check: in index? no, should check in BBSArticle
        article = BBSArticle()
        while not article.finish:
            content = self.right().CtrlL().wait().safe_content()
            content = content.split('\x1b[H\x1b[2J')[-1]  # CtrlL will keep response, just append new content
            article.feedpage(content)
        article.save()
        self.keyin('q')
        return self

    def download_article_dev_data(self):
        # pre-check: in index? no, check in BBSArticle
        article = BBSArticle()
        while not article.finish:
            content = self.safe_content()
            BBSArticle.feedpage(content)
            self.right()  # if in last page, will back to index page.
        article.save()
        return self


