#!/usr/bin/env python
#
# Copyright 2008, 2009 Aurelian Oancea
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
#

import os
import sys
import logging
from config import Routes
from gaeskel.wsgi import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

#
# not used.
# format-> mimetype
# def MimeTypes():
#  return= {
#      'html':'text/html',
#      'xml':'application/xml',
#      'rss':'application/rss+xml',
#      'atom':'application/atom+xml',
#      'pdf':'application/pdf'
#  }
#

def Main():
  app = WSGIApplication(Routes(), debug = True)
  run_wsgi_app(app)

if __name__ == '__main__':
  Main()

