To remove an allocated IP address in Kali Linux, you have several options depending on how it was assigned:

**If the IP was assigned via DHCP:**
```bash
sudo dhclient -r eth0
```
Replace `eth0` with your actual interface name. This releases the DHCP lease.

**If the IP was assigned statically:**
```bash
sudo ip addr del 192.168.1.100/24 dev eth0
```
Replace the IP address, subnet mask, and interface name accordingly.

**Using ifdown (older method):**
```bash
sudo ifdown eth0
```

**Using nmcli (NetworkManager):**
```bash
sudo nmcli device disconnect eth0
```

**To remove all IPs from an interface:**
```bash
sudo ip addr flush dev eth0
```

**To view current IP assignments:**
```bash
ip addr show
```
or
```bash
ifconfig
```

**Find your interface name:** If you're unsure which interface to target, run:
```bash
ip link show
```

The most common approach is using `sudo dhclient -r` for DHCP-assigned IPs or `sudo ip addr del` for static assignments. Choose based on whether your IP was dynamically or statically configured.
