def find_permission_type(operation, target_type):
    if operation == 'read' and target_type == 'space':
        return 'view_space'
    elif operation == 'delete' and target_type == 'space':
        return 'delete_own'
    elif operation == 'create' and target_type == 'page':
        return 'add_page'
    elif operation == 'archive' and target_type == 'page':
        return 'archive_page'
    elif operation == 'delete' and target_type == 'page':
        return 'delete_page'
    elif operation == 'create' and target_type == 'blogpost':
        return 'add_blogg'
    elif operation == 'delete' and target_type == 'blogpost':
        return 'delete_blogg'
    elif operation == 'create' and target_type == 'comment':
        return 'add_comment'
    elif operation == 'delete' and target_type == 'comment':
        return 'delete_comment'
    elif operation == 'create' and target_type == 'attachment':
        return 'add_attachment'
    elif operation == 'delete' and target_type == 'attachment':
        return 'delete_attachment'
    elif operation == 'restrict_content' and target_type == 'space':
        return 'add_delete_restrictions'
    elif operation == 'export' and target_type == 'space':
        return 'export_space'
    elif operation == 'administer' and target_type == 'space':
        return 'administer_space'
    else:
        return 'unknown'

def exel_collumn_mapping():
    collumn_mapping = {'space_key': 1,
                       'user_type': 2,
                       'user_id': 3,
                       'user_name': 4,
                       'view_space': 5,
                       'delete_own': 6,
                       'add_page': 7,
                       'archive_page': 8,
                       'delete_page': 9,
                       'add_blogg': 10,
                       'delete_blogg': 11,
                       'add_comment': 12,
                       'delete_comment': 13,
                       'add_attachment': 14,
                       'delete_attachment': 15,
                       'add_delete_restrictions': 16,
                       'export_space': 17,
                       'administer_space': 18
                       }
    return collumn_mapping
