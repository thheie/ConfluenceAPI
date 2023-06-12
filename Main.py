from manage_space_access import Confluence_api

def main():
    confluence_api = Confluence_api()
    # confluence_api.set_space_permission('ID','test1_user_group')
    # confluence_api.delete_space_permission('ID', 31555092496)
    confluence_api.get_space_permissions()
    confluence_api.find_types()
    # confluence_api.decode_space_persmissions()


if __name__ == '__main__':
    main()