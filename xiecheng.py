from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import re
import csv

count = 0


class trains_routine_infurmation(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_request(self):
        broswer = webdriver.Chrome()
        try:
            broswer.get('https://www.ctrip.com/')
        except exceptions.WebDriverException or exceptions.TimeoutException as e:
            print('Error in Response', e.args)
        try:
            train_url = broswer.find_element_by_id('cui_nav').find_elements_by_id('nav_trains')[0].get_attribute('href')
            broswer.get(train_url)
            broswer.forward()
            EC = WebDriverWait(broswer, 5)
            inupt_start_city = broswer.find_elements_by_id('notice01')[0]
            inupt_start_city.send_keys(self.start)
            input_end_city = broswer.find_element(By.ID, 'notice08')
            input_end_city.send_keys(self.end)
            # broswer.find_element_by_id('dateObj').click() 执行JavaScript才可以选择日期
            broswer.find_element_by_id('searchbtn').click()
            broswer.forward()
            return broswer.page_source
        except exceptions.ErrorInResponseException as e:
            print('ErrorInResponse', e.args)

    def parse_page(self, source_page):
        soup = BeautifulSoup(source_page, 'lxml')
        train_list_information = soup.find_all('div', class_='tbody')
        trains_infoamation = {}
        for train in train_list_information:
            trains_infoamation['train_name'] = train.find('div', class_='w1').find('strong').string
            trains_infoamation['start_time'] = train.find('div', class_='w2').find('strong').string
            trains_infoamation['start_city'] = train.find('div', class_='w2').find('span').string
            trains_infoamation['take_time'] = train.find('div', class_='w4').find('div', class_='haoshi').contents[0]
            trains_infoamation['end_time'] = train.find('div', class_='w3').find('strong').string
            trains_infoamation['end_city'] = train.find('div', class_='w3').find('span').string
            seats_information = train.find('div', class_='w5 ').contents
            for i, seat_information in enumerate(seats_information):
                list1 = []
                if not seat_information == '\n':
                    list1.append(seat_information.find('span').string)
                    list1.append(seat_information.find('b').string)
                    if seat_information.find('strong').string is not None:
                        list1.append(seat_information.find('strong').string)
                    trains_infoamation['seattype{0}_price'.format(i)] = list1.copy()
                list1.clear()
            yield trains_infoamation
    def save_to_csv(self, information):
        fieldnames = information.keys()
        with open("D://raw_data.csv", 'a+', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if count == 0:
                writer.writeheader()
            writer.writerow(information)

if __name__ == '__main__':
    start = input('请输入出发城市：')
    end = input('请输入到达城市：')
    item = trains_routine_infurmation(start, end)
    response = item.get_request()
    results = item.parse_page(response)
    for result in results:
        print(result)
        count += 1
        item.save_to_csv(result)
        print('已将{0}条数据写入文件'.format(count))
    print('共{0}条数据'.format(count))
