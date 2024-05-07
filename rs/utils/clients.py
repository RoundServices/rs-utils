# rs-utils is available under the MIT License. https://github.com/RoundServices/rs-utils/
# Copyright (c) 2022, Round Services LLC - https://roundservices.biz/
#
# Author: Ezequiel O Sandoval - esandoval@roundservices.biz
#

import requests
import json
import jwt
from rs.utils import http, validators
from rs.utils.basics import Logger


class OIDCClient:
    """
    OIDCClient has multiple basic functionality that can be useful for OpenID python interactions
    """
    def __init__(self, idp_url, logger=Logger("OIDCClient"), verify=True):
        """
        Params
        :param idp_url: for instance 'https://myidp.myorg.com'
        :param logger: RoundServices log. If None, default will be created
        """
        self.idp_url = idp_url
        self.logger = logger
        self.verify = verify
        self.well_known = self.get_well_known()

    def get_well_known(self):
        """
        Executes a basic request to .well-known endpoint from a standard IDP
        :return: a dict that represent the information from endpoint. otherwise it will raise an error
        """
        url = self.idp_url + "/.well-known/openid-configuration"
        self.logger.trace("GET request to {}", url)
        response = requests.get(url, verify=self.verify)
        http.validate_response(response, self.logger, "Can not reach Wellknown endpoint, with idp_url {} - DNS or host file?", self.idp_url)
        well_known_json = response.json()
        self.logger.trace("obtained wellknown info: {}", well_known_json)
        return well_known_json

    def validate_idp(self):
        """
        Checks connectivity with the idp well-known endpoint and verifies the issuer.
        :return: Boolean if there is no connectivity issues. Otherwise raise an error
        """
        self.logger.trace("Validating IDP with idp_url {}", self.idp_url)
        return self.get_well_known()['issuer'] == self.idp_url

    def request_to_token_endpoint(self, b64_client_credentials, params_in_dict):
        """
        Executes a POST request to IDP token endpoint with Content-type 'application/x-www-form-urlencoded',
        authenticates clients ONLY in BASIC mode.
        :param b64_client_credentials: 'client_id:client_secret' in base64 encode type
        :param params_in_dict: receives all POST parameters in a dict
        :return: a dict that represents json response from endpoint. otherwise raise an error
        """
        self.logger.trace("Getting AccToken with these values {}", params_in_dict)
        payload = ""
        for k, v in params_in_dict.items():
            payload = "{}={}&{}".format(k, v, payload)
        self.logger.trace("about to request acc_token with this payload {}", payload)
        response = requests.request("POST", self.well_known['token_endpoint'], data=payload, headers=self._get_basic_header(b64_client_credentials), verify=self.verify)
        http.validate_response(response, self.logger, "Can not get access_token with these values {} - HTTP {}", payload, response.status_code)
        response_json = response.json()
        self.logger.debug("JSON Response obj is: {}", response_json)
        return response_json

    def _get_basic_header(self, credentials):
        """
        returns a basic header for post operations, adding client_credentials
        :param credentials: 'client_id:client_secret' in base64 encoded format
        :return: a dict that represents a HTTP Header
        """
        return {
            'Authorization': "Basic %s" % credentials,
            'Cache-Control': "no-cache",
            'Content-Type': "application/x-www-form-urlencoded",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

    def validate_jwt(self, claims, token, error_claim=None):
        """
        Validates a jwt based on the presence of claims' list and the ausence of an error_claim inside the token
        :param claims: list of strings that represent claims inside the token
        :param token: jwt to be decoded and validated
        :param error_claim: default None, is an string that represents a claim that warns about an error inside the token
        :return: Boolean
        """
        self.logger.debug('validate_jwt - token: {} - claims: {} - error_claim: {}', token, claims, error_claim)
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
        except Exception as err:
            self.logger.error("Could not decode token err msg: {}", err)
            return False
        self.logger.debug('Decoded token: {}', decoded_token)
        for key in claims:
            if key not in decoded_token:
                self.logger.error("{} key is not included in json", key)
                return False
        return False if error_claim is not None and error_claim in decoded_token else True


class UMAClient:
    """
    Provides basic UMA interaction on a protected UMA API - clients authenticate with basic_credentials
    """

    def __init__(self, api_base_endpoint, b64_client_credentials, logger=Logger("UMAClient"), verify=True, is_gluu_45=False):
        """
        Constructor
        :param api_base_endpoint: for instance "https://myidp.org.com/identity/restv1/api/v1
        :param b64_client_credentials: 'client_id:client_secret' in base64 encoded format
        :param logger: RoundServices log. If it is None, default will be created.
        """
        self.api_base_endpoint = api_base_endpoint
        self.b64_client_credentials = b64_client_credentials
        self.logger = logger
        self.verify = verify
        self.is_gluu_45 = is_gluu_45
        self.logger.debug("is_gluu_45 deployment: {}", is_gluu_45)

    def get_rpt(self, path, operation="GET"):
        """
        Gets an RPT from API endpoint.
        First gets a ticket (401 HTTP error with a header called ticket in response), then
        uses that ticket to obtain RPT from IDP token endpoint
        :param path: to the requested endpoint (it will be concatenated to api_base_endpoint)
        :param operation: Default GET, can be one of HTTP Methods
        :return: an String that represents a valid access_token for that resource. otherwise raise an error.
        """

        if not self.is_gluu_45:
            url = self.api_base_endpoint + "/" + path
            self.logger.trace("Starting RPT with url {} with operation: {}", url, operation)
            response = requests.request(operation, url, data="", headers=self._get_operation_headers(""), verify=self.verify)
            if response.status_code != 401:
                response.close()
                validators.raise_and_log(self.logger, IOError, "Can not get ticket to be exchanged for RPT, maybe UMA not enabled? - HTTP {}", response.status_code)
            ticket = dict(x.split("=") for x in response.headers['WWW-Authenticate'].split(",")).get(' ticket')
            self.logger.trace("Ticket value is {}", ticket)
            response.close()
            idp_url = "/".join(self.api_base_endpoint.split("/", 3)[:3])
            self.logger.trace("idp_url is {}", idp_url)
            payload = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
                'ticket': ticket
            }
        else:
            idp_url = "/".join(self.api_base_endpoint.split("/", 3)[:3])
            self.logger.trace("idp_url is {}", idp_url)
            payload = {
                'grant_type': 'client_credentials',
                'scope': '\
                https://gluu.org/auth/oxtrust.attribute.read \
                https://gluu.org/auth/oxtrust.attribute.write \
                https://gluu.org/auth/oxtrust.authenticationmethod.read \
                https://gluu.org/auth/oxtrust.authenticationmethod.write \
                https://gluu.org/auth/oxtrust.client.read \
                https://gluu.org/auth/oxtrust.client.write \
                https://gluu.org/auth/oxtrust.customscript.read \
                https://gluu.org/auth/oxtrust.customscript.write \
                https://gluu.org/auth/oxtrust.ldapauthentication.read \
                https://gluu.org/auth/oxtrust.ldapauthentication.write \
                https://gluu.org/auth/oxtrust.OxauthjsonSetting.read \
                https://gluu.org/auth/oxtrust.oxauthjsonSetting.write \
                https://gluu.org/auth/oxtrust.oxtrustjsonSetting.write \
                https://gluu.org/auth/oxtrust.oxtrustjsonSetting.read \
                https://gluu.org/auth/oxtrust.oxtrustsetting.read \
                https://gluu.org/auth/oxtrust.oxtrustsetting.write \
                https://gluu.org/auth/oxtrust.saml.read \
                https://gluu.org/auth/oxtrust.saml.write \
                https://gluu.org/auth/oxtrust.scope.read \
                https://gluu.org/auth/oxtrust.scope.write \
                https://gluu.org/auth/oxtrust.smtpconfiguration.read \
                https://gluu.org/auth/oxtrust.smtpconfiguration.write'
            }
        return OIDCClient(idp_url, self.logger, self.verify).request_to_token_endpoint(self.b64_client_credentials, payload)['access_token']

    def get(self, sub_path):
        """
        GET operation
        :param sub_path: string that will be concatenated with api_base_endpoint
        :return: dict, represent json_obj returned by API
        """
        return self.execute("GET", sub_path)

    def post(self, sub_path, json_obj):
        """
        POST operation
        :param sub_path: string that will be concatenated with api_base_endpoint
        :param json_obj: dict, represents body params
        :return: dict, represent json_obj returned by API
        """
        return self.execute("POST", sub_path, json_obj)

    def put(self, sub_path, json_obj):
        """
        PUT operation
        :param sub_path: string that will be concatenated with api_base_endpoint
        :param json_obj: dict, represents body params
        :return: dict, represent json_obj returned by API
        """
        return self.execute("PUT", sub_path, json_obj)

    def delete(self, sub_path):
        """
        DELETE operation
        :param sub_path: string that will be concatenated with api_base_endpoint
        :return: dict, represent json_obj returned by API
        """
        return self.execute("DELETE", sub_path)

    def execute(self, operation, sub_path, json_obj=None, rpt=None):
        """
        Executes HTTP calls on protected UMA API
        :param operation: GET/POST/PUT/DELETE string
        :param sub_path: string that will be concatenated with api_base_endpoint
        :param json_obj: Parameters on body message, used for POST/PUT operations, default None
        :param rpt: Optional
        :return: returns a dict based on the json returned by API
        """
        url = "{}/{}".format(self.api_base_endpoint, sub_path)
        body = "" if json_obj is None else json.dumps(json_obj)
        self.logger.debug("""
        UMA requests with params:
        operation: {}
        url: {}
        json_obj: {}
        """, operation, url, json.dumps(json_obj))
        response = requests.request(
            operation,
            url,
            data=body,
            headers=self._get_operation_headers(self.get_rpt(sub_path, operation) if rpt is None else rpt),
            verify=self.verify
        )
        http.validate_response(response, self.logger, "Execute Failed - HTTP Code: {}".format(response.status_code))
        try:
            return response.json()
        except:
            return {}

    def _get_operation_headers(self, ticket):
        """
        Generates a dict that represents a HTTP headed for a requests call with an RPT for UMA requests.
        :param ticket: RPT token value
        :return: a dict to be used as a 'headers' parameter on a request object
        """
        return {
            'Authorization': "Bearer %s" % ticket,
            'Content-Type': "application/json",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

