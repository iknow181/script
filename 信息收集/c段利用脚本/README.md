# 域名收集

旨在收集指定 IP 地址段的域名信息，并将结果保存到 `resulit.txt` 文件中

### 脚本功能概述

1. **获取 IP 地址段**：
   - 从用户输入的 IP 地址（假设为 `xxx.xxx.xxx.x`）生成一个 IP 地址段 `xxx.xxx.xxx.1` 到 `xxx.xxx.xxx.255`。
2. **请求域名信息**：
   - 对每个 IP 地址进行查询请求，使用 `http://api.webscan.cc/?action=query&ip={ip}` API 接口获取相关域名信息。
3. **处理响应**：
   - 解析 API 返回的 JSON 数据，并提取出每个域名和标题。
4. **并发处理**：
   - 使用 `ThreadPoolExecutor` 来并发地处理多个 IP 地址，以提高执行效率。
5. **保存结果**：
   - 将所有查询结果写入到 `resulit.txt` 文件中。