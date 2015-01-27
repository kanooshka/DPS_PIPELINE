# The conf.py defines global settings information for the projex.docgen
# module
import os

# specify the title to display at the top of the documentation 
# specify the version to display at the top of the documentation
# module.__name__ will be used by default for MODULE_TITLE
# module.__version__ will be used by default for MODULE_VERSION
#MODULE_TITLE = ''
#MODULE_VERSION = '0.0.0'

# Specify the company information to display at the bottom of the documentation
COMPANY_TITLE = 'Projex Software, LLC'
COMPANY_URL   = 'http://www.projexsoftware.com'

# copyright options
SHOW_DOCGEN_LINK = True

# Define title bar links to other information.  The links here are a list of
# tuples containing (<str> title, <str> url) and will become the links that
# will be displayed on the navigation of the documentation
NAVIGATION_LINKS = [
    ('HOME', '%(base_url)s/index.html'),
    ('API REFERENCE', '%(base_url)s/api/index.html'),
    ('DOCS HOME', 'http://docs.projexsoftware.com'),
]

# Defines a list of modules that should be ignored when generating documentation
IGNORE = []

# Define the theme options.  You can specify the name of the default theme
# you wish to use (found in projex/resources/docgen) or the path to a custom
# theme that you wish to use
THEME = os.environ.get('PROJEX_DOCGEN_THEME', 'base')
THEME_PATH = os.environ.get('PROJEX_DOCGEN_THEMEPATH', '')