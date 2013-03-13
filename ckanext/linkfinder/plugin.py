import logging
import ckan.lib.helpers as h
import ckan.plugins as p
from ckan.plugins import implements, toolkit
from ckanext.linkfinder.model import make_uuid
from ckan.logic import get_action

log = logging.getLogger('ckanext.linkfinder')

class LinkFinderPlugin(p.SingletonPlugin):
    implements(p.IConfigurer, inherit=True)
    implements(p.ITemplateHelpers, inherit=True)
    implements(p.IDomainObjectModification, inherit=True)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    def get_helpers(self):
        """
        A dictionary of extra helpers that will be available to provide
        ga report info to templates.
        """
        return {
            'linkfinder_installed': lambda: True,
        }

    def notify(self, entity, operation=None):
        """
        if not isinstance(entity, model.Resource):
            return

        if operation:
            if operation == model.DomainObjectOperation.new:
                self._create_task(entity)
        else:
            # if operation is None, resource URL has been changed, as the
            # notify function in IResourceUrlChange only takes 1 parameter
            self._create_task(entity)
        """

    def _create_task(self, resource):
        user = get_action('get_site_user')({'model': model,
                                            'ignore_auth': True,
                                            'defer_commit': True}, {})
        context = json.dumps({
            'site_url': self.site_url,
            'apikey': user.get('apikey')
        })
        data = json.dumps(resource_dictize(resource, {'model': model}))

        task_id = make_uuid()
        task_status = {
            'entity_id': resource.id,
            'entity_type': u'resource',
            'task_type': u'qa',
            'key': u'celery_task_id',
            'value': task_id,
            'error': u'',
            'last_updated': datetime.now().isoformat()
        }
        task_context = {
            'model': model,
            'user': user.get('name'),
        }

        get_action('task_status_update')(task_context, task_status)
        celery.send_task("qa.update", args=[context, data], task_id=task_id)
