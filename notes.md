## Process guidelines

Always ban/delete things from lowest to highest ranking so it's hard to visually see it on discord screen.

This will make it very hard to notice that bad stuff is going on all up to the last moments.

If any of the previous steps in process fails (permissions etc) just move to the next step.

## Best process

1. Ban all members (starting from bottom of the hierarchy). 
Do not ban last 30 users because you can visually see them being removed (in discord member list on the right side of screen) and that can alert admins.
I tested and with 1920 * 1080 you can see around 25 members in that list so it's rounded to 30.
Save those 30 for later.

2. Delete all emojis. 
This will be fast since we can remove up to 50/s and is pretty much unnoticeable.
 
3. Delete all text+voice channels except categories (don't want to waste API calls on categories since they
serve no real purpose anyway).

4. Delete all roles starting from lowest in hierarchy.

5. Ban those remaining 30 members.

6. Remove guild icon and change it's name to random string.

7. Start creating tons of random channels so it makes it impossible for the guild to recover (better to create new guild than to delete all of channels).
