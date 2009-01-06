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

import urlparse

class Application(object):

  def __init__(self):
    self.request= None
    self.response= None
    self.logging= None
    
    self.controller_name= None
    self.action_name= None
    
    self.template_env= None
    self.template_name= None
    self.template_variables= {}

    self.action_performed= False

  def initialize(self, request, response):
    self.request= request
    self.response= response

    self.template_variables= {
        'controller':self.controller_name, 
        'action':self.action_name,
        'request':self.request
      }
  
  def index(self, id= None):
    self.render_text('Hello World!')

  # {{{ renders

  def render(self, wha= None):
    if wha is None:
      template= self.template_env.get_template( self.template_name )
    else:
      template= self.template_env.get_template( wha )
    self.response.out.write( template.render( self.template_variables ) )
    self.action_performed= True

  def render_text(self, text):
    self.response.headers['Content-Type']= 'text/plain'
    self.response.out.write( text )
    self.action_performed= True

  # }}}

  # {{{ redirects

  def redirect(self, uri, permanent= False):
    if permanent:
      self.response.set_status(301)
    else:
      self.response.set_status(302)
    absolute_url = urlparse.urljoin(self.request.uri, uri)
    self.logging.info('will redirect to %s' % (str(absolute_url)))
    self.response.headers['Location'] = str(absolute_url)
    self.response.clear()
    self.action_performed= True

  # }}}

  def handle_exception(self, exception, debug):
    import traceback
    self.response.clear()
    self.response.headers['Content-Type']= 'text/plain'
    self.response.out.write( "Got exception: %s with message:\n%s\n\nResponse Headers:\n%s\n" % \
        (exception.__class__, exception, self.response.headers) )
    self.action_performed= True

