#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# notes to self
# http://didipkerabat.com/post/2724838963/nginx-file-upload-and-tornado-framework
# http://kevinworthington.com/nginx-for-mac-os-x-mavericks-in-2-minutes/
# https://github.com/vkholodkov/nginx-upload-module/tree/2.2
# sudo ./configure --prefix=/usr/local --with-http_ssl_module --with-pcre=../pcre-8.33 --add-module=/Users/johantenbroeke/Desktop/nginx-upload-module-2.2m
# sudo /usr/local/sbin/nginx -c /Users/johantenbroeke/Sites/projects/fullscreen_github/blackstripes/blackstripesMK2/webbased_preview/nginx.conf


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import Image
import StringIO
import time

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Blackstripes preview server.")

class UploadHandler(tornado.web.RequestHandler):
    # get post data
    def post(self):
        time.sleep(30)
        imagename = self.get_argument('image.name', default=None)
        path = self.get_argument('image.path', default=None)
        self.write(imagename)
        img = Image.open(path)
        img.save("plaatje.jpg")


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/images/upload", UploadHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
