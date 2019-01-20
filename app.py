import os

from data_share.KeyGeneration import KeyGeneration

FOLDERS = ['logs', 'data_acquisition', 'nodes', 'keys']


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
    keys = KeyGeneration()
    keys.load_or_generate()

    from ngs.ngs import server

    # if int(os.environ.get('FLASK_DEBUG', 0)):
    #     server.run(debug=True, port=8080, host='0.0.0.0')
    # else:
    #     server.run(host='0.0.0.0')
    server.run(host='0.0.0.0')
