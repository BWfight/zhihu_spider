import time
import random
import requests
import json
import jsonpath
import pandas as pd
import os

'''
author: BW
vision: 1.0
'''

headers={
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }


def spider_by_keyword(keyword, page):
    """
    根据关键词，爬取搜索结果中的问题
    :param keyword: 关键字
    :param page: 分页
    :return: info_list
    """
    url = 'https://www.zhihu.com/api/v4/search_v3?'
    params = {
        't': 'general',
        'q': keyword,
        'correction': '1',
        'offset': str((page)*20),   
        'limit': '20',                
        'lc_idx': str((page)*20),
        'show_all_topics': '0',
        'search_hash_id': '1105d34171faf880cf9fe08a08ca4319',
        'vertical_info': '0,0,0,0,0,0,0,0,0,1'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print('=====正在爬取第' + str(page+1) + '页=====')    
        response_json = get_question_id(response.json())  
        return response_json
    else:
        print('=====错误！状态码为' + str(response.status_code) + '。=====')


def get_question_id(response_json):
    """
    获取回答信息
    :param response_json 
    :return: info_list
    """
    question_id_list = jsonpath.jsonpath(response_json, '$.data[*].object.question.id')
    question_name_list = jsonpath.jsonpath(response_json, '$.data[*].object.question.name')
    if question_id_list != [] and question_name_list != []:
        print('-----相关数据获取成功-----')
        return [question_id_list, question_name_list]
    else:
        print('-----未能获取相关数据-----')
        return []


def patch_spider_question_id(keyword, pages):
    """
    批量爬取
    :param keyword: 关键字
    :param pages: 共爬取页数
    :return: 
    """
    # 先清空之前的数据
    if os.path.exists(excel_path):
        os.remove(excel_path)
    # 开始爬取
    question_ids_list = []
    question_names_list =[]
    for page in range(0, pages):                         
        info_list = spider_by_keyword(keyword, page)
        time.sleep(random.randint(1, 3))
        if info_list != []:
            question_ids_list += info_list[0]
            question_names_list += info_list[1]
    return [question_ids_list, question_names_list]


def data_cleaning(question_ids_names_list):
    '''
    清理数据
    1、去除重复，
    2、List 转化为 DataFrame
    :param question_ids_names_list = [question_ids_list, question_names_list]
    :return data    DataFrame 
    '''
    info_dict={
        "id": question_ids_names_list[0], 
        "name": question_ids_names_list[1]
        }
    data = pd.DataFrame(info_dict)
    data = data.drop_duplicates()   # 去重
    return data


def spider_ans_id(qus_id, qus_name, num, vote):
    '''
    访问各个问题页，爬取高赞回答的id
    :param qus_id 
    :param qus_name 
    :param num 
    :param vote 
    :return ans_list
    '''
    url = 'https://www.zhihu.com/api/v4/questions/' + qus_id + '/answers?'
    print('爬取问题：“' + qus_name + '”的高赞回答')
    qvac_list = []
    for n in range(num): 
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
            'limit': '5',
            'offset': str(5*n),
            'platform': 'desktop',
            'sort_by': 'default'
            }
        res = requests.get(url, headers = headers, params=params)
        time.sleep(random.randint(1, 3))
        if res.status_code == 200:
            res_json = res.json()
            vote_list = jsonpath.jsonpath(res_json, '$.data[*].voteup_count')  # 赞 
            author_list = jsonpath.jsonpath(res_json, '$.data[*].author.name')   # 回答者
            content_list = jsonpath.jsonpath(res_json, '$.data[*].content')   # 回答
            if type(vote_list) != bool:   # 回答数不足5条，则 num==2 时，vote_list 是布尔型
                for i in range(len(vote_list)):
                    if int(vote_list[i]) >= vote:
                        qvac_list.append([qus_name, vote_list[i], author_list[i], content_list[i]])
    return qvac_list
                    

def patch_spider_ans_id(data, number, vote):
    '''
    批量爬取
    :param data    DataFrame  id  name 
    :param number  每个问题爬取前几条回答，取5的倍数，否则向下取整
    :param vote  最低赞数
    :return ans_list
    '''
    num = int(number)//5
    all_list = []
    for qus_id, qus_name in zip(data['id'], data['name']):
        qvac_list = spider_ans_id(qus_id, qus_name, num, vote)
        all_list += qvac_list
    data = pd.DataFrame(all_list)    # 按行合并
    data.rename(columns={0:'question',1:'vote',2:'author',3:'answer'},inplace=True)
    data.to_excel(excel_path) 

if __name__ == '__main__':
    excel_path = '知乎情话.xlsx'
    keyword = '情话'
    pages = 10      # 爬取10页回答，至多200个问题
    df = data_cleaning(patch_spider_question_id(keyword, pages))
    number = 10    # 每个问题爬取前10的回答(万赞答案不多，估计前10条足矣)
    vote = 10000   # 只保存万赞以上回答
    patch_spider_ans_id(df, number, vote)
