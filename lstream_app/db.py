from motor.motor_asyncio import AsyncIOMotorClient


async def init_mongo(app):

    mongo_config = app['config']['mongo']
    db = AsyncIOMotorClient(mongo_config['host'], mongo_config['port'])[mongo_config['db']]
    await events_setup(db)
    app['db'] = db

    return db


async def events_setup(db):

    indexes = await db.events.index_information()

    if 'type_state' not in indexes:

        await db.events.create_index(
            [
                ('type', 1),
                ('state', 1)
            ],
            name='type_state'
        )
