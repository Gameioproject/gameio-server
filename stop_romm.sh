#!/bin/bash
SVC=/home/naifa/romm_svc
CONDA_SVC=/home/naifa/miniconda3/envs/romm-svc
export PATH="${CONDA_SVC}/bin:${PATH}"
for p in frontend watcher rqworker rqscheduler backend; do
	if [[ -f "${SVC}/${p}.pid" ]]; then
		pkill -TERM -P "$(cat "${SVC}/${p}.pid")" 2>/dev/null
		kill -TERM "$(cat "${SVC}/${p}.pid")" 2>/dev/null
		rm -f "${SVC}/${p}.pid"
	fi
done
pkill -f "rommfork/backend" 2>/dev/null
pkill -f "vite --host" 2>/dev/null
redis-cli -p 6379 shutdown 2>/dev/null
pg_ctl -D "${SVC}/pgdata" stop -m fast 2>/dev/null
echo "RomM stopped."
