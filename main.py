import cv2
import pyautogui
import time
import random
import numpy as np


def find_image(image_path, confidence=0.8):
    """
    在屏幕截图中找到与模板图片相符的位置
    :param image_path: 输入图片的路径
    :param confidence: 匹配的可信度 默认值设置为0.8
    :return: 目标图像的中心点位置
    """
    template = cv2.imread(image_path, 0)
    screen = pyautogui.screenshot()
    screen = np.array(screen)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= confidence)

    for pt in zip(*loc[::-1]):
        height, width = template.shape[:2]
        center_x = pt[0] + width // 2
        center_y = pt[1] + height // 2
        return center_x, center_y
    return None


def random_click(x, y, offset=10):
    """
    模拟鼠标点击并产生随机偏移
    :param x: 初始x坐标
    :param y: 初始y坐标
    :param offset: 偏移量
    :return: 无
    """
    xx = random.randint(-offset, offset)
    yy = random.randint(-offset, offset)
    pyautogui.moveTo(x + xx, y + yy, duration=0.1)
    pyautogui.click()


def click_image(image_path, confidence1=0.8, offset=10, wait_time=5, next_image_path = None,confidence2 = 0.8):
    """
    点击指定图片的中心点，若找到图片则点击并返回True，否则返回False
    :param image_path: 图片的路径
    :param confidence1: 匹配的置信度，默认值为0.8
    :param offset: 随机偏移量，默认值为10
    :param wait_time: 点击后等待的时间，默认值为5秒
    :param next_image_path: 下一步需要检测的图片路径，若不为None则循环检测
    :param confidence2: 下一步需要检测的图片置信度 默认值为0.8
    :return: 若找到图片并点击返回True，否则返回False
    """
    loc1 = find_image(image_path, confidence1)
    if loc1:
        random_click(loc1[0], loc1[1], offset)
        if next_image_path is None:
            # 如果没有检查点 则等待手动输入的时长
            time.sleep(wait_time)
        else:
            # 循环检测是否到达下一个检查点
            attempt = 0
            max_attempts = 20
            while attempt < max_attempts:
                if find_image(next_image_path, confidence2):
                    break
                time.sleep(0.5)
                attempt += 1
            if attempt == max_attempts:
                print(f"多次尝试后仍未检测到{next_image_path}请手动处理")
        return True
    print(f"未找到图片{image_path}")
    return False


def get_midpoint_between_images(image_path1, image_path2, confidence1=0.8, confidence2=0.8):
    """
    获取两个图片位置的中点坐标
    :param image_path1: 图片1的路径
    :param image_path2: 图片2的路径
    :param confidence1: 图片1匹配的置信度，默认值设置为 0.8
    :param confidence2: 图片2匹配的置信度，默认值设置为 0.8
    :return: 中点坐标 (mid_x, mid_y)，如果有图片未找到则返回 None
    """
    loc1 = find_image(image_path1, confidence1)
    loc2 = find_image(image_path2, confidence2)

    if loc1 and loc2:
        x1, y1 = loc1
        x2, y2 = loc2

        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2

        return mid_x, mid_y
    return None


def drag_between_images(image_path1, image_path2, confidence1=0.8, confidence2=0.8):
    """
    从图片1位置中点拖拽到图片2位置中点
    :param image_path1: 图片1的路径
    :param image_path2: 图片2的路径
    :param confidence1: 图片1匹配的置信度，默认值为 0.8
    :param confidence2: 图片2匹配的置信度，默认值为 0.8
    """
    loc1 = find_image(image_path1, confidence1)
    loc2 = find_image(image_path2, confidence2)
    attempt = 0
    max_attempts = 30
    while not loc1 and not loc2:
        time.sleep(0.5)
        attempt += 1
        if attempt == max_attempts:
            print ("定位超时")
            break

    if loc1 and loc2:
        try:
            x1, y1 = loc1
            x2, y2 = loc2

            pyautogui.moveTo(x1, y1)
            time.sleep(0.2)
            pyautogui.dragTo(x2, y2, duration=0.5, button='left')
        except Exception as e:
            print(f"在执行拖拽操作时发生错误: {e}")
    else:
        print("鼠标定位失败 无法进行拖拽操作。")


def check_proxy():
    """
    检查代理指挥状态，若未开启则尝试开启，最多尝试5次
    :return: 若代理指挥开启返回True，否则返回False
    """
    proxy_enabled = False
    max_attempts = 5
    attempt = 0
    proxy_off_image_path = r'.\model\proxy_off.png'
    proxy_on_image_path = r'.\model\proxy_on.png'
    while not proxy_enabled and attempt < max_attempts:
        if find_image(proxy_on_image_path):
            proxy_enabled = True
            print("代理指挥已开启 开始行动")
        elif find_image(proxy_off_image_path):
            print("代理指挥未开启 尝试开启")
            if click_image(proxy_off_image_path):
                time.sleep(1)  # 等待界面更新
            else:
                print("开启代理指挥失败 未找到按键")
        attempt += 1

    if not proxy_enabled:
        print("多次尝试后仍未能开启代理指挥 请手动处理")
    return proxy_enabled

def return_to_home():
    """
    连续按下 ESC 键，直到找到“终端”按钮 即代表回到首页
    """
    terminal_image_path = r'.\model\terminal.png'
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        if find_image(terminal_image_path):
            print("已返回首页")
            break
        pyautogui.press('esc')
        time.sleep(0.5)
        attempt += 1
    if attempt == max_attempts:
        print("多次尝试后仍未返回首页 请手动处理")



def login():
    """
    执行登录操作 点击开始按钮和唤醒按钮 关闭弹出的签到页面和活动页（如果有的话） 循环检测“终端”是否出现以确认是否到达首页
    """
    start_image_path = r'.\model\start.png'
    wake_image_path = r'.\model\wake.png'
    terminal_image_path = r'.\model\terminal.png'
    logout_image_path = r'.\model\logout.png'
    loading_image_path = r'.\model\loading.png'
    arknights_image_path = r'.\model\arknights.png'
    max_attempts = 60
    attempt = 0

    # 明日方舟，启动 ！！！
    while attempt <= max_attempts:
        if find_image(arknights_image_path):
            print("\n明日方舟，启动 ！！！")
            click_image(arknights_image_path, 0.8, wait_time=2)
            break
        time.sleep(1)
        attempt += 1

    if attempt == max_attempts and find_image(arknights_image_path):
        print("游戏打开超时")
        return 1

    # 等待游戏打开
    attempt = 0
    while attempt <= max_attempts:
        time.sleep(1)
        attempt += 1
        if find_image( start_image_path, 0.6):
            print("正在登录")
            break
        if attempt == max_attempts:
            print("游戏打开超时 请检查网络")
            return 1

    time.sleep(2)

    # 点击开始
    while find_image(start_image_path) :
        click_image(start_image_path, 0.6, next_image_path=wake_image_path)
    print("点击唤醒")
    click_image(wake_image_path, 0.6, wait_time=2)

    # 登录加载检测
    attempt = 0
    max_attempts = 30
    while not find_image(loading_image_path, 0.6) and attempt < max_attempts:
        time.sleep(1)
        attempt += 1
    if attempt == max_attempts:
        print("登录超时 请检查网络")
        return 1
    if find_image(loading_image_path, 0.8):
        print("游戏正在载入……")
    attempt = 0
    while find_image(loading_image_path, 0.6) and attempt < max_attempts:
        time.sleep(1)
        attempt += 1
    if attempt == max_attempts:
        print("登录超时 请检查网络")
        return 1

    # 检测是否进入首页 并关闭弹出页
    attempt = 0
    max_attempts = 60
    while not find_image(loading_image_path, 0.5) and attempt < max_attempts:
        time.sleep(1)
        if find_image(terminal_image_path):
            print("已到达首页")
            break
        elif not find_image(terminal_image_path) or find_image(logout_image_path):
            pyautogui.press('esc')
        attempt += 1
    if attempt == max_attempts:
        print("登录超时 请检查网络")
        return 0
    return 1

def turn_to_1_7():
    """
    进入主线关卡类目 寻找关卡1-7
    :return: 用来检查错误原因的
    """


    back_image_path = r'.\model\back.png'
    terminal_image_path=r'.\model\terminal.png'
    terminal2_image_path = r'.\model\terminal2.png'
    target_image_path = r'.\model\hour_of_an_awaking.png'
    theme_image_path=r'.\model\theme.png'

    #检查是否已关闭弹窗
    time.sleep(1)
    if not find_image(terminal_image_path):
        return_to_home()
    else:
        print("正在自动寻找关卡：1-7")

    # 进入主线关卡类目：主题曲
    click_image(terminal_image_path, 0.6, next_image_path=theme_image_path)
    click_image(theme_image_path, 0.6, wait_time=1)

    # 从主线关卡类目下逐步寻找关卡1-7
    midpoint = get_midpoint_between_images(back_image_path, terminal2_image_path)
    if midpoint:
        mid_x, mid_y = midpoint
        pyautogui.moveTo(mid_x, mid_y)
        time.sleep(0.5)

        found = False
        scroll_attempts = 0
        while not found and scroll_attempts < 100:
            pyautogui.scroll(100)
            time.sleep(0.5)
            if find_image(target_image_path):
                found = True
            scroll_attempts += 1
        if not found:
            print("找不到“Act 觉醒”")
            return_to_home()
            return 0
    else:
        print("页面错误，请手动回到主题曲")
        return_to_home()
        return 0

    # 从 章节“同卵异生” 中点拖拽到 章节“二次呼吸” 中点，以找到章节“黑暗时代”
    separated_hearts_image_path = r'.\model\separated_hearts.png'
    stinging_shock_image_path = r'.\model\stinging_shock.png'
    drag_between_images(separated_hearts_image_path, stinging_shock_image_path, 0.6, 0.6)

    # 点击以进入章节“黑暗时代”
    click_image(r'.\model\evil_time.png', wait_time = 2)

    # 点击1-7进行代理作战
    click_image(r'.\model\1-7.png', wait_time = 2)

    return 1

def fight():
    """
     检查代理指挥状态 若开启则点击开始行动按钮 重复战斗直到理智不足
    :return: 用来检查错误原因的
    """
    operation_start1_image_path = r'.\model\operation_start1.png'
    operation_start2_image_path = r'.\model\operation_start2.png'
    takeover_image_path = r'.\model\takeover_combat.png'

    while find_image(operation_start1_image_path):
        if check_proxy():
            if not click_image(operation_start1_image_path):
                print("未能找到开始行动按钮 请检查页面遮挡")
                return_to_home()
                break

            # 检查理智是否充足
            sanity_image_path = r".\model\sanity.png"
            if find_image(sanity_image_path):
                print("理智已耗尽 正在返回首页")
                return_to_home()
                break

            # 点击开始行动2确认进入战斗
            if not click_image(operation_start2_image_path,0.6, next_image_path = takeover_image_path, confidence2=0.6):
                print("开始行动失败 进程终止")
                return_to_home()
                return 1

            # 等待一段时间 确保进入战斗状态
            time.sleep(2)

            # 检查战斗是否正在进行
            attempt = 0
            operation_completed_image_path = r'.\model\operation_completed.png'
            while find_image(takeover_image_path):
                attempt += 1
                print(f"战斗正在进行中...{attempt*5}s")
                time.sleep(5)  # 每隔5秒检查一次

            # 战斗状态结束后 检测结束页面
            attempt = 0
            while not find_image(takeover_image_path) and attempt < 60:
                if find_image(operation_completed_image_path):
                    break
                else:
                    print(f"战斗结算中……{attempt}")
                    time.sleep(1)
                    attempt += 1
                    if attempt == 120:
                        print("加载时间过长 请检查网络")
                        return 2

            while find_image(operation_completed_image_path):
                time.sleep(2)
                print("行动结束 尝试退出")
                click_image(operation_completed_image_path, next_image_path= operation_start1_image_path)
                if find_image(operation_start1_image_path):
                    print("行动结束 准备进行下一次战斗")
                    break
                else:
                    print("未检测到战斗状态或行动结束 继续检查...")
                    time.sleep(2)

            # 等待一段时间后，继续下一轮战斗
            time.sleep(3)
        else:
            return_to_home()
            break
    return 0


if __name__ == "__main__":
    if login() :
        if turn_to_1_7():
            fight()
        else:
            print("寻找关卡失败 程序结束")



