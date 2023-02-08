"""Here are your needed imports you may need to add to theese depending on what your doing"""
from datetime import datetime
from interactions import Option, Choice, Embed, OptionType, ComponentContext, autodefer, ButtonStyle, Button, ActionRow

from interactions.ext.tasks import IntervalTrigger, create_task

import interactions
import asyncio

from functions.canvas_functions import CanvasFunctions
from functions.db_functions import dbFunctions
from secret import host, user, password, db

"""
This creates the class your cog runs in, 'ExampleCog' should be replaced with whatever you want your cog name to be.
"""


class instructure(interactions.Extension):
    """This creates and defines the needed info for you"""

    def __init__(self, bot):
        self.bot = bot
        self.db = dbFunctions(host, user, password, db)
        self.method.start(self)


    @interactions.extension_listener()
    async def on_ready(self):  # When the bot is ready
        print('canvas cog loaded')

    @interactions.extension_command(name="register", description="Link your canvas account to your discord account. This requires providing your API Key")
    async def register(self, ctx):
        try:
            api_info = await self.db.get_canvas(ctx.author.id)
        except AttributeError:
            api_info = await self.db.get_canvas(ctx.user.id)

        if api_info is not None:
            try:
                await ctx.send(embeds=Embed(title="You are already registered. Use the unregister command to remove your data", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                await ctx.user.send(embeds=Embed(title="You are already registered. Use the unregister command to remove your data", color=0xFFFFFF), ephemeral=True)
            return

        #send modal getting API key and url
        modal = interactions.Modal(
            title="Registration Info",
            custom_id="canvas_form",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="API Key",
                    placeholder="This can be created in Canvas Settings, /help for more info",
                    custom_id="api_key",
                    min_length=1,
                    max_length=100,
                ),

                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="What is your canvas url?",
                    custom_id="url",
                    placeholder="https://canvas.instructure.com",
                    min_length=1,
                    max_length=100,
                )
            ],
        )

       


        response = await ctx.popup(modal)

    
    @interactions.extension_modal("canvas_form")
    async def modal_response(self, ctx, api: str, url: str):
        try:
            await self.db.insert_canvas(ctx.author.id, api, url)
        except AttributeError:
            await self.db.insert_canvas(ctx.user.id, api, url)
        try:
            await ctx.send(embeds=Embed(title="Registration succesful.", color=0xFFFFFF), ephemeral=True)
        except AttributeError:
            await ctx.user.send(embeds=Embed(title="Registration succesful.", color=0xFFFFFF), ephemeral=True)

    @interactions.extension_command(name="unregister", description="Unlink your canvas account from your discord account.")
    async def unregister(self, ctx):
        try:
            api_info = await self.db.get_canvas(ctx.author.id)
        except AttributeError:
            api_info = await self.db.get_canvas(ctx.user.id)
        if api_info is None:
            try:
                await ctx.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                await ctx.user.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            
            
            return

        #check if user is sure
        buttons = [
            ActionRow(components=[
                Button(style=ButtonStyle.DANGER, label="Yes", custom_id="yes"),
                Button(style=ButtonStyle.PRIMARY, label="No", custom_id="no")
            ]
            )
        ]
        try:
            await ctx.send(
                "Are you sure you want to unregister your canvas account? This will delete all of your data.", components=buttons
            )
        except AttributeError:
            await ctx.user.send(
                "Are you sure you want to unregister your canvas account? This will delete all of your data.", components=buttons
            )

        def check(interaction):
            return interaction.user == ctx.author and interaction.message == ctx.message or interaction.user == ctx.user and interaction.message == ctx.message

        try:
            interaction = await self.bot.wait_for_component(components=buttons, check=check, timeout=15)
        except asyncio.TimeoutError:
            try:
                await ctx.send("You took too long to respond", ephemeral=True)
            except AttributeError:
                await ctx.user.send("You took too long to respond", ephemeral=True)
            return
        

        if interaction.custom_id == "yes":
            try:
                await self.db.remove_canvas(ctx.author.id)
            except AttributeError:
                await self.db.remove_canvas(ctx.user.id)
            await interaction.send("Your canvas account has been unregistered.", ephemeral=True)
            return
        else:
            await interaction.send("Your canvas account has not been unregistered.", ephemeral=True)
            return

    @interactions.extension_command(name="courses", description="List all of your courses")
    async def courses(self, ctx):
        try:
            api_info = await self.db.get_canvas(ctx.author.id)
        except AttributeError:
            api_info = await self.db.get_canvas(ctx.user.id)
        if api_info is None:
            try:
                await ctx.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                await ctx.user.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            
            return

        
        canvas = CanvasFunctions(api_info[2], api_info[3])
        courses = canvas.get_courses()
        embed = Embed(title="Courses", description="Here are all of your courses", color=0xFFFFFF)
        for course in courses:
            embed.add_field(name=course[0], value=course[1])

        try:
            await ctx.send(embeds=embed, ephemeral=api_info[4])
        except AttributeError:
            await ctx.user.send(embeds=embed, ephemeral=api_info[4])
        

    @interactions.extension_command(name="assignments", description="List all of your assignments")
    async def assignments(self, ctx):
        try:
            api_info = await self.db.get_canvas(ctx.author.id)
        except AttributeError:
            api_info = await self.db.get_canvas(ctx.user.id)
        if api_info is None:
            try:
                await ctx.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                await ctx.user.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            
            return

        if api_info[4] == 0:
            try:
                message =  await ctx.send(embeds=Embed(title="Loading", description="Loading your assignments...", color=0xFFFFFF))
            except AttributeError:
                message = await ctx.user.send(embeds=Embed(title="Loading", description="Loading your assignments...", color=0xFFFFFF))
        else:
            try:
                message =  await ctx.send(embeds=Embed(title="Loading", description="Loading your assignments...", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                message = await ctx.user.send(embeds=Embed(title="Loading", description="Loading your assignments...", color=0xFFFFFF))

        

        canvas = CanvasFunctions(api_info[2], api_info[3])
        assignments = canvas.format_assignments()

        embed = await self.assignment_embed(assignments)
        
        if api_info[4] == 0:
            await message.edit(embeds=embed)
        else:
            await ctx.send(embeds=embed, ephemeral=True)
        

    @interactions.extension_command(name="help", description="Get help with the canvas cog")
    async def help(self, ctx):
        embed = Embed(title="Canvas Help", description="Here is some help with the canvas cog", color=0xFFFFFF)
        embed.add_field(name="/Register", value="Use the register command to register your canvas account. This will allow you to use the other commands.")
        embed.add_field(name="/Unregister", value="Use the unregister command to unregister your canvas account. This will delete all of your data.")
        embed.add_field(name="/Courses", value="Use the courses command to list all of your courses.")
        embed.add_field(name="/Assignments", value="Use the assignments command to list all of your assignments.")
        embed.add_field(name="API Key Info", value="1.Go to the **Settings** menu under the **Account** option.\n2.Click on the **New Access Token** button.\n3.Enter a description for the token and click the **Generate Token** button.\n4.Copy the token and paste it into the API Key field in the register command. ")

        try:
            await ctx.send(embeds=embed)
        except AttributeError:
            await ctx.user.send(embeds=embed)


    @interactions.extension_command(name="options", description="Get information about the privacy of the canvas cog")
    async def options(self, ctx):

        try:
            api_info = await self.db.get_canvas(ctx.author.id)
        except AttributeError:
            api_info = await self.db.get_canvas(ctx.user.id)

        if api_info is None:
            try:
                await ctx.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)
            except AttributeError:
                await ctx.user.send(embeds=Embed(title="You need to register your canvas account first. Use the register command to do so.", color=0xFFFFFF), ephemeral=True)

        #add button to toggle response type
        buttons = [
            ActionRow(components=[
                Button(style=ButtonStyle.PRIMARY, label="Toggle Response Type", custom_id="toggle"),
                Button(style=ButtonStyle.PRIMARY, label="Edit Canvas URL", custom_id="url"),
                Button(style=ButtonStyle.PRIMARY, label="Toggle Daily Reminder", custom_id="reminder")
            ]
            )
        ]
        public_status = api_info[4]
        reminder_status = api_info[5]
        embed = Embed(title="Canvas Options", description="Here are the options for the canvas cog", color=0xFFFFFF)
        embed.add_field(name="Repsonse Type", value= "Hidden"  if public_status == True  else "Public")
        embed.add_field(name="API Key", value="This can not be changed or viewed. To reset API Key use the unregister command and then register again.")
        print(api_info[4])
        embed.add_field(name="Reminder", value= "Active"  if reminder_status == True  else "Inactive")
        embed.add_field(name="API URL", value=api_info[3])



        try:
            message = await ctx.send(embeds=embed, components=buttons)
        except AttributeError:
            message = await ctx.user.send(embeds=embed, components=buttons)
        

        def check(interaction):
            return interaction.user == ctx.author and interaction.message == ctx.message or interaction.user == ctx.user and interaction.message == ctx.message

        active = True 
        while active:
            try:
                interaction = await self.bot.wait_for_component(components=buttons, check=check, timeout=45)
                print(interaction.custom_id)

                if interaction.custom_id == "toggle":
                    public_status = not public_status
                    print(public_status)
                    try:
                        await self.db.toggle_canvas(ctx.author.id, public_status)
                    except AttributeError:
                        await self.db.toggle_canvas(ctx.user.id, public_status)
                    embed.fields[0].value = "Hidden" if public_status == True else "Public"
                    await message.edit(embeds=embed, components=buttons)
                    await interaction.send("Response type changed", ephemeral=True)

                elif interaction.custom_id == "reminder":
                    reminder_status = not reminder_status
                    try:
                        await self.db.toggle_reminder(ctx.author.id, reminder_status)
                    except AttributeError:
                        await self.db.toggle_reminder(ctx.user.id, reminder_status)

                    embed.fields[2].value = "Active" if reminder_status == True else "Inactive"

                    await message.edit(embeds=embed, components=buttons)
                    await interaction.send("Reminder status changed", ephemeral=True)

                elif interaction.custom_id == "url":
                    modal = interactions.Modal(
                    title="URL Update",
                    custom_id="url_form",
                    components=[
                            interactions.TextInput(
                                style=interactions.TextStyleType.SHORT,
                                label="What is your canvas url?",
                                custom_id="url",
                                placeholder=api_info[3],
                                min_length=1,
                                max_length=100,
                            )
                        ],
                    )

                    await interaction.popup(modal)


            except asyncio.TimeoutError:
                await message.edit(embeds=embed, components=[])
                active = False


    @interactions.extension_modal("url_form")
    async def url_response(self, ctx, url: str):
        embed = ctx.message.embeds[0]
        embed.fields[3].value = url
        try:
            await self.db.update_url(ctx.author.id, url)
            await ctx.message.edit(embeds=embed, components=ctx.message.components)
            await ctx.send("URL updated", ephemeral=True)
        except AttributeError:
            await self.db.update_url(ctx.user.id, url)
            await ctx.message.edit(embeds=embed, components=ctx.message.components)
            await ctx.user.send("URL updated", ephemeral=True)
    

    @create_task(IntervalTrigger(86400))
    async def method(self):
        data = await self.db.get_all()

        for user in data:
            if(user[3] == True):
                #get user object
                user_channel = await interactions.get(self.bot, interactions.User, object_id=user[0])

                canvas = CanvasFunctions(user[1], user[2])
                assignments = canvas.format_assignments()

                embed = await self.assignment_embed(assignments)

                user_channel._client = self.bot._http
                await user_channel.send(embeds=embed)
            
    async def assignment_embed(self,assignments):
        embed = Embed(title="Assignments", description=f"Here are your assignements for {datetime.now().strftime('%m/%d/%Y')}", color=0xFFFFFF)
        
        due_today = assignments[0]
        due_week = assignments[1]
        due_future = assignments[2]

        if len(due_today) > 0:

            
            due_today_string = ""
            for assignment in due_today:
                new_item = f"{assignment[0]} - {assignment[2]}: {assignment[1]}"
                if len(due_today_string) + len(new_item) > 1024:
                   break
                due_today_string += new_item + "\n"
            embed.add_field(name="Due Today", value=due_today_string)
        
        if len(due_week) > 0:
            due_week = sorted(due_week, key=lambda x: datetime.strptime(x[2], "%A, %B %d: %I:%M %p"))
            due_week_string = ""
            for assignment in due_week:
                new_item = f"{assignment[0]} - {assignment[2]}: {assignment[1]}"
                if len(due_week_string) + len(new_item) > 1024:
                   break
                due_week_string += new_item + "\n"

            embed.add_field(name="Due This Week", value=due_week_string)

        if len(due_future) > 0:
            #sort by first due
            due_future = sorted(due_future, key=lambda x: datetime.strptime(x[2], "%A, %B %d: %I:%M %p"))
    


            due_future = "\n".join([f"{assignment[0]} - {assignment[2]}: {assignment[1]}" for assignment in due_future[0:5]])
            embed.add_field(name="Due Later", value=due_future[:1024])

        return embed
        


def setup(bot):
    """Imports the cog, this should also be set to the name of the class"""
    instructure(bot)
