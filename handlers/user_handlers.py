import asyncio
import datetime
import os

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from keyboards import main_kb
from external_services import ai
from lexicon import LEXICON_EN
from db.models import UserManager, ImageManager

router = Router()
router.message.filter()

usermanager = UserManager()
imagemanager = ImageManager()


@router.message(CommandStart())
async def process_start_command(message: Message):
    # add a user to a database if he's new
    user = message.from_user
    usermanager.check_user(user)
    # send a keyboard with actions and explain how it works
    await message.answer(text=LEXICON_EN["/start"], reply_markup=main_kb)


@router.message(Command("rules"))
async def process_help_command(message: Message):
    # explanation of a game's rules
    await message.answer(LEXICON_EN["/rules"])


@router.message(F.text.in_(["Upload a photo 🚖", "Upload a photo", "/upload"]))
async def process_upload_photo(message: Message):
    # ask a user to send a photo
    await message.answer(LEXICON_EN["/upload"])


@router.message(F.photo)
async def process_recognize_car(message: Message, bot: Bot):
    # add user in a db if he's new
    user = message.from_user
    usermanager.check_user(user)
    # answer user that we've got his image and will check it
    await message.answer(LEXICON_EN["got_upload_request"])
    # download the photo in a 'static' folder
    image_id = message.photo[-1].file_id
    image_path = rf"static\{image_id}.jpg"
    await bot.download(message.photo[-1], destination=image_path)
    # send a query to openai to recognize a yellow car on the photo
    task = asyncio.create_task(ai.recognize_car(image_path))
    # get an answer
    r = await asyncio.gather(task)
    # if there's a yellow car we increase score, add image to a database and congratulate
    if int(r[0]):
        usermanager.increase_score(user_id=message.from_user.id)
        imagemanager.add_image(
            image_id=image_id, user_id=user.id, date=datetime.date.today()
        )
        await message.reply(LEXICON_EN["success_upload"])
    # otherwise we say there's no a yellow car and ask to send a photo again
    else:
        await message.reply(LEXICON_EN["not_success_upload"])
    # remove the image from a 'static' folder because we no longer need this image downloaded
    # if we'll need the image we can get it from a database by its id
    os.remove(image_path)


@router.message(F.text.in_(["Check my balance 📊", "Check my balance", "/balance"]))
async def process_check_balance(message: Message):
    # add user to a database if he's new
    user = message.from_user
    usermanager.check_user(user)
    # checking how many scores has a user
    balance: list[int, int] = usermanager.get_balance(user_id=user.id)
    if balance:
        await message.answer(f"Current scores: {balance[0]}\nSpent scores: {balance[1]}")
    else:
        # this is a some error because after a row "await usermanager.check_user(user)" the program
        # must find a user to a database and put out his balance
        await message.answer(LEXICON_EN["not_success_check"])


@router.message(F.text.in_(["Spend a score 🤜", "Spend a score", "/spend"]))
async def process_spend_score(message: Message, bot: Bot):
    # get a user and his balance
    user_id = message.from_user.id
    balance: list[int, int] = usermanager.get_balance(user_id=user_id)
    if balance and balance[0] > 0:
        # if the user does have a positive balance we answer everything is ok, decrease his current score
        # and mark an uploaded image as used to not use it anymore
        usermanager.decrease_score(user_id=user_id)
        await message.answer(LEXICON_EN["success_spend"])
        image = imagemanager.get_not_used_images(user_id)[0]
        imagemanager.get_used(image)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=image.image_id,
            caption=f'{LEXICON_EN["show_image"]} The photo was uploaded in {image.date}.',
        )
        await message.answer("🤜")
    else:
        # if a user is new and don't have a balance yet or his current score = 0 he can't spend score
        await message.answer(LEXICON_EN["not_success_spend"])


@router.message(F.text.in_(["See all", "see all", "/see_all"]))
async def process_send_all_photos(message: Message, bot: Bot):
    # if a user wants to see all his images we get them from a database
    images = imagemanager.get_all_images(message.from_user.id)
    if not images:
        # if he's new and don't present to a database or didn't make any photos
        # tell him there's no photos
        await message.answer(LEXICON_EN["no_photos"])
    else:
        # if everything is ok we send him every image he made
        for image in images:
            caption = f"The photo was uploaded in {str(image.date)}."
            # extra comments if the image is already used or can be exchanged
            if image.is_used:
                caption += " It's been already used."
            else:
                caption += " It hasn't been used yet."
            await bot.send_photo(
                chat_id=message.chat.id, photo=image.image_id, caption=caption
            )


@router.message(F.file)
async def process_file_instead_of_photo(message: Message):
    await message.answer(LEXICON_EN["file_instead_of_photo"])


@router.message()
async def process_other_messages(message: Message, bot: Bot):
    await message.answer(LEXICON_EN["other_messages"])
