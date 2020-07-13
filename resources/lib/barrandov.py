# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2013 Maros Ondrasek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re
import os
import urllib2
import cookielib
from threading import Lock

import util
from provider import ContentProvider,cached

VIDEOLINK_ITER_RE = 'source src="(?P<url>[^"]+)".+?label=.*? res="(?P<quality>[^"]+)"'

class BarrandovContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'barrandov.tv', 'http://www.barrandov.tv', username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        
    def capabilities(self):
        return ['categories', 'resolve']

    def list(self, page=1):
        result = []
        url = 'moje-zpravy/video?page=%s' % page

        tree = util.parse_html(self._url(url))
        for element in tree.select('.col .show-box--date'):
            title = element.text.strip()
            link = self._url(element.parent.findNextSibling().a['href'])
            img = self._url(element.parent.findNextSibling().img.get('src'))

            item = self.video_item()
            item['title'] = title
            item['url']= link
            item['img']= img
            result.append(item)

        item = self.dir_item()
        item['type'] = 'next'
        item['url'] = str(int(page)+1)
        result.append(item)

        if page > 1:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = str(int(page)-1)
            result.append(item)

        return result
    
    def categories(self):
        return self.list()

    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        item = item.copy()
        data = util.request(self._url(item['url']))
        for m in re.finditer(VIDEOLINK_ITER_RE, data, re.DOTALL | re.IGNORECASE):
            item = self.video_item()
            item['url' ]= self._url(m.group('url'))
            item['quality'] = m.group('quality')
            result.append(item)
        result.reverse()
        return select_cb(result)
