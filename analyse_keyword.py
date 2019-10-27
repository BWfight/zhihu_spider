import pandas as pd
# from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
import prettytable as pt
import os

'''
author: BW
vision: 1.0
'''

excel_path = '知乎情话.xlsx'
df = pd.read_excel(excel_path)

'''
==========各问题下万赞回答的个数==========
'''
# # ------------Counter，已排序
# qus_count = Counter(df['question'])  
# q_c = qus_count.most_common() 
# q_list = []
# c_list = []
# for i in range(len(q_c)):
#     q_list.append(q_c[i][0])
#     c_list.append(q_c[i][1])
# # ------------value_counts，已排序
# q_c = pd.value_counts(df['question'])   # Series类
# q_list = q_c.index.tolist()
# c_list = q_c.values.tolist()  # List类
# --------------未排序
q_list = []
repeat_bool = df['question'].duplicated()    
for i in range(len(df['question'])):
    if repeat_bool[i] == False:
        q_list.append(df['question'][i])

c_list = [0] * len(q_list)
for i in range(len(q_list)):
    for q in df['question']:
        if q_list[i] == q:
            c_list[i] += 1

vote_stack_list = [0] * len(q_list)
for i in range(len(q_list)):
    for q, v in zip(df['question'], df['vote']):
        if q_list[i] == q:
            vote_stack_list[i] += v
'''
直方图
'''
bar = (
    Bar()  
        .add_xaxis(q_list)             
        .add_yaxis("", c_list)           
        .set_global_opts(
            title_opts=opts.TitleOpts(title="问题下万赞回答数"),
            yaxis_opts=opts.AxisOpts(name="频数"),
            xaxis_opts=opts.AxisOpts(name="问题", axislabel_opts=opts.LabelOpts(rotate=-25))    
            )
        .set_series_opts(
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值") 
                    ]
                )
            )
        .set_series_opts(itemstyle_opts={    
            "normal": {
                "color": JsCode(
                    """new echarts.graphic.LinearGradient(
                        0, 0, 0, 1, 
                        [
                            {offset: 0, color: 'rgba(0, 244, 255, 1)'}, 
                            {offset: 1, color: 'rgba(0, 77, 167, 1)'}
                        ], 
                        false
                        )"""
                    ),
                "barBorderRadius": [30, 30, 30, 30],
                "shadowColor": 'rgb(0, 160, 221)',
                    }
                }
            )
        .render('情话优秀问题柱状图count.html')
    )
bar = (
    Bar()  
        .add_xaxis(q_list)             
        .add_yaxis("", vote_stack_list)           
        .set_global_opts(
            title_opts=opts.TitleOpts(title="问题下万赞回答的总赞数"),
            yaxis_opts=opts.AxisOpts(name="总赞数"),
            xaxis_opts=opts.AxisOpts(name="问题", axislabel_opts=opts.LabelOpts(rotate=-25))    
            )
        .set_series_opts(
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值")  
                    ]
                )
            )
        .set_series_opts(itemstyle_opts={     
            "normal": {
                "color": JsCode(
                    """new echarts.graphic.LinearGradient(
                        0, 0, 0, 1, 
                        [
                            {offset: 0, color: 'rgba(0, 244, 255, 1)'}, 
                            {offset: 1, color: 'rgba(0, 77, 167, 1)'}
                        ], 
                        false
                        )"""
                    ),
                "barBorderRadius": [30, 30, 30, 30],
                "shadowColor": 'rgb(0, 160, 221)',
                    }
                }
            )
        .render('情话优秀问题柱状图vote.html')
    )
print('=====情话优秀问题柱状图完成=====')
'''
玫瑰图
'''
pie = (
    Pie(init_opts=opts.InitOpts(theme=ThemeType.ROMANTIC))  # 浪漫主题
        .add("", [list(z) for z in zip(q_list, c_list)],
            radius=["20%", "75%"],
            center=["40%", "50%"],
            rosetype="radius")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="问题&万赞回答数"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical")
            )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render('情话优秀问题玫瑰图count.html')
    )
pie = (
    Pie(init_opts=opts.InitOpts(theme=ThemeType.ROMANTIC)) 
        .add("", [list(z) for z in zip(q_list, vote_stack_list)],
            radius=["20%", "75%"],
            center=["40%", "50%"],
            rosetype="radius")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="问题下万赞回答赞数和"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical")
            )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .render('情话优秀问题玫瑰图vote.html')
    )
print('=====情话优秀问题玫瑰图完成=====')

'''
==========最佳回答==========
'''
df_vote = df.sort_values(by='vote', ascending=False)   # df.sort_index 有 FutureWarning
a_list = df_vote['author'].tolist()[:10]
v_list = df_vote['vote'].tolist()[:10]
ans_list = df_vote['answer'].tolist()[:10]
qus_list = df_vote['question'].tolist()[:10]
'''
直方图
'''
bar = (
    Bar()  
        .add_xaxis(a_list)             
        .add_yaxis(
            "", 
            v_list,
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(                        # 同问题同色  # 添加注释？
                    """function (params) {
                        if (params.value > 60000) {return 'red';} 
                        else if (params.value == 56610) {return 'blue';}
                        else if (params.value == 51240 || params.value == 35316) {return 'gray';}
                        else if (params.value == 39119) {return 'orange';}
                        else if (params.value == 31998) {return 'pink';}
                        else if (params.value == 30562) {return 'purple';}
                        return 'green';}
                    """
                    )
                )
            )           
        .set_global_opts(
            title_opts=opts.TitleOpts(title="万赞回答TOP10"),
            yaxis_opts=opts.AxisOpts(name="赞数"),
            xaxis_opts=opts.AxisOpts(name="作者", axislabel_opts=opts.LabelOpts(rotate=-45))    
            )
        .render('情话优秀回答柱状图.html')
    )
print('=====情话优秀回答柱状图完成=====')

tb = pt.PrettyTable()
tb.add_column("question", qus_list)
tb.add_column("vote", v_list)
tb.add_column("author", a_list)
# tb.add_column("answer", ans_list)
print(tb)
