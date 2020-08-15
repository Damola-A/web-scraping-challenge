#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import requests
import os
import datetime as dt

executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless=False)

mars_web = {}
def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    news_soup = bs(html, 'html.parser')

    news_title = (news_soup.find_all('div', class_='content_title'))[0].get_text()
    news_p = (news_soup.find_all('div', class_='article_teaser_body'))[0].get_text()
    
    mars_web['news_title'] = news_title
    mars_web['news_paragraph'] = news_p
   
    browser.quit()
    return mars_web

def featured_image(browser):
    jurl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jurl)

    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()
    
    html_image = browser.html
    soup_image = bs(html_image, 'html.parser')

    img = soup_image.select_one("figure.lede a img")
    try:
        img_url = img.get("src")
    except AttributeError:
        return None 
    img_url = f"https://www.jpl.nasa.gov{img_url}"
    return img_url


def twitter_weather(browser):
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    
    html_weather = browser.html
    soup_weather = bs(html_weather, 'html.parser')
    
    mars_weather_tweet = soup_weather.find("div", 
                                       attrs={
                                           "class": "tweet", 
                                            "data-name": "Mars Weather"
                                        })

    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()
    return mars_weather


def mars_facts():
    try:
        df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None
    df.columns=["Description", "Value"]
    df.set_index("Description", inplace=True)

    return df.to_html(classes="table table-striped")


def hemisphere(browser):
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    hemisphere_image_urls = []
     
    links = browser.find_by_css("a.product-item h3")
    for item in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[item].click()
        sample_element = browser.find_link_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        hemisphere["title"] = browser.find_by_css("h2.title").text
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()
    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    hemisphere_soup = bs(html_text, "html.parser")
    try: 
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_element = None
        sample_element = None 
    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemisphere

def scrape_all():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    browser = Browser("chrome", **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    img_url = featured_image(browser)
    mars_weather = twitter_weather(browser)
    facts = mars_facts()
    hemisphere_image_urls = hemisphere(browser)
    timestamp = dt.datetime.now()

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": img_url,
        "weather": mars_weather,
        "facts": facts,
        "hemispheres": hemisphere_image_urls,
        "last_modified": timestamp
    }
    browser.quit()
    return data


print("Done") 

