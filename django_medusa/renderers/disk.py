from django.conf import settings
from django.test.client import Client
import mimetypes
import os
from .base import COMMON_MIME_MAPS, BaseStaticSiteRenderer

__all__ = ('DiskStaticSiteRenderer', )



class DiskStaticSiteRenderer(BaseStaticSiteRenderer):
    @classmethod
    def initialize_output(cls):
        cls.redirects = []

    @classmethod
    def finalize_output(cls):
        if not cls.redirects:
            return
        DEPLOY_DIR = settings.MEDUSA_DEPLOY_DIR
        filename = os.path.join(DEPLOY_DIR, '.htaccess')
        contents = ''
        if os.path.exists(filename):
            with open(filename) as f:
                contents = f.read()
        fmt = 'Redirect {} {} {}\n\n'
        for redirect in cls.redirects:
            contents += fmt.format(*redirect)
        with open(filename, 'w') as f:
            f.write(contents)
        print "Generated .htaccess"


        
        

    def _prepare_path(self, path):
        DEPLOY_DIR = settings.MEDUSA_DEPLOY_DIR
        realpath = path
        if path.startswith("/"):
            realpath = realpath[1:]

        output_dir = os.path.abspath(os.path.join(
            DEPLOY_DIR,
            os.path.dirname(realpath)
        ))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        outpath = os.path.join(DEPLOY_DIR, realpath)
        return outpath


    def handle_non_200(self, path, resp):
        if resp.status_code == 301 or resp.status_code == 302:
            location = resp['Location']
            location = self._get_path_with_ext(location, location, resp)
            path = self._get_path_with_ext(path, path, resp)
            
            DiskStaticSiteRenderer.redirects.append((resp.status_code, path, location))
            print "[{}] {} -> {}".format(resp.status_code, path, location)
        else:
            raise ValueError("Can not handle status {} at path {}".format(resp.status_code, path))


    def _get_path_with_ext(self, path, outpath, resp):
        if path.endswith("/"):
            needs_ext = True
        else:
            needs_ext = False

        if needs_ext:
            mime = resp['Content-Type']
            mime = mime.split(';', 1)[0]

            # Check our override list above first.
            ext = COMMON_MIME_MAPS.get(
                mime,
                mimetypes.guess_extension(mime)
            )
            if ext is None:
                ext = ".html"
            outpath += "index" + ext
        return outpath
        

    def _write_to_disk(self, path, outpath, resp):
        outpath = self._get_path_with_ext(path, outpath, resp)
        print "[{}] {} -> {}".format(resp.status_code, path, outpath)
        with open(outpath, 'w') as f:
            f.write(resp.content)
        

    def _disk_render_path(self, path):
        outpath = self._prepare_path(path)

        resp = self.client.get(path)
        if resp.status_code != 200:
            self.handle_non_200(path, resp)
            return

        self._write_to_disk(path, outpath, resp)


    def render_path(self, path):
        self._disk_render_path(path)

    def generate(self, defaults=None):
        if defaults is None:
            defaults = {}
        self.client = Client(**defaults)
        for path in self.paths:
            self.render_path(path)
