mk1_test
============

This test is used for improving working code.
The test will create a reference data set, so it should be run before refactoring/optimizing code, with code that is known to run on the machine.

1) make sure we have working code, tested on the machine
2) run the test, this will create reference data and a testcase. The test will always pass as the data is genereted with the same codebase
3) refactor / optimize
4) run the test, this will now only create the testcase and compare the machine instruction to the reference data. The test will fail if the data is not the same.
5) if the test passes push data to master

