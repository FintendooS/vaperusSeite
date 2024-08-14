import sys
sys.path.insert(0,'/var/www/vapeApp')

from website import app as application

if __name__ == "__main__":
    application.run(debug=True)