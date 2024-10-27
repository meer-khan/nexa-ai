import base64

def binary_into_utf8(img): 
    return base64.b64encode(img).decode('utf-8')
    