import time
import random
import re
import requests
from lxml import etree
import json
import jsonpath
import os

'''
author: BWfight
vision: 1.0
'''


def spider_fig_by_url_in_ans(number):
    '''
    提取回答页网址
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }  
    url = 'https://www.zhihu.com/api/v4/questions/50426133/answers?'   # 可更换网址 以 平常人可以漂亮到什么程度？为例
    for n in range(number):      # 可以从0开始
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
            'limit': '5',            # 一个json有5个回答
            'offset': str(5*n), 
            'platform': 'desktop',
            'sort_by': 'default',
            }
        response = requests.get(url, headers = headers, params=params)
        data = response.json()

        q_url_list = jsonpath.jsonpath(data, '$.data[*].question.url') 
        a_url_list = jsonpath.jsonpath(data, '$.data[*].url') 

        for q_url, a_url in zip(q_url_list, a_url_list):
            q_number = re.findall('\d+', q_url)[1]
            a_number = re.findall('\d+', a_url)[1]
            href = 'https://www.zhihu.com/question/' + q_number + '/answer/' + a_number
 
            spider_fig_in_one_ans(href)


def spider_fig_in_one_ans(url):
    '''
    回答页下载图片
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }  
    response = requests.get(url, headers = headers)
    html = etree.HTML(response.text) 

    title_list = html.xpath('//*[@id="root"]/div/main/div/meta[1]/@content')  # 问题
    vote_list = html.xpath('//div[@class="AnswerItem-extraInfo"]/span/button/text()')   # 赞

    author_list = html.xpath('//div[@class="AuthorInfo-content"]/div/span/div/div/a/text()')    # 回答者
    if author_list == []:
        author = '匿名用户'
    else:
        author = author_list[0]
    
    figure_list = html.xpath('//div[@class="RichContent-inner"]/span/figure/img/@data-original')   # 图片
    if figure_list != []:
        coll_name = title_list[0] + author + vote_list[0]
        if os.path.exists('D:/' + coll_name) == False:  # 若文件夹不存在
            os.mkdir('D:/' + coll_name)   # 创建目录
        else:
            os.removedirs('D:/' + coll_name)   # 需要以管理者身份运行
            os.mkdir('D:/' + coll_name)  
    
        print('=====开始' + url + '的爬取=====')
        count = 1
        for figure in figure_list:
            print("正在抓取第" + str(count) + "张图片")
            res = requests.get(figure, headers=headers)
            # time.sleep(random.randint(1, 2))  
            file_name = str(count) + '.jpg'
            try:
                with open('D:/' + coll_name + '/' + file_name, "wb") as f:
                    f.write(res.content)
            except:
                print("文件名有误")
            count += 1
        print('=====' + url + '完成=====')
        time.sleep(random.randint(1, 6))
    else:
        print('该答案无图片')



def spider_fig_in_quetion(number):
    '''
    直接在问题页提取
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }  
    url = 'https://www.zhihu.com/api/v4/questions/34243513/answers?'   # 可更换网址   以 你见过最漂亮的女生长什么样？为例
    for n in range(number): 
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
            'limit': '5',        
            'offset': str(5*n),      
            'platform': 'desktop',
            'sort_by': 'default',
            }
        response = requests.get(url, headers = headers, params=params)
        data = response.json()

        title_list = jsonpath.jsonpath(data, '$.data[*].question.title')    # 问题
        vote_list = jsonpath.jsonpath(data, '$.data[*].voteup_count')  # 赞 
        author_list = jsonpath.jsonpath(data, '$.data[*].author.name')   # 回答者

        content_0 = jsonpath.jsonpath(data, '$.data[0].content')[0]   # 只能爬全文内容
        content_1 = jsonpath.jsonpath(data, '$.data[1].content')[0]
        content_2 = jsonpath.jsonpath(data, '$.data[2].content')[0]
        content_3 = jsonpath.jsonpath(data, '$.data[3].content')[0]
        content_4 = jsonpath.jsonpath(data, '$.data[4].content')[0]

        pattern = re.compile('data-original="(https:.*?jpg)"')    # 非贪婪匹配，返回括号里url    # 贪婪匹配出错
        fig_list_0 = pattern.findall(content_0)    # 返回列表  
        figure_list_0 = take_even_index_element_in_list(fig_list_0)    # 同一图片重复两遍，所以取偶数下标     
        fig_list_1 = pattern.findall(content_1) 
        figure_list_1 = take_even_index_element_in_list(fig_list_1)          
        fig_list_2 = pattern.findall(content_2)  
        figure_list_2 = take_even_index_element_in_list(fig_list_2)         
        fig_list_3 = pattern.findall(content_3)  
        figure_list_3 = take_even_index_element_in_list(fig_list_3)         
        fig_list_4 = pattern.findall(content_4)
        figure_list_4 = take_even_index_element_in_list(fig_list_4) 
        figure_list_list = [figure_list_0, figure_list_1, figure_list_2, figure_list_3, figure_list_4]

        for title, vote, author, figure_list in zip(title_list, vote_list, author_list, figure_list_list):
            coll_name = title + author + str(vote) + "赞"
            if os.path.exists('D:/' + coll_name) == False: 
                os.mkdir('D:/' + coll_name)   # 创建目录
            else:
                os.remove('D:/' + coll_name) 
                os.mkdir('D:/' + coll_name) 
            
            print('=====开始' + title + author + '的爬取=====')
            count = 1
            for figure in figure_list:
                print("正在抓取第" + str(count) + "张图片")
                res = requests.get(figure, headers=headers)
                file_name = str(count) + '.jpg'
                try:
                    with open('D:/' + coll_name + '/' + file_name, "wb") as f:
                        f.write(res.content)
                except:
                    print("文件名有误")
                count += 1
            print('=====' + title + author + '爬取完成=====')
        print('=====图片爬取完成=====')
        time.sleep(random.randint(1, 6))

def take_even_index_element_in_list(list_old):
    '''
    取list中所有偶数下标元素
    :param list_old
    :return list_new
    '''
    list_new = []
    for i in range(len(list_old)//2):   # / 得到 float，range 不能处理
        list_new.append(list_old[2*i])
    return list_new


if __name__ == '__main__':
    spider_fig_by_url_in_ans(24)   # 爬取前24 * 5 = 120条答案  以 平常人可以漂亮到什么程度？为例 

    spider_fig_in_one_ans('https://www.zhihu.com/question/29289467/answer/72898476')   # 爬取一条回答的图片  输入网址 生活中你见过的最美女性长什么样？ 为例 

    spider_fig_in_quetion(24)  # 爬取前120条答案  以 你见过最漂亮的女生长什么样？为例
