#!/bin/sh
# wipes ONLY the local test database and re-seeds it (never touches the live one)
npx wrangler d1 execute scentro-db --local --command="DELETE FROM orders; DELETE FROM attempts; DELETE FROM products; DELETE FROM rules; DELETE FROM settings;" >/dev/null 2>&1
npx wrangler d1 execute scentro-db --local --file=seed.sql >/dev/null 2>&1 && echo local db reset
