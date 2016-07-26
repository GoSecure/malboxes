test:
	pylint malboxes
	./tests/profiles_json_valid.sh
	./tests/config_example_valid.sh

pkg_clean:
	rm -r build/ dist/ malboxes.egg-info/
