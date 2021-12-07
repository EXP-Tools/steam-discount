#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import os
import erb.yml as yaml
PRJ_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
CHARSET = 'utf-8'
SETTINGS_PATH = '%s/config/settings.yml' % PRJ_DIR


class Config :

    def __init__(self, settings_path, charset) -> None:
        if os.path.exists(settings_path) :
            with open(settings_path, 'r', encoding=charset) as file:
                context = yaml.load(file.read())
                self.steam = context.get('steam')
                self.database = context.get('database')


settings = Config(SETTINGS_PATH, CHARSET)
