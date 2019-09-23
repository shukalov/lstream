from .views import v1_start, v1_finish


def setup_routes(app):

    app.router.add_get('/v1/start', v1_start, name='v1_start')
    app.router.add_post('/v1/start', v1_start, name='v1_start')
    app.router.add_post('/v1/finish', v1_finish, name='v1_finish')
