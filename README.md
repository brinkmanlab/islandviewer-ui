islandviewer-ui
===============

Web UI for Islandviewer.

= User Management

If the iv_social module is enabled a number of commands to manage users becomes available.

List the registered users:

  python manager.py ivuser list

Toggle a user active/inactive:

  python manager.py ivuser active <userid>

Toggle a user staff/not staff:

  python manager.py ivuser staff <userid>


