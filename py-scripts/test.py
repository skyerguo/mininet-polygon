import dns.resolver;
import os;
dns_ip = '10.0.200.1';
my_resolver = dns.resolver.Resolver();
my_resolver.nameservers = [dns_ip];
DNS_resolving = my_resolver.query("server2.example.com");