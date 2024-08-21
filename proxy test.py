import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_socket(proxy_host, proxy_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((proxy_host, proxy_port))
    return sock

def check_http_proxy(proxy_host, proxy_port):
    try:
        with create_socket(proxy_host, proxy_port) as sock:
            request = "GET http://www.apple.com/ HTTP/1.1\r\nHost: www.apple.com\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            response = sock.recv(4096)
            logging.info(f"Received response of length {len(response)} from {proxy_host}:{proxy_port}")
            if len(response) > 0 and b"HTTP/" in response:
                return "HTTP Proxy"
    except (socket.timeout, socket.error) as e:
        logging.error(f"Error checking HTTP proxy {proxy_host}:{proxy_port} - {e}")
        return None

def check_socks5_proxy(proxy_host, proxy_port):
    try:
        with create_socket(proxy_host, proxy_port) as sock:
            sock.sendall(b'\x05\x01\x00')  # SOCKS5: 版本号 5，支持 0 个认证方法
            response = sock.recv(2)
            if response == b'\x05\x00':  # 服务器同意使用无认证
                return "SOCKS5 Proxy"
    except (socket.timeout, socket.error) as e:
        logging.error(f"Error checking SOCKS5 proxy {proxy_host}:{proxy_port} - {e}")
        return None

def check_socks4_proxy(proxy_host, proxy_port):
    try:
        with create_socket(proxy_host, proxy_port) as sock:
            request = b'\x04\x01\x00\x00\x00\x00\x00\x00\x00'  # SOCKS4 握手请求
            sock.sendall(request)
            response = sock.recv(8)
            if len(response) >= 8 and response[0] == 0x00:  # 0x00 表示成功
                return "SOCKS4 Proxy"
    except (socket.timeout, socket.error) as e:
        logging.error(f"Error checking SOCKS4 proxy {proxy_host}:{proxy_port} - {e}")
        return None

def check_proxy(proxy):
    host, port = proxy.split(':')
    port = int(port)
    

    for attempt in range(5):
        # 先检查 SOCKS5 代理
        result = check_socks5_proxy(host, port)
        if result:
            return proxy, result
        
        # 检查 SOCKS4 代理
        result = check_socks4_proxy(host, port)
        if result:
            return proxy, result
        
        # 检查 HTTP 代理
        result = check_http_proxy(host, port)
        if result:
            return proxy, result
        
        logging.info(f"Attempt {attempt + 1} failed for {proxy}. Retrying...")

    return proxy, "Bad Proxy"

def classify_proxies(input_file, socks5_file, socks4_file, http_file, bad_file):
    with open(input_file, 'r') as f:
        proxies = f.readlines()

    with open(socks5_file, 'w') as socks5_f, open(socks4_file, 'w') as socks4_f, open(http_file, 'w') as http_f, open(bad_file, 'w') as bad_f:
        with ThreadPoolExecutor(max_workers=1000) as executor:
            future_to_proxy = {executor.submit(check_proxy, proxy.strip()): proxy.strip() for proxy in proxies if proxy.strip()}
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    proxy, proxy_type = future.result()
                    logging.info(f"Checked {proxy}: {proxy_type}")
                    if proxy_type == "SOCKS5 Proxy":
                        socks5_f.write(proxy + '\n')
                    elif proxy_type == "SOCKS4 Proxy":
                        socks4_f.write(proxy + '\n')
                    elif proxy_type == "HTTP Proxy":
                        http_f.write(proxy + '\n')
                    else:
                        bad_f.write(proxy + '\n')
                except Exception as e:
                    logging.error(f"Error checking {proxy}: {e}")
                    bad_f.write(proxy + '\n')

if __name__ == "__main__":
    classify_proxies('proxy.txt', 'socks5.txt', 'socks4.txt', 'http.txt', 'bad.txt')
