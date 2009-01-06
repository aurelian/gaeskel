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
# Based on http://appengine-cookbook.appspot.com/recipe/match-webapp-urls-using-routes/
#


import os
import sys
import logging
import mimetypes

from google.appengine.ext.webapp import Request
from google.appengine.ext.webapp import Response
from jinja2 import Template, Environment, FileSystemLoader

class WSGIApplication(object):
  """Wraps a set of webapp RequestHandlers in a WSGI-compatible application.
    This is based on webapp's WSGIApplication by Google, but uses Routes library
    (http://routes.groovie.org/) to match url's.
  """
  def __init__(self, mapper, debug = False):
    """Initializes this application with the given URL mapping.
    Args:
      mapper: a routes.mapper.Mapper instance
      debug: if true, we send Python stack traces to the browser on errors
    """
    self.mapper = mapper
    self.__debug = debug
    WSGIApplication.active_instance = self
    logging.info("WSGI initialized")
    self.current_request_args = ()

  def __call__(self, environ, start_response):
    """Called by WSGI when a request comes in."""
    request = Request(environ)
    response = Response()
    WSGIApplication.active_instance = self
    # Match the path against registered routes.
    kargs = self.mapper.match(request.path)
    if kargs is None:
      raise TypeError('No routes match. Provide a fallback to avoid this.')

    # Extract the module and controller names from the route.
    try:
      module_name, class_name = kargs['controller'].split(':', 1)
      del kargs['controller']
    except:
      raise TypeError('Controller is not set, or not formatted in the form "my.module.name:MyControllerName".')

    # Initialize matched controller from given module.
    try:
      __import__(module_name)
      module = sys.modules[module_name]
      controller = getattr(module, class_name)()
      controller.initialize(request, response)
    except Exception, ex:
      raise ImportError('Controller %s from module %s could not be initialized [%s].' % (class_name, module_name, ex))

    # Use the action set in the route, or the HTTP method.
    if 'action' in kargs:
      action = kargs['action']
      del kargs['action']
    else:
      action = environ['REQUEST_METHOD'].lower()
      if action not in ['get', 'post', 'head', 'options', 'put', 'delete', 'trace']:
        action = None

    if controller and action:
      controller.controller_name= class_name
      controller.action_name= action
      controller.logging= logging

      # setup response type:
      format= 'html'
      if 'format' in kargs:
        format= kargs['format']
        del kargs['format']
      response.headers['Content-Type'] , response.headers['Content-Encoding']= \
          mimetypes.guess_type('.'+format)
      controller.format= format
      # setup templating system
      controller.template_name= module_name.split('.').pop() + '/' + action + '.' + format
      # gaeskel/../$controller-module-name/templates
      directory = os.path.join(os.path.dirname(__file__), '..', module_name.split('.')[0])
      path      = os.path.join(directory, os.path.join('templates'))
      controller.template_env= Environment(loader=FileSystemLoader(path))

      logging.info("will execute %s.%s::%s with method %s (wants: %s)" % \
          (module_name, class_name, action, request.method, format))
      logging.info( "Content-Type: %s, Content-Encoding: %s " % \
          (response.headers['Content-Type'], response.headers['Content-Encoding']) )

      # Execute the requested action, passing the route dictionary as named parameters.
      try:
        getattr(controller, action)(**kargs)
        logging.info('action executed!')
      except Exception, e:
        logging.warn('OMG, got an exception: %s' % (e))
        controller.handle_exception(e, self.__debug)
      
      if not controller.action_performed:
        # logging.info('template path: %s' % (path))
        # XXX: this can raise TemplateNotFound
        # controller.template= env.get_template( controller.template_name )
        controller.render()

      response.wsgi_write(start_response)
      return ['']
    else:
      response.set_status(404)

