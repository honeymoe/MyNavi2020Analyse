# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MyNavi2020_Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ID = scrapy.Field()
    Update = scrapy.Field()
    Honsha = scrapy.Field()
    Name = scrapy.Field()
    Business_Area = scrapy.Field()
    Location = scrapy.Field()
    Email = scrapy.Field()
    Number_of_Employeees = scrapy.Field()
    Overtime_avg = scrapy.Field()
    Capital = scrapy.Field()
    Sales = scrapy.Field()
    Paid_avg = scrapy.Field()

    Salary = scrapy.Field()
    #Bonus = scrapy.Field()
    Vacation = scrapy.Field()
    Worktime = scrapy.Field()
    Pickup = scrapy.Field()
    Pickup_Tags = scrapy.Field()