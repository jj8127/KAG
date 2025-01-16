# -*- coding: utf-8 -*-
# Copyright 2023 OpenSPG Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import ast
from datetime import datetime
import json
import html
import copy
from binascii import b2a_hex
import time
import requests
from Crypto.Cipher import AES
from kag.interface import LLMClient
import logging

logger = logging.getLogger(__name__)


@LLMClient.register("ant_deepseek")
class AntDeepSeekClient(LLMClient):
    def __init__(
        self,
        model: str,
        key: str,
        url: str,
        visitDomain: str,
        visitBiz: str,
        visitBizLine: str,
        cacheInterval: int = -1,
        is_async: bool = False,
        max_tokens: int = 4096,
        n: int = 1,
    ):
        super().__init__()
        self.model = model
        self.key = key
        self.url = url
        self.visitDomain = visitDomain
        self.visitBiz = visitBiz
        self.visitBizLine = visitBizLine
        self.cacheInterval = cacheInterval
        self.is_async = is_async
        self.max_tokens = max_tokens
        self.n = n
        self.param = {
            "visitDomain": self.visitDomain,
            "visitBiz": self.visitBiz,
            "visitBizLine": self.visitBizLine,
            "cacheInterval": self.cacheInterval,
        }

        self.service_names = {
            "sync": "deepseek_chat_completions_dataview",
            "async": "asyn_large_model_query_dataview",  # TODO
            "query": "chatgpt_response_query_dataview",  # TODO
        }

    def aes_encrypt(self, data):
        """
        Encrypts the provided data using AES algorithm.

        Parameters:
            data (str): The data to be encrypted.

        Returns:
            str: The encrypted data.

        Description:
            This function encrypts the provided data using the AES algorithm with CBC mode and a fixed initialization vector (IV).
            If the length of the data is not a multiple of the AES block size, padding is added to make it fit.
            The encrypted data is returned as a hexadecimal string.
        """
        # Fixed initialization vector (IV)
        iv = "1234567890123456"
        # Create an AES cipher using UTF-8 encoded key and CBC mode, IV also encoded in UTF-8
        cipher = AES.new(self.key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        # Get the AES block size
        block_size = AES.block_size

        # Calculate padding needed if data length is not a multiple of block size
        if len(data) % block_size != 0:
            add = block_size - (len(data) % block_size)
        else:
            add = 0
        # Convert data to UTF-8 bytes and add padding
        data = data.encode("utf-8") + b"\0" * add
        # Encrypt the data
        encrypted = cipher.encrypt(data)
        # Convert the encrypted data to a hexadecimal string
        result = b2a_hex(encrypted)
        # Return the encrypted data (as a UTF-8 encoded string)
        return result.decode("utf-8")

    def sync_request(self, prompt):
        # import pdb; pdb.set_trace()
        encodeurl = "%s" % self.url.encode("utf8")

        self.param["serviceName"] = self.service_names["sync"]
        self.param["queryConditions"] = {
            # "url": encodeurl,
            "model": self.model,
            "max_tokens": self.max_tokens,
            # "temperature": self.temperature,
            # "n": self.n,
            # "api_key": self.api_key,
            "messages": prompt,
        }
        data = json.dumps(self.param)
        post_data = {"encryptedParam": self.aes_encrypt(data)}
        response = requests.post(
            self.url,
            data=json.dumps(post_data),
            headers={"Content-Type": "application/json"},
            verify=True,
        )
        return response

    def async_request(self, prompt, message_key):
        encodeurl = "%s" % self.url.encode("utf8")
        self.param["serviceName"] = self.service_names["async"]
        self.param["queryConditions"] = {
            "service_name": self.service_names["sync"],
            "model": self.model,
            "max_tokens": self.max_tokens,
            "request_params": json.dumps(
                {
                    "messages": prompt,
                }
            ),
            "messageKey": message_key,
            "outputType": "PULL",
        }
        data = json.dumps(self.param)
        post_data = {"encryptedParam": self.aes_encrypt(data)}
        response = requests.post(
            self.url,
            data=json.dumps(post_data),
            headers={"Content-Type": "application/json"},
            verify=True,
        )
        return response

    def async_response(self, message_key, interval=1, timeout=120):
        self.param["serviceName"] = self.service_names["query"]
        self.param["queryConditions"] = {
            "messageKey": message_key,
        }
        data = json.dumps(self.param)
        post_data = {"encryptedParam": self.aes_encrypt(data)}

        start_time = time.time()
        count = 1
        while True:
            # logger.info(
            #     f"{count} attempts to query asynchronous deepseek_client response..."
            # )
            response = requests.post(
                self.url,
                data=json.dumps(post_data),
                headers={"Content-Type": "application/json"},
                verify=True,
            )
            values = response.json()["data"]["values"]
            if values:
                logger.info(f"Async response finish after: {time.time() - start_time} s")
                return response

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Polling timed out, exceeding {timeout} seconds.")
            time.sleep(interval)
            count += 1

    def async_generate(self, prompt):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        async_message_key = "KAG_" + str(timestamp * 1000).split(".")[0]
        _response = self.async_request(prompt, async_message_key)
        if _response:
            response = self.async_response(async_message_key)
        else:
            raise ValueError("Async request error.")
        return response

    def parse_response_sync(self, response, **kwargs):
        try:
            x = response.json()["data"]["values"]["data"]
        except Exception as e:
            error_msg = response.json()["msg"]
            data_error = response.json()['data']['errorMessage']
            raise RuntimeError(f"Call error:{error_msg}, msg: {data_error}")
        ast_str = ast.literal_eval("'" + x + "'")
        js = html.unescape(ast_str)
        data = json.loads(js)
        content = data["choices"][0]["message"]["content"]
        content = content.replace("&rdquo;", "”").replace("&ldquo;", "“")
        content = content.replace("&middot;", "")
        return content

    def parse_response_async(self, response, **kwargs):
        x = response.json()["data"]["values"]["response"]
        ast_str = ast.literal_eval("'" + x + "'")
        js = html.unescape(ast_str)
        data = json.loads(js)
        print(data)
        content = data["choices"][0]["message"]["content"]
        content = content.replace("&rdquo;", "”").replace("&ldquo;", "“")
        content = content.replace("&middot;", "")
        return content

    def __call__(self, prompt, image_url=None):
        if image_url:
            content = [
                {"role": "system", "content": "you are a helpful assistant"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ]
            if self.is_async:
                response = self.async_generate(content)
                res = self.parse_response_async(response)
            else:
                response = self.sync_request(content)
                res = self.parse_response_sync(response)
        else:
            content = [{"role": "user", "content": prompt}]
            if self.is_async:
                response = self.async_generate(content)
                res = self.parse_response_async(response)
            else:
                response = self.sync_request(content)
                res = self.parse_response_sync(response)
        return res

    def call_with_json_parse(self, prompt):
        res = self(prompt)
        _end = res.rfind("```")
        _start = res.find("```json")
        if _end != -1 and _start != -1:
            json_str = res[_start + len("```json") : _end].strip()
        else:
            json_str = res
        try:
            json_result = json.loads(json_str)
        except:
            return res
        return json_result
    