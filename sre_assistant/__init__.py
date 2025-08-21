
# -*- coding: utf-8 -*-
# 套件入口：僅導出 VERSION 常數，避免外部誤用內部 API
from .version import VERSION
__all__ = ["VERSION"]
