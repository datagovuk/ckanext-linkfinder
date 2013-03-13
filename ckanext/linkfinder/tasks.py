"""
Score datasets on Sir Tim Berners-Lee's five stars of openness based on mime-type.
"""
import datetime
import mimetypes
import json
import requests
import urlparse
from ckan.lib.celery_app import celery


def _update_task_status(context, data):
    """
    Use CKAN API to update the task status. The data parameter
    should be a dict representing one row in the task_status table.

    Returns the content of the response.
    """
    api_url = urlparse.urljoin(context['site_url'], 'api/action')
    res = requests.post(
        api_url + '/task_status_update', json.dumps(data),
        headers = {'Authorization': context['apikey'],
                   'Content-Type': 'application/json'}
    )
    if res.status_code == 200:
        return res.content
    else:
        raise CkanError('ckan failed to update task_status, status_code (%s), error %s'
                        % (res.status_code, res.content))


@celery.task(name = "linkfinder.search")
def update(context, data):
    """
    TODO: Implement the callbacks
    """
    log = update.get_logger()
    try:
        data = json.loads(data)
        context = json.loads(context)

        result = resource_score(context, data)
        log.info('')

        task_status_data = {}
"""            'entity_id': id,
            'entity_type': u'resource',
            'task_type': 'qa',
            'key': u'openness_score',
            'value': result['openness_score'],
            'last_updated': datetime.datetime.now().isoformat()"""

        api_url = urlparse.urljoin(context['site_url'], 'api/action')
        response = requests.post(
            api_url + '/task_status_update_many',
            json.dumps({'data': task_status_data}),
            headers = {'Authorization': context['apikey'],
                       'Content-Type': 'application/json'}
        )
        if not response.ok:
            err = 'ckan failed to update task_status, error %s' \
                  % response.error
            log.error(err)
            raise CkanError(err)
        elif response.status_code != 200:
            err = 'ckan failed to update task_status, status_code (%s), error %s' \
                  % (response.status_code, response.content)
            log.error(err)
            raise CkanError(err)

        return json.dumps(result)
    except Exception, e:
        log.error('Exception occurred during Linkfinder search: %s: %s', e.__class__.__name__,  unicode(e))
        _update_task_status(context, {
            'entity_id': data['id'],
            'entity_type': u'resource',
            'task_type': 'qa',
            'key': u'celery_task_id',
            'value': unicode(update.request.id),
            'error': '%s: %s' % (e.__class__.__name__,  unicode(e)),
            'last_updated': datetime.datetime.now().isoformat()
        })
        raise
