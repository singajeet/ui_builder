from datetime import datetime
import asyncio
from aiohttp.hdrs import METH_POST
from aiohttp.web import json_response
from aiohttp.web import StreamResponse, Response
from aiohttp.web_exceptions import HTTPFound
from aiohttp_jinja2 import template


@template('index.jinja')
async def index(request):
    """
    This is the view handler for the "/" url.

    :param request: the request object see http://aiohttp.readthedocs.io/en/stable/web_reference.html#request
    :return: context for the template.
    """
    # Note: we return a dict not a response because of the @template decorator
    return {
        'title': request.app['name'],
        'intro': "Success! you've setup a basic aiohttp app.",
    }


async def process_form(request):
    new_message, missing_fields = {}, []
    fields = ['username', 'message']
    data = await request.post()
    for f in fields:
        new_message[f] = data.get(f)
        if not new_message[f]:
            missing_fields.append(f)

    if missing_fields:
        return 'Invalid form submission, missing fields: {}'.format(', '.join(missing_fields))

    # hack: if no database is available we use a plain old file to store messages.
    # Don't do this kind of thing in production!
    # This very simple storage uses "|" to split fields so we need to replace "|" in the username
    new_message['username'] = new_message['username'].replace('|', '')
    with request.app['settings'].MESSAGE_FILE.open('a') as f:
        now = datetime.now().isoformat()
        f.write('{username}|{timestamp}|{message}\n'.format(timestamp=now, **new_message))

    raise HTTPFound(request.app.router['messages'].url_for())


@template('messages.jinja')
async def messages(request):
    if request.method == METH_POST:
        # the 302 redirect is processed as an exception, so if this coroutine returns there's a form error
        form_errors = await process_form(request)
    else:
        form_errors = None
    # we're not using sessions so there's no way to pre-populate the username
    username = ''

    return {
        'title': 'Message board',
        'form_errors': form_errors,
        'username': username,
    }

async def package_handler(request):
    """docstring for package_handler"""
    _response = StreamResponse()
    action = request.match_info.get('action', None)
    if action is not None:
        if action == 'index':
            return await _package_index()
        elif action == 'count':
            local_index_count = request.match_info.get('local_index', '0')
            if local_index_count is not None:
                server_index_count = '2'
                if local_index_count == server_index_count:
                    return json_response({'result':'True'})
                else:
                    return json_response({'result':'False'})
        elif action == 'download':
            package_name = request.match_info.get('package_name', 'NA')
            return Response(body='Download for package <a href=#>{0}</a> will start soon'.format(package_name))
        else:
            return Response(body='Invalid value provided for parameter "action"')
    else:
        _ahref_index = '<li>Get package <a href="/message?action=index">Index</a></li>'
        _ahref_count = '<li>Get package <a href="/message?action=count&local_index={0}">count</a></li>'.format('2')
        _ahref_download = '<li>Get <a href="/message?action=download&package_name={0}">{1}</a></li>'.format('package1','Package1')
        _list = '<div><ul>{0}{1}{2}</ul></div>'.format(_ahref_index, _ahref_count, _ahref_download)
        _message = '<center><div>Welcome to package index service. You have below options to work with this service:</div></center><div/><div/>{0}'.format(_list)
        h_body = '<html><head><title>PackageService</title></head><body>{0}</body></html>'.format(_message)
        _response.content_length = len(h_body)
        _response.content_type = 'text/html'
        binary = h_body.encode('utf8')
        await _response.prepare(request)
        _response.write(binary)
        return _response

async def _package_index():
    """docstring for _package_index"""
    server_pkg_index={
        'package1': '1.0.0',
        'package2': '1.5.0',
        'package3': '2.0.0',
        'package4': '2.5.0',
                     }
    await asyncio.sleep(1)
    return json_response(server_pkg_index)

async def message_data(request):
    """
    As an example of aiohttp providing a non-html response, we load the actual messages for the "messages" view above
    via ajax using this endpoint to get data. see static/message_display.js for details of rendering.
    """
    messages = []
    if request.app['settings'].MESSAGE_FILE.exists():
        # read the message file, process it and populate the "messages" list
        with request.app['settings'].MESSAGE_FILE.open() as msg_file:
            for line in msg_file:
                if not line:
                    # ignore blank lines eg. end of file
                    continue
                # split the line into it constituent parts, see process_form above
                username, ts, message = line.split('|', 2)
                # parse the datetime string and render it in a more readable format.
                ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f'))
                messages.append({'username': username, 'timestamp':  ts, 'message': message})
        messages.reverse()
    return json_response(messages)
