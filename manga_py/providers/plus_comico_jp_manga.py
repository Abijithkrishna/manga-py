from manga_py.provider import Provider
from .helpers.std import Std


class PlusComicoJp(Provider, Std):

    def get_chapter_index(self) -> str:
        return self.re.search('/manga/\d+/(\d+)', self.chapter).group(1)

    def get_content(self):
        content = self._storage.get('main_content', None)
        if content:
            return content
        idx = self.re.search('/manga/(\d+)', self.get_url())
        url = '{}/manga/{}/'.format(self.domain, idx.group(1))
        return self.http_get(url)

    def get_manga_name(self) -> str:
        return self.text_content(self.content, '.stage__body h1')

    def get_chapters(self):
        idx = self.re.search(r'/manga/(\d+)', self.get_url()).group(1)
        with self.http().post('{}/api/getArticleList.nhn'.format(
            self.domain
        ), data={
            'titleNo': idx
        }) as resp:
            json = resp.json()
        items = []
        for i in json.get('result', {}).get('list', {}):
            if i.get('freeFlg', 'N') == 'Y':
                items.append(i.get('articleDetailUrl'))
        return items[::-1]

    def get_files(self):
        content = self.http_get(self.chapter)
        images = [i.get('src') for i in self.document_fromstring(content, '.comic-image > img')]
        images += self.re.findall(r'\'(http://comicimg.comico.jp/onetimecontents/.+)\'', content)
        return images

    def get_cover(self) -> str:
        item = self.document_fromstring(self.content, '.stage div[class^="article-hero"]')
        if item:
            return self.parse_background(item[0])

    def save_file(self, idx=None, callback=None, url=None, in_arc_name=None):
        if in_arc_name is None:
            in_arc_name = '{}_image.jpg'.format(idx)
        super().save_file(idx, callback, url, in_arc_name)


main = PlusComicoJp
