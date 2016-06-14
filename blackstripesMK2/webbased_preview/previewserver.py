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
# git clone -b 2.2 git://github.com/vkholodkov/nginx-upload-module.git nginx-upload-module-2.2m
# sudo ./configure --prefix=/usr/local --with-http_ssl_module --with-pcre=../pcre-8.33 --add-module=/Users/johantenbroeke/Desktop/nginx-upload-module-2.2m
# sudo /usr/local/sbin/nginx -c /Users/johantenbroeke/Sites/projects/fullscreen_github/blackstripes/blackstripesMK2/webbased_preview/nginx.conf


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

from PIL import Image as Image
import webbased_preview

import hashlib

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Blackstripes preview server.")

class UploadHandler(tornado.web.RequestHandler):

    def post(self):
        imagename = self.get_argument('image.name', default=None)
        path = self.get_argument('image.path', default=None)

        m = hashlib.md5()
        m.update(path+"fullscreen zacht spul is beter")
        md5str = m.hexdigest()

        pr = webbased_preview.Cropper(path,md5str,self.version)
        self.write(pr.getJSON())

class UploadHandler_v1(UploadHandler):
    version = "v1"

class UploadHandler_v2(UploadHandler):
    version = "v2"

class UploadHandler_v3(UploadHandler):
    version = "v3"

class ColorHandler(tornado.web.RequestHandler):

    def get(self,version,image_id):
        if version == "v3":
            pr = webbased_preview.SketchyColorOptions(image_id,version)
            self.write(pr.getJSON())
        else:
            pr = webbased_preview.ColorOptions(image_id,version)
            self.write(pr.getJSON())

class PreviewHandler(tornado.web.RequestHandler):

    def get(self,version,image_id):
        if version == "v3":
            pass
        else:
            pr = webbased_preview.Preview(image_id,version)
            self.write(pr.getJSON())

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/v1/images/upload", UploadHandler_v1),
        (r"/v2/images/upload", UploadHandler_v2),
        (r"/v3/images/upload", UploadHandler_v3),
        (r"/?(?P<version>[^\/]+)?/color/?(?P<image_id>[^\/]+)?", ColorHandler),
        (r"/?(?P<version>[^\/]+)?/preview/?(?P<image_id>[^\/]+)?", PreviewHandler),
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './www/static/'}),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
