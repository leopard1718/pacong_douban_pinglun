# coding:utf-8

import warnings
import jieba  # 分词包
import numpy  # numpy计算包
import codecs  # codecs提供的open方法来指定打开的文件的语言编码，它会在读取的时候自动转换为内部unicode
import pandas as pd
import matplotlib
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import urllib.request
import sys
from wordcloud import WordCloud  # 词云包
import json

header = {
'Cookie': 'bid=pArJsgRATKM; douban-fav-remind=1; __utmz=223695111.1577960207.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; dbcl2="218241843:VnfGfKNHlqM"; ck=hbx0; push_doumail_num=0; push_noty_num=0; __utma=30149280.1657488056.1577441166.1590719021.1592373846.5; __utmc=30149280; __utmz=30149280.1592373846.5.5.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/register; __utmt=1; __utmv=30149280.21824; __utmb=30149280.14.10.1592373846; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1592374174%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D_rSEnhsCCJduZ-8-BPSzRzAFwS2ye64agnRGlvX70H3FBws8PG_GjY6wJ4WKw4CUJP3DebHSnO-omuJvl1bFt_%26wd%3D%26eqid%3Df3572c8a0007311c000000065e0dc092%22%5D; _pk_id.100001.4cf6=eeeb8cbd05cfd405.1577960207.2.1592374174.1577960207.; _pk_ses.100001.4cf6=*; __utma=223695111.2052048094.1577960207.1577960207.1592374174.2; __utmb=223695111.0.10.1592374174; __utmc=223695111',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}

matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
warnings.filterwarnings("ignore")


# 分析网页函数
def getNowPlayingMovie_list():
    resp = urllib.request.Request('https://movie.douban.com/nowplaying/hangzhou/', headers=header)
    response = urllib.request.urlopen(resp)
    html_data = response.read().decode('utf-8')
    # print html_data
    soup = bs(html_data, 'html.parser')
    nowplaying_movie = soup.find_all('div', id='nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dict = {}
        # nowplaying_dict['name'] = item['data-title']
        nowplaying_dict['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):
            #nowplaying_dict['img_src'] = tag_img_item['src']
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list
'''
    for abcd in nowplaying_list:
        print json.dumps(abcd, encoding="UTF-8", ensure_ascii=False)

    # print nowplaying_list
    print json.dumps(nowplaying_list, encoding="UTF-8", ensure_ascii=False)

getNowPlayingMovie_list()
'''

# 爬取评论函数
def getCommentsById(movieId, pageNum):
    eachCommentList = []
    if pageNum > 0:
        start = (pageNum - 1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments' + '?' + 'start=' + str(start) + '&limit=20'
    # print(requrl)
    resp = urllib.request.Request(requrl, headers=header)
    response = urllib.request.urlopen(resp)
    # print(response)
    html_data = response.read().decode('utf-8')
    # print(html_data)
    soup = bs(html_data, 'html.parser')
    comment_div_lits = soup.find_all('div', class_='comment')
    # print(comment_div_lits)
    eachCommentList = []
    for item in comment_div_lits:
        if item.find_all('span', class_='short')[0].string is not None:
            # print(item.find_all('span', class_='short')[0].string)
            eachCommentList.append(item.find_all('span', class_='short')[0].string)
    # print(eachCommentList)
    return eachCommentList



def main():
    # 循环获取第一个电影的前10页评论
    commentList = []
    NowPlayingMovie_list = getNowPlayingMovie_list()
    for i in range(10):
        num = i + 1
        commentList_temp = getCommentsById(NowPlayingMovie_list[2]['id'], num)
        commentList.append(commentList_temp)
    # print(commentList)
    # print json.dumps(commentList, encoding="UTF-8", ensure_ascii=False)
# 分页写入列表后实际上是个二维表，列表元素转换字符串的时候只解一维，导致后续数据转换错误

    # 将列表中的数据转换为字符串
    comments = ''
    for k in range(len(commentList)):
        commentList_temp_01 = commentList[k]
        for x in range(len(commentList_temp_01)):
            comments = comments + (str(commentList_temp_01[x])).strip()
        '''
        comments_01 = str(commentList[k])
        for i in range(len(comments_01)):
            print i
            comments = comments + (str(comments_01[i])).strip()'''
    # print(comments)

    '''
    # 使用正则表达式去除标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    print pattern
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)
    print cleaned_comments
'''
    # 使用结巴分词进行中文分词
    segment = jieba.lcut(comments)
    words_df = pd.DataFrame({'segment': segment})
    # print(words_df)
    print(json.dumps(segment, ensure_ascii=False))

    # 去掉停用词
    stopwords = pd.read_csv("chinese-stopword.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],
                            encoding='utf-8')  # quoting=3全不引用
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
    # print(words_df)

    # 统计词频


    words_df.loc[:, 'count'] = 1
    words_stat = words_df.groupby('segment').agg({"count": 'count'})
    words_stat = words_stat.reset_index().sort_values(by=["count"], ascending=False)
    print(words_stat)
    #print json.dumps(words_stat, encoding="UTF-8", ensure_ascii=False)


    # 用词云进行显示
    wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", max_font_size=80)
    # if len(wordcloud) <= 0:
    #     raise ValueError("We need at least 1 word to plot a word cloud, "
    #                      "got %d." % len(wordcloud))
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}
    '''
    word_frequence_list = []
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)
    '''
    wordcloud = wordcloud.fit_words(word_frequence)
    # wordcloud = wordcloud.fit_words(word_frequence_list)
    # fit_words want's your dictionary, not a list of key/value pairs
    plt.imshow(wordcloud)
    plt.show()


# 主函数
main()
