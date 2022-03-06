import dns.resolver;
import os;
dns_ip = '10.177.53.237';
my_resolver = dns.resolver.Resolver();
my_resolver.nameservers = [dns_ip];
DNS_resolving = my_resolver.query("server1.example.com");