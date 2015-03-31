git_backup_branch
=================

Sublime plugin for putting all your saves to a backup branch

With this plugin every time you save a file that is in a git repo the diff is committed to a local backup branch

What it will do
------------

Let you retrieve work that you have lost due to not commiting frequently enough
Let you keep backups of different branches

What it will *NOT* do
------------

Monitor the size of your backup branches and keep it resonable (you might want to delete the branch every so often presently)
Let you configure repos to back up and others to not
let you use a git alias other than "git"
Alter the aggressiveness of backups
Put your backups on a remote branch
Let you configure the names of your branch backups

Issues
------------
If you are adding new files you can sometimes get merge failures - also it can take too long to run - causing sublime warnings.

Finally the switch between branches causes the editor to reload the file which can lose things like pep8 notes etc.

I have stopped using this

