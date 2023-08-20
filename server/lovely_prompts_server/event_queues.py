
from fastapi import FastAPI
from asyncio import Queue

def update_event_queues(app: FastAPI, news: dict, project: str):
    for q in app.event_queues[project]:
        q.put_nowait(news)


def append_event_queue(app: FastAPI, project: str):
    event_queue = Queue()
    app.event_queues[project].append(event_queue)
    return event_queue

def remove_event_queue(app: FastAPI, event_queue: Queue, project: str):
    app.event_queues[project].remove(event_queue)

