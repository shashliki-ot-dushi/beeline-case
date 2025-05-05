#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/psf/requests.git"

echo "Запускаем задачу с use_gpt=true..."
resp=$(curl -s -X POST http://localhost:8003/generate-diagram \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\":\"${REPO_URL}\",\"use_gpt\":true}")
echo "RAW RESPONSE: $resp"

JOB=$(echo "$resp" | jq -r .job_id)
if [[ -z "$JOB" || "$JOB" == "null" ]]; then
  echo "Не удалось получить job_id. Проверьте RAW RESPONSE выше."
  exit 1
fi
echo "JOB_ID=$JOB"

echo "Ожидаем завершения задачи..."
while true; do
  status=$(curl -s http://localhost:8003/generate-diagram/$JOB | jq -r .status)
  echo "  Статус: $status"
  if [[ "$status" == "done" ]]; then
    break
  elif [[ "$status" == "failed" ]]; then
    echo "🚨 Задача упала с ошибкой:"
    curl -s http://localhost:8003/generate-diagram/$JOB | jq .error
    exit 1
  fi
  sleep 5
done

echo "Задача завершена, сохраняем элементы..."
curl -s http://localhost:8003/jobs/$JOB/elements | jq . > elements.json
echo "elements.json готов"

echo "Первые 10 компонентов с описаниями:"
jq '.[] | select(.type=="component" and .description!="" ) | {id,description}' elements.json \
  | head -n 20

echo "Готово!"
