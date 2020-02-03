# Stardew-Save-Sync
In development program to synchronize Stardew Valley saves between PC's and Mobile Devices.
This is a learning project to teach myself PyQt, Google API interaction, and OOP in Python.
Any tips on how to improve my code are welcome.

# Contributors
The following people actively develop the project
- InValidFire[https://twitter.com/InValidFire]

# To-Do
- save list (**Done**)
  - shows all saves in a tree view: (**Done**)
    - file name
    - player name
    - playtime on file
- sync Stardew Files from device to Google Drive (**Done**)
  - General Sync = Syncs the latest version of the file found
    - if newer, sync replacing older
    - if file doesn't exist, sync
  - Selective Sync = Syncs the selected version, ignoring timestamps (**Done**)
- threading
  - split google authentication from UI thread
    - stops application from freezing while loading google drive data
- console window
  - redirects stdout to display all errors there after application is frozen
- autosync (toggleable)
  - Check every 2 minutes for changes, sending out desktop notifications
- updates
  - using PyUpdater[https://www.pyupdater.org/]
  - Pull latest release from git