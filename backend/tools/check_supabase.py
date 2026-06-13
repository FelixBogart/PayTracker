import os
import traceback
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
print('SUPABASE_URL =', url)
base = url or ''
# remove any trailing '/rest/v1' or '/rest/v1/' if present
if '/rest/v1' in base:
    base = base.split('/rest/v1')[0]
base = base.rstrip('/')
print('base used =', base)
try:
    client = create_client(base, key)
    resp = client.table('shift_logs').select('*').execute()
    print('resp.data =', resp.data)
except Exception:
    traceback.print_exc()
