import datetime
import re
import logging
from aiohttp import web


async def v1_start(request):

    typ = await check_type(request)

    if not typ:
        return web.HTTPBadRequest()

    logging.info(f'Получен запрос на создание события типа {typ}')

    db = request.app['db']

    await db.events.update_one(
        {
            'type': typ,
            'state': 0,
        },
        {
            '$setOnInsert': {
                'type': typ,
                'state': 0,
                'started_at': datetime.datetime.utcnow(),
                'finished_at': 0
            },
        },
        upsert=True
    )

    return web.Response(text='OK')


async def v1_finish(request):

    typ = await check_type(request)

    if not typ:
        return web.HTTPBadRequest()

    logging.info(f'Получен запрос на завершение события типа {typ}')

    db = request.app['db']

    result = await db.events.update_one(
        {
            'type': typ,
            'state': 0,
        },
        {
            '$set':
                {
                    'state': 1,
                    'finished_at': datetime.datetime.utcnow()
                }
        }
    )

    if not result.matched_count:
        logging.error('Незавершенного события такого типа в БД не найдено')
        return web.HTTPNotFound()

    return web.Response(text='OK')


async def check_type(request):

    try:
        json_request_dict = await request.json()
        typ = json_request_dict['type']

    except Exception as e:
        logging.error(f'Неправильный запрос({e})')
        return False

    if not re.match('^[a-z0-9]+$', typ):
        logging.error('Ошибка формата type')
        return False
    return typ
