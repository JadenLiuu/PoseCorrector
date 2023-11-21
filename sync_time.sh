sudo ntpdate 192.168.101.94
sudo echo "10 5 * * * root (/usr/sbin/ntpdate 192.168.101.94 && /sbin/hwclock -w) &> /dev/null" >> /etc/crontab
