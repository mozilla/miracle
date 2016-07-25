import json

HISTORY_SCHEMA = [
    # (field name, field type, required)
    ('url', str, True),
    ('start_time', int, False),
    ('duration', int, False),
]


def json_encode(data):
    return json.dumps(
        data, separators=(',', ':'), sort_keys=True).encode('utf-8')


def validate(data):
    if (not isinstance(data, dict) or
            'sessions' not in data or
            not isinstance(data['sessions'], list)):
        return

    sessions = []
    for entry in data['sessions']:
        if not isinstance(entry, dict):
            continue

        missing_field = False
        validated_entry = {}
        for field, type_, required in HISTORY_SCHEMA:
            value = entry.get(field)
            if not isinstance(value, type_):
                value = None

            if not value and required:
                missing_field = True
                break

            validated_entry[field] = value

        if not missing_field:
            sessions.append(validated_entry)

    output = {}
    if sessions:
        output['sessions'] = sessions

    return output


def main(task, user, payload):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return False

    validated_data = validate(data)
    if not validated_data:
        return False

    key = ('user_%s' % user).encode('ascii')
    output = json_encode(validated_data)
    task.cache.set(key, output, ex=3600)
    return True
