import os

if __name__ == '__main__':
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    from ngs.ngs import server

    if int(os.environ.get('FLASK_DEBUG', 0)):
        server.run(debug=True)
    else:
        server.run(host='0.0.0.0')
