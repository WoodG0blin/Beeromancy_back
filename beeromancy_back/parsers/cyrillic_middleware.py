from urllib.parse import urlparse, urlunparse, unquote

class CyrillicUrlMiddleware:
    def _decode_url(self, url):
        """Внутренний метод для конвертации URL в кириллицу"""
        try:
            parsed_url = urlparse(url)
            cyrillic_netloc = parsed_url.netloc.encode('utf-8').decode('idna')
            cyrillic_path = unquote(parsed_url.path)
            cyrillic_query = unquote(parsed_url.query)
            
            return urlunparse(parsed_url._replace(
                netloc=cyrillic_netloc,
                path=cyrillic_path,
                query=cyrillic_query
            ))
        except Exception:
            return url

    def process_response(self, request, response, spider):
        response._set_url(self._decode_url(response.url))
        return response
