import base64
from jphouse.tools.Proxy import Proxy


# Start your middleware class
class ProxyMiddleware(object):
    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        p = Proxy()
        request.meta['proxy'] = p.get_proxy()

        # Use the following lines if your proxy requires authentication
        #proxy_user_pass = "USERNAME:PASSWORD"
        #encoded_user_pass = base64.encodestring(proxy_user_pass)
        #request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
