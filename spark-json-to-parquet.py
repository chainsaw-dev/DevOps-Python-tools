#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-11-03 21:38:52 +0000 (Tue, 03 Nov 2015)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon
#

""" PySpark program to convert JSON file(s) to Parquet """

from __future__ import print_function

__author__  = 'Hari Sekhon'
__version__ = '0.2'

try:
    import os
    import sys
    # using optparse rather than argparse for servers still on Python 2.6
    from optparse import OptionParser
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])) + '/lib')
    from HariSekhonUtils import *
    spark_home = os.getenv('SPARK_HOME', None)
    if spark_home:
        sys.path.append(os.path.join(spark_home, 'python'))
        # better to use build dir it's more generic as it's not tied to a specific version
        #sys.path.append(os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))
        sys.path.append(os.path.join(spark_home, 'python/build'))
    else:
        warn("SPARK_HOME not set - probably won't find PySpark libs")
    from pyspark import SparkContext
    from pyspark import SparkConf
    from pyspark.sql import SQLContext
except ImportError, e:
    printerr('module import failed: %s' % e)
    sys.exit(3)
except Exception, e:
    printerr('exception encountered during module import: %s' % e)
    sys.exit(3)

def main():
    parser = OptionParser()
    parser.add_option('-j', '--json', dest='jsonFile', help='JSON input file/dir', metavar='<file/dir>')
    parser.add_option('-p', '--parquetDir', dest='parquetDir', help='Parquet output dir', metavar='<dir>')

    (options, args) = parser.parse_args()

    jsonFile   = options.jsonFile
    parquetDir = options.parquetDir

    if args or not jsonFile or not parquetDir:
        parser.print_help()
        sys.exit(ERRORS['UNKNOWN'])

    conf = SparkConf().setAppName('HS PySpark JSON => Parquet')
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)
    spark_version = sc.version
    print('Spark version detected as %s' % spark_version)
    try:
        major_version = int(spark_version.split('.')[0])
        minor_version = int(spark_version.split('.')[1])
    except ValueError, e:
        die('failed to detect Spark version: %s' % e)
    print('major version = %s, minor version = %s' % (major_version, minor_version))
    # Spark <= 1.3 - API has changed for newer versions
    if major_version <= 1 and minor_version <= 3:
        print('running legacy code for Spark <= 1.3')
        json = sqlContext.jsonFile(jsonFile)
        json.saveAsParquetFile(parquetDir)
    else:
        json = sqlContext.read.json(jsonFile)
        json.write.parquet(parquetDir)

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print("unhandled exception occurred during main() execution: %s" % e)
        sys.exit(ERRORS["UNKNOWN"])
