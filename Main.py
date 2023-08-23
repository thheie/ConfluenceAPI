from manage_space_access import Confluence_api

def main():
    confluence_api = Confluence_api()
    # confluence_api.get_space_permissions()
    # confluence_api.decode_space_persmissions()
    # confluence_api.bach_delete_user_permissions('5c1912aab4d5d75a3b513a57')
    #confluence_api.set_space_permission('ACME', '5be17e704b76d050e2971ab2', 'user', 'create', 'page')
    # confluence_api.delete_space_permission('ACME', 31557910529)
    # confluence_api.get_space_permissions()
    # confluence_api.find_types()
    # confluence_api.decode_space_persmissions()
    # confluence_api.group_permissions()
    # confluence_api.bach_delete_permissions('NOR', user_email='thh@computas.com')
    # confluence_api.bach_delete_user_permissions()
    #confluence_api.write_to_excel()
    confluence_api.replace_user_groups('test group old', 'test group new', space_list=['ID','NOR'])

if __name__ == '__main__':
    main()