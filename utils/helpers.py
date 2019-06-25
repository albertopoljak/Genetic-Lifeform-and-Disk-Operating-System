import string
import random

# Discord request rate-limit is 50requests/s per user.
# That's global and should cover every category we use (ban, delete)
# except channel creation which is it's own thing.
# discord.py manages rate-limiting but it's way faster to fire loads of coroutines
# at the same time than to fire one by one.
RATE_LIMIT = 50


def get_list_chunks(input_list):
    """ We're dividing original list in multiple smaller lists with length of RATE_LIMIT or
        smaller if it's the last list and there's not enough elements to fill it.
        Example: original list is range(15) and RATE_LIMIT is 6
        return: [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14]]
    """
    list_length = len(input_list)
    list_chunks = [input_list[x:x + RATE_LIMIT] for x in range(0, list_length, RATE_LIMIT)]
    return list_chunks


def remove_unmanageable_members(member_list, max_role_guild_position):
    """ If you have administrator/ban permission you can ban everyone BELOW YOUR role.
        In general permission you have that affect other members can only apply to those below you.
        So here we remove (in-place) all members in list that are higher or equal rank than you.
        This way we save API ban calls and some processing time later when we sort the list.
    """
    # Don't iterate trough list at the same time as removing in place
    to_remove = []
    for member in member_list:
        if _member_top_role_position(member) >= max_role_guild_position:
            to_remove.append(member)
    for member in to_remove:
        member_list.remove(member)


def sort_members_by_roles(member_list):
    """ We sort (in-place) members by their highest role (list will be from lowest to highest).
        We do this to increase the time needed for administrators to notice that we
        are banning tons of members. It's easier to see members disappearing in your
        discord members guild panel if they are higher role thus higher on list (because
        you can actually see them being removed).
        But if we start banning from the bottom of the list it's very hard to notice
        since the list will not move at all until we get to members in view aka higher ranking
        members.
    """
    member_list.sort(key=_member_top_role_position)


def _member_top_role_position(member):
    return member.top_role.position


def remove_unmanageable_roles(roles_list, max_role_guild_position):
    """ If you have administrator/manage role permission you can manage roles BELOW YOUR role.
        So here we remove (in-place) all roles in list that have higher or equal
        position than the bot highest role. We also remove roles that can't be deleted
        manually (managed roles and @everyone). This way we save API calls.
    """
    # Don't iterate trough list at the same time as removing in place
    to_remove = []
    for role in roles_list:
        if role.position >= max_role_guild_position or role.managed or role.name == "@everyone":
            to_remove.append(role)
    for role in to_remove:
        roles_list.remove(role)


def remove_all_managed_emojis(emoji_list):
    """ Managed emojis can't be modified by the bot so we remove them
        from the list to save some API calls.
    """
    # Don't iterate trough list at the same time as removing in place
    to_remove = []
    for emoji in emoji_list:
        if emoji.managed:
            to_remove.append(emoji)
    for emoji in to_remove:
        emoji_list.remove(emoji)


def get_visually_sorted_channels(guild):
    """ Never never never use channel.position!
        Returns list of channels sorted as they are visually in your discord channel list
        where the top channel is the first channel in returned list.
    """
    visually_sorted_channels = []
    by_category = guild.by_category()  # List[Tuple[Optional[CategoryChannel], List[abc.GuildChannel]]]
    for tple in by_category:
        for channel in tple[1]:
            visually_sorted_channels.append(channel)
    return visually_sorted_channels


def remove_unmanageable_channels(channel_list, bot_member):
    """ Unmanageable means that hte bot can't manage aka delete/rename/etc channels.
        Unmanageable channels only exist if the bot doesn't have admin powers.
        If bot has manage channels True then the only unmanageable channels are
        those who have specific channel overwrites or those that are hidden from bot (read message False).
        We remove those because channel overwrites can stop the bot from deleting them
        thus wasting API calls.
    """
    # Don't iterate trough list at the same time as removing in place
    to_remove = []
    for channel in channel_list:
        if not channel.permissions_for(bot_member).manage_channels:
            to_remove.append(channel)
    for channel in to_remove:
        channel_list.remove(channel)


def generate_random_string():
    """ 32 is maximum channel/nickname length so we stick to that.
        14 is just for lower limit so the generated string isn't too short.
    """
    string_length = random.randint(14, 32)
    allowed_chars = string.ascii_letters + string.digits
    return "".join(random.choice(allowed_chars) for i in range(string_length))




