import uiautomator2 as u2
import sys
from uiautomator2.exceptions import UiObjectNotFoundError
import gevent
import threading
import time

# 需要匹配的信息
set_info = {
    'search_user': '303815003',  # 来自服务器的用户名
}

# 页面上所有的信息元素的id
page_class = {
    # '''广告页id组'''
    'adve_id': 'com.smile.gifmaker:id/play_end_content_container',  # 广告查看详情按钮id
    'draw_id': 'com.smile.gifmaker:id/thanos_ad_caption_tv',  # 弹窗id
    'positive': 'com.xingin.xhs:id/c2z',  # 同意按钮id
    'close': 'com.kuaishou.nebula:id/close',  # 关闭页
    # '''信息页id组'''
    # 单个作品标题的id
    'title1_id': 'com.xingin.xhs:id/cvc',  # 作品一级标题id
    'title2_id': 'com.xingin.xhs:id/bh_',  # 作品二级标题
    # 用户总共交互按钮信息（评论、点赞、分享...）
    'total_fabulous': 'com.xingin.xhs:id/bup',  # 总共的点赞数
    'total_fans':'com.xingin.xhs:id/awl',   # 总共的粉丝数
    'total_follow': '//*[@resource-id="com.xingin.xhs:id/pp"]/android.widget.FrameLayout[1]',   # 总共的关注数
    # 用户单个作品交互信息(评论数、收藏数、喜欢数)
    'works_comment': 'com.xingin.xhs:id/ctv',   # 用户单个作品的评论数
    'works_collection': 'com.xingin.xhs:id/ctp',     # 用户单个作品的收藏数
    'works_like': 'com.xingin.xhs:id/cuq',   # 用户单个作品的喜欢数
    'works_card': 'com.xingin.xhs:id/a5s',   # 用户作品卡片id
    # 按钮
    'top_search': 'com.xingin.xhs:id/do3',  # 头部搜索按钮
    'right_search': 'com.xingin.xhs:id/cck',    #
    # 输入框
    'top_input': 'com.xingin.xhs:id/ccg',  # 头部输入框
    # 用户信息
    'userId': 'com.kuaishou.nebula:id/text1',  # 用户id
    'user_term_page': 'com.xingin.xhs:id/cc3', # 用户项页
    'user_term': 'com.xingin.xhs:id/ccp',   # 用户项id
    'user_works_page': 'com.xingin.xhs:id/chj',     # 用户全部作品列表页
    'user_speak_page': 'com.xingin.xhs:id/aue',     # 用户单个作品页
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
        size_xy = self.d.window_size()
        print('设备尺寸：', size_xy)
        return size_xy

    # 判断该id的元素是否存在
    def id_exists(self, id):
        return self.d(resourceId=page_class[id]).exists

    def xpath_exists(self, path):
        return self.d.xpath(page_class[path]).exists

    # 获取指定id的单个数据
    def get_text(self, id_path, info=None):
        if self.id_exists(id_path):
            text = self.d(resourceId=page_class[id_path]).get_text()
        elif self.xpath_exists(id_path):
            text = self.d.xpath(page_class[id_path]).get_text()
        else:
            text = self.get_text(id_path, info)
        if info != None:
            info[id_path] = text
        return text

    # 通过text查询元素
    def select_text(self, text):
        return self.d(text=text).exists

    # # 获取指定id的父元素中的子元素
    # def get_parent(self, id_path):
    #     if self.id_exists(id_path):
    #         text = self.d(resourceId=page_class[id_path]).child(className="android.widget.TextView")
    #     else:
    #         text = ''
    #     return text

    # 获取多个指定id的信息(一组)
    def get_class_text(self, id_class):
        text_dist = {}
        for id in id_class:
            text = self.get_text(id, None)
            text_dist[id] = text
        return text_dist


class Control(GetInfo, Connect):
    def __init__(self, d, connect):
        self.d = d
        GetInfo.__init__(self, d)
        self.connect = connect
        self.error_flag = True

    # 启动app
    def start_app(self):
        self.d.app_start(self.connect.app_name)
        if self.d(resourceId=page_class['positive']).exists:
            self.d(resourceId=page_class['positive']).click()

    # 进入用户主页（搜索用户ID进入）
    def enter_main(self):
        if self.id_exists('user_works_page'):   # 当处在作品列表页时退出操作
            return
        implement_list = ['top_search', 'right_search', 'user_term']
        imp_index = -1
        for imp in implement_list:
            if self.id_exists(imp):
                imp_index = implement_list.index(imp)
                print('imp_index：', imp_index)
        if imp_index < 0:
            self.start_app()
            self.enter_main()
        else:
            for i in range(imp_index, len(implement_list)):
                if i == 1:
                    self.d(resourceId='com.xingin.xhs:id/ccg').set_text(set_info['search_user'])  # 设置搜索框中的内容
                if i == 2:
                    self.d.xpath('//*[@resource-id="com.xingin.xhs:id/cc5"]/android.widget.LinearLayout[1]/androidx.appcompat.app.ActionBar-Tab[3]').click()  # 点击用户标签
                    time.sleep(1)
                    if self.select_text('小红书号：' + set_info['search_user']):
                        print('已找到该用户！')
                    else:
                        print('未找到该用户')
                        return
                self.d(resourceId=page_class[implement_list[i]]).click()
            if self.id_exists('user_works_page'):
                d.swipe(360, (self.d.window_size()[1]/2 + 25), 360, 0, 0.1)
                time.sleep(1)




    # 错误处理（用户是否在中途退出应用等等）
    def error_handle(self):
        while self.error_flag:
            print('异常操作监测...')
            if not self.id_exists('user_speak_page') and not self.id_exists('user_works_page'):
                print('已退出app界面，重新启动中...')
                self.start_app()
            gevent.sleep(0)
        sys.exit(0)


# 开始运行整个操作
class Run(GetInfo):
    def __init__(self, d, control):
        self.d = d
        self.control = control
        GetInfo.__init__(self, d)
        self.phone_size = self.get_size()

    # 交互信息获取
    def play_obtain(self, play_list, info):
            print('XXXXXXXXXXX')
            for play in play_list:
                g = gevent.spawn(self.get_text, play, info)
                g.run()
            gevent.sleep(0)


    def title_obtain(self, title_list, info):
        print('aaaaaaaaaaaaaa')
        for title in title_list:
            if self.id_exists(title):
                info[title] = self.get_text(title, None)
            else:
                self.d.swipe(self.phone_size[0]/2, self.phone_size[1]/2,
                        self.phone_size[0]/2, 0, 0.1)
                gevent.sleep(0)
                self.title_obtain(title_list, info)


    def run(self, count):
        if self.id_exists('works_card'):
            info = {}
            total_play_list = ['total_follow', 'total_fans', 'total_follow']  # 总的交互信息
            works_play_list = ['works_comment', 'works_collection', 'works_like']  # 单个作品的交互信息
            title_list = ['title1_id', 'title2_id']  # 作品标题
            works_page_old = []
            while True:
                works_page = d(resourceId='com.xingin.xhs:id/a5s')

                for work in works_page:
                    print(works_page[-1].info['bounds'].get('top', None),works_page[-1].info['bounds'].get('bottom', None))
                    print(dir(works_page[-1].info))
                    if works_page_old != []:
                        print('old：', dir(works_page_old[0].info.values()))
                        if work == works_page_old[0] or work == works_page_old[1]:
                            print('wwwwwwwwwww')
                            continue
                    work.click()
                    g1 = gevent.spawn(self.play_obtain, works_play_list, info)
                    g2 = gevent.spawn(self.title_obtain, title_list, info)
                    gevent.joinall([g1, g2])
                    self.d.swipe(20, self.phone_size[1] - 25, 700, self.phone_size[1] - 25, 0.001)
                    print(info)
                time.sleep(1)
                works_page_old = [*works_page][-2:]
                self.d.swipe(self.phone_size[0]/2, self.phone_size[1]-1,
                        self.phone_size[0]/2, self.phone_size[1]*0.175-1)
                time.sleep(1)
            # self.control.error_flag = False
        else:
            self.run(count)




        # self.d.swipe(360, 1270, 360, 50, 0.1)     # 上滑进入作品列表
        #
        # for i in range(count):
        #     t1 = time.time()
        #     if self.id_exists('adve_id') or self.id_exists('draw_id') or self.id_exists('close'):
        #         if self.id_exists('adve_id'):
        #             d.press("back")  # 返回按键
        #         elif self.id_exists('close'):
        #             d(resourceId=page_class['close']).click()
        #         else:
        #             continue
        #     else:
        #         g_title = gevent.spawn(self.title_obtain, title_list, info)
        #         g_play = gevent.spawn(self.play_obtain, play_list, info)
        #         g_play.run()
        #         print('第' + str(i + 1) + '条：', info)
        #
        #     t2 = time.time()
        #     print('用时：', t2 - t1)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    connect = Connect('192.168.1.4', 'com.xingin.xhs')  # 创建连接对象
    d = connect.connect()  # 连接手机
    control = Control(d, connect)  # 获取控制对象
    control.start_app()  # 启动app
    control.enter_main()  # 进入搜索页面
    get_info = GetInfo(d)  # 获取信息对象
    get_info.get_size()  # 获取设备尺寸

    run = Run(d, control)
    t1 = threading.Thread(target=run.run, args=(1000,))
    t1.start()
    control.error_handle()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
