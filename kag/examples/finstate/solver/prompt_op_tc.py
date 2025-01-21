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

from abc import ABC
from string import Template
from typing import List

class PromptOpTC(ABC):
    """
    Provides a template for generating and parsing prompts related to specific business scenes.

    Subclasses must implement the template strings for specific languages (English or Chinese)
    and override the `template_variables` and `parse_response` methods.
    """

    """English template string"""
    template_en: str = ""
    """Chinese template string"""
    template_zh: str = ""

    def __init__(self, language = "en", **kwargs):
        """
        Initializes the PromptOp instance with the selected language.

        Args:
            language (str): The language for the prompt, should be either "en" or "zh".

        Raises:
            AssertionError: If the provided language is not supported.
        """

        self.template = self.template_en if language == "en" else self.template_zh
        self.language = language
        self.template_variables_value = {}

    @property
    def template_variables(self) -> List[str]:
        """
        Gets the list of template variables.

        Must be implemented by subclasses.

        Returns:
        - List[str]: A list of template variable names.

        Raises:
        - NotImplementedError: If the subclass does not implement this method.
        """

        return ["question", "context", "error", "dk"]

    def process_template_string_to_avoid_dollar_problem(self, template_string):
        new_template_str = template_string.replace('$', '$$')
        for var in self.template_variables:
            new_template_str = new_template_str.replace(f'$${var}', f'${var}')
        return new_template_str

    def build_prompt(self, input_str, variables) -> str:
        """
        Build a prompt based on the template and provided variables.

        This method replaces placeholders in the template with actual variable values.
        If a variable is not provided, it defaults to an empty string.

        Parameters:
        - variables: A dictionary containing variable names and their corresponding values.

        Returns:
        - A string or list of strings, depending on the template content.
        """

        self.template_variables_value = variables
        template_string = self.process_template_string_to_avoid_dollar_problem(input_str)
        template = Template(template_string)
        return template.substitute(**variables)

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = rsp.strip("```").strip("python")
        return rsp
