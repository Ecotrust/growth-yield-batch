from tasks import add, square
import random
import time
from celery import chain

tasklist = []
for i in range(10):
    x = random.randint(0, 20)
    y = random.randint(0, 20)
    print "Starting task to add then square the result", x, "+", y
    res = chain(add.s(x, y) | square.s()).apply_async()
    tasklist.append((x, y, res))

alldone = False

while not alldone:
    alldone = True
    for x, y, tt in tasklist:
        if not tt.result:
            alldone = False
        print " %s :: (%s + %s) ^ 2 is %s" % (tt.status, x, y, tt.result)
    time.sleep(1)
    print "--------------------------------------"
