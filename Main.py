from manage_space_access import Confluence_api

def main():
    confluence_api = Confluence_api()
    #confluence_api.set_space_permission('ACME', '5be17e704b76d050e2971ab2', 'user', 'create', 'page')
    # confluence_api.delete_space_permission('ACME', 31557910529)
    confluence_api.get_space_permissions()
    # confluence_api.find_types()
    confluence_api.decode_space_persmissions()
    confluence_api.bach_delete_permissions('ACME', user_email='thh@computas.com')

if __name__ == '__main__':
    main()