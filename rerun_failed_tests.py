import xml.etree.ElementTree as ET
import subprocess

def parse_test_results(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    failed_tests = []
    for testcase in root.iter('testcase'):
        if testcase.find('failure') is not None:
            failed_tests.append(testcase.get('name'))
    return failed_tests

def rerun_failed_tests(failed_tests):
    if failed_tests:
        print("Initial failed tests:", failed_tests)
        failed_test_names = ' '.join(failed_tests)
        result = subprocess.run(f'pytest --headless {failed_test_names}', shell=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    else:
        print('All tests passed.')

if __name__ == "__main__":
    failed_tests = parse_test_results('test-reports/junit_intg.xml')
    rerun_failed_tests(failed_tests)
