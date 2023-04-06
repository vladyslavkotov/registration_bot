import logging, re
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import aiohttp

host="http://127.0.0.1:8000/"

url_new_user=f"{host}new_user/"
url_check_username=f"{host}check_username/"
url_login=f"{host}login/"

logging.basicConfig(level=logging.INFO)

token = "6120533190:AAFr5st-RIEYoma6kYe3mDivZqs6JTV-RHU"
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

regex_username = r'(?=[0-9a-z_]{4,20})(?=^[a-z])'
regex_password = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"

class Form(StatesGroup):
   username = State()
   password1 = State()
   password2 = State()
   userpicname = State()
# -----------------------------------------START---------------------------------------
@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
   text = f'Greetings, {message.from_user.full_name}. Please enter your username.\nA username can be 4 to 20 characters long and may contain lowercase letters, digits and underscores.\nA username must only start with a letter.'
   await Form.username.set()
   await message.reply(text)

# --------------------------------------GET USERNAME------------------------------------
@dp.message_handler(state=Form.username)
async def get_username(message: types.Message, state: FSMContext):
   if re.findall(regex_username, message.text):
      logging.info("valid username")
      async with state.proxy() as data:
         data['username'] = message.text
         post_data={"username":data['username']}

      async with aiohttp.ClientSession() as session:
         async with session.post(url_check_username, data=post_data) as post_req:
            response=await post_req.text()
            logging.info(response)

            if "available" in response:
               await Form.next()
               return await message.reply("Please enter your password. Your password must be at least 8 characters long, contain >=1 uppwercase latter, >=1 lowercase letter, >=1 digit and >=1 special character.")

            else:
               logging.info("username taken")
               return await message.reply("This username is taken. Please come up with another username.")
   else:
      logging.info("invalid username")
      return await message.reply("Please enter a valid username")

# --------------------------------------GET PASSWORD1------------------------------------
@dp.message_handler(state=Form.password1)
async def get_pw1(message: types.Message, state: FSMContext):
   if re.findall(regex_password, message.text):
      logging.info("valid password1")
      async with state.proxy() as data:
         data['password1'] = message.text
      await Form.next()
      return await message.reply("Please confirm your password")
   else:
      logging.info("invalid password")
      return await message.reply("Please enter a valid password")

# --------------------------------------GET PASSWORD2------------------------------------
@dp.message_handler(state=Form.password2)
async def get_pw2(message: types.Message, state: FSMContext):
   if re.findall(regex_password, message.text):
      async with state.proxy() as data:
         if data['password1'] == message.text:
            data['password2']= message.text
            logging.info("pw confirmed")
            await Form.next()
            return await message.reply("Please upload your userpic")
         else:
            logging.info("pw mismatch")
            await Form.password1.set()
            data['password1']=''
            return await message.reply("Your passwords dont match. Please try again.")
   else:
      logging.info("pw mismatch")
      await Form.password1.set()
      async with state.proxy() as data:
         data['password1'] = ''
      return await message.reply("Your passwords dont match. Please try again.")

# --------------------------------------GET USERPIC------------------------------------
@dp.message_handler(content_types=[types.ContentType.ANY], state=Form.userpicname)
async def get_userpic(message: types.Message, state: FSMContext):
   if message.photo:
      logging.info("found image")
      async with state.proxy() as data:
         userpic=await message.photo[-1].get_url()
         logging.info(userpic)
         post_data={"username":data['username'],"password":data['password2'],"userpic":userpic}

         async with aiohttp.ClientSession() as session:
            async with session.post(url_new_user, data=post_data) as post_req:
               logging.info(await post_req.text())
               await session.close()
               await message.reply(f"Your registration is complete. Please <a href='{url_login}'>log in</a>",parse_mode=types.ParseMode.HTML)
               return await state.finish()
   else:
      logging.info("no image")
      return await message.reply("Please upload a photo")

executor.start_polling(dp, skip_updates=True)