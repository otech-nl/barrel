''' test a web page by following links '''

import unittest
import requests
import bs4


class NavigationTest(unittest.TestCase):

    root = 'http://localhost:5000'

    def setUp(self):
        self.pages_visited = []
        self.session = requests.Session()

    def tearDown(self):
        print('Pages visited:\n   %s' % '\n   '.join(sorted(self.pages_visited)))

    def login(self, email, password):
        page = '%s/login' % self.root
        print('Logging as %s in via: %s' % (email, page))
        response = self.session.get(page)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            token = soup.find(id='csrf_token').get('value')
            self.session.post(page, data=dict(email=email, password=password, csrf_token=token))

    def logout(self):
        page = '%s/logout' % self.root
        print('Logging out: %s' %  page)
        self.get(page)

    def crawl(self, page, depth=3):
        page = page or self.root
        if page in self.pages_visited or 'logout' in page:
            return
        self.pages_visited.append(page)

        response = self.session.get(page)
        if page != response.url and 'login' in response.url:
            response = self.login(response.url)
            self.pages_visited.append(response.url)
        self.assertEqual(response.status_code, 200, response.url)

        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            print(soup.prettify())
            for link in soup.find_all('a'):
                url = link.get('href')
                if not url.startswith(self.root):
                    url = '%s%s' % (self.root, url)
                self.test_navigation(url, depth - 1)

        def test_users(self):
            for email, password in [('steets@otech', 'test123')]:
                self.login(email, password)
                self.crawl(self.root)
                self.logout()
