from aiofile import async_open
from aiofiles.os import remove


async def read_file(name_file, mode='r'):
    async with async_open(name_file, mode=mode) as afp:
        return await afp.read()


async def write_file(name_file, data, mode='w'):
    async with async_open(name_file, mode=mode) as afp:
        await afp.write(data)


async def remove_file(name_file):
    try:
        await remove(name_file)
        return True
    except FileNotFoundError:
        return False
