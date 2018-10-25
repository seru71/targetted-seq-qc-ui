import os

FOLDERS = ['logs', 'data_acquisition', 'nodes']


def check_folder(folder_name):
    """
    This function makes a folder needed for application to run correctly.
    :param folder_name: str
    :return: None
    """
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)


if __name__ == '__main__':

    [check_folder(folder) for folder in FOLDERS]

    from ngs.ngs import server

    if int(os.environ.get('FLASK_DEBUG', 0)):
        server.run(debug=True)
    else:
        server.run(host='0.0.0.0')
