#!/bin/bash
# Starts the full RomM stack (Postgres, Redis, backend, RQ worker/scheduler, watcher, frontend)
# Logs go to ~/romm_svc/logs/. Stop with ./stop_romm.sh
set -e
ROOT=/home/naifa/rommfork
SVC=/home/naifa/romm_svc
CONDA_SVC=/home/naifa/miniconda3/envs/romm-svc
mkdir -p "${SVC}/logs"

export PATH="${CONDA_SVC}/bin:${HOME}/.local/bin:${PATH}"
export LD_LIBRARY_PATH="${CONDA_SVC}/lib:${LD_LIBRARY_PATH-}"
source ~/.nvm/nvm.sh && nvm use 24 >/dev/null

set -a
source "${ROOT}/.env"
set +a

# --- Postgres ---
if ! pg_ctl -D "${SVC}/pgdata" status >/dev/null 2>&1; then
	pg_ctl -D "${SVC}/pgdata" -l "${SVC}/logs/postgres.log" -o "-p 5432 -k /tmp" start
fi
# --- Redis ---
if ! redis-cli -p 6379 ping >/dev/null 2>&1; then
	redis-server --port 6379 --dir "${SVC}/redis" --daemonize yes --logfile "${SVC}/logs/redis.log" --save "3600 1"
fi
sleep 1

# --- Backend API (runs migrations on start) ---
cd "${ROOT}/backend"
nohup uv run python main.py >"${SVC}/logs/backend.log" 2>&1 &
echo $! >"${SVC}/backend.pid"

# --- RQ scheduler + worker (background tasks: scans, metadata) ---
RQ_REDIS_HOST=${REDIS_HOST} RQ_REDIS_PORT=${REDIS_PORT} RQ_REDIS_DB=0 \
	nohup uv run rqscheduler --path "${ROOT}/backend" >"${SVC}/logs/rqscheduler.log" 2>&1 &
echo $! >"${SVC}/rqscheduler.pid"

PYTHONPATH="${ROOT}/backend" RQ_REDIS_URL="redis://${REDIS_HOST}:${REDIS_PORT}/0" \
	nohup uv run rq worker --path "${ROOT}/backend" --worker-class handler.rq_worker.RomMWorker \
	--logging_level "${LOGLEVEL:-INFO}" high default low >"${SVC}/logs/rqworker.log" 2>&1 &
echo $! >"${SVC}/rqworker.pid"

# --- Filesystem watcher (auto-detect new ROMs) ---
nohup uv run watchfiles --target-type command 'uv run python watcher.py' "${ROMM_BASE_PATH}/library" \
	>"${SVC}/logs/watcher.log" 2>&1 &
echo $! >"${SVC}/watcher.pid"

# --- Frontend (Vite dev server on :3000) ---
cd "${ROOT}/frontend"
nohup npm run dev >"${SVC}/logs/frontend.log" 2>&1 &
echo $! >"${SVC}/frontend.pid"

echo "RomM starting. Web UI: http://localhost:3000   API: http://localhost:5000/docs"
echo "Logs: ${SVC}/logs/"
