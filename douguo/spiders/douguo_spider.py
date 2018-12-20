# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import DouguoItem


class DouguoSpiderSpider(scrapy.Spider):
    name = 'douguo_spider'
    allowed_domains = ['api.douguo.net']
    start_urls = ['http://api.douguo.net/recipe/flatcatalogs']
    # offset = 0

    def start_requests(self):
        data = {
            'client': '4'
        }
        yield scrapy.FormRequest(url=self.start_urls[0],formdata=data)

    def parse(self, response):
        items_content = json.loads(response.text)
        # if items_content['state'] == "success":
        # 获取分类名称
        main_content = items_content['result']['catalogs']
        for item in main_content:
            items = DouguoItem()
            items['main_name'] = item['name']
            # 获取类别下的种类，例如蔬菜下的土豆
            for key in item['tags']:
                detail_data = {
                    'client': '4',
                    'order': '0',
                    'keyword': key['t'],
                }
                # print(detail_data)
                for i in range(0,21):   # 不定页数
                    detail_url = 'http://api.douguo.net/recipe/s/{}/15'.format(i*15)
                    # self.offset += 1
                    # 对土豆下的菜品请求
                    yield scrapy.FormRequest(url=detail_url,formdata=detail_data,callback=self.detail_page,meta={'items':items},dont_filter=True)

    def detail_page(self,response):
        items = response.meta.get('items')
        items_content = json.loads(response.text)
        if items_content["result"]['list']:          # 判断是否返回数据，无数据是空列表。
            items['key_name'] = items_content['result']['sts']
            items_list = items_content["result"]['list']
            for item in items_list:
                items['chufang'] = item['r']['an']
                items['caiming'] = item['r']['n']
                yield items
