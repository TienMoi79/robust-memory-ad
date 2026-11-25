"""Join efficiency with quality without silently losing groups or multiplying rows."""
import argparse
import csv
from pathlib import Path


def read(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f'Empty table: {path}')
    return rows


def join(efficiency, quality):
    keys = ['run_id', 'image_group']
    if 'device' in quality[0]:
        keys.append('device')
    def key(row):
        if any(not row.get(column) for column in keys):
            raise ValueError(f'Missing join key: {keys}')
        return tuple(row[column] for column in keys)
    lookup = {}
    for row in quality:
        item = key(row)
        if item in lookup:
            raise ValueError(f'Duplicate quality key {item}; filter threshold/split first')
        lookup[item] = row
    result = []
    for row in efficiency:
        if row.get('kind') == 'instrumentation_smoke':
            raise ValueError('Smoke instrumentation cannot be joined to model quality')
        item = key(row)
        if item not in lookup:
            raise ValueError(f'No quality row for {item}; keep efficiency separate until supplied')
        result.append({**row, **{f'quality_{name}': value for name, value in lookup[item].items() if name not in keys}})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--efficiency', type=Path, nargs='+', required=True)
    parser.add_argument('--quality', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = join([row for path in args.efficiency for row in read(path)], read(args.quality))
    with args.output.open('x', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict.fromkeys(key for row in rows for key in row)))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
