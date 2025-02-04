@reboot cd hitch && screen -d -m bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/waitress-serve server:app; bash'
# every minute
* * * * * cd hitch && /usr/bin/flock -n /tmp/show.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python flask --app hitch generate show' > cronlog.txt 2>&1
# every 10 minutes
*/10 * * * * cd hitch && /usr/bin/flock -n /tmp/show.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python flask --app hitch generate show --args light' > cronlog-light.txt 2>&1
# each day at midnight
0 0 * * * cd hitch && /usr/bin/flock -n /tmp/dump.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python flask --app hitch generate dump' > dumplog.txt 2>&1
# every day at midnight
0 0 * * * cd hitch && /usr/bin/flock -n /tmp/dashboard.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python flask --app hitch generate dashboard' > dashboard.txt 2>&1
# every month
0 0 1 * * cd hitch && /usr/bin/flock -n /tmp/hitchhiking.lockfile bash -c '. $HOME/.bashrc; /home/bob/.asdf/shims/python flask --app hitch generate hitchhiking' > hitchhiking.txt 2>&1
