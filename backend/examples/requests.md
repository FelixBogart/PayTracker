# Example requests for Pay Tracker backend

Set environment variables (or copy `.env.example` to `.env`) before running.

Create a shift (POST):

```bash
curl -X POST http://localhost:8000/shifts/ \
  -H "Content-Type: application/json" \
  -d '{"shift_date":"2026-06-01","points":1200,"tipped_hours":4.5,"untipped_hours":3.0,"point_value":0.007}'
```

Get shifts in a date range (GET):

```bash
curl http://localhost:8000/shifts/2026-06-01/2026-06-15
```

Get monthly summary (GET):

```bash
curl http://localhost:8000/summary/2026-06
```

Health check:

```bash
curl http://localhost:8000/health
```
