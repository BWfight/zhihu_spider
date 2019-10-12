import requests
import json
import openpyxl
import time
import random
# import re
import os

'''
author: BW
vision: 1.0
'''

def spider_question(question, page):
    """
    爬取知乎提问网页
    :param question: 问题
    :param page: 分页
    :return: info_list
    """
    headers={
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
    url = 'https://www.zhihu.com/api/v4/search_v3?'
    params = {
        't': 'general',
        'q': question,
        'correction': '1',
        'offset': str((page)*20),         # 从第几篇文章开始    # 不能从0（第1个答案）开始爬取，有时状态码500，有时爬到空data_list
        'limit': '20',                    # 一个xhr加载几篇
        'lc_idx': str((page)*20+2),
        'show_all_topics': '0',
        'search_hash_id': '1105d34171faf880cf9fe08a08ca4319',
        'vertical_info': '0,0,0,0,0,0,0,0,0,1'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print('=====正在爬取第' + str(page+1) + '页=====')    
        info_list = get_answer_info(response.json())  
        return info_list
    else:
        print('=====错误！状态码为' + str(response.status_code) + '。=====')
    

def get_answer_info(response_json):
    """
    获取回答信息
    :param response_json:
    :return: info_list
    """
    data_list = response_json['data']
    info_list= []
    for i in data_list:
        if 'question' in i['object']:
            title = i['object']['question']['name'].replace('<em>', '').replace('</em>', '')
        else:
            title = i['object']['title'].replace('<em>', '').replace('</em>', '')

        if 'excerpt' in i['object']: 
            excerpt = i['object']['excerpt'].replace('<em>', '').replace('</em>', '')
        else:
            excerpt = '无'

        if 'author' in i['object']:  
            author = i['object']['author']['name']
        else:
            author = '匿名'
         
        if 'content' in i['object']:              
            raw_content = i['object']['content']
            content = raw_content.replace('<h2>', '').replace('</h2>', '').replace('<p>', '').replace('</p>', '').replace('<hr/>', '').replace('<br/>', '').replace('<b>', '')
            # pattern = re.compile(r'[\u4e00-\u9fa5 0-9 ， 。 ？ ！]')  # re匹配中文，数字等。 
            # content_list = pattern.findall(raw_content)    # 返回列表  
            # content = ''.join(content_list)  # 连接为字符串
        else:
            content = '无' 
        

        url = i['object']['url']

        if 'voteup_count' in i['object']: 
            voteup_count = i['object']['voteup_count']
        else:
            voteup_count = '无'
        
        info = [title.encode('gbk','ignore').decode('gbk'), author, \
                excerpt.encode('gbk','ignore').decode('gbk'), \
                content.encode('gbk','ignore').decode('gbk'), \
                url, voteup_count]
        info_list.append(info)
    return info_list


def patch_spider_place(question, page):
    """
    批量爬取
    :param question: 搜索关键字
    :return:
    """
    # 写入数据前先清空之前的数据
    if os.path.exists(place_excel_path):
        os.remove(place_excel_path)
    
    for i in range(1, page):                           # 从第21个答案开始爬取
        info_list = spider_question(question, i)
        save_info_excel(info_list)
        # 设置一个时间间隔
        time.sleep(random.randint(3, 6))
    print('=====爬取完成！=====')


def save_info_excel(info_list):
    """
    将数据保存成excel文件的准备工作
    :param place_list: 数据列表
    :return:
    """
    for info in info_list:
        sheet.append(info)


if __name__ == '__main__':
    place_excel_path = '知乎提问.xlsx'

    wb=openpyxl.Workbook()    # 创建工作薄
    sheet=wb.active   # 获取工作薄的活动表
    sheet.title="Ans"    # 工作表重命名
    sheet['A1'] ='标题'     # 加表头，给单元格赋值
    sheet['B1'] ='作者'
    sheet['C1'] ='摘要' 
    sheet['D1'] ='回答'   
    sheet['E1'] ='链接'   
    sheet['F1'] ='点赞数' 
    
    question = '你见过的有些人能漂亮到什么程度？'
    page = 21      # 会爬取21-1 * 20 = 400 条，头20条遗漏
    patch_spider_place(question, page)

    wb.save(place_excel_path)   # 保存
    print('=====Excel文件已保存！=====')
