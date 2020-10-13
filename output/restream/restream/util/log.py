from enum import Enum
import xml.etree.ElementTree as ET
from datetime import datetime

class Log:

    class Type(Enum):
        NoLog = 0
        Error = 1
        Warning = 2
        Info = 3
        All = 4

    LOG_LEVEL = Type.All

    CLASS_NAME = ''
    WRITE_TO_XML = False
    XML_FILE_PATH = ''
    TEST_SUITES_NAME = 'End-2-End'
    TEST_SUITE_NAME = ''

    TEST_RESULTS = []
    TESTS_FAILED = 0

    @staticmethod
    def error(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Error.value:
            print( "\033[1;31m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Warning.value:
            print( "\033[1;33m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def info(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Info.value:
            print( "\033[0m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def happy(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Info.value:
            print( "\033[1;32m" + " ".join(map(str,args)), **kwargs)

    #ci

    @staticmethod
    def start_ci_test(name: str):
        print('\033[0m      Start', name)

    @staticmethod
    def finish_ci_test(name: str, passed: bool):
        print('\033[0m      Stop', name)
        if passed:
            print('\033[0m ----------------------------------- Passed')
        else:
            print('\033[0m ----------------------------------- Failed')
        
        if Log.WRITE_TO_XML:
            Log.add_xml_test_result(name, passed)

    @staticmethod
    def write_xml():
        if not Log.TEST_RESULTS:
            Log.error('No xml test results added.')
            return

        # testsuites
        testsuites = ET.Element('testsuites')
        testsuites.set('tests', '1')
        testsuites.set('failures', str(Log.TESTS_FAILED))
        testsuites.set('disabled', '0')
        testsuites.set('errors', '0')
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        testsuites.set('timestamp', timestamp)
        testsuites.set('time', '0')
        testsuites.set('name', Log.TEST_SUITES_NAME)
        # testsuite
        testsuite = ET.SubElement(testsuites, 'testsuite')
        testsuite.set('name', Log.TEST_SUITE_NAME)
        testsuite.set('tests', str(len(Log.TEST_RESULTS)))
        testsuite.set('failures', str(Log.TESTS_FAILED))
        testsuite.set('disabled', '0')
        testsuite.set('errors', '0')
        testsuite.set('time', '0')
        # add tests
        for test in Log.TEST_RESULTS:
            testsuite.append(test)

        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(testsuites)
        tree.write(Log.XML_FILE_PATH,
            xml_declaration=True,encoding='utf-8',
            method="xml")

    @staticmethod
    def add_xml_test_result(test_name: str, passed: bool):
        test = ET.Element('testcase')
        test.set('name', test_name)
        test.set('status', 'run')
        test.set('result', 'completed')
        test.set('time', '0')
        test.set('classname', Log.CLASS_NAME)
        Log.TEST_RESULTS.append(test)
