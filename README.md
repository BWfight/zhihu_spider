# zhihu_spider



1.
spider_fig_of_question.py

下载一个问题（或回答）下的图片。需要问题（或回答）的网址。参数：page url

照片保存在 问题+作者+点赞数 的文件夹下



2.
spider_ans_of_q_save_excel.py

爬取一个问题下的或回答。参数：question page。保存为excel文件

结果：知乎提问.xlsx



3.
analysis_wordcloud_bar.py

分析爬取的excel文件。参数：excel_path

结果：

词云：title_content-word-cloud.html。

柱状图：title_content-word-agree-bar.html
