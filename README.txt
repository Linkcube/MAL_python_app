MAL_python_app
==============

MyAnimeList interaction through python script utilizing cUrl to acess and change values/continue wathcing via streams.

The program should ask the user for information in a clear fashion such that no instructions are needed.

However there are several values that the user can change depending on perseonal prefference, namely the ability
to save a user's password (unsecure method at the moment) and the ability for the program to log actions. Both of these
values can be found in the .py file at the start of the program (look down until there is a large commented section letting
the user know that the specified values are there).

!!=======>
Noticed MAL is whitelisting access, however from what I have read this whitelisting isn't working correctly/consitently
!!=======>

Read the changelog for feature notes and functionality issues.

The program should be able to do the following:
- Access MAL website, and log into the user's account given credentials
- Display relative series to the user for both anime and manga lists in categories
- Change series' status, progress, score, 
- Search for a series and add it to the user's list
- Continue watching a series from their current progress (given that streaming sites have said series/epsiode)
- Log actions to help with debugging
- Store password for easy login ability