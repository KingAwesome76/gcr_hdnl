def allowed(headers, secret):
    allow = [False]
    for key in secret.keys():
        header_key = headers.get(key, "None")
        if isinstance(secret[key], list):
            allow.append(header_key in secret[key])
            continue
        allow.append(secret[key] == header_key)
    return True in allow
