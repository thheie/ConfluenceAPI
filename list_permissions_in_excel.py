from manage_space_access import Confluence_api

def main():
    confluence_api = Confluence_api()
    confluence_api.write_to_excel()

if __name__ == '__main__':
    main()