# Database Editor Routing Test Suite

Contains test suite of integration tests for CRUD routes, implemented in `routers`.
The tests in this test suite can be run on their own via `pytest -m "integration"`; 
for other markers, see `pytest.ini` in the top-level directory. 

This test suite is undergoing migration to Hypothesis property-based testing, 
which will noticeably increase its running time but also substantially improve test quality.