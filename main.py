import uiautomator2 as u2
from uiautomator2.exceptions import UiObjectNotFoundError
import gevent
import threading
import time


# 需要匹配的信息
set_info = {
   'search_user': '123',    # 来自服务器的用户名
}

# 页面上所有的信息元素的id
page_class = {
    #'''广告页id组'''
        'adve_id' : 'com.smile.gifmaker:id/play_end_content_container',  # 广告查看详情按钮id
        'draw_id' : 'com.smile.gifmaker:id/thanos_ad_caption_tv',  # 弹窗id
        'positive': 'com.kuaishou.nebula:id/positive',   # 同意按钮id
    #'''信息页id组'''
        # 标题的id
        'fansNum': 'com.kuaishou.nebula:id/follower',
        'follow': 'com.kuaishou.nebula:id/following',
        'title1_id' : 'com.smile.gifmaker:id/nebula_thanos_user_name_layout',  # 视频一级标题id
        'title2_id' : 'com.kuaishou.nebula:id/label',  # 视频二级标题
        'title1_path': '//*[@resource-id="com.smile.gifmaker:id/nasa_user_info_content"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]',
        # 交互按钮信息（评论、点赞、分享...）
        'like_id' : 'com.smile.gifmaker:id/like_count_view',  # 喜欢按钮id
        'comment_id' : 'com.smile.gifmaker:id/comment_count_view',  # 评论按钮id
        'forward_id' : 'com.smile.gifmaker:id/forward_count',  # 分享按钮id
        'play': 'com.kuaishou.nebula:id/slide_play_right_button_layout',  # 交互按钮父元素id
        'main_view': 'com.kuaishou.nebula:id/refresh_layout',      # 精选主界面id

        # 按钮
        'top_search': 'com.kuaishou.nebula:id/thanos_home_top_search',      # 头部搜索按钮
        'right_search': 'com.kuaishou.nebula:id/right_btn_layout',
        # 输入框
        'top_input': 'com.kuaishou.nebula:id/editor',      # 头部输入框
        # 用户信息
        'userId': 'com.kuaishou.nebula:id/text1',   # 用户id
}

# 抓取的结果
get_list = []


# 负责连接设备&启动app
class Connect:
    def __init__(self, address, app_name):
        self.address = address
        self.app_name = app_name
        self.d = None

    # 连接设备
    def connect(self):
        self.d = u2.connect(self.address)
        return self.d



# 负责获取信息
class GetInfo:
    def __init__(self, d):
        self.d = d

    # 获取设备尺寸
    def get_size(self):
        print('设备尺寸：', self.d.window_size())

    # 判断该id的元素是否存在
    def id_exists(self, id):
        return self.d(resourceId=page_class[id]).exists

    def xpath_exists(self, path):
        return self.d.xpath(page_class[path]).exists

    # 获取指定id的单个数据
    def get_text(self, id_path):
        if self.id_exists(id_path):
            text = self.d(resourceId=page_class[id_path]).get_text()
        elif self.xpath_exists(id_path):
            text = self.d.xpath(page_class[id_path]).get_text()
        else:
            text = ''
        return text

    # 通过text查询元素
    def select_text(self, text):
        return self.d(text=text).exists

    # 获取指定id的父元素中的子元素
    def get_parent(self, id_path):
        if self.id_exists(id_path):
            text = self.d(resourceId=page_class[id_path]).child(className="android.widget.TextView")
        else:
            text = ''
        return text

    # 获取多个指定id的信息(一组)
    def get_class_text(self, id_class):
        text_dist = {}
        for id in id_class:
            text = self.get_text(id)
            text_dist[id] = text
        return text_dist

# 控制模块（启动app、进入页面，退出app）
class Control(GetInfo, Connect):
    def __init__(self, d, connect):
        self.d = d
        GetInfo.__init__(self, d)
        self.connect = connect

    # 启动app
    def start_app(self):
        self.d.app_start(self.connect.app_name)
        # time.sleep(3)
        # if self.d(resourceId=page_class['positive']).exists:
        #     self.d(resourceId=page_class['positive']).click()

    # 进入用户主页（搜索用户ID进入）
    def enter_main(self):
        if self.id_exists('top_search'):
            if self.id_exists('positive'):
                self.d(resourceId=page_class['positive']).click()
            self.d(resourceId=page_class['top_search']).click()    # 点击头部搜索按钮
            self.d(resourceId=page_class['top_input']).click()  # 点击头部搜索输入框
            self.d(resourceId=page_class['top_input']).set_text(set_info['search_user'])    # 设置搜索框中的内容
            self.d(resourceId=page_class['right_search']).click()  # 点击右侧搜索按钮
        else:
            self.enter_main()

    # 错误处理（用户是否在中途退出应用等等）
    def error_handle(self):
        while True:
            print('异常操作监测...')
            if not self.id_exists('main_view'):
                print('已退出app界面，重新启动中...')
                self.start_app()
            gevent.sleep(0)




# 开始运行整个操作
class Run(GetInfo):
    def __init__(self, d):
        self.d = d
        GetInfo.__init__(self, d)
        self.gevent_list = [None, None, None]

    def child_text(self, index, play_list, info, play):
        try:
            info[play_list[index]] = play[index].get_text()
        except IndexError as IE:
            print('进入界面...')
            gevent.sleep(0)
        except AssertionError as AE:
            print('进入界面...')
            gevent.sleep(0)

    # 交互信息获取
    def play_obtain(self, play_list, info):
        try:
            play = self.get_parent('play')
            for i in range(-1, -4, -1):
                self.gevent_list[i + 3] = gevent.spawn(self.child_text, i, play_list, info, play)
            # get_list.append(info)  # 获取一页的所需信息
            gevent.sleep(0)
        except UiObjectNotFoundError as UFE:
            gevent.sleep(0)
            
    def title_obtain(self, title_list, info):
        for title in title_list:
            if self.id_exists(title):
                text = self.get_text(title)
            else:
                text = ''
            info[title] = text
            gevent.sleep(0)

    def run(self, count):
        info = {}
        play_list = ['like_id', 'comment_id', 'forward_id']
        title_list = ['title2_id']
        for i in range(count):
            t1 = time.time()
            if self.id_exists('adve_id') or self.id_exists('draw_id'):
                if self.id_exists('adve_id'):
                    d.press("back")  # 返回按键
                continue
            else:
                    g_title = gevent.spawn(self.title_obtain, title_list, info)
                    g_play = gevent.spawn(self.play_obtain, play_list, info)
                    g_title.run()
                    print('第' + str(i + 1) + '条：', info)
            self.d.swipe(360, 1100, 360, 200, 0.1)
            t2 = time.time()
            print('用时：', t2 - t1)




# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    connect = Connect('192.168.1.4', 'com.kuaishou.nebula')  # 创建连接对象
    d = connect.connect()  # 连接手机
    control = Control(d, connect)   # 获取控制对象
    control.start_app()  # 启动app
    # control.enter_main()    # 进入主页
    get_info = GetInfo(d)  # 获取信息对象
    get_info.get_size()     # 获取设备尺寸

    run = Run(d)
    t1 = threading.Thread(target=run.run, args=(1000, ))
    t1.start()
    control.error_handle()


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
