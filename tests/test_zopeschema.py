##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests of ZConfig schemas."""

import unittest
import ZConfig

from ZConfig.tests.test_schema import BaseSchemaTest

try:
    True
except NameError:
    True = 1
    False = 0
    
class StreamHandler:
    pass

class Formatter:
    pass

def _assert(expr):
    if not expr:
        raise AssertionError, expr

def _get_arglist(s):
    pos = []
    kw = {}
    args = s.split(',')
    args = filter(None, args)
    while args:
        arg = args.pop(0)
        try:
            if '=' in arg:
                k,v=arg.split('=', 1)
                k = k.strip()
                v = v.strip()
                kw[k] = eval(v)
            else:
                arg = arg.strip()
                pos.append(eval(arg))
        except SyntaxError:
            if not args:
                raise
            args[0] = '%s, %s' % (arg, args[0])
    return pos, kw

def _get_classandargs(constructor):
    klass, args = parse_constructor(constructor)
    pos, kw = get_arglist(args)
    return klass, pos, kw

def _parse_constructor(value):
    parenmsg = (
        'Invalid constructor (unbalanced parenthesis in "%s")' % value
        )
    openparen = value.find('(')
    if openparen < 0:
        raise ValueError(parenmsg)
    klass = value[:openparen]
    if not value.endswith(')'):
        raise ValueError(parenmsg)
    arglist = value[openparen+1:-1]
    return klass, arglist

def _importer(name):
    if not "." in name:
        raise ValueError("unloadable datatype name: " + `name`)
    components = name.split('.')
    start = components[0]
    g = globals()
    package = __import__(start, g, g)
    modulenames = [start]
    for component in components[1:]:
        modulenames.append(component)
        try:
            package = getattr(package, component)
        except AttributeError:
            n = '.'.join(modulenames)
            package = __import__(n, g, g, component)
    return package

def ipaddr(value):
    if value is None:
        return
    import socket
    try:
        socket.gethostbyaddr(value)
    except socket.error:
        socket.gethostbyname(value)

def directory(value):
    _assert(os.path.isdir(value))
    return value

def dirname(value):
    _assert( os.path.exists(os.path.dirname(value)) )
    return value

def constructor(value):
    klass, arglist = _parse_constructor(value)
    _importer(klass)
    pos, kw = _get_arglist(arglist)
    return klass, pos, kw

class ZopeSchemaTestCase(BaseSchemaTest):

    # tests

    def test_defaultbug(self):
        schema, conf = self.load_both('zope.xml', 'empty.conf')

    def test_load_populated(self):
        schema, conf = self.load_both('zope.xml', 'zope-allpopulated.conf')
        self.assertEqual(conf.zope_home, '.')
        self.assertEqual(conf.instance_home, '.')
        self.assertEqual(conf.software_home, '.')
        self.assertEqual(conf.client_home, '.')
        self.assertEqual(conf.debug_mode, True)
        self.assertEqual(conf.effective_user, 'chrism')
        self.assertEqual(conf.enable_product_installation, True)
        self.assertEqual(conf.locale, None)
        self.assertEqual(conf.zserver_threads, 4)
        self.assertEqual(conf.python_check_interval, 500)
        self.assertEqual(conf.use_daemon_process, True)
        self.assertEqual(conf.zserver_read_only_mode, False)
        self.assertEqual(conf.pid_filename, 'Z2.pid')
        self.assertEqual(conf.lock_filename, 'Z2.lock')
        constructor = ('ZConfig.tests.test_zopeschema.StreamHandler', [], {})
        formatter   = ('ZConfig.tests.test_zopeschema.Formatter', [], {})
        self.assertEqual(conf.event.level, 10)
        self.assertEqual(conf.event.handlers[0].constructor, constructor)
        self.assertEqual(conf.event.handlers[0].formatter, formatter)
        self.assertEqual(conf.event.handlers[1].constructor, constructor)
        self.assertEqual(conf.event.handlers[1].formatter, formatter)
        self.assertEqual(conf.trace.level, 20)
        self.assertEqual(conf.trace.handlers[0].constructor, constructor)
        self.assertEqual(conf.trace.handlers[0].formatter, formatter)
        self.assertEqual(conf.access.level, 30)
        self.assertEqual(conf.access.handlers[0].constructor, constructor)
        self.assertEqual(conf.access.handlers[0].formatter, formatter)
        self.assertEqual(conf.structured_text_header_level, 3)
        self.assertEqual(conf.maximum_security_manager_stack_size, 100)
        self.assertEqual(conf.publisher_profile_file, 'bleah')
        self.assertEqual(conf.module, 'Zope')
        self.assertEqual(conf.cgi_environment_variables,
                         [['A','1'], ['B', '2']])
        self.assertEqual(conf.dns_ip_address, '127.0.0.1')
        self.assertEqual(conf.http_realm, 'Zope')
        servers = conf.servers
        for n in range(len(servers)):
            if n == 0:
                self.assertEqual(servers[n].port, 8080)
                self.assertEqual(servers[n].force_connection_close, False)
            if n == 1:
                self.assertEqual(servers[n].port, 8081)
                self.assertEqual(servers[n].force_connection_close, True)
            if n == 2:
                self.assertEqual(servers[n].port, 8021)
            if n == 3:
                self.assertEqual(servers[n].resource, '/foo/bar/fcgi.soc')
        self.assertEqual(conf.automatically_quote_dtml_request_data, True)
        self.assertEqual(conf.skip_authentication_checking, True)
        self.assertEqual(conf.skip_ownership_checking, True)
        self.assertEqual(conf.maximum_number_of_session_objects, 1000)
        self.assertEqual(conf.session_add_notify_script_path, '/flab')
        self.assertEqual(conf.session_delete_notify_script_path, '/flab')
        self.assertEqual(conf.session_timeout_minutes, 20)
        self.assertEqual(conf.suppress_all_access_rules, True)
        self.assertEqual(conf.suppress_all_site_roots, True)
        self.assertEqual(conf.database_quota_size, 100)
        self.assertEqual(conf.read_only_database, False)
        self.assertEqual(conf.zeo_client_name, 'chris')
        databases = conf.databases
        for n in range(len(databases)):
            if n == 0:
                self.assertEqual(databases[n].mount_point, '/')
                self.assertEqual(databases[n].storages[0].file_name, 'foo/bar')
            if n == 1:
                self.assertEqual(databases[n].mount_point, '/mount')
                self.assertEqual(databases[n].storages[0].file_name, 'foo/baz')
                self.assertEqual(databases[n].storages[1].file_name, 'bar/baz')
            self.assertEqual(databases[n].db_class, 'ZODB.DB')
            self.assertEqual(databases[n].cache_size, 5000)
            self.assertEqual(databases[n].pool_size, 7)
            self.assertEqual(databases[n].cache_deactivate_after, 60)
            self.assertEqual(databases[n].version_pool_size, 3)
            self.assertEqual(databases[n].version_cache_size, 100)
            self.assertEqual(databases[n].version_cache_deactivate_after, 10)

def test_suite():
    return unittest.makeSuite(ZopeSchemaTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
