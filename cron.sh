@reboot cd hitch && screen -d -m bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/waitress-serve server:app; bash'
# every minute
* * * * * cd hitch && /usr/bin/flock -n /tmp/show.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python scripts/show.py' > cronlog.txt 2>&1
# every 10 minutes
*/10 * * * * cd hitch && /usr/bin/flock -n /tmp/show.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python scripts/show.py light' > cronlog-light.txt 2>&1
# each day at midnight
0 0 * * * cd hitch && /usr/bin/flock -n /tmp/dump.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python scripts/dump.py' > dumplog.txt 2>&1
# every day at midnight
0 0 * * * cd hitch && /usr/bin/flock -n /tmp/dashboard.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python scripts/dashboard.py' > dashboard.txt 2>&1

0 0 1 * * cd hitch && /usr/bin/flock -n /tmp/hitchhiking.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python scripts/hitchhiking.py' > hitchhiking.txt 2>&1
