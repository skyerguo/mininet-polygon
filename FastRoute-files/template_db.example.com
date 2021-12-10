;
; BIND data file for local loopback interface
$TTL    604800
@       IN      SOA     dns.example.com. admin.example.com. (
          2         ; Serial
     604800         ; Refresh
      86400         ; Retry
    2419200         ; Expire
     604800 )       ; Negative Cache TTL
;
;
; name servers - NS records
     IN      NS      dns.example.com.
; name servers - A records
dns.example.com.          IN      A       