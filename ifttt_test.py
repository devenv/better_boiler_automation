from connectors.ifttt.ifttt import Ifttt


if __name__ == '__main__':
    Ifttt().send_json({'status': 'test'})