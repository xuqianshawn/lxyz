# -*- coding: utf-8 -*-

BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'

# DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
DUPEFILTER_CLASS = 'project.duplicate_filter.CustomFilter'
DUPEFILTER_DEBUG = True


FEED_FORMAT = "json"
FEED_URI = "tempitems.json"
#DOWNLOAD_HANDLERS={'s3': None}
SPIDER_MIDDLEWARES = {
'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': True,
}


