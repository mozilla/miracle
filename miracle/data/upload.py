import json

HISTORY_SCHEMA = [
    # (field name, field type, required)
    ('uri', str, True),
    ('lastAccessTime', int, False),
    ('title', str, False),
]


def validate(data):
    if (not isinstance(data, dict) or
            'history' not in data or
            not isinstance(data['history'], list)):
        return

    history = []
    for entry in data['history']:
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
            history.append(validated_entry)

    output = {}
    if history:
        output['history'] = history

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
    output = json.dumps(validated_data, separators=(',', ':')).encode('utf-8')
    task.cache.set(key, output, ex=3600)
    return True
