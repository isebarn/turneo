def querystring(path, dictionary):
    return path + "?" + "&".join(["{}={}".format(k, v) for k, v in dictionary.items()])
