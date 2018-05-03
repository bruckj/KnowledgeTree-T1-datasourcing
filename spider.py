import re
import json,ast
from urlparse import urlparse
import urllib
import pdb
import os.path
import sys


from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.http import Request


from googlescholar.items import *
from misc.log import *
from misc.spider import CommonSpider


def _monkey_patching_HTTPClientParser_statusReceived():
    """
    monkey patching for scrapy.xlib.tx._newclient.HTTPClientParser.statusReceived
    """
    from twisted.web._newclient import HTTPClientParser, ParseError
    old_sr = HTTPClientParser.statusReceived

    def statusReceived(self, status):
        try:
            return old_sr(self, status)
        except ParseError, e:
            if e.args[0] == 'wrong number of parts':
                return old_sr(self, status + ' OK')
            raise
    statusReceived.__doc__ == old_sr.__doc__
    HTTPClientParser.statusReceived = statusReceived


class googlescholarSpider(CommonSpider):
    name = "googlescholar"
    allowed_domains = ["google.com"]
    with open("terms.txt", 'r') as f:
        termstohandle=[line.strip() for line in f]
    #testurl="https://scholar.google.com/scholar?as_ylo=2011&q=machine+learning&hl=en&as_sdt=0,5"
    start_urls = [
        #'"https://scholar.google.com/scholar?as_ylo=2011&q=", midstring + "&hl=en&as_sdt=0,5"'
        #"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&as_ylo=2011&q=saccharomyces+cerevisiae&btnG=",
		#"http://scholar.google.com/scholar?as_ylo=2011&q=machine+learning&hl=en&as_sdt=0,5",
        #"http://scholar.google.com/scholar?q=estimate+ctr&btnG=&hl=en&as_sdt=0%2C5&as_ylo=2011",
        #"http://scholar.google.com",
        #testurl
    ]
    for x in termstohandle:
        x=x.replace(" ", "+")
        x="https://scholar.google.com/scholar?as_ylo=2011&q={}&hl=en&as_sdt=0,5".format(x)
        start_urls.append(x)
    #with open('letssee.txt', 'w') as f:
        #for x in start_urls:
            #f.write("%s\n" % x)
    rules = [
        Rule(sle(allow=("scholar\?.*")), callback='parse_1', follow=False),
        Rule(sle(allow=(".*\.pdf"))),
    ]

    def __init__(self, start_url='', *args, **kwargs):
        _monkey_patching_HTTPClientParser_statusReceived()
        if start_url:
            self.start_urls = [start_url]
        super(googlescholarSpider, self).__init__(*args, **kwargs)

    #.gs_ri: content besides related html/pdf
    list_css_rules = {
        '.gs_r': {
            'title': '.gs_rt a *::text',
            'url': '.gs_rt a::attr(href)',
            'related-text': '.gs_ggsS::text',
            'related-type': '.gs_ggsS .gs_ctg2::text',
            'related-url': '.gs_ggs a::attr(href)',
            'citation-text': '.gs_fl > a:nth-child(1)::text',
            'citation-url': '.gs_fl > a:nth-child(1)::attr(href)',
            'authors': '.gs_a a::text',
            'description': '.gs_rs *::text',
            'journal-year-src': '.gs_a::text',
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            _monkey_patching_HTTPClientParser_statusReceived()
            yield Request(url, dont_filter=True)

    # def save_pdf(self, response):
        # #path = self.get_path(response.url)
        # #path=response.url.split("/")[-2]
        # #path="./pdfs/item['title'].pdf"
        # #info(path)
        # g=open('confirm.txt','a')
        # g.write("confirmed \n")
        # g.close()
        # with open(os.path.join("C:\Users\Zsolt\pdfs",response.title+".pdf"), wb) as f:
            # f.write(response.body)
        # #with open(path, "wb") as f:
            # #f.write(response.body)

    def parse_1(self, response):
        info('Parse '+response.url)
        #i=0
        #sel = Selector(response)
        #v = sel.css('.gs_ggs a::attr(href)').extract()
        #import pdb; pdb.set_trace()
        x = self.parse_with_rules(response, self.list_css_rules, dict)
        items = []
        if len(x) > 0:
            items = x[0]['.gs_r']
            pp.pprint(items)
        for item in items:
            #i+=1
            #['related-url']=['related
            #l=len(item['related-url'])
            item['journal-year-src'] = item['journal-year-src'].encode('ascii', 'ignore').decode('ascii')
            splitindex=item['journal-year-src'].find('-')
            item['authors']=item['authors']+item['journal-year-src'][:splitindex]
            item['journal-year-src']=item['journal-year-src'][splitindex:]
            #g=open('resultsML4.txt','a')
            #g.write(str(item)+"\n"+str(item['journal-year-src'])+"\n")
            #g.write(str(item)+"\n")
            #g.write(str(item['journal-year-src'])+"\n")
            #g.write("{} \n" .format(i))
            #g.close()
        #import pdb; pdb.set_trace()
        # return self.parse_with_rules(response, self.css_rules, googlescholarItem)

        for item in items:
            l=len(item['related-url'])-3
            #f=open('endings.txt', 'a')
            #f.write(str(item['related-url'][l:])+"\n")
            #f.close()
            item['related-url']=urllib.unquote(item['related-url'])
            if item['related-url'] == '' or item['related-url'][l:] != 'pdf':
                #g=open('test2.txt', 'a')
                #g.write(str(item['related-url'])+"\n")
                #g.close()
                continue
            url = item['related-url']
            info('pdf-url: ' + url)
            #g=open('test.txt', 'a')
            #g.write(str(item['related-url'])+"\n")
            #g.write(str(item['title'])+"\n")
            #g.close()
            #if item['title'] == '':
            #   name=item['related-url'][7:]
            #else:
            name=((item['title']+".pdf")).replace(":", "_")
            #finalname=name.replace(" ", "_")
            #finalname=finalname.replace(":", "_")
            urllib.urlretrieve(url, str(name))
            #yield Request(url, callback=self.save_pdf)
        import pdb; pdb.set_trace()
