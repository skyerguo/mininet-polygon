#include <ifaddrs.h>
#include <iostream>
#include <cstring>
#include <string>

int main() {
    struct ifaddrs *addrs ,*tmp;
    int fd = -1;

    getifaddrs(&addrs);
    tmp = addrs;

    while (tmp) {
        if (tmp->ifa_addr->sa_family != AF_INET) {
            tmp = tmp->ifa_next;
            continue;
        }
        //   balancer_interfaces.insert(std::string(tmp->ifa_name));
          fd = socket(2, SOCK_DGRAM, 17);
          std::cout << "???" << tmp->ifa_name << std::endl;
          std::cout << fd << std::endl;
          std::cout << setsockopt(fd, SOL_SOCKET, SO_BINDTODEVICE, tmp->ifa_name, sizeof(tmp->ifa_name)) << std::endl;
        //   if (setsockopt(fd, SOL_SOCKET, SO_BINDTODEVICE, tmp->ifa_name, sizeof(tmp->ifa_name)) < 0) {
        //     std::cerr << "Failed to bind on interface: " << tmp->ifa_name << ", " << strerror(errno) << std::endl;
        //     close(fd);
        //     tmp = tmp->ifa_next;
        //     continue;
        //   }
        //   struct sockaddr_in sa;
        //   memset(&sa, 0, sizeof(sa));
        //   sa.sin_family = AF_INET;
        //   sa.sin_port = htons(port);
        //   sa.sin_addr.s_addr = htonl(INADDR_ANY);

        //   if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        //     std::cerr << "failed to listen on udp port: " << tmp->ifa_name << ":" << ntohs(sa.sin_port) << ", " << strerror(errno) << std::endl;
        //     close(fd);
        //     tmp = tmp->ifa_next;
        //     continue;
        //   }
        //   fds->push_back(fd);
        //   if (!strcmp(tmp->ifa_name, interface)) {
        //     std::cerr << "set unicast fd: " << fd << std::endl;
        //     s.unicast_fd(fd);
        //   }
            // printf("listening on interface: %s, port: %d, fd: %d\n", tmp->ifa_name, port, fd);
        tmp = tmp->ifa_next;
    }
    freeifaddrs(addrs);
    return 0;
}