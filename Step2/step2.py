#!/usr/bin/env python
import json
import os
import sys
from pprint import pprint
import logging
from copy import deepcopy
import glob

def combine(payload_file_name, url_file_name, user_name, password, step1_folder_name = '../Step1/results/'):
    try:
        step2_folder_name = './step2results/'
        results = []
        url_data_with_param = []

        with open(payload_file_name, 'rb') as payload_file:
            payloads = payload_file.read().splitlines()
            print payloads
            print 'payloads', len(payloads)

        # filenames = glob.glob(step_result_folder + '/*.json')
        # for url_file_name in filenames:
        with open(step1_folder_name + url_file_name, 'rb') as url_file:
            url_data = json.load(url_file)
            # filter out all urls without parameters
            url_data_with_param.extend([x for x in url_data['urls'] if x['param']])
            print 'url_data_with_param', len(url_data_with_param)

        for i in url_data_with_param:
            if 'username' in i['param']:
                i['param']['username'] = user_name
            if 'password' in i['param']:
                i['param']['password'] = password

            for payload in payloads:
                item = deepcopy(i)
                updated = False
                for single_param in item['param']:
                    if single_param != 'username' and single_param != 'password' and single_param != 'dologin':
                        item['param'][single_param] = payload
                        updated = True
                # print item
                if updated:
                    results.append(item)

        # # separate them out by post and get
        # post_urls = [x for x in url_data_with_param if x['type'] == 'POST']
        # print 'post_urls', len(post_urls)
        #
        # get_urls = [x for x in url_data_with_param if x['type'] == 'GET']
        # print 'get_urls', len(get_urls)

    except:
        print 'load file with error: ', url_file_name
        raise
    else:
        if not os.path.exists(step2_folder_name):
            os.makedirs(step2_folder_name)
        with open(step2_folder_name+'result_'+ url_file_name, 'w') as fp:
            print 'results:', len(results)
            json.dump(results, fp)


# 'xss_payloads_6-20-12_text_cases.txt'
def step2(payloadfolder_name, step1_folder_name='../Step1/results/'):
    step1_result_file_names = glob.glob(step1_folder_name+'*.json')
    for file_name in step1_result_file_names:
        combine(payloadfolder_name, os.path.basename(file_name), 'username', 'password', step1_folder_name)

step2('payloads.txt')
