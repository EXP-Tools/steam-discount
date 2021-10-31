# steam-discount
Steam 特惠游戏榜单

------

## 运行环境

![](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg) 


## 项目介绍

从 Steam 商城爬取游戏的【打折（史低）】、【测评】、【热度】情况的榜单整理并展示。

> 随着脚本的运行次数越来越多，缓存到本地的数据库会越来越完善


## 官方接口文档

- https://steamcommunity.com/dev?l=schinese
- https://partner.steamgames.com/doc/webapi


## 目录说明

```
steam-discount
├── README.md ............................... [项目说明]
├── main.py ................................. [程序运行入口]
├── data
│   └── steam.db ............................ [sqlite: Steam 游戏库归档]
├── docs .................................... [Github Page 特惠排行一览]
├── src ..................................... [项目源码]
├── script .................................. [数据库脚本]
├── tpl ..................................... [模板文件]
└── log ..................................... [项目日志]
```

## 开发者部署


本项目已配置 [Github Actions](https://docs.github.com/cn/actions/configuring-and-managing-workflows/configuring-a-workflow)，因此你只需轻松几步即可实现部署：

- [Fork 本项目](https://github.com/lyy289065406/steam-discount) 到你的代码仓库
- 启用 Settings --> Actions 功能

> 尔后程序便会每半时执行一次，并自动生成 [Github Page](https://lyy289065406.github.io/steam-discount/) 特惠排行榜单（若要调整执行频率，可修改 [`autorun.yml`](.github/workflows/autorun.yml) 的 `schedule` 触发时点）


## 赞助途径

| 支付宝 | 微信 |
|:---:|:---:|
| ![](docs/imgs/alipay.png) | ![](docs/imgs/wechat.png) |


## 版权声明

　[![Copyright (C) EXP,2016](https://img.shields.io/badge/Copyright%20(C)-EXP%202016-blue.svg)](http://exp-blog.com)　[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

- Site: [http://exp-blog.com](http://exp-blog.com) 
- Mail: <a href="mailto:289065406@qq.com?subject=[EXP's Github]%20Your%20Question%20（请写下您的疑问）&amp;body=What%20can%20I%20help%20you?%20（需要我提供什么帮助吗？）">289065406@qq.com</a>


------



