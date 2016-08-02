test:
	pylint malboxes
	./tests/config_example_valid.sh
	./tests/profiles_json_valid.py

pkg_clean:
	rm -r build/ dist/ malboxes.egg-info/
