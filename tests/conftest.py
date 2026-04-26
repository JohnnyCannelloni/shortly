import app.core.redis as redis_module


class FakeRedis:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, ex=None):
        self._store[key] = value

    def delete(self, key):
        self._store.pop(key, None)


_fake = FakeRedis()

redis_module.get_redis = lambda: _fake