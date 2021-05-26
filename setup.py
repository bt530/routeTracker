from setuptools import find_packages, setup

setup(
  name="routeTracker",
  description="A fleet carrier route tracker for Elite: Dangerous",
  packages=find_packages(),
  install_requires=[
    "everett[yaml]",
    "loguru",
    "pyperclip"
  ],
  setup_requires="setuptools_scm",
  use_scm_version=True
)
