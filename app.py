import os

from ngs.ngs import server


if __name__ == '__main__':
    if int(os.environ.get('FLASK_DEBUG', 0)):
        server.run(debug=True)
    else:
        server.run(host='0.0.0.0')
