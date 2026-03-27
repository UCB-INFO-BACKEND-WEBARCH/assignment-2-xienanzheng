from redis import Redis
from rq import Connection, Queue, Worker

from app.jobs import get_redis_url


listen = ["default"]


def main():
    redis_conn = Redis.from_url(get_redis_url())
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()


if __name__ == "__main__":
    main()
