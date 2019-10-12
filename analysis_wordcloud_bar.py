import numpy as np
import pandas as pd
import jieba.analyse
from pyecharts import options as opts
from pyecharts.globals import SymbolType
from pyecharts.charts import Bar, WordCloud
import os

'''
author: BW
vision: 1.0
注释：用词云分析文本效果并不好
'''


place_excel_path = '知乎提问.xlsx'
DF = pd.read_excel(place_excel_path)
stop_words_file_path = 'stop_words.txt'    

def analysis_title_content():
    """
    词云分析回答的标题+回答
    :return:
    """
    # 引入全局数据
    global DF
    # 数据清洗，去掉无效词
    jieba.analyse.set_stop_words(stop_words_file_path)
    # 1、词数统计
    title_string = ' '.join(DF['标题'])
    excerpt_string = ' '.join(DF['回答'])
    string = ' '.join([title_string, excerpt_string])
    keywords_count_list = jieba.analyse.textrank(string, topK=50, withWeight=True)
    print(keywords_count_list)
    # 生成词云
    word_cloud = (
        WordCloud()
            .add("", keywords_count_list, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
            .set_global_opts(title_opts=opts.TitleOpts(title="标题+回答常用词词云TOP50"))
    )
    word_cloud.render('title_content-word-cloud.html')

    # 2、回答常用词生成柱状图
    # 2.1统计词数
    keywords_count_dict = {i[0]: 0 for i in reversed(keywords_count_list[:20])}  # 取前20高频的关键词
    cut_words = jieba.cut(string)
    for word in cut_words:
        for keyword in keywords_count_dict.keys():
            if word == keyword:
                keywords_count_dict[keyword] = keywords_count_dict[keyword] + 1
    print(keywords_count_dict)
    # 2.2生成柱状图
    keywords_count_bar = (
        Bar()
            .add_xaxis(list(keywords_count_dict.keys()))
            .add_yaxis("", list(keywords_count_dict.values()))
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="标题+回答常用词TOP20"),
            yaxis_opts=opts.AxisOpts(name="词"),
            xaxis_opts=opts.AxisOpts(name="出现数")
        )
    )
    keywords_count_bar.render('title_excerpt-word-count-bar.html')

    # 3、回答高频关键字与点赞数关系
    keywords_sales_dict = analysis_title_keywords(keywords_count_list, '点赞数', 20)
    # 生成柱状图
    keywords_sales_bar = (
        Bar()
            .add_xaxis(list(keywords_sales_dict.keys()))
            .add_yaxis("", list(keywords_sales_dict.values()))
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="标题+回答高频关键字与点赞数关系TOP20"),
            yaxis_opts=opts.AxisOpts(name="词"),
            xaxis_opts=opts.AxisOpts(name="点赞数")
        )
    )
    keywords_sales_bar.render('title_content-word-agree-bar.html')

def analysis_title_keywords(keywords_count_list, column, top_num) -> dict:
    """
    分析标题关键字与其他属性的关系
    :param keywords_count_list: 关键字列表
    :param column: 需要分析的属性名
    :param top_num: 截取前多少个
    :return:
    """
    # 1、获取高频词，生成一个dict={'keyword1':agree_number1, 'keyword2':agree_number2,...}
    keywords_column_dict = {i[0]: 0 for i in keywords_count_list}
    for row in DF.iterrows():
        for keyword in keywords_column_dict.keys():
            if (keyword in row[1]['标题']) or (keyword in row[1]['回答']):
                if row[1]['点赞数'] != '无':
    # 2、 将标题包含关键字的属性值放在列表中，dict={'keyword1':[属性值1,属性值2,..]}
                    keywords_column_dict[keyword] += row[1]['点赞数']
    # 3、 根据总点赞数排序，从小到大
    keywords_agree_dict = dict(sorted(keywords_column_dict.items(), key=lambda d: d[1], reverse=True))
    # 4、截取平均值最高的20个关键字
    keywords_agree_dict = {k: keywords_agree_dict[k] for k in list(keywords_agree_dict.keys())[-top_num:]}
    print(keywords_agree_dict)
    return keywords_agree_dict

if __name__ == '__main__':
    analysis_title_content()
