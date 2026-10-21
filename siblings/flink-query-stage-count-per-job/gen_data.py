import gzip
import os
import random

random.seed(20240611)
os.makedirs('data', exist_ok=True)
S = 1_000_000
GAP = 600 * S
task_rows = []
job_rows = []


def trow(t, jid, idx, m, et, user, sc, prio, cpu, mem):
    return '%d,,%d,%d,%s,%d,%s,%d,%d,%s,%s,0.0001,0' % (t, jid, idx, m, et, user, sc, prio, cpu, mem)


def make_job(jid, user, sc, with_job_events):
    t = random.randint(700, 5000) * S + random.randint(0, 999999)
    if with_job_events:
        job_rows.append('%d,,%d,0,%s,%d,n%d,l%d' % (t - random.randint(1, 50) * S, jid, user, sc, jid, jid))
    nst = random.randint(1, 4)
    nidx = 0
    for s in range(nst):
        if s > 0:
            if random.random() < 0.2:
                t += GAP
            else:
                t += random.randint(601, 2500) * S + random.randint(0, 999999)
        ntask = random.randint(1, 8)
        for k in range(ntask):
            if k > 0:
                if random.random() < 0.1:
                    t += GAP - 1
                else:
                    t += random.randint(0, 400) * S + random.randint(0, 999999)
            if nidx > 0 and random.random() < 0.15:
                idx = random.randrange(nidx)
            else:
                idx = nidx
                nidx += 1
            prio = random.randint(0, 11)
            cpu = random.choice(['0.03125', '0.0625', '0.125'])
            mem = random.choice(['0.01553', '0.02179', '0.04657'])
            task_rows.append(trow(t, jid, idx, '', 0, user, sc, prio, cpu, mem))
            if random.random() < 0.8:
                m = str(300000 + random.randint(0, 40) * 7)
                task_rows.append(trow(t + random.randint(1, 30) * S, jid, idx, m, 1, user, sc, prio, cpu, mem))
                if random.random() < 0.5:
                    task_rows.append(trow(t + random.randint(31, 900) * S, jid, idx, m, random.choice([2, 3, 4]), user, sc, prio, cpu, mem))
    if with_job_events:
        end = t + random.randint(60, 900) * S
        job_rows.append('%d,,%d,%d,%s,%d,n%d,l%d' % (end, jid, 4 if random.random() < 0.7 else 5, user, sc, jid, jid))


for j in range(26):
    jid = 6250000000 + j * 1013 + random.randint(0, 999)
    make_job(jid, 'u%02d' % (j % 7), random.randint(0, 3), True)
for j in range(2):
    jid = 6260000000 + j * 777
    make_job(jid, 'u99', 1, False)

random.shuffle(task_rows)
random.shuffle(job_rows)
with open('data/task_events.csv.gz', 'wb') as f:
    f.write(gzip.compress(('\n'.join(task_rows) + '\n').encode(), mtime=0))
with open('data/job_events.csv.gz', 'wb') as f:
    f.write(gzip.compress(('\n'.join(job_rows) + '\n').encode(), mtime=0))
