sudo pkill uvi -9
sudo pkill python -9
sleep 3
cd /home/dev/Documents/PoseCorrector
sh mnt.sh
cd server
./set.sh &
