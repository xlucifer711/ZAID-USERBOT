import os
import sys
from re import sub
from time import time
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import ChatPermissions, ChatPrivileges, Message


DEVS = ["1355571767", "1050898456", "1001132193"]
admins_in_chat = {}

from Zaid.modules.help import add_command_help
from Zaid.modules.basic.profile import extract_user

async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if not reply.from_user:
            if (
                reply.sender_chat
                and reply.sender_chat != message.chat.id
                and sender_chat
            ):
                id_ = reply.sender_chat.id
            else:
                return None, None
        else:
            id_ = reply.from_user.id

        if len(args) < 2:
            reason = None
        else:
            reason = text.split(None, 1)[1]
        return id_, reason

    if len(args) == 2:
        user = text.split(None, 1)[1]
        return await extract_userid(message, user), None

    if len(args) > 2:
        user, reason = text.split(None, 2)[1:]
        return await extract_userid(message, user), reason

    return user, reason


async def list_admins(client: Client, chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in client.get_chat_members(
                chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            )
        ],
    }
    return admins_in_chat[chat_id]["data"]




unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)


@Client.on_message(
    filters.group & filters.command(["صورة شات", "وضع صورة"], ".") & filters.me
)
async def set_chat_photo(client: Client, message: Message):
    zuzu = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    can_change_admin = zuzu.can_change_info
    can_change_member = message.chat.permissions.can_change_info
    if not (can_change_admin or can_change_member):
        await message.edit_text("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if message.reply_to_message:
        if message.reply_to_message.photo:
            await client.set_chat_photo(
                message.chat.id, photo=message.reply_to_message.photo.file_id
            )
            return
    else:
        await message.edit_text("ا؏ـمـل عـليـهہ‌‏ ࢪيـبـ !")



@Client.on_message(filters.group & filters.command("حظر", ".") & filters.me)
async def member_ban(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    rd = await message.edit_text("`Processing...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيه‏ ڪـافـيـهہ‌")
    if not user_id:
        return await rd.edit("مـشـ لاقـيـ يـوزࢪهہ‌")
    if user_id == client.me.id:
        return await rd.edit("هـتحظـࢪ نفسـگ آزآيـ يـسـطـآآ.")
    if user_id in DEVS:
        return await rd.edit("دهہ‌‏ آلمـطـوࢪ يـهـبـل")
    if user_id in (await list_admins(client, message.chat.id)):
        return await rd.edit("مـيـنفعشـ تحظـࢪ آدمـن نزل مـن آلآدمـن وآࢪزعهہ‌‏ حظـࢪ")
    try:
        mention = (await client.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )
    msg = (
        f"**اتـحـظࢪ خـلاصـ:** {mention}\n"
        f"**اتـحـظࢪ خـلاصـ:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.ban_member(user_id)
    await rd.edit(msg)



@Client.on_message(filters.group & filters.command("الغاء حظر", ".") & filters.me)
async def member_unban(client: Client, message: Message):
    reply = message.reply_to_message
    rd = await message.edit_text("`بـشـيـلـ الـحـظـࢪ اهـو بـيـحـمـلـ...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await rd.edit("لا يـمڪـن الغـاء حـظـࢪ قـنـاة")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await rd.edit(
            "لازمـ تـڪـتـب يـوزࢪهہ‌‏ جـنـب الامـࢪ او تعـمـل ࢪيـب عـلـي ڪلامهہ‌‏."
        )
    await message.chat.unban_member(user)
    umention = (await client.get_users(user)).mention
    await rd.edit(f"تم الغاء حظره! {umention}")



@Client.on_message(filters.command(["تثبيت", "شيل التثبيت"], ".") & filters.me)
async def pin_message(client: Client, message):
    if not message.reply_to_message:
        return await message.edit_text("آعمـل ࢪيـب عليـ رسـآلهہ‌‏ عآوزهہ‌‏ تتثبت آو آل عآوز تشـيـلـهـآ.")
    rd = await message.edit_text("`بــتــتــثـبـتـ اهـي...`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_pin_messages:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await rd.edit(
            f"**Unpinned [this]({r.link}) message.**",
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=True)
    await rd.edit(
        f"**Pinned [this]({r.link}) message.**",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("كتم", ".") & filters.me)
async def mute(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    rd = await message.edit_text("`╮ ❐ ... جـاࢪِ الکتم ... ❏╰`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if not user_id:
        return await rd.edit("مـشـ لاقـيـ يـوزࢪهہ‌‏.")
    if user_id == client.me.id:
        return await rd.edit("𖡛... . لمـاذا تࢪيـد كتم نفسـك؟  ...𖡛")
    if user_id in DEVS:
        return await rd.edit("لا يمڪنني كتـم مطـور السـورس")
    if user_id in (await list_admins(client, message.chat.id)):
        return await rd.edit("أنـا لسـت مشـرف هنـا ؟!! ")
    mention = (await client.get_users(user_id)).mention
    msg = (
        f"**#كتــم_الخــاص:** {mention}\n"
        f"**الشخص:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if reason:
        msg += f"**السبب:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    await rd.edit(msg)



@Client.on_message(filters.group & filters.command("الغاء كتم", ".") & filters.me)
async def unmute(client: Client, message: Message):
    user_id = await extract_user(message)
    rd = await message.edit_text("`╮ ❐ ... جـاࢪِ الغـاء الکتم ... ❏╰`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if not user_id:
        return await rd.edit("⪼ يرجى الرد المستخدم لالغـاء ڪتمه او اضافته الى الامر 𓆰..")
    await message.chat.restrict_member(user_id, permissions=unmute_permissions)
    umention = (await client.get_users(user_id)).mention
    await rd.edit(f"⪼ تم الغاء ڪتم المستخـدم 🔔𓆰! {umention}")


@Client.on_message(filters.command(["طرد", "dkick"], ".") & filters.me)
async def kick_user(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    rd = await message.edit_text("`╮ ❐... جـاࢪِ الحـظـࢪ ...❏╰`")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_restrict_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if not user_id:
        return await rd.edit("مـشـ لاقـيـ يـوزࢪهہ‌‏.")
    if user_id == client.me.id:
        return await rd.edit("هـتحظـࢪ نفسـگ آزآيـ يـسـطـآآ.")
    if user_id == DEVS:
        return await rd.edit("دهہ‌‏ آلمـطـوࢪ يـهـبـل.")
    if user_id in (await list_admins(client, message.chat.id)):
        return await rd.edit("مـيـنفعشـ تحظـࢪ آدمـن نزل مـن آلآدمـن وآࢪزعهہ‌‏ حظـࢪ")
    mention = (await client.get_users(user_id)).mention
    msg = f"""
**معرف المستخدم :** {mention}
**ده طرده:** {message.from_user.mention if message.from_user else 'Anon'}"""
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if reason:
        msg += f"\n**السبب:** `{reason}`"
    try:
        await message.chat.ban_member(user_id)
        await rd.edit(msg)
        await asyncio.sleep(1)
        await message.chat.unban_member(user_id)
    except ChatAdminRequired:
        return await rd.edit("**مـيـنفعشـ تحظـࢪ آدمـن نزل مـن آلآدمـن وآࢪزعهہ‌‏ حظـࢪ**")


@Client.on_message(
    filters.group & filters.command(["رول", "رول كامل"], ".") & filters.me
)
async def promotte(client: Client, message: Message):
    user_id = await extract_user(message)
    umention = (await client.get_users(user_id)).mention
    rd = await message.edit_text("`╮ ❐  جـاري ࢪفعه مشرف  ❏╰`")
    if not user_id:
        return await rd.edit("مـشـ لاقـيـ يـوزࢪهہ‌‏.")
    bot = (await client.get_chat_member(message.chat.id, client.me.id)).privileges
    if not bot.can_promote_members:
        return await rd.edit("مشـ مـعـاڪـ صـلاحـيـهہ‌‏ ڪـافـيـهہ‌‏")
    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=True,
            ),
        )
        return await rd.edit(f"- ❝ ⌊  تم تـرقيتـه مشـرف 𓆰.! {umention}")

    await message.chat.promote_member(
        user_id,
        privileges=ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=False,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False,
        ),
    )
    await rd.edit(f"- ❝ ⌊  تم تـرقيتـه مشـرف 𓆰.! {umention}")


@Client.on_message(filters.group & filters.command("تك", ".") & filters.me)
async def demote(client: Client, message: Message):
    user_id = await extract_user(message)
    rd = await message.edit_text("`↮`")
    if not user_id:
        return await rd.edit("مـشـ لاقـيـ يـوزࢪهہ‌‏.")
    if user_id == client.me.id:
        return await rd.edit("مينفعش تنزل نفسك.")
    await message.chat.promote_member(
        user_id,
        privileges=ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
        ),
    )
    umention = (await client.get_users(user_id)).mention
    await rd.edit(f"- ❝ ⌊  تم تنزلـيه من الاشـرف بنجـاح  𓆰.! {umention}")


add_command_help(
    "admin",
    [
        ["حظر [ريب عليه/اليوزر/الايدي]", "عشان تحظر واحد."],
        [
            f"الغاء حظر [ريب عليه/اليوزر/الايدي]",
            "عشان تلغي حظره.",
        ],
        ["طرد [ريب عليه/اليوزر/الايدي]", "عشان تطرد واحد م البار."],
        [
            f"رول `or` .رول كامل",
            "ترفع ادمن.",
        ],
        ["تك", "تنزيل من الادمن."],
        [
            "كتم [ريب عليه/اليوزر/الايدي]",
            "عشان تكتم حد.",
        ],
        [
            "الغاء كتم [ريب عليه/اليوزر/الايدي]",
            "عشان تشيل الكتم.",
        ],
        [
            "تثبيت [ريب]",
            "عشان تثبت رساله.",
        ],
        [
            "الغاء تثبيت [ريب]",
            "عشان تشيل رساله مثبته.",
        ],
        [
            "وضع صورة [ريب ع رابط صوره]",
            "عشان تحط صوره للبار",
        ],
    ],
)
