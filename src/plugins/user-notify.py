from ipalib.plugins.user import user_add, user_mod, user_del
from ipalib.plugins.basenotify import PreOperation, PostOperation, DeleteOperation

"""Setup callbacks"""
user_add.register_pre_callback(PreOperation('org.freeipa.notifications', '/UserAdded', 'org.freeipa.notifications.user.added'))
user_add.register_post_callback(PostOperation('org.freeipa.notifications', '/UserAdded', 'org.freeipa.notifications.user.added'))
user_mod.register_pre_callback(PreOperation('org.freeipa.notifications', '/UserModified', 'org.freeipa.notifications.user.modified'))
user_mod.register_post_callback(PostOperation('org.freeipa.notifications', '/UserModified', 'org.freeipa.notifications.user.modified'))
user_del.register_pre_callback(DeleteOperation('org.freeipa.notifications', '/UserRemoved', 'org.freeipa.notifications.user.removed', 'pre'))
user_del.register_post_callback(DeleteOperation('org.freeipa.notifications', '/UserRemoved', 'org.freeipa.notifications.user.removed', 'post'))
