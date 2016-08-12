# import httplib
import http
import mimetypes


def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    # h = httplib.HTTP(host)
    # h = http.client.HTTPConnection(host)
    # h.putrequest('POST', selector)
    # h.putheader('content-type', content_type)
    # h.putheader('content-length', str(len(body)))
    # h.endheaders()
    # h.send(body)

    headers = {"Content-type": content_type, 'content-length': str(len(body))}
    conn = http.client.HTTPConnection(host)
    conn.request('POST', '', headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)

    conn.close()
    # errcode, errmsg, headers = h.getreply()
    return h.file.read()


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value.decode('GB2312', 'ignore'))
    L.append('--' + BOUNDARY + '--')
    L.append('')
    # body = CRLF.join(str(i, encoding="utf-8") for i in L)
    print(type(L[1]))
    body = bytes(CRLF.join(L), encoding='utf-8')
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
