# proxy-check
# Proxy Checker

## 简介
用于检查和分类代理服务器的 Python 工具。它可以识别 SOCKS5、SOCKS4 和 HTTP 代理，并将结果输出到不同的文件中，方便后续使用。

## 功能

- 从指定文件读取代理列表
- 检查每个代理的类型（SOCKS5、SOCKS4、HTTP）
- 使用多线程提高检查效率
- 将结果分类输出到不同的文件

## 使用方法

1. 确保您已安装 Python 3.x。
2. 将代理地址列表保存到 `proxy.txt` 文件中，每行一个代理，格式为 `host:port`。
3. 运行以下命令：

   ```bash
   python proxy_checker.py
