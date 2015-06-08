
# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


""" Provides requests Authentication providers for use with Riverbed REST APIS

"""

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import base64
import logging
import requests
from requests.packages.urllib3 import util


class RvbdOAuth2(requests.auth.AuthBase):
    """ Authentication handler that implements Riverbed's OAuth2 interface.

    This Authentication provider authenticates appliances that implement
    the /api/common/1.0/oauth/token resource.

    For any response that returns a 401, this Auth provider will request a
    token from the token resource, and re-issues the original request
    transparently to the original request.

    First log in to the appliance and generate an access code from web UI
    Then initialize an auth object as below
    >>> auth = RvbdOAuth2(ACCESS_CODE)
    >>> import requests
    >>> url = 'https://<riverbed_appliance_hostname>/<resource_uri>'
    >>> resp = requests.get(url, auth=auth)
  
    or 
    >>> session = requests.session()
    >>> session.auth = auth
    >>> session.verify = False
    >>> response = session.request(<method>, url, **kwargs)

    """

    log = logging.getLogger("RvbdOAuth2")
    token_resource_uri = '/api/common/1.0/oauth/token'

    def __init__(self, access_code):
        self.access_code = access_code
        self._token = None
        self._auth_type = None

    @property
    def token(self):
        """ Get the authentication Token """
        return self._token

    @token.setter
    def token(self, token):
        """ Set the authentication token """
        parts = token.split('.')
        if len(parts) == 1:
            self._auth_type = "Bearer"
        elif len(parts) == 3:
            self._auth_type = "SignedBearer"
        else:
            raise ValueError("token is in unidentifed format")

        self._token = token

    def _add_auth_header(self, request):
        """ Add Authorization header to a requests.Request

        Args:
            request (requests.Request): The request object add header to.
        """
        if self.token:
            request.headers['Authorization'] = '{type} {token}'.format(
                type=self._auth_type,
                token=self._token)

    def __call__(self, request):
        # modify and return the request
        if not self.token:
            response = self.fetch_token(request.url, request.connection)
            self._add_auth_header(request)
    
        request.register_hook('response', self.handle_response)
        self.log.debug("Making initial request: %r", request)
        return request

    def __eq__(self, other):
        # Define equality based on access code so that a ConnectionManager
        # re-uses an existing connection even if it's a new RvbdOAuth2 object
        return self.access_code ==  other.access_code

    def _get_auth_str(self):
        """Generate a string to post for access token. The string is formatted
        as 'grant_type=<grant_type>&assertion=<assertion>&state=<state>'.
        grant_type should be set as 'access_code'. assertion is formatted as
        '<encoded_header>.<access_code>.<signature>'. 
        """
        import random, string
        header_encoded = base64.urlsafe_b64encode('{"alg":"none"}')
        signature_encoded = ''
        assertion = '.'.join([header_encoded, self.access_code, signature_encoded])

        grant_type = 'access_code'
        state = ''.join(random.choice(string.letters) for i in range(10))

        return 'grant_type=%s&assertion=%s&state=%s' % (grant_type, assertion, state)

    def fetch_token(self, url, session_or_adapter, **kwargs):
        """ Issue a request to fetch an authentication token.

        :param url: Url for the resource to fetch a token for.
        :param session_or_adapter: The Session or Adapter to issue this request
            on.
        :param kwargs:  additional keyword arguments to pass to
            session_or_adapter.send()

        :return: requests.Response, The response content for the request.

        self.token is also set upon a successful token request. This token will
        be used by future requests that use this session object.
        """
        # TODO: support signing algorithms? Should access_code include the alg
        # part too?
        assertion = '.'.join([
            base64.urlsafe_b64encode('{"alg":"none"}'),
            self.access_code,
            ''
        ])
        token_req_data = {
            "grant_type": "access_code",
            "assertion": assertion,
            "state": "random_str"  # TODO: "optional" 400 if not supplied/blank?
        }
        original_url = util.parse_url(url)
        # TODO: Are all API calls https, or do we need to force this to https?
        #new_url = util.Url(scheme=original_url.scheme,
        #                       host=original_url.host,
        #                       port=original_url.port,
        #                       path=self.token_resource_url)
        #new_url = ''
        new_url = original_url.scheme + '://' + original_url.netloc + self.token_resource_uri
        req = requests.Request(method="POST", url=new_url, data=token_req_data)
        
        prepared_request = req.prepare()
        #self.log.debug("Issuing Request to generate token: %s",
        #               prepared_request)
        
        response = session_or_adapter.send(prepared_request, **kwargs)
        
        #response = session_or_adapter.send(prepared_request, **kwargs)
        response.raise_for_status()

        self.token = response.json()['access_token']
        return response

    def handle_response(self, response, **kwargs):
        """ Callback for when response is received

        On 401 responses, issues a request to generate a new token with the
        stored access code, and automatically re-issues the request.

        """
        self.log.debug("Got response: %s", response)
        print("Got response %s" % response)
        print(response.status_code)
        if response.status_code == 401:
            # consume content so we can get the token and re-issue the request
            response.content
            response.raw.release_conn()

            token_response = self.fetch_token(response.request.url,
                                              response.connection,
                                              **kwargs)
            token_response.history.append(response)
            self._add_auth_header(response.request)
            self.log.debug("Re-issuing request: %s", response.request)
            new_response = response.connection.send(response.request, **kwargs)
            new_response.history.append(token_response)
            self.log.debug("Got response: %s", new_response)
            return new_response
        else:
            return response
