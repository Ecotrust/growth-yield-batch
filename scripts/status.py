#!/bin/env python
"""FVS Batch Status
"""
import os
import sys
from tasks import fvs
from models import Task, db
from celery.result import AsyncResult

if __name__ == "__main__":

    started = Task.query.all()

    for task_record in started:
        task = fvs.AsyncResult(task_record.id)
        print "\t".join(str(x) for x in [task_record.id, task.status, task_record.batchdir, task_record.datadir, task_record.result])
