test:
	pylint malboxes
	./tests/config_example_valid.sh
	python -m unittest discover

pkg_clean:
	rm -r build/ dist/ malboxes.egg-info/
