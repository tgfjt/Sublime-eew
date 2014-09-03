# -*- coding: utf8 -*-

import sublime
import sublime_plugin
import urllib
import os
import codecs
from datetime import datetime as dt


api_url = 'http://api.p2pquake.net/userquake'
tmp = []
message = '地震速報: %s頃, %sで震度%sの地震が発生しました。'
package_path = sublime.packages_path()
cache_file = os.path.join(package_path + '/Sublime-eew/cache/result.txt')

f = codecs.open(cache_file, 'r', 'utf-8')
result = f.readlines()
f.close()


class EewListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        view.run_command('eew_update')

    def on_post_save_async(self, view):
        view.run_command('eew_update')

    def on_pre_close(self, view):
        f = codecs.open(cache_file, 'w', 'utf-8')
        f.write('')
        f.close()


class EewUpdate(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_status('eew_result', self.update())

    def message(self, str):
        arr = str.split('/')
        return message % (arr[0], arr[4], arr[1])

    def update(self):
        url = self.get_url()
        res = urllib.request.urlopen(url)
        data = res.read().decode('sjis')

        if data == '':
            return ''

        cr = data.split('\n')

        for row in cr:
            # 地震感知情報は省く
            if row and row.split(',')[1] != 'UQU':
                tmp.append(row.split(',')[2])

        tmp.reverse()
        str = tmp[0].replace('\r', '')

        if result:
            if result[0].replace('\n', '') == str:
                # 同じ結果の場合は、空にする
                return ''
        else:
            result[:] = tmp
            f = codecs.open(cache_file, 'w', 'utf-8')
            f.write(str)
            f.close()

        return self.message(tmp[0])

    def get_query(self):
        date = dt.now()
        query = {
            'date': date.strftime('%m/%d')
        }
        return urllib.parse.urlencode(query)

    def get_url(self):
        return api_url + '?' + self.get_query()
