import pytest

from lstream_app.main import init_app
from lstream_app.db import init_mongo

from lib.config import BASE_DIR, get_config
TEST_CONFIG_PATH = BASE_DIR / 'config' / 'test_config.yml'


@pytest.fixture
async def cli(loop, aiohttp_client):
    app = init_app()
    app['config'] = get_config(TEST_CONFIG_PATH)
    return await aiohttp_client(app)


async def test_start_event(cli, db):
    resp = await cli.post('/v1/start', json={'test': 'object'})
    assert resp.status == 400, 'В запросе обязательно должен быть type'

    resp = await cli.post('/v1/start', json={'a':'1', 'type':'t1#'})
    assert resp.status == 400, '"type" может содержать только строчные буквы латинского алфавита и цифры'

    resp = await cli.post('/v1/start', json={'a': '1', 'type': 'event1'})
    assert resp.status == 200, 'Сервис должен возвращать 200'

    resp = await cli.post('/v1/start', json={'a': '1', 'type': 'event1'})
    assert resp.status == 200, 'Сервис должен возвращать 200'

    resp = await cli.post('/v1/start', json={'a': '1', 'type': 'event2'})
    assert resp.status == 200, 'Сервис должен возвращать 200'

    result = await db.events.find({'type': 'event1', 'state': 0}).to_list(None)
    assert len(result) == 1, 'Только одна запись для незавершенного события одного типа'

    resp = await cli.post('/v1/finish', json={'type': 'event1'})
    assert resp.status == 200, 'Сервис должен возвращать 200'

    result = await db.events.find({'type': 'event1', 'state': 0}).to_list(None)
    assert len(result) == 0, 'Событие event1 должно завершиться'

    resp = await cli.post('/v1/finish', json={'type': 'event7'})
    assert resp.status == 404, 'Если завершаем не существующую задачу сервис должен возвращать 404'

    result = await db.events.find({'type': 'event2', 'state': 0}).to_list(None)
    assert len(result) == 1, 'Событие event2 должно остаться'


@pytest.fixture
async def db():
    app = init_app()
    app['config'] = get_config(TEST_CONFIG_PATH)

    await init_mongo(app)

    db = app['db']

    await db.command('dropDatabase', 1)

    yield db

    await db.command('dropDatabase', 1)
