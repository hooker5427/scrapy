# -*- coding: utf-8 -*-
import scrapy
from anjuke.items import AnjukeItem
from lxml import etree
import re


class AnjukespiderSpider(scrapy.Spider):
    name = 'anjukeSpider'
    # allowed_domains = ['https://beijing.anjuke.com/community/']
    start_urls = ["https://beijing.anjuke.com/community/chaoyang/",
                  "https://beijing.anjuke.com/community/haidian/",
                  "https://beijing.anjuke.com/community/dongchenga/",
                  "https://beijing.anjuke.com/community/xicheng/",
                  "https://shenzhen.anjuke.com/community/longgang/",
                  "https://shenzhen.anjuke.com/community/nanshan/",
                  "https://shenzhen.anjuke.com/community/futian/",
                  "https://shenzhen.anjuke.com/community/longhuaq/",
                  "https://shanghai.anjuke.com/community/pudong/",
                  "https://shanghai.anjuke.com/community/minhang/",
                  "https://shanghai.anjuke.com/community/baoshan/",
                  "https://shanghai.anjuke.com/community/xuhui/",
                  "https://shanghai.anjuke.com/community/songjiang/"]

    def parse(self, response):

        try:

            print("正在抓取列表页 ", response.url)
            html = response.text
            mytree = etree.HTML(html)
            titles = mytree.xpath("//div[@class=\"li-itemmod\"]//div[@class=\"li-info\"]/h3/a/@title")
            links = mytree.xpath("//div[@class=\"li-itemmod\"]//div[@class=\"li-info\"]/h3/a/@href")
            address_list = mytree.xpath("//div[@class=\"li-itemmod\"]//div[@class=\"li-info\"]/address//text()")
            prices_list = mytree.xpath("//div[@class=\"li-itemmod\"]//div[@class=\"li-side\"]//strong/text()")
            to_last_months = mytree.xpath(
                "//div[@class=\"li-itemmod\"]//div[@class=\"li-side\"]/p[contains(@class ,\"price-txt\")]//text()")
            dates = mytree.xpath("//div[@class=\"li-itemmod\"]//div[@class=\"li-info\"]//p[@class =\"date\"]//text()")
            newdates = dates[::2]

            info = []
            for title, link, area, price, change, date in zip(titles, links, address_list, prices_list, to_last_months,
                                                              newdates):
                info_dict = {}

                area = area.strip().rstrip().replace(" ", "")
                info_dict['area'] = area
                info_dict['url'] = link
                info_dict['address'] = title
                info_dict['average_prices'] = price
                info_dict['to_last_months'] = change

                if len(re.findall(r'(\d+).*', date)) > 0:
                    date = re.findall(r'(\d+).*', date)[0]
                else:
                    date = "暂无数据"
                info.append(info_dict)

            detail_urls = [d.get("url") for d in info]
            # i =0
            for i, detail_url in enumerate(detail_urls):
                print("跳转detail ", detail_url)
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"info1": info[i]})
                # i+=1
                # if i>1:
                #     break
                # 下一页
            has_next_str = mytree.xpath("//div[@class=\"page-content\"]//*[contains( text(), \"下一页\")]//@class")[0]
            if has_next_str.startswith('a'):
                next_url = mytree.xpath("//div[@class=\"page-content\"]//*[contains( text(), \"下一页\")]//@href")[0]
                print("正在抓取下一页................")
                yield scrapy.Request(
                    url=next_url, callback=self.parse
                )
        except Exception  as  e:
            pass

    def parse_detail(self, response):

        print("正在下载详情页", response.url)
        html = response.body.decode("utf-8", 'ignore')
        info = response.meta['info1']

        res = re.search(r'.*area.*?(\[.*?\]).*', html).group(1)
        if res:
            res_list = eval(res)
            history = []
            for item in res_list:
                for _, v in item.items():
                    history.append(v)
            info['history'] = '|'.join(history)

        from items import AnjukeItem

        item = AnjukeItem()

        for k in info.keys():
            item[k] = info[k]
        yield item
