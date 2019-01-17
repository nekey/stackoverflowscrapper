#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Nikolay Nezhevenko <nikolay.nezhevenko@gmail.com>"
# c:\Python36\Scripts\scrapy.exe crawl comboquestion -o comboquestion.jl --logfile comboquestion.log
# c:\Python36\Scripts\scrapy.exe shell "http://stackoverflow.com/questions/43046151/"




import os
import scrapy
import time


TMP_HTML_DIR = './tmp/'
MAX_PAGE_NUMBER = 1000
PAGE_TIMEOUT = 0.1


class QuestionListSpider(scrapy.Spider):
    name = "questionlist"

    start_urls = [
        'http://stackoverflow.com/questions?page=1&sort=newest',
    ]

    def parse(self, response):
        for link in response.xpath('//div[@id="questions"]//div[@class="summary"]/h3/a/@href').extract():
            yield {'question': {
                'link': link
            }}

        next_link = response.xpath('//div[contains(@class,"pager")]/a/span[contains(text(), "next")]/../@href').extract_first()
        if next_link is not None:
            next_link_full = response.urljoin(next_link)
            self.log("Detected new link = %s" % next_link_full)
            yield scrapy.Request(next_link_full, callback=self.parse)


class QuestionSpider(scrapy.Spider):
    name = "question"

    def start_requests(self):
        urls = [
            'http://stackoverflow.com/questions/43046151/',
            'http://stackoverflow.com/questions/43167045/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # save response as HTML to ./tmp/question
        self.log("Response url = %s" % response.url)
        page = response.url.split("/")[-2]
        filename = 'question-%s.html' % page
        with open(os.path.join(TMP_HTML_DIR, filename), 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        # extract question data
        yield {
            'question': {
                'text': ''.join(response.xpath('//td[@class="postcell"]//div[@class="post-text"]//text()').extract()),
                'date_asked': response.xpath('//td[contains(@class,"owner")]//div[@class="user-action-time"]/span/@title').extract_first()
            },
            'author': {
                'name': response.xpath('//td[contains(@class,"owner")]//div[@class="user-details"]/a/text()').extract_first(),
                'link': response.xpath('//td[contains(@class,"owner")]//div[@class="user-details"]/a/@href').extract_first(),
            }
        }


class ComboQuestionSpider(scrapy.Spider):
    name = "comboquestion"

    def start_requests(self):
        url_pattern = 'http://stackoverflow.com/questions?page=%s&sort=newest'
        # urls = [
        #     'http://stackoverflow.com/questions?page=1&sort=newest',
        # ]
        for i in range(1, MAX_PAGE_NUMBER + 1):
            time.sleep(PAGE_TIMEOUT)
            yield scrapy.Request(url=url_pattern % i,
                                 callback=self.parse_list,
                                 priority=2,
                                 meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]}
                                 )

    def parse_list(self, response):
        self._save_response_body(response)

        # parse questions in list and go for other links
        questions = response.xpath('//div[@id="questions"]//div[@class="summary"]/h3/a/@href').extract()
        if len(questions) != 15:
            self.log("Question count '%s' in list page not valid, resend request by response info '%s'" % (len(questions), response))
            yield scrapy.Request(response.url,
                                  dont_filter=True,
                                  callback=self.parse_list,
                                  priority=2,
                                  meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]}
                                  )

        for question_ref_link in questions:
            question_link = response.urljoin(question_ref_link)
            self.log("List parsing iteration on page: %s" % response.url)
            self.log("Detected question link = %s, scrape it" % question_link)
            request = scrapy.Request(question_link,
                                     callback=self.parse_question_page,
                                     priority=1,
                                     meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]}
                                     )
            # request.meta['item'] = item # TODO!
            yield request

    def parse_question_page(self, response):
        self._save_response_body(response)
        # extract question data
        question_text = ''.join(response.xpath('//td[@class="postcell"]//div[@class="post-text"]//text()').extract())
        question_date_asked = response.xpath('//td[contains(@class,"owner")]//div[@class="user-action-time"]/span/@title').extract_first()
        author_name = response.xpath('//td[contains(@class,"owner")]//div[@class="user-details"]/a/text()').extract_first()
        author_link = response.xpath('//td[contains(@class,"owner")]//div[@class="user-details"]/a/@href').extract_first()

        target_item = {
            'question': {
                'text': question_text,
                'date_asked': question_date_asked
            },
            'author': {
                'name': author_name,
                'link': author_link,
            }
        }

        if not all([question_text, question_date_asked, author_name, author_link]):
            self.log("Some data not scrapped, retry it")
            self.log("Temporary result: %s" % repr(target_item))
            yield scrapy.Request(response.url,
                                  dont_filter=True,
                                  callback=self.parse_question_page,
                                  priority=1,
                                  meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]}
                                  )
        yield target_item

    def _save_response_body(self, response):
        # save response as HTML to ./tmp/question
        self.log("Response url = %s" % response.url)
        page = '_'.join(response.url.split("/")[2:]).replace('&', '_').replace('?', '_').replace(':', '_').replace('%', '_')[:80]
        filename = 'response-%s.html' % page
        with open(os.path.join(TMP_HTML_DIR, filename), 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
