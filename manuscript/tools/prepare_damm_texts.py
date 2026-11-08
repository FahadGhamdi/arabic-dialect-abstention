#!/usr/bin/env python3
"""Rebuild the private text input for S2 and G2, without running a model.

Requires pandas and pyarrow. The public publisher snapshot is pinned below.
No question text is printed or redistributed. Validate against the released
text-free skeleton by (key, dialect), never by row order.
"""
from pathlib import Path
import argparse, hashlib, json, urllib.request
import pandas as pd

REPO = 'MBZUAI/Dialectal-Arabic-MMLU'
REVISION = 'd7ca5ac8dc2bed489ac00bbfaa3656c3a0bd8c85'
FILE = 'data/test-00000-of-00001.parquet'
EXPECTED_SHA256 = 'e4d548f482f202cd50c1ac0daa5a0a7202fe1fa4c28ccf846cc8d71c552227e2'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skeleton', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    pq = a.output_dir/'publisher.parquet'
    url = f'https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/{FILE}'
    if not pq.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            pq.write_bytes(response.read())
    assert hashlib.sha256(pq.read_bytes()).hexdigest() == EXPECTED_SHA256, "Publisher file checksum mismatch"
    df = pd.read_parquet(pq)
    df['key'] = df['domain']+'|'+df['qid'].astype(str)
    assert not df.duplicated(['key','dialect']).any()
    assert df['choices'].map(len).eq(4).all()
    columns = ['dialect','qid','key','answer','domain']
    expected = pd.read_csv(a.skeleton)[columns].sort_values(['key','dialect']).reset_index(drop=True)
    actual = df[columns].sort_values(['key','dialect']).reset_index(drop=True)
    pd.testing.assert_frame_equal(expected, actual, check_dtype=False)
    df['choices'] = df['choices'].map(lambda x: '|||'.join(x))
    df.to_csv(a.output_dir/'damm.csv', index=False)
    provenance = {'dataset': REPO, 'revision': REVISION, 'file': FILE,
                  'parquet_sha256': hashlib.sha256(pq.read_bytes()).hexdigest(),
                  'csv_sha256': hashlib.sha256((a.output_dir/'damm.csv').read_bytes()).hexdigest(),
                  'rows': len(df), 'keys': int(df.key.nunique()),
                  'skeleton_matches': True, 'private_text_input': True,
                  'historical_inference_snapshot_verified': False}
    (a.output_dir/'DATA_PREPARATION.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({k:v for k,v in provenance.items() if k not in ['csv_sha256']},indent=2))

if __name__ == '__main__':
    main()
