#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from __future__ import annotations

import asyncio
import typing
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utilities import exceptions, objects, paginators

if TYPE_CHECKING:
    from cogs.voice.custom.player import Player


class Context(commands.Context):

    @property
    def user_config(self) -> typing.Union[objects.DefaultUserConfig, objects.UserConfig]:

        if not self.author:
            return self.bot.user_manager.default_user_config

        return self.bot.user_manager.get_user_config(user_id=self.author.id)

    @property
    def guild_config(self) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:

        if not self.guild:
            return self.bot.guild_manager.default_guild_config

        return self.bot.guild_manager.get_guild_config(guild_id=self.guild.id)

    @property
    def colour(self) -> discord.Colour:

        if str(self.user_config.colour) == str(discord.Colour(int('f1c40f', 16))):
            return self.guild_config.colour

        return self.user_config.colour

    @property
    def voice_client(self) -> Player:
        return super().voice_client

    async def paginate(self, **kwargs) -> paginators.Paginator:
        paginator = paginators.Paginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_embed(self, **kwargs) -> paginators.EmbedPaginator:
        paginator = paginators.EmbedPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_embeds(self, **kwargs) -> paginators.EmbedsPaginator:
        paginator = paginators.EmbedsPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_choice(self, **kwargs) -> typing.Any:

        paginator = await self.paginate_embed(**kwargs)

        try:
            response = await self.bot.wait_for('message', check=lambda msg: msg.author == self.author and msg.channel == self.channel, timeout=30.0)
        except asyncio.TimeoutError:
            raise exceptions.ArgumentError('You took too long to respond.')

        response = await commands.clean_content().convert(ctx=self, argument=response.content)
        try:
            response = int(response) - 1
        except ValueError:
            raise exceptions.ArgumentError('That was not a valid number.')
        if response < 0 or response >= len(kwargs.get('entries')):
            raise exceptions.ArgumentError('That was not one of the available options.')

        await paginator.stop()
        return kwargs.get('entries')[response]

    async def try_dm(self, **kwargs) -> typing.Optional[discord.Message]:

        try:
            return await self.author.send(**kwargs)
        except discord.Forbidden:
            try:
                return await self.channel.send(**kwargs)
            except discord.Forbidden:
                return
