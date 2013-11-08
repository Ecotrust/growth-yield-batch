#!/usr/bin/env python
"""FVS Batch Status
"""
import os
import sys
from tasks import fvs
from models import Task, db
from celery.result import AsyncResult
import json

if __name__ == "__main__":

    full_list = True
    if len(sys.argv) > 1 and sys.argv[1] == 'summary':
        full_list = False

    started = Task.query.all()
    status_count = {}
    trs = []

    for task_record in started:
        task = fvs.AsyncResult(task_record.id)
        if task.status not in status_count.keys():
            status_count[task.status] = 1
        else:
            status_count[task.status] += 1
        trs.append([task_record.id, task.status, task_record.batchdir, task_record.datadir, task_record.result])

    print json.dumps(status_count, indent=2)
    if full_list:
        print "\n".join(['\t'.join(str(x) for x in tr) for tr in trs])
