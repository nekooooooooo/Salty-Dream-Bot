import discord
import io
import aiohttp
import base64
import os
from urllib.parse import urlparse
from discord import option
from discord.ext import commands
from modules import values, extras

class Extras(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = "interrogate", description = "interrogate image")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=False
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
    )
    @option(
        "model",
        str,
        description="Model to use for interrogating (default CLIP)",
        required=False,
        default="CLIP",
        choices=["CLIP", "DeepDanbooru"]
    )
    async def interrogate(
            self,
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment,
            image_url: str,
            model: str
        ):

        await ctx.response.defer()

        # check if url and image is valid
        #! this implementation is extremely ugly and dirty, need to find a better way
        image_url = await self.check_image(ctx, image_url, image_attachment)

        if image_url is None:
            return
        
        await ctx.followup.send(f"Interrogating...")

        image, file = await self.get_image_from_url(image_url)

        image_b64 = base64.b64encode(image).decode('utf-8')
        output = await extras.interrogate(image_b64, model.lower())

        tags = output['caption']

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 Interrogated Prompt", value=f"```{tags}```")
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        await ctx.interaction.edit_original_response(content="Interrogated!",embed=embed, file=file)

    @discord.slash_command(name = "pnginfo", description = "View information about generation parameters")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=False
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
    )
    async def pnginfo(
            self,
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment,
            image_url: str,
        ):

        await ctx.response.defer()

        # check if image is valid
        #! this implementation is extremely ugly and dirty, need to find a better way
        new_image_url = await self.check_image(ctx, image_url, image_attachment)

        if new_image_url is None:
            return
        
        await ctx.followup.send(f"Getting info...")
        
        image, file = await self.get_image_from_url(new_image_url)

        image_b64 = base64.b64encode(image).decode('utf-8')
        output = await extras.pnginfo(image_b64)

        png_info = output['info']
        print(png_info)

        if png_info == '':
            png_info = "No info found"

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 PNG Info", value=f"```{png_info}```")
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        await ctx.interaction.edit_original_response(content="",embed=embed, file=file)
        

    async def check_image(self, ctx, image_url, image_attachment):
        # check if image url is valid
        if image_url:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            await resp.read()
                        else:
                            embed = self.error_embed("", "URL image not found...")
                            await ctx.followup.send(embed=embed, ephemeral=True)
                            return None
                except aiohttp.ClientConnectorError as e:
                    print('Connection Error', str(e))
                    return None
        
        # checks if url is used otherwise use attachment
        if image_url is None:
            # checks if both url and attachment params are missing, then checks if attachment is an image
            if image_attachment is None or image_attachment.content_type not in values.image_media_types:
                embed = self.error_embed("", "Please attach an image...")
                await ctx.followup.send(embed=embed, ephemeral=True)
                return None

            image_url = image_attachment.url

        return image_url
    
    async def get_image_from_url(self, image_url):
        # TODO find a better way to convert image to a discord file
        # get image from url then send it as discord.file
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                image = await resp.read()
                with io.BytesIO(image) as img:
                    # get filename from url
                    a = urlparse(image_url)
                    filename = os.path.basename(a.path)
                    file = discord.File(img, filename=filename)

        return image, file

    def error_embed(self, title, desc):
        embed = discord.Embed(
            color=discord.Colour.red(),
            title=title,
            description=desc
        )
        return embed
    
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    hns = list(chunks(values.hypernetworks, 10))
    print(f"{len(hns)} pages of hypernetworks loaded...")

    # TODO Pagination for large lists of hypernetworks
    @discord.slash_command(name = "hypernetworks", description = "Show list of hypernetworks")
    @option(
        "page",
        int,
        description="Select page",
        required=True,
        default=1,
        min_value=1,
        max_value=len(hns)
    )
    async def hypernetworks(self, 
            ctx: discord.ApplicationContext,
            page: int,
        ):

        value=""

        for hypernetwork in self.hns[page-1]:
            value = value + f"``{hypernetwork}``\n"

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="Hypernetworks", value=f"{value}")
        await ctx.respond(embed=embed)

    
def setup(bot):
    bot.add_cog(Extras(bot))