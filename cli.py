#!/usr/bin/env python3

import sys
import json
import functools

import requests
import click

import client

_EP_TOKENS = 'tokens'

def auth_required(func):

    @functools.wraps(func)
    def _wrapper(obj, *args, **kwargs):

        if not obj['connection'].is_authenticated():

            # Token
            if obj['token']:
                obj['connection'].authenticate(token=obj['token'])

            # Username:Password
            else:
                if not obj['username']:
                    obj['username'] = click.prompt("Username", hide_input=False)
                if not obj['password']:
                    obj['password'] = click.prompt("Password", hide_input=True)
                obj['connection'].authenticate(username=obj['username'], password=obj['password'])

        # Call Function
        return func(obj, *args, **kwargs)

    return _wrapper

@click.group()
@click.option('--url', default=None, prompt=True, help='API URL')
@click.option('--username', default=None, help='API Username')
@click.option('--password', default=None, help='API Password')
@click.option('--token', default=None, help='API Token')
@click.pass_context
def cli(ctx, url, username, password, token):
    """COG CLI"""

    # Setup Context
    ctx.obj = {}
    ctx.obj['url'] = url
    ctx.obj['username'] = username
    ctx.obj['password'] = password
    ctx.obj['token'] = token
    ctx.obj['connection'] = client.Connection(ctx.obj['url'])

@cli.group(name='file')
@click.pass_obj
def fle(obj):

    # Setup Client Class
    obj['files'] = client.Files(obj['connection'])

@fle.command(name='create')
@click.option('--path', default=None, prompt=True, type=click.File('rb'), help='File Path')
@click.option('--extract', is_flag=True, help='Control whether file is extracted')
@click.pass_obj
@auth_required
def fle_create(obj, path, extract):

    fle_list = obj['files'].create(path, extract)
    click.echo("{}".format(fle_list))

@fle.command(name='list')
@click.option('--tst_uid', default=None, help='Only list files attached to a specific test')
@click.option('--sub_uid', default=None, help='Only list files attached to a specific submission')
@click.pass_obj
@auth_required
def fle_list(obj, tst_uid, sub_uid):

    fle_list = obj['files'].list(tst_uid=tst_uid, sub_uid=sub_uid)
    click.echo("{}".format(fle_list))

@fle.command(name='show')
@click.option('--uid', default=None, prompt=True, help='File UUID')
@click.pass_obj
@auth_required
def fle_show(obj, uid):

    fle = obj['files'].show(uid)
    click.echo("{}".format(fle))

@fle.command(name='delete')
@click.option('--uid', default=None, prompt=True, help='File UUID')
@click.pass_obj
@auth_required
def fle_delete(obj, uid):

    fle = obj['files'].delete(uid)
    click.echo("{}".format(fle))

@cli.group()
@click.pass_obj
def assignment(obj):

    # Setup Client Class
    obj['assignments'] = client.Assignments(obj['connection'])

@assignment.command(name='create')
@click.option('--name', default=None, prompt=True, help='Assignment Name')
@click.option('--env', default=None, prompt=True, help='Assignment Environment')
@click.pass_obj
@auth_required
def assignment_create(obj, name, env):

    asn_list = obj['assignments'].create(name, env)
    click.echo("{}".format(asn_list))

@assignment.command(name='list')
@click.pass_obj
@auth_required
def assignment_list(obj):

    asn_list = obj['assignments'].list()
    click.echo("{}".format(asn_list))

@assignment.command(name='show')
@click.option('--uid', default=None, prompt=True, help='Assignment UUID')
@click.pass_obj
@auth_required
def assignment_show(obj, uid):

    asn = obj['assignments'].show(uid)
    click.echo("{}".format(asn))

@assignment.command(name='delete')
@click.option('--uid', default=None, prompt=True, help='Assignment UUID')
@click.pass_obj
@auth_required
def assignment_delete(obj, uid):

    asn = obj['assignments'].delete(uid)
    click.echo("{}".format(asn))

@cli.group()
@click.pass_obj
def test(obj):

    # Setup Client Class
    obj['tests'] = client.Tests(obj['connection'])

@test.command(name='create')
@click.option('--asn_uid', default=None, prompt=True, help='Assignment UUID')
@click.option('--name', default=None, prompt=True, help='Test Name')
@click.option('--tester', default=None, prompt=True, help='Test Module')
@click.option('--maxscore', default=None, prompt=True, help='Max Score')
@click.pass_obj
@auth_required
def test_create(obj, asn_uid, name, tester, maxscore):

    tst_list = obj['tests'].create(asn_uid, name, tester, maxscore)
    click.echo("{}".format(tst_list))

@test.command(name='list')
@click.pass_obj
@auth_required
def test_list(obj):

    tst_list = obj['tests'].list()
    click.echo("{}".format(tst_list))

@test.command(name='show')
@click.option('--uid', default=None, prompt=True, help='Test UUID')
@click.pass_obj
@auth_required
def test_show(obj, uid):

    tst = obj['tests'].show(uid)
    click.echo("{}".format(tst))

@test.command(name='delete')
@click.option('--uid', default=None, prompt=True, help='Test UUID')
@click.pass_obj
@auth_required
def test_delete(obj, uid):

    tst = obj['tests'].delete(uid)
    click.echo("{}".format(tst))

# @cli.group()
# def file():
#     pass

# @file.command(name='create')
# @click.option('--path', default=None, prompt=True, type=click.File('rb'), help='File Path')
# @click.option('--extract', is_flag=True, help='Control whether file is extracted')
# @click.pass_obj
# def file_create(obj, path, extract):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Creating file...")
#     fle_list = client.file_create(obj['url'], obj['connection'], path, extract)
#     click.echo("Files:\n {}".format(fle_list))

# @file.command(name='list')
# @click.option('--tst_uid', default=None, help='Only Show Files from Test with UUID tst_uid')
# @click.pass_obj
# def file_list(obj, tst_uid):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Listing files...")
#     fle_list = client.file_list(obj['url'], obj['connection'], tst_uid=tst_uid)
#     click.echo("Files:\n {}".format(fle_list))

# @file.command(name='show')
# @click.option('--uid', default=None, prompt=True, help='File UUID')
# @click.pass_obj
# def file_show(obj, uid):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Showing file...")
#     fle = client.file_show(obj['url'], obj['connection'], uid)
#     click.echo("File '{}':\n {}".format(uid, fle))

# @file.command(name='show')
# @click.option('--uid', default=None, prompt=True, help='File UUID')
# @click.pass_obj
# def file_delete(obj, uid):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Deleting file...")
#     fle = client.file_delete(obj['url'], obj['connection'], uid)
#     click.echo("Deleted file '{}':\n {}".format(uid, fle))

# @cli.group()
# def util():
#     pass

# @util.command(name='replace-files')
# @click.option('--path', default=None, prompt=True, type=click.File('rb'), help='File Path')
# @click.option('--extract', is_flag=True, help='Control whether file is extracted')
# @click.option('--tst_uid', default=None, prompt=True, help='Test UUID')
# @click.pass_obj
# def util_replace_files(obj, path, extract, tst_uid):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Listing old files...")
#     old_fle_list = client.file_list(obj['url'], obj['connection'], tst_uid=tst_uid)
#     click.echo("Old files:\n {}".format(old_fle_list))

#     click.echo("Removing old files...")
#     rem_fle_list = client.test_file_remove(obj['url'], obj['connection'], tst_uid, old_fle_list)
#     click.echo("Attached files:\n {}".format(rem_fle_list))

#     click.echo("Deleting old files...")
#     for fle_uid in old_fle_list:
#         click.echo("Deleting file '{}'...".format(fle_uid))
#         fle = client.file_delete(obj['url'], obj['connection'], fle_uid)

#     click.echo("Creating new files...")
#     new_fle_list = client.file_create(obj['url'], obj['connection'], path, extract)
#     click.echo("New files:\n {}".format(new_fle_list))

#     click.echo("Attaching files...")
#     tst_fle_list = client.test_file_add(obj['url'], obj['connection'], tst_uid, new_fle_list)
#     click.echo("Attached files:\n {}".format(tst_fle_list))

# @util.command(name='token-show')
# @click.pass_obj
# def util_token_show(obj):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("{} Token: '{}'".format(obj['username'], obj['token']))

# @util.command(name='setup-assignment')
# @click.option('--asn_name', default=None, prompt=True, help='Assignment Name')
# @click.option('--env', default=None, prompt=True, help='Assignemnt Environment')
# @click.option('--tst_name', default=None, prompt=True, help='Test Name')
# @click.option('--tester', default=None, prompt=True, help='Test Module')
# @click.option('--maxscore', default=None, prompt=True, help='Max Score')
# @click.option('--path', default=None, prompt=True, type=click.File('rb'), help='File Path')
# @click.option('--extract', is_flag=True, help='Control whether file is extracted')
# @click.pass_obj
# def setup_assignment(obj, asn_name, env, tst_name, tester, maxscore, path, extract):

#     if not obj['connection']:
#         obj['connection'] = _connect(obj)

#     click.echo("Creating assignment...")
#     asn_list = client.assignment_create(obj['url'], obj['connection'], asn_name, env)
#     click.echo("Created assignments:\n {}".format(asn_list))
#     asn_uid = asn_list[0]

#     click.echo("Creating test...")
#     tst_list = client.assignment_test_create(obj['url'], obj['connection'], asn_uid, tst_name, tester, maxscore)
#     click.echo("Created tests:\n {}".format(tst_list))
#     tst_uid = tst_list[0]

#     click.echo("Creating files...")
#     new_fle_list = client.file_create(obj['url'], obj['connection'], path, extract)
#     click.echo("Created files:\n {}".format(new_fle_list))

#     click.echo("Attaching files...")
#     tst_fle_list = client.test_file_add(obj['url'], obj['connection'], tst_uid, new_fle_list)
#     click.echo("Attached files:\n {}".format(tst_fle_list))

if __name__ == '__main__':
    sys.exit(cli())
